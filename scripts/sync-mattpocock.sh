#!/usr/bin/env bash
# Sync mattpocock/skills into this repo with a 3-way merge so local
# in-place tweaks under skills/ are preserved across upstream releases.
#
# Merge base = skills/ tree at the currently pinned tag (fetched on demand).
# Ours       = skills/ in this repo (may include local tweaks).
# Theirs     = skills/ tree at the new upstream tag.
set -euo pipefail

REPO="${MATTPCOCK_SKILLS_REPO:-mattpocock/skills}"
PIN_FILE=".upstream/mattpocock-version"
OURS_DIR="skills"
LOCAL_DIR="skills/local"
PR_BODY_FILE="${PR_BODY_FILE:-.github/sync-pr-body.md}"

cd "$(git rev-parse --show-toplevel)"

if [[ ! -f "$PIN_FILE" ]]; then
  echo "error: missing $PIN_FILE" >&2
  exit 1
fi

current="$(tr -d '[:space:]' <"$PIN_FILE")"
if [[ -z "$current" ]]; then
  echo "error: $PIN_FILE is empty" >&2
  exit 1
fi

if [[ -n "${MATTPCOCK_SKILLS_REF:-}" ]]; then
  latest="$MATTPCOCK_SKILLS_REF"
else
  latest="$(gh api "repos/${REPO}/releases/latest" --jq .tag_name)"
fi

echo "Pinned:  ${current}"
echo "Target:  ${latest}"

emit_no_sync() {
  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    echo "synced=false" >>"$GITHUB_OUTPUT"
    echo "version=${current}" >>"$GITHUB_OUTPUT"
  fi
}

if [[ "$current" == "$latest" ]]; then
  echo "Already up to date — nothing to sync."
  emit_no_sync
  exit 0
fi

tmp="$(mktemp -d)"
cleanup() { rm -rf "$tmp"; }
trap cleanup EXIT

clone_skills() {
  local ref="$1"
  local dest="$2"
  echo "Fetching ${REPO}@${ref}..."
  git clone --depth 1 --branch "$ref" "https://github.com/${REPO}.git" "$dest"
  if [[ ! -d "$dest/skills" ]]; then
    echo "error: ${REPO}@${ref} has no skills/ directory" >&2
    exit 1
  fi
}

clone_skills "$current" "$tmp/base-repo"
clone_skills "$latest" "$tmp/theirs-repo"
base_dir="$tmp/base-repo/skills"
theirs_dir="$tmp/theirs-repo/skills"

list_rel_files() {
  local root="$1"
  (cd "$root" && find . -type f ! -path './.git/*' | sed 's|^\./||' | sort)
}

mapfile -t base_files < <(list_rel_files "$base_dir")
mapfile -t theirs_files < <(list_rel_files "$theirs_dir")

declare -A base_set theirs_set all_set
for f in "${base_files[@]}"; do
  [[ -n "$f" ]] || continue
  base_set["$f"]=1
  all_set["$f"]=1
done
for f in "${theirs_files[@]}"; do
  [[ -n "$f" ]] || continue
  theirs_set["$f"]=1
  all_set["$f"]=1
done

conflicts=0
notes=()
conflict_lines=()
added_files=()
updated_files=()
removed_files=()
merged_files=()

is_under_local() {
  case "$1" in
    local|local/*) return 0 ;;
    *) return 1 ;;
  esac
}

ensure_parent() {
  mkdir -p "$(dirname "$1")"
}

for rel in $(printf '%s\n' "${!all_set[@]}" | sort); do
  if is_under_local "$rel"; then
    continue
  fi

  base_file="${base_dir}/${rel}"
  ours_file="${OURS_DIR}/${rel}"
  theirs_file="${theirs_dir}/${rel}"

  in_base=${base_set[$rel]+1}
  in_theirs=${theirs_set[$rel]+1}
  in_ours=0
  [[ -e "$ours_file" ]] && in_ours=1

  # Deleted upstream
  if [[ -n "$in_base" && -z "$in_theirs" ]]; then
    if [[ "$in_ours" -eq 0 ]]; then
      continue
    fi
    if cmp -s "$ours_file" "$base_file"; then
      rm -f "$ours_file"
      rmdir -p "$(dirname "$ours_file")" 2>/dev/null || true
      removed_files+=("${ours_file}")
      notes+=("removed ${ours_file} (deleted upstream)")
    else
      conflicts=$((conflicts + 1))
      conflict_lines+=("- ${ours_file} — upstream deleted this file, but you have local edits. Decide: keep your copy, or delete it.")
      notes+=("CONFLICT: keep local ${ours_file}; upstream deleted it")
    fi
    continue
  fi

  # Added upstream
  if [[ -z "$in_base" && -n "$in_theirs" ]]; then
    if [[ "$in_ours" -eq 0 ]]; then
      ensure_parent "$ours_file"
      cp "$theirs_file" "$ours_file"
      added_files+=("${ours_file}")
      notes+=("added ${ours_file}")
    elif cmp -s "$ours_file" "$theirs_file"; then
      continue
    else
      conflicts=$((conflicts + 1))
      conflict_lines+=("- ${ours_file} — new upstream file conflicts with an existing local file. Compare both and pick/merge manually.")
      notes+=("CONFLICT: ${ours_file} exists locally and is new upstream; kept local copy")
    fi
    continue
  fi

  # Present in both base and theirs
  if [[ "$in_ours" -eq 0 ]]; then
    ensure_parent "$ours_file"
    cp "$theirs_file" "$ours_file"
    added_files+=("${ours_file}")
    notes+=("restored ${ours_file} from upstream")
    continue
  fi

  if cmp -s "$ours_file" "$base_file"; then
    if ! cmp -s "$ours_file" "$theirs_file"; then
      ensure_parent "$ours_file"
      cp "$theirs_file" "$ours_file"
      updated_files+=("${ours_file}")
      notes+=("updated ${ours_file} (no local edits)")
    fi
    continue
  fi

  if cmp -s "$base_file" "$theirs_file"; then
    # Local edits only; keep ours
    continue
  fi

  if cmp -s "$ours_file" "$theirs_file"; then
    continue
  fi

  # Both changed — 3-way merge
  if git merge-file -p "$ours_file" "$base_file" "$theirs_file" >"$tmp/merged" 2>"$tmp/merge-err"; then
    if ! cmp -s "$ours_file" "$tmp/merged"; then
      cp "$tmp/merged" "$ours_file"
      merged_files+=("${ours_file}")
      notes+=("merged ${ours_file}")
    fi
  else
    cp "$tmp/merged" "$ours_file"
    conflicts=$((conflicts + 1))
    conflict_lines+=("- ${ours_file} — both you and upstream changed this file. Open it and resolve git conflict markers, then remove the markers.")
    merged_files+=("${ours_file}")
    notes+=("CONFLICT: ${ours_file} (resolve conflict markers)")
  fi
done

printf '%s\n' "$latest" >"$PIN_FILE"
mkdir -p "$LOCAL_DIR"

# Upstream-only file delta (pinned tag → new tag), independent of local merge result
upstream_added=()
upstream_removed=()
upstream_modified=()
for rel in $(printf '%s\n' "${!all_set[@]}" | sort); do
  if is_under_local "$rel"; then
    continue
  fi
  in_base=${base_set[$rel]+1}
  in_theirs=${theirs_set[$rel]+1}
  if [[ -n "$in_base" && -z "$in_theirs" ]]; then
    upstream_removed+=("skills/${rel}")
  elif [[ -z "$in_base" && -n "$in_theirs" ]]; then
    upstream_added+=("skills/${rel}")
  elif ! cmp -s "${base_dir}/${rel}" "${theirs_dir}/${rel}"; then
    upstream_modified+=("skills/${rel}")
  fi
done

# Upstream release notes (best-effort)
release_body="$(gh api "repos/${REPO}/releases/tags/${latest}" --jq .body 2>/dev/null || true)"
if [[ -z "${release_body//[[:space:]]/}" ]]; then
  release_body="_No release notes published for this tag._"
fi

compare_url="https://github.com/${REPO}/compare/${current}...${latest}"

write_file_list() {
  local title="$1"
  shift
  echo "### ${title}"
  if [[ "$#" -eq 0 ]]; then
    echo "_None._"
  else
    for item in "$@"; do
      printf -- '- `%s`\n' "$item"
    done
  fi
  echo
}

{
  echo "## Upstream sync: \`${current}\` → \`${latest}\`"
  echo
  echo "Automated sync of [${REPO}](https://github.com/${REPO}) into this repo."
  echo
  echo "- **Compare:** ${compare_url}"
  echo "- **Release:** https://github.com/${REPO}/releases/tag/${latest}"
  echo "- **Conflict count:** ${conflicts}"
  echo
  echo "## Summary of upstream changes"
  echo
  echo "What changed in mattpocock/skills between the pins (before applying your local tweaks):"
  echo
  write_file_list "Added upstream" ${upstream_added[@]+"${upstream_added[@]}"}
  write_file_list "Modified upstream" ${upstream_modified[@]+"${upstream_modified[@]}"}
  write_file_list "Removed upstream" ${upstream_removed[@]+"${upstream_removed[@]}"}
  echo "How that landed in this repo after 3-way merge:"
  echo
  write_file_list "Applied cleanly (no local edits on that file)" ${updated_files[@]+"${updated_files[@]}"} ${added_files[@]+"${added_files[@]}"} ${removed_files[@]+"${removed_files[@]}"}
  write_file_list "Merged with your local edits" ${merged_files[@]+"${merged_files[@]}"}
  echo "## Merge conflicts to resolve"
  echo
  if [[ "$conflicts" -eq 0 ]]; then
    echo "_None. Safe to review the diff and merge._"
  else
    echo "Resolve these before merging this PR:"
    echo
    printf '%s\n' "${conflict_lines[@]}"
    echo
    echo "Search the branch for conflict markers with:"
    echo
    echo '```bash'
    echo "rg -n '^(<<<<<<<|=======|>>>>>>>)' skills/"
    echo '```'
  fi
  echo
  echo "## Upstream release notes (\`${latest}\`)"
  echo
  echo "$release_body"
  echo
  echo "## Review checklist"
  echo
  echo "- [ ] Read the summary and release notes above"
  echo "- [ ] Resolve every item under **Merge conflicts to resolve**"
  echo "- [ ] Skim the PR diff for skills you customize in place"
  echo "- [ ] Confirm \`skills/local/\` was not touched"
  echo "- [ ] Confirm \`.upstream/mattpocock-version\` is \`${latest}\`"
} >"$PR_BODY_FILE"

echo "---- sync notes ----"
if [[ ${#notes[@]} -eq 0 ]]; then
  echo "(pin updated; no skill file content changes detected)"
else
  printf '%s\n' "${notes[@]}"
fi
echo "Conflicts: ${conflicts}"
echo "Wrote PR body to ${PR_BODY_FILE}"

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "synced=true"
    echo "version=${latest}"
    echo "previous=${current}"
    echo "conflicts=${conflicts}"
    echo "pr_body_file=${PR_BODY_FILE}"
  } >>"$GITHUB_OUTPUT"
fi

if [[ "$conflicts" -gt 0 ]]; then
  echo "Sync completed with conflicts that need manual resolution in the PR."
fi

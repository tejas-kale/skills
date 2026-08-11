#!/usr/bin/env bash
# Sync mattpocock/skills into this repo with a 3-way merge so local
# in-place tweaks under skills/ are preserved across upstream releases.
set -euo pipefail

REPO="${MATTPCOCK_SKILLS_REPO:-mattpocock/skills}"
PIN_FILE=".upstream/mattpocock-version"
BASE_DIR=".upstream/mattpocock"
OURS_DIR="skills"
LOCAL_DIR="skills/local"

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

if [[ "$current" == "$latest" && "${FORCE_SYNC:-}" != "1" ]]; then
  echo "Already up to date."
  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    echo "synced=false" >>"$GITHUB_OUTPUT"
    echo "version=${current}" >>"$GITHUB_OUTPUT"
  fi
  exit 0
fi

tmp="$(mktemp -d)"
cleanup() { rm -rf "$tmp"; }
trap cleanup EXIT

echo "Fetching ${REPO}@${latest}..."
git clone --depth 1 --branch "$latest" "https://github.com/${REPO}.git" "$tmp/repo"
theirs_dir="$tmp/repo/skills"

if [[ ! -d "$theirs_dir" ]]; then
  echo "error: upstream checkout has no skills/ directory" >&2
  exit 1
fi

list_rel_files() {
  local root="$1"
  (cd "$root" && find . -type f ! -path './.git/*' | sed 's|^\./||' | sort)
}

mapfile -t base_files < <(list_rel_files "$BASE_DIR")
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
changed=0
notes=()

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

  base_file="${BASE_DIR}/${rel}"
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
      changed=1
      notes+=("removed ${ours_file} (deleted upstream)")
    else
      conflicts=$((conflicts + 1))
      notes+=("CONFLICT: keep local ${ours_file}; upstream deleted it")
    fi
    continue
  fi

  # Added upstream
  if [[ -z "$in_base" && -n "$in_theirs" ]]; then
    if [[ "$in_ours" -eq 0 ]]; then
      ensure_parent "$ours_file"
      cp "$theirs_file" "$ours_file"
      changed=1
      notes+=("added ${ours_file}")
    elif cmp -s "$ours_file" "$theirs_file"; then
      continue
    else
      # Local file exists without upstream ancestry — keep ours, flag it
      conflicts=$((conflicts + 1))
      notes+=("CONFLICT: ${ours_file} exists locally and is new upstream; kept local copy")
    fi
    continue
  fi

  # Present in both base and theirs
  if [[ "$in_ours" -eq 0 ]]; then
    ensure_parent "$ours_file"
    cp "$theirs_file" "$ours_file"
    changed=1
    notes+=("restored ${ours_file} from upstream")
    continue
  fi

  if cmp -s "$ours_file" "$base_file"; then
    if ! cmp -s "$ours_file" "$theirs_file"; then
      ensure_parent "$ours_file"
      cp "$theirs_file" "$ours_file"
      changed=1
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
      changed=1
      notes+=("merged ${ours_file}")
    fi
  else
    cp "$tmp/merged" "$ours_file"
    changed=1
    conflicts=$((conflicts + 1))
    notes+=("CONFLICT: ${ours_file} (resolve conflict markers)")
  fi
done

# Refresh pristine upstream mirror
rm -rf "$BASE_DIR"
mkdir -p "$BASE_DIR"
cp -a "${theirs_dir}/." "$BASE_DIR/"
printf '%s\n' "$latest" >"$PIN_FILE"

# Ensure local skills dir survives
mkdir -p "$LOCAL_DIR"

echo "---- sync notes ----"
if [[ ${#notes[@]} -eq 0 ]]; then
  echo "(pin/mirror updated; no skill file content changes)"
else
  printf '%s\n' "${notes[@]}"
fi
echo "Conflicts: ${conflicts}"

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "synced=true"
    echo "version=${latest}"
    echo "previous=${current}"
    echo "conflicts=${conflicts}"
  } >>"$GITHUB_OUTPUT"
fi

if [[ "$conflicts" -gt 0 ]]; then
  echo "Sync completed with conflicts that need manual resolution in the PR."
fi

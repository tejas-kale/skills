---
name: macos-disk-cleanup
description: Reclaim disk space on macOS. Use when storage is low, disk usage needs investigating, or the user asks what is safe to delete.
---

# macOS Disk Cleanup

Measure before deleting, spend the safe wins first, and treat anything holding local-only state as **confirm-first** — it needs the user's explicit go-ahead, because nothing re-downloads it.

## Process

1. Measure top-level and home usage.
2. Drill into the largest user-owned directories.
3. Classify every candidate as a quick win or confirm-first, and present the two groups separately.
4. Run the quick wins; ask before each confirm-first deletion.
5. Re-measure and report the delta.

Done when every consumer above ~1G is classified, each confirm-first deletion was individually approved, and a before/after `df -h /` frames what the run actually freed.

## Measure

```bash
# 1. Top-level
du -sh /System /Users /private /Applications /Library 2>/dev/null | sort -rh

# 2. Home breakdown
du -sh ~/Library ~/Code ~/Downloads 2>/dev/null | sort -rh

# 3. Library breakdown
du -sh ~/Library/Application\ Support/* ~/Library/Caches/* ~/Library/Group\ Containers/* 2>/dev/null | sort -rh | head -20
```

Aim the drill-down with the user's profile:

| Profile | Check first | Typical gain |
|---|---|---|
| Developer | Homebrew, uv/npm/pip, DerivedData, simulators | 10–20G |
| AI/ML user | Ollama unused models, HuggingFace, LM Studio | 5–15G |
| Chrome-heavy | OptGuideOnDeviceModel, GoogleUpdater | ~5G |

## Quick Wins

Everything here rebuilds or re-downloads on demand — run without asking.

| Command | Frees | Notes |
|---|---|---|
| `brew cleanup --prune=all` | 2–10G | Cached installers |
| `uv cache clean --force` | 1–10G | uv package cache |
| `npm cache clean --force` | 500M–2G | npm cache |
| `pip3 cache purge` | 100–500M | pip cache |
| `pre-commit clean` | 200–500M | pre-commit envs |
| `rm -rf ~/Library/Developer/Xcode/DerivedData` | 500M–5G | Rebuilds on demand |
| `xcrun simctl delete unavailable` | 1–10G | Unused iOS simulators |

## Path catalog

For the per-path verdicts — Chrome, AI model caches, dev tool caches, and the confirm-first app data — read [`references/paths.md`](references/paths.md) before proposing any deletion outside the quick wins above.

## After Cleanup

`df -h /` lags because APFS local snapshots still hold the freed blocks. Check `tmutil listlocalsnapshots /` and tell the user they thin themselves within ~24h — the number is already correct underneath, so the next move is to wait rather than clean again.

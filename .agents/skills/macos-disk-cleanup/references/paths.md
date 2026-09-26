# Path catalog

Per-path verdicts for [`macos-disk-cleanup`](../SKILL.md). **Safe** paths rebuild or re-download on demand; **confirm-first** paths hold local-only state and need the user's explicit go-ahead.

## Chrome

Quit Chrome before deleting any of these.

| Path | Verdict | Notes |
|---|---|---|
| `~/Library/Application Support/Google/Chrome/OptGuideOnDeviceModel` | Safe | Gemini Nano weights; re-downloads if AI features are used |
| `~/Library/Application Support/Google/Chrome/Default/Service Worker` | Safe | PWA offline caches |
| `~/Library/Application Support/Google/GoogleUpdater` | Safe | Old update packages |
| `~/Library/Application Support/Google/Chrome/Default/Extensions` | Confirm-first | Removes installed extensions |

```bash
rm -rf ~/Library/"Application Support"/Google/Chrome/OptGuideOnDeviceModel
rm -rf ~/Library/"Application Support"/Google/GoogleUpdater
```

## AI model caches

| Path | Verdict | Notes |
|---|---|---|
| `~/.cache/huggingface` | Safe | Re-downloads on demand |
| `~/.cache/lm-studio` | Safe if LM Studio is unused | Extensions + binaries |
| `~/.cache/lm-studio/hub` | Safe if LM Studio is unused | Model weights cache |
| `~/Library/Application Support/io.datasette.llm/whisper.cpp` | Safe if the `llm` CLI is unused | Whisper model cache |
| `~/.ollama/models` | Confirm-first | Deletes local LLMs — large re-downloads |

Remove one Ollama model through the CLI, which prunes its blobs correctly:

```bash
ollama rm <model-name>
```

With the server offline, delete the manifest by hand:

```bash
rm -rf ~/.ollama/models/manifests/registry.ollama.ai/library/<model>
```

Blobs under `~/.ollama/models/blobs` are shared between models. Prune one only after confirming no remaining manifest references it.

## Dev tool caches

| Path | Verdict | Notes |
|---|---|---|
| `~/.cache/codex-runtimes` | Safe | Re-fetches on use |
| `~/Library/Application Support/virtualenv` | Safe | Orphaned venvs |
| `~/Library/Python/3.x/site-packages` | Safe for versions of Python no longer installed | Check `ls /Library/Frameworks/Python.framework/Versions` first |
| `~/.cargo` | Confirm-first | Rust toolchain + crates — Rust stops working until reinstalled |

## Confirm-first app data

Each of these loses local history or state.

| App | Path | Risk |
|---|---|---|
| Signal | `~/Library/Application Support/Signal` | Local messages lost permanently; no cloud backup |
| Telegram | `~/Library/Group Containers/6N38VWS5BX.ru.keepcoder.Telegram` | Re-syncs from server; local media lost |
| WhatsApp | `~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared` | Local media and history |
| Zed | `~/Library/Application Support/Zed` | Editor state |

## Keep

`~/Library/Application Support/Claude/vm_bundles` stays while Claude.app is installed. Once the app is uninstalled the whole `~/Library/Application Support/Claude` tree is orphaned and safe.

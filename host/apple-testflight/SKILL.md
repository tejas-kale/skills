---
name: apple-testflight
description: Ship the user's iOS and macOS apps to TestFlight. Use for a TestFlight build or upload, App Store Connect, signing or bundle IDs, or setting up an app's Xcode project with xcodegen.
---

# Shipping an Apple app to TestFlight

Every app is an xcodegen project: `project.yml` is the source of truth and the generated `.xcodeproj` is gitignored.
Releases run locally through [`release.sh`](release.sh) in this folder; GitHub Actions only runs tests. Uploading is
outward-facing: upload only when the user asks for it in this session.

Steps marked **User** are ones only the user can do: walk them through one at a time and wait for their confirmation.

## Account facts

- Team `NDMG62GXZA` (paid membership). Bundle ID `com.tejaskale.<app>`; an app on iOS and Mac uses that one ID for
  both targets and one App Store Connect record with both platforms. Extensions append a suffix
  (`com.tejaskale.<app>.ShareExtension`).
- App Store Connect API key: `ASC_KEY_ID` and `ASC_ISSUER_ID` are exported in `~/.zshrc`, which the Bash tool does not
  load. The `.p8` lives only in the login Keychain, item `deepwell.asc-api-key` (base64; a team key despite the name,
  shared by every app). `release.sh` loads both itself.
- `xcode-select` points at CommandLineTools: prefix `xcodebuild` and `swift test` with
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`. `python3` on PATH is broken; use `/usr/bin/python3`.
- Signing is automatic. `-allowProvisioningUpdates` makes Xcode create the cloud-managed distribution certificate and
  App Store profiles, so the Keychain needs no distribution certificate. Export signs through the Apple ID in Xcode;
  when `xcodebuild` cannot see it, export fails with "No Accounts" even though Xcode's settings show the account.
  **User** removes the account in Xcode > Settings > Apple Accounts and adds it again.

## The project spec

`project.yml` carries, in `settings.base`: `DEVELOPMENT_TEAM: NDMG62GXZA`, `CODE_SIGN_STYLE: Automatic`,
`MARKETING_VERSION`, an integer `CURRENT_PROJECT_VERSION` (quoted, the first one in the file; `release.sh` bumps it),
`PRODUCT_BUNDLE_IDENTIFIER`, and `ASSETCATALOG_COMPILER_APPICON_NAME: AppIcon`. Each upload blocker below is a
rejection when missing:

- **Icon**: asset catalog `AppIcon` listed in each app target's `sources`. iOS takes one 1024×1024 full-bleed square
  with no alpha (the system rounds it); the Mac takes the 16–512@2x sizes with the artwork as an 824 px rounded tile
  on a transparent 1024 canvas.
- **Export compliance**: `INFOPLIST_KEY_ITSAppUsesNonExemptEncryption: NO` when the app uses only Apple's standard
  encryption, so TestFlight does not hold each build for the question.
- **Usage strings**: an `INFOPLIST_KEY_NS…UsageDescription` for every privacy-sensitive API the code calls (speech,
  microphone, camera, photos, contacts, location…). Grep the sources for the frameworks before the first upload.
- **Mac target**: `ENABLE_HARDENED_RUNTIME: YES`, `INFOPLIST_KEY_LSApplicationCategoryType`, and an `entitlements`
  block with `com.apple.security.app-sandbox: true` plus only the access the code needs (files, network, iCloud).
  Every Mac extension needs the sandbox too, and `PROVISIONING_PROFILE_REQUIRED: YES` so it gets a profile.

When the Swift package is in the repo, reference it under `packages:` with `path:` relative to the spec, and depend on
its products. Run `xcodegen generate` in the spec's folder, then build each app scheme unsigned
(`CODE_SIGNING_ALLOWED=NO`) for `generic/platform=iOS` and `generic/platform=macOS` to prove the spec before signing.

## Releasing

1. The tree is clean apart from the release and the package tests pass.
2. First upload of a new app only:
   1. The first signed archive registers the bundle ID (`release.sh` archives with `-allowProvisioningUpdates`).
   2. **User** creates the app record: appstoreconnect.apple.com > Apps > + > New App. Tick iOS and macOS for a
      two-platform app; a name unique on the whole App Store; primary language; the bundle ID from the dropdown (it
      appears once registered, so run `release.sh --export-only` first if it is missing); the app's short name as SKU;
      full access.
3. Run `release.sh` from this skill's folder: `<skill dir>/release.sh --spec <path>/project.yml --ios <iOS scheme> --mac <Mac scheme>`
   with `run_in_background` (processing takes minutes). One bump serves both platforms. Per platform it archives,
   exports, checks the package against the blockers above, validates, uploads, and waits for processing.
4. On failure, read the reason, fix it, then re-run:
   - failed before upload (archive, export, check, validate): `--keep-build`;
   - rejected in processing: without `--keep-build`, since an upload spends its number even when rejected;
   - "Your team has no devices": the development-signed archive needs a registered device of that platform; the
     message says how to register one.
5. Done when every requested platform printed "processed". Commit the bumped `CURRENT_PROJECT_VERSION` and push.
6. First upload only: **User** opens App Store Connect > the app > TestFlight, creates an internal group with their
   own Apple ID and adds the build. Builds then reach the TestFlight app on their devices.

Never launch a locally signed build whose bundle ID matches the TestFlight install on this Mac: it shares the real
app's data container and can migrate the real data.

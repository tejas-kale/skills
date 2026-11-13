#!/usr/bin/env bash
# Archive, export, check, validate and upload one xcodegen app to TestFlight, for iOS, macOS or both.
#
#   release.sh --ios SCHEME --mac SCHEME     bump CURRENT_PROJECT_VERSION once, ship both platforms with that number
#   release.sh --ios SCHEME                  one platform only
#   --spec PATH        the xcodegen spec (default ./project.yml); everything runs in its directory
#   --keep-build       reuse the current build number (after a failed archive/export; refused if already uploaded)
#   --export-only      stop after the local package checks; nothing reaches App Store Connect
#
# Outputs and the record of uploaded numbers live in <spec dir>/build/release/ (gitignore build/).
set -euo pipefail
export DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}"

SPEC=project.yml IOS_SCHEME="" MAC_SCHEME="" KEEP_BUILD=0 EXPORT_ONLY=0
while (( $# )); do
  case "$1" in
    --spec) shift; SPEC="$1" ;;
    --ios) shift; IOS_SCHEME="$1" ;;
    --mac) shift; MAC_SCHEME="$1" ;;
    --keep-build) KEEP_BUILD=1 ;;
    --export-only) EXPORT_ONLY=1 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "error: unknown option $1 (see --help)" >&2; exit 2 ;;
  esac
  shift
done
die() { echo "error: $*" >&2; exit 1; }
[[ -n "$IOS_SCHEME$MAC_SCHEME" ]] || die "give --ios SCHEME and/or --mac SCHEME"
[[ -f "$SPEC" ]] || die "no xcodegen spec at $SPEC"
cd "$(dirname "$SPEC")"; SPEC=$(basename "$SPEC")
command -v xcodegen >/dev/null || die "xcodegen not found (brew install xcodegen)"

NAME=$(sed -nE 's/^name:[[:space:]]*"?([^"]+)"?[[:space:]]*$/\1/p' "$SPEC" | head -1)
TEAM=$(sed -nE 's/^[[:space:]]*DEVELOPMENT_TEAM:[[:space:]]*"?([A-Z0-9]{10})"?.*/\1/p' "$SPEC" | head -1)
VERSION=$(sed -nE 's/^[[:space:]]*MARKETING_VERSION:[[:space:]]*"?([0-9.]+)"?.*/\1/p' "$SPEC" | head -1)
BUILD=$(sed -nE 's/^[[:space:]]*CURRENT_PROJECT_VERSION:[[:space:]]*"?([0-9]+)"?.*/\1/p' "$SPEC" | head -1)
[[ -n "$NAME" && -n "$TEAM" && -n "$VERSION" && -n "$BUILD" ]] \
  || die "$SPEC needs name, DEVELOPMENT_TEAM, MARKETING_VERSION and an integer CURRENT_PROJECT_VERSION"
OUT=build/release
mkdir -p "$OUT"

# --- API key (team key, used only by altool): checked before the build number changes. ----------------------
KEYDIR=""
cleanup() { [[ -n "$KEYDIR" ]] && rm -rf "$KEYDIR"; return 0; }
trap cleanup EXIT
if [[ $EXPORT_ONLY == 0 ]]; then
  if [[ -z "${ASC_KEY_ID:-}" || -z "${ASC_ISSUER_ID:-}" ]]; then
    eval "$(grep -E '^export ASC_(KEY_ID|ISSUER_ID)=' ~/.zshrc 2>/dev/null || true)"
  fi
  [[ -n "${ASC_KEY_ID:-}" && -n "${ASC_ISSUER_ID:-}" ]] || die "ASC_KEY_ID / ASC_ISSUER_ID not set and not in ~/.zshrc"
  KEYDIR=$(mktemp -d); chmod 700 "$KEYDIR"
  KEYFILE="$KEYDIR/AuthKey_$ASC_KEY_ID.p8"
  security find-generic-password -s deepwell.asc-api-key -a "$ASC_KEY_ID" -w 2>/dev/null | base64 -D > "$KEYFILE" \
    || die "no Keychain item deepwell.asc-api-key for account $ASC_KEY_ID"
  chmod 600 "$KEYFILE"
  grep -q 'BEGIN PRIVATE KEY' "$KEYFILE" || die "the Keychain item for $ASC_KEY_ID is not a .p8 private key"
  export API_PRIVATE_KEYS_DIR="$KEYDIR"
  AUTH=(--api-key "$ASC_KEY_ID" --api-issuer "$ASC_ISSUER_ID")
fi

# --- Build number: one bump shared by every platform in this run. -----------------------------------------
if [[ $KEEP_BUILD == 0 ]]; then
  BUILD=$((BUILD + 1))
  sed -i '' -E "s/^([[:space:]]*CURRENT_PROJECT_VERSION:[[:space:]]*).*/\1\"$BUILD\"/" "$SPEC"
elif [[ $EXPORT_ONLY == 0 ]]; then
  for p in ${IOS_SCHEME:+ios} ${MAC_SCHEME:+mac}; do
    grep -qx "$BUILD" "$OUT/uploaded-$p" 2>/dev/null && die "build $BUILD was already uploaded for $p; drop --keep-build"
  done
fi
echo "==> $NAME $VERSION ($BUILD), team $TEAM"
xcodegen generate --spec "$SPEC" --quiet
PROJECT="$NAME.xcodeproj"

# Export signs through the Apple ID in Xcode (cloud-managed distribution certificate), not the API key.
defaults read com.apple.dt.Xcode DVTDeveloperAccountManagerAppleIDLists 2>/dev/null | grep identifier >/dev/null \
  || die "xcodebuild sees no Apple ID: in Xcode > Settings > Apple Accounts remove the account and add it again"

cat > "$OUT/ExportOptions.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>method</key><string>app-store-connect</string>
	<key>destination</key><string>export</string>
	<key>teamID</key><string>$TEAM</string>
	<key>signingStyle</key><string>automatic</string>
	<key>uploadSymbols</key><true/>
	<key>manageAppVersionAndBuildNumber</key><false/>
</dict>
</plist>
PLIST

# check_bundle BUNDLE PROFILE_PATH: team, signature and embedded profile of one app or extension.
check_bundle() {
  local bundle=$1 profile=$2 team
  codesign --verify --deep --strict "$bundle" || die "$(basename "$bundle") fails codesign --verify"
  team=$(codesign -dvv "$bundle" 2>&1 | sed -n 's/^TeamIdentifier=//p')
  [[ "$team" == "$TEAM" ]] || die "$(basename "$bundle") is signed by team '$team', expected $TEAM"
  [[ -f "$bundle/$profile" ]] || die "$(basename "$bundle") has no $profile (TestFlight rejects it: ITMS-90889)"
}
plist_has() { /usr/libexec/PlistBuddy -c "Print :$2" "$1" >/dev/null 2>&1; }

ship() {
  local platform=$1 scheme=$2 dest type dir archive export pkg check app
  case $platform in
    ios) dest='generic/platform=iOS'; type=ios ;;
    mac) dest='generic/platform=macOS'; type=macos ;;
  esac
  dir="$OUT/$platform"; archive="$dir/$scheme.xcarchive"; export="$dir/export"; check="$dir/check"
  rm -rf "$dir"; mkdir -p "$dir"

  echo "==> [$platform] Archiving $scheme"
  xcodebuild -project "$PROJECT" -scheme "$scheme" -configuration Release -destination "$dest" \
    -archivePath "$archive" -allowProvisioningUpdates archive -quiet \
    || die "[$platform] archive failed. \"Your team has no devices\": build once for a real device (iPhone via Xcode
       with the phone connected; this Mac with -destination 'platform=macOS' -allowProvisioningDeviceRegistration),
       then re-run with --keep-build."

  echo "==> [$platform] Exporting for App Store Connect"
  xcodebuild -exportArchive -archivePath "$archive" -exportPath "$export" \
    -exportOptionsPlist "$OUT/ExportOptions.plist" -allowProvisioningUpdates -quiet \
    || die "[$platform] export failed; re-run with --keep-build once fixed"

  echo "==> [$platform] Checking the package"
  if [[ $platform == ios ]]; then
    pkg=$(ls "$export"/*.ipa 2>/dev/null | head -1 || true); [[ -n "$pkg" ]] || die "export produced no .ipa"
    ditto -x -k "$pkg" "$check"
    app=$(find "$check/Payload" -maxdepth 1 -name '*.app' -type d | head -1)
    check_bundle "$app" embedded.mobileprovision
    for ext in "$app"/PlugIns/*.appex; do [[ -e "$ext" ]] && check_bundle "$ext" embedded.mobileprovision; done
    plist_has "$app/Info.plist" CFBundleIcons || die "no app icon (asset catalog AppIcon)"
    plist_has "$app/Info.plist" ITSAppUsesNonExemptEncryption || die "Info.plist lacks ITSAppUsesNonExemptEncryption"
  else
    pkg=$(ls "$export"/*.pkg 2>/dev/null | head -1 || true); [[ -n "$pkg" ]] || die "export produced no .pkg"
    pkgutil --check-signature "$pkg" | sed -n '1,2p'
    pkgutil --expand-full "$pkg" "$check" >/dev/null
    app=$(find "$check" -maxdepth 3 -name '*.app' -type d | head -1)
    for bundle in "$app" "$app"/Contents/PlugIns/*.appex; do
      [[ -e "$bundle" ]] || continue
      check_bundle "$bundle" Contents/embedded.provisionprofile
      codesign -d --entitlements - --xml "$bundle" 2>/dev/null | grep 'com.apple.security.app-sandbox' >/dev/null \
        || die "$(basename "$bundle") lacks the App Sandbox entitlement"
    done
    codesign -dv "$app" 2>&1 | grep 'flags=.*runtime' >/dev/null || die "$(basename "$app") lacks the hardened runtime"
    plist_has "$app/Contents/Info.plist" CFBundleIconName || die "no app icon (asset catalog AppIcon)"
    plist_has "$app/Contents/Info.plist" LSApplicationCategoryType || die "Info.plist lacks LSApplicationCategoryType"
    plist_has "$app/Contents/Info.plist" ITSAppUsesNonExemptEncryption || die "Info.plist lacks ITSAppUsesNonExemptEncryption"
  fi
  rm -rf "$check"   # an expanded Mac app would otherwise register with Launch Services
  [[ $EXPORT_ONLY == 1 ]] && { echo "==> [$platform] Export only: $pkg"; return; }

  echo "==> [$platform] Validating"
  xcrun altool --validate-app -f "$pkg" -t "$type" "${AUTH[@]}" \
    || die "[$platform] validation failed. \"No suitable application records\": the App Store Connect app record is
       missing or lacks this platform. Re-run with --keep-build once fixed."

  echo "==> [$platform] Uploading build $BUILD"
  xcrun altool --upload-app -f "$pkg" -t "$type" "${AUTH[@]}" 2>&1 | tee "$dir/upload.log"
  echo "$BUILD" >> "$OUT/uploaded-$platform"
  local delivery status
  delivery=$(sed -nE 's/^Delivery UUID: ([0-9a-fA-F-]+).*/\1/p' "$dir/upload.log" | tail -1)
  [[ -n "$delivery" ]] || die "[$platform] no Delivery UUID in the upload output; check App Store Connect"

  # An accepted upload can still be rejected in processing (e.g. a missing usage string): wait for the verdict.
  echo "==> [$platform] Waiting for processing (up to 20 minutes)"
  for _ in $(seq 40); do
    status=$(xcrun altool --build-status --delivery-id "$delivery" "${AUTH[@]}" 2>&1 || true)
    if grep -q 'BUILD-STATUS: FAILED' <<<"$status"; then
      sed -n '/PROCESSING-ERRORS/,/IMPORT-STATUS/p' <<<"$status" >&2
      die "[$platform] build $BUILD rejected in processing (above). Fix, then run again without --keep-build."
    fi
    if grep -q 'IS-ON-APP-STORE-CONNECT: true' <<<"$status"; then
      echo "==> [$platform] Build $BUILD processed; it appears in TestFlight shortly."; return
    fi
    sleep 30
  done
  echo "==> [$platform] Still processing after 20 minutes. Check with:"
  echo "    xcrun altool --build-status --delivery-id $delivery --api-key \$ASC_KEY_ID --api-issuer \$ASC_ISSUER_ID"
}

[[ -n "$IOS_SCHEME" ]] && ship ios "$IOS_SCHEME"
[[ -n "$MAC_SCHEME" ]] && ship mac "$MAC_SCHEME"
echo "==> Done. Commit the bumped CURRENT_PROJECT_VERSION in $SPEC."

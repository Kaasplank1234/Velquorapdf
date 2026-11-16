#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist/reports
# Keep output for failed as well as successful builds. pipefail propagates errors.
exec > >(tee -a dist/reports/build.log) 2>&1
[[ "$(uname -s)" == Darwin ]] || { echo 'Requires a macOS build host'; exit 1; }
architecture="$(uname -m)"
case "$architecture" in
  x86_64) edition=Intel ;;
  arm64) edition=AppleSilicon ;;
  *) echo "Unsupported architecture: $architecture"; exit 1 ;;
esac
dmg="Velqora-PDF-10.3-macOS-${edition}.dmg"
export MACOSX_DEPLOYMENT_TARGET=11.0
python3.11 -c 'import platform,sys; assert sys.version_info[:2]==(3,11) and platform.machine()==sys.argv[1]' "$architecture"
python3.11 -m venv .venv-build
source .venv-build/bin/activate
if [[ "$architecture" == x86_64 ]]; then
  python -m pip install --only-binary=:all: --require-hashes -r requirements-macos.lock
else
  python -m pip install --only-binary=:all: -r requirements-macos-arm64.txt
fi
python -m pip check
python -m pip freeze > dist/reports/installed-dependencies.txt
python -m pip inspect > dist/reports/installed-dependencies.json
python -c 'import platform,sys; print(sys.version); print(platform.platform())' > dist/reports/build-host.txt
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen python tests/smoke_gui.py
python scripts/make_icon.py
python -m PyInstaller --clean --noconfirm LibrePDF.spec
cp build/LibrePDF/warn-LibrePDF.txt dist/reports/pyinstaller-warnings.txt
python scripts/audit_macos.py 'dist/Velqora PDF.app' --architecture "$architecture" > dist/reports/bundle-audit.json
python scripts/run_app_test.py 'dist/Velqora PDF.app' dist/reports/app-offscreen-selftest.json --platform offscreen
python scripts/run_app_test.py 'dist/Velqora PDF.app' dist/reports/app-cocoa-selftest.json --platform cocoa
codesign --display --verbose=4 'dist/Velqora PDF.app' > dist/reports/signature.txt 2>&1
codesign --verify --deep --strict 'dist/Velqora PDF.app'
# A temporary staging tree makes reruns safe and keeps stale files out of the DMG.
staging_dir="$(mktemp -d "${TMPDIR:-/tmp}/librepdf-stage.XXXXXX")"
trap 'rm -rf "$staging_dir"' EXIT
/usr/bin/ditto 'dist/Velqora PDF.app' "$staging_dir/Velqora PDF.app"
ln -s /Applications "$staging_dir/Applications"
hdiutil create -volname 'Velqora PDF' -srcfolder "$staging_dir" -ov -fs HFS+ -format UDZO "dist/$dmg"
python scripts/verify_dmg.py "dist/$dmg"
(cd dist && shasum -a 256 "$dmg" > SHA256SUMS)
echo 'Build and mounted-DMG checks passed on this build host. Big Sur runtime is not verified.'

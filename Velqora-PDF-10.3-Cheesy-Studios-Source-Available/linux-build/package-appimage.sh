#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 4 ]]; then
    echo "Usage: $0 FROZEN_APP APPIMAGE_RUNTIME MKSQUASHFS OUTPUT.AppImage" >&2
    exit 2
fi
frozen=$(realpath "$1")
runtime=$(realpath "$2")
squash=$(realpath "$3")
output=$(realpath -m "$4")
script_dir=$(cd "$(dirname "$0")" && pwd)
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/AppDir/usr/bin"
cp -a "$frozen/." "$stage/AppDir/usr/bin/"
cp "$script_dir/AppRun" "$script_dir/org.velqora.pdf.desktop" "$stage/AppDir/"
cp "$frozen/_internal/assets/icon.png" "$stage/AppDir/org.velqora.pdf.png"
ln -s org.velqora.pdf.png "$stage/AppDir/.DirIcon"
"$squash" "$stage/AppDir" "$stage/filesystem.squashfs" -comp zstd -Xcompression-level 17 -b 1048576 -noappend -no-xattrs -all-root -processors 4 -no-progress
mkdir -p "$(dirname "$output")"
cat "$runtime" "$stage/filesystem.squashfs" > "$output"
chmod 755 "$output"

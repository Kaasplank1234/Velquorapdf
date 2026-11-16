# Velqora PDF 10.3 on Linux

For 64-bit Intel and AMD Linux. Give the downloaded AppImage execute permission and run it. On systems without FUSE, pass `--appimage-extract-and-run`.

The package contains Python and Qt, the six offline OCR models and the 200 font families from the existing Velqora Linux package. It uses the system's Linux desktop libraries. The bundled ELF objects require glibc symbols through version 2.28. A full native desktop session was not tested on Ubuntu or Manjaro.

## Rebuild from this archive

Use CPython 3.12 x86_64 on Linux with a glibc 2.28-compatible build of Python. From the archive root:

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r linux-build/requirements-linux.txt
.venv/bin/pyinstaller --noconfirm --distpath linux-build/dist --workpath linux-build/work linux-build/Velqora-Linux.spec
```

Copy `libxcb-cursor.so.0` (dereferencing any symlink) into `linux-build/dist/velqora-pdf/_internal/`, along with the library's copyright notice. The release used Debian's `libxcb-cursor0_0.1.4-1_amd64.deb`. Its [source](https://sources.debian.org/src/xcb-util-cursor/0.1.4-1/) and [binary package](https://deb.debian.org/debian/pool/main/x/xcb-util-cursor/libxcb-cursor0_0.1.4-1_amd64.deb) are available from Debian.

Then pass the official [x86_64 AppImage Type 2 runtime](https://github.com/AppImage/type2-runtime/tree/fedfad5) and a `mksquashfs` executable with Zstd support to:

```sh
linux-build/package-appimage.sh linux-build/dist/velqora-pdf ./runtime-x86_64 "$(command -v mksquashfs)" Velqora-PDF-10.3-Linux-x86_64.AppImage
QT_QPA_PLATFORM=offscreen ./Velqora-PDF-10.3-Linux-x86_64.AppImage --appimage-extract-and-run --self-test --report ./linux-test.json
```

The release's test report is included. Velqora source and font notices are under `project/`.

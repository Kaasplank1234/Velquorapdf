# Velqora PDF 10.3 development guide

This document describes how to work with the project source as it is currently organized in this repository.

## Repository layout

The source package is kept under:

- `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/`

The desktop application entry point is:

- `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/src/main.py`

The build scripts and platform-specific dependency files are also inside that source package directory.

## Required Python version

The project build scripts and release files target Python 3.11 for the native macOS and Windows packaging workflow.

Recommended source-development setup:

- Python 3.11.x
- `venv` support enabled
- An appropriate GUI-capable system for running Qt/PySide6 locally

## Install dependencies

From the source package directory:

```bash
cd Velqora-PDF-10.3-Cheesy-Studios-Source-Available
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

## Run the application from source

From the same directory after activation:

```bash
python src/main.py
```

## Run the available tests

The repository includes unit tests under the source package's `tests/` directory.

```bash
cd Velqora-PDF-10.3-Cheesy-Studios-Source-Available
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

The app also has a built-in self-test mode:

```bash
python src/main.py --self-test --report report.json
```

## Build Windows packages

From the source package directory on a Windows x64 machine with Python 3.11 installed:

```powershell
cd Velqora-PDF-10.3-Cheesy-Studios-Source-Available
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-windows.txt
python -m unittest discover -s tests -v
python scripts\make_icon.py
python -m PyInstaller --clean --noconfirm Velqora-Windows.spec
```

The packaging script `scripts/build_windows.ps1` reflects the repository's intended Windows build workflow.

## Build macOS Intel and Apple Silicon packages

The macOS build script is located at:

- `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/scripts/build_macos.sh`

Run it on a macOS host:

```bash
cd Velqora-PDF-10.3-Cheesy-Studios-Source-Available
bash scripts/build_macos.sh
```

This script enforces Python 3.11 and architecture-specific dependency installation. It also runs the project test set and packaging validations before creating the DMG.

## Build Linux AppImages

The Linux packaging flow is in:

- `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/linux-build/`

Typical workflow:

```bash
cd Velqora-PDF-10.3-Cheesy-Studios-Source-Available
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r linux-build/requirements-linux.txt
python -m PyInstaller --noconfirm --distpath linux-build/dist --workpath linux-build/work linux-build/Velqora-Linux.spec
```

See `linux-build/README.md` for the full AppImage instructions and runtime requirements.

## Known build limitations

- The release scripts are platform-specific and were written for native build hosts.
- Local macOS packaging requires a genuine macOS machine with the correct Xcode/toolchain environment.
- Linux packaging may require system libraries or AppImage runtime pieces not present in every distro.
- The repository preserves build artifacts and audits, but not every platform was tested in this environment.

## Notes

This project is source-available and free for local use under the repository license terms. The build instructions above are intended for development and packaging review only, not as a promise of legal distribution rights beyond the repository's applicable license terms.


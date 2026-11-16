# Velqora PDF source package

This directory contains the source package for Velqora PDF 10.3 and the platform-specific build scripts used to package the application for Windows, macOS, and Linux.

## Project entry point

The desktop application entry point is:

- `src/main.py`

## Repository layout

- `src/` — application source code and GUI logic
- `tests/` — project tests
- `scripts/` — packaging and validation utilities
- `linux-build/` — Linux AppImage build files
- `assets/` — packaged UI assets and resources
- `requirements*.txt` — dependency declarations
- `*.spec` — PyInstaller build definitions

## Development notes

The project is designed around Python 3.11 for native package builds. See the repository root `DEVELOPMENT.md` for the working setup and build commands.

The project remains source-available and keeps third-party notices in the repository root `THIRD_PARTY.md` and the preserved license archive directories.


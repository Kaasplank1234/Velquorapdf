# Velqora PDF 10.3

**Your PDFs. Your Freedom.**

Velqora PDF is a free, offline PDF editor for Windows, macOS and Linux. The project keeps a local-first workflow without subscriptions, cloud uploads, or external OCR credits. This repository preserves the extracted source package, the remaining project files, and the applicable third-party notices in a browsable layout.

## Project overview

This repository contains the extracted Velqora PDF 10.3 source package and its supporting materials. The original folders are kept in place for provenance, while the root-level structure below makes the project easier to navigate without changing the underlying source code or licensing terms.

## Downloads and support

- [Download Velqora PDF](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download)
- [Official website](https://velqorapdf.pages.dev/)
- [Get support](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)

## Features

- Edit existing PDF text, retain formatting where possible, and change colors or fonts.
- Add text, notes, comments, annotations, and drawing overlays.
- Manage pages by rotating, deleting, extracting, inserting and reordering them.
- Use local OCR for scanned documents in Dutch, English, German, French, Spanish and Turkish.
- Work entirely offline without cloud uploads or account sign-in.

## Source Code and Repository Structure

The repository has been organized around a conventional Python layout while preserving the original extracted directories. The main top-level areas are:

- `src/` — application source code, document engine logic, OCR integration, and Qt workspace code.
- `assets/` — project assets and UI resources used by the desktop app.
- `scripts/` — build, audit and packaging utilities for Windows, macOS and Linux.
- `tests/` — automated validation for document behavior, OCR and page-range handling.
- `linux-build/` — Linux packaging artifacts and AppImage-related build instructions.
- `third_party/` — license notices, dependency notes, and third-party materials.

The original extracted folders remain in the repository for traceability and legal review, but the active project structure is now rooted in these conventional directories.

The source code entry point is the application in [src/main.py](./src/main.py). For the active package tree, see [src/](./src).

## Developer setup

The project uses Python 3.11 and dependency pins defined in the project files. For a local development environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

For the build toolchain used by project packaging and validation:

```bash
pip install -r requirements-build.txt
```

Platform-specific dependency files are available for Windows and macOS builds:

- `requirements-windows.txt`
- `requirements-macos-arm64.txt`
- `requirements-macos.lock`
- `linux-build/requirements-linux.txt`

The application entry point is `src/main.py`, which starts the Qt application and routes the OCR worker process for offline recognition. This is the documented launch point used by the code and the project scripts.

## Testing and validation

The repository includes multiple validations for OCR, page handling and document logic. A basic project-level check is:

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

The application also supports a self-test mode:

```bash
python src/main.py --self-test --report report.json
```

These checks are useful for local validation, but no claim is made here that a full reproducible build is available unless it has been formally verified with the project’s packaging scripts and build reports.

## Third-party licensing

This project keeps the root `LICENSE` unchanged and retains the Velqora PDF Source-Available License 1.0 as the governing license for the project-owned code.

Third-party materials remain subject to their original rights and obligations. The project-level license summary is in [THIRD_PARTY.md](./THIRD_PARTY.md), and the preserved notices live under [third_party/licenses/](./third_party/licenses).

The repository contains AGPL-licensed dependencies, including PyMuPDF/MuPDF, which may impose obligations when combined with the application or redistributed as a single bundle. This is a documented licensing concern and should be reviewed carefully before any broad redistribution or downstream distribution.

## Source availability and licensing summary

Velqora PDF is source-available rather than open source as defined by the Open Source Initiative. The application remains locally processable and source-inspectable, but the actual rights granted are governed by the repository `LICENSE` file, not by this README summary alone.

## About

Velqora PDF is an independent project by Cheesy Studios. It keeps the project identity and source-available licensing terms intact while making the extracted files easier to browse and review.

---

This repository is being reorganized for clarity and review only. The original extracted directories and their associated notices are retained for provenance and legal review, and no source files are being deleted or re-licensed in this branch.

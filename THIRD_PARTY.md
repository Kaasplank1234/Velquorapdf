# Third-party notices and licensing overview

This file summarizes the third-party material present in the repository and points to the preserved notices under `third_party/licenses/`.

## Project-owned license

The root `LICENSE` file remains the governing Velqora PDF Source-Available License 1.0 for the project-owned code in this repository.

## Preserved third-party directories

The repository keeps the original extracted license directories for provenance:

- `Velqora-PDF-10.3-License-AGPL-3.0/`
- `Velqora-PDF-10.3-License-Apache-2.0/`
- `Velqora-PDF-10.3-License-BSD-3-Clause/`
- `Velqora-PDF-10.3-License-GPL-with-exception/`
- `Velqora-PDF-10.3-License-HPND-Pillow/`
- `Velqora-PDF-10.3-License-LGPL-3.0/`
- `Velqora-PDF-10.3-License-PSF/`

Their contents are organized under `third_party/licenses/` in a browsable structure, while the original extracted archive directories remain preserved for reference and legal review.

## Dependency summary

The main project dependencies recorded in the project files include:

- PySide6 6.5.3 — Qt bindings; licensing is LGPL/GPL/commercial option depending on how the component is used.
- PyMuPDF / MuPDF 1.24.11 — AGPL-3.0.
- Pillow 11.0.0 — HPND/Pillow notices.
- NumPy 1.26.4 — BSD-3-Clause.
- Tesseract OCR language data — Apache-2.0, bundled as offline OCR language packs.
- PyInstaller 6.11.1 — GPL with bootloader exception.
- CPython 3.11 — Python Software Foundation license.

## Licensing risk note

The repository includes AGPL-licensed components, notably PyMuPDF/MuPDF. A combined distribution of the application and AGPL libraries may impose obligations on redistribution or downstream use that are not eliminated by merely separating notices or directories. This repository does not claim full legal compliance for every possible distribution scenario without a written license review.

Third-party rights therefore remain applicable even when the project code and notices are reorganized into a cleaner source tree.

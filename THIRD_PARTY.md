# Third-party notices and licensing overview

This repository keeps the project-owned license in the root `LICENSE` file and preserves third-party provenance under the archived license directories.

## Project-owned license

The root `LICENSE` file governs the Cheesy Studios-owned material in this repository. The license is source-available rather than OSI-approved open source. It is intentionally restrictive for redistribution and publication of modified versions.

## Preserved third-party directories

The repository preserves the original extracted license packages and notices for legal review:

- `Velqora-PDF-10.3-License-AGPL-3.0/`
- `Velqora-PDF-10.3-License-Apache-2.0/`
- `Velqora-PDF-10.3-License-BSD-3-Clause/`
- `Velqora-PDF-10.3-License-GPL-with-exception/`
- `Velqora-PDF-10.3-License-HPND-Pillow/`
- `Velqora-PDF-10.3-License-LGPL-3.0/`
- `Velqora-PDF-10.3-License-PSF/`

## Dependency summary

The project depends on the following notable components:

- PySide6 / Qt / Shiboken — LGPL/GPL/commercial licensing depending on component usage.
- PyMuPDF / MuPDF — AGPL-3.0.
- Pillow — HPND/Pillow notices.
- NumPy — BSD-3-Clause.
- Tesseract OCR language data — Apache-2.0.
- PyInstaller — GPL with a bootloader exception.
- CPython — Python Software Foundation license.

## Licensing risk note

This repository includes AGPL-licensed material, notably PyMuPDF/MuPDF. A custom source-available license cannot override the rights and obligations that arise under an applicable third-party license. In particular, redistribution or combined distribution of AGPL-covered components may trigger obligations that differ from the project-owned source-available terms.

The repository preserves the original notices and third-party archives, but this area still requires formal legal review before any broader redistribution or downstream remixing beyond the official release is treated as compliant.


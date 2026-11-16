# Velqora PDF 10.3

### Your PDFs. Your Freedom.

**A powerful, completely free and offline PDF editor for Windows, macOS and Linux.**

Edit existing PDF text, annotate documents, organize pages and make scanned PDFs searchable — all from your desktop. No subscriptions, no accounts, no OCR credits and no unnecessary cloud services.

**[Download Velqora PDF](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download)** · **[Official Website](https://velqorapdf.pages.dev/)** · **[Get Support](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)**

**Free to use · Offline-first · Source-available · Cross-platform**

---

## Why Velqora PDF?

PDF editing should be simple, accessible and affordable.

Velqora PDF is an independent desktop application that combines text editing, annotations, page management and offline OCR in one modern workspace.

Your documents can be processed locally, without uploading them to an online PDF editor.

### Key benefits

- **Completely free:** No subscriptions, paid editing features or OCR credits.
- **Privacy-focused:** Supported PDF operations run locally.
- **Offline-first:** Core editing and OCR features work without internet access.
- **Cross-platform:** Available for Windows, macOS and Linux.
- **Modern interface:** Organized editing tools and a dedicated Comments panel.
- **Source-available:** Inspect and privately modify the source code under the applicable license terms.

---

## Features

### Edit PDF text and images

- Edit existing PDF text while preserving original formatting and fonts where possible.
- Change text colors and choose alternative fonts.
- Add new text, movable text boxes and images.
- Customize font families, sizes and colors.
- Move images and adjust document elements.

### Highlight, annotate and draw

- Highlight text in **yellow, green, blue, pink or orange**.
- Strike through text while preserving its original color, including multicolored selections.
- Draw with a pen, marker or brush.
- Customize drawing colors and line thicknesses.
- Add notes, underlines and shapes.
- Undo edits and remove individual annotations.
- Access annotation tools through the redesigned **Comments** panel.

### Offline OCR

Turn scanned PDFs into searchable documents without uploading them to a server.

- Recognize text locally, including background processing.
- Search, select and copy recognized text.
- Run OCR on individual pages or entire documents.
- No OCR credits, subscriptions or additional payments.

**Supported languages:** Dutch, English, German, French, Spanish and Turkish.

OCR accuracy depends on the quality and layout of the scanned document.

### Organize PDF pages

- Add, delete, rotate and reorder pages.
- Merge multiple PDF documents.
- Extract selected pages.
- Navigate using thumbnails, continuous scrolling and page jumping.

### Built-in Help Center

- Interactive welcome tour.
- Searchable Help Center.
- Offline help documentation.
- Guidance for common PDF editing tasks.

---

## Download Velqora PDF

**Version 10.3 — Official Downloads**

All official builds are distributed through **GitHub Releases**.

| Operating system | Download | Architecture |
|---|---|---|
| Windows | [Download Windows ZIP](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Windows-x64.zip) | x86-64 |
| macOS Intel | [Download Intel DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-Intel.dmg) | Intel 64-bit |
| macOS Apple Silicon | [Download Apple Silicon DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-AppleSilicon.dmg) | Apple M-series |
| Linux | [Download Linux AppImage](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Linux-x86_64.AppImage) | x86-64 |

**[View Official GitHub Releases](https://github.com/Kaasplank1234/Velquorapdf/releases)**

For the latest available downloads, release notes and version information, always use the official GitHub repository.

---

## Installation

### Windows

1. Download the Windows ZIP.
2. Right-click the archive and select **Extract All**.
3. Open the extracted folder.
4. Launch `Velqora PDF.exe`.

Keep the extracted application files together.

Windows SmartScreen may display a warning for independently distributed software. Verify that your download came from the official release before deciding whether to proceed.

### macOS

1. Download the DMG matching your processor.
2. Open the downloaded DMG.
3. Drag Velqora PDF into **Applications**.
4. Launch the application from Finder.

Velqora PDF is currently unsigned and not notarized by Apple. macOS may block the initial launch.

After verifying the download, check **System Settings → Privacy & Security** for the available opening options.

For additional guidance, consult [Apple's official documentation](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac).

**Compatibility:** The Intel build targets macOS 11 Big Sur or later and has been tested on macOS 15. Direct testing on macOS 11.7.11 remains pending.

### Linux

Download the Linux AppImage and run:

```bash
cd ~/Downloads
chmod +x Velqora-PDF-10.3-Linux-x86_64.AppImage
./Velqora-PDF-10.3-Linux-x86_64.AppImage
```

If the AppImage reports a FUSE-related error, try the `--appimage-extract-and-run` option if supported.

**Compatibility:** The Linux AppImage passed 75 automated checks in a test environment. Direct GUI testing on Ubuntu and Manjaro is still pending.

---

## Privacy and offline processing

Velqora PDF is designed to keep document processing on your computer.

- No cloud uploads are required for supported editing and OCR operations.
- No user account is required.
- No subscription is necessary.
- No OCR credits or external OCR processing fees.
- Core document-processing functionality works offline.
- Built-in help documentation is available offline.

Your PDF files remain on your device during supported offline operations.

This does not imply that every operating-system component or third-party dependency is incapable of network activity.

---

## Source code and development

Velqora PDF's source code is publicly available for inspection and private experimentation under the applicable licenses.

**[Browse the Application Source Code](https://github.com/Kaasplank1234/Velquorapdf/tree/main/Velqora-PDF-10.3-Cheesy-Studios-Source-Available/src)**

**[Browse Additional Project Files](https://github.com/Kaasplank1234/Velquorapdf/tree/main/Velqora-PDF-10.3-Remaining-Project-Files)**

### Repository structure

| Directory | Contents |
|---|---|
| `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/` | Python source, scripts, tests, dependency files and build configurations |
| `Velqora-PDF-10.3-Remaining-Project-Files/` | Additional assets and project documentation |
| `Velqora-PDF-10.3-License-*/` | Third-party license information |
| `README.md` | Project overview |
| `LICENSE` | Source-Available License 1.0 |

The repository may be reorganized into a more conventional Python project structure in a future update.

### Building from source

The repository contains Python application modules, dependency specifications and platform-specific build scripts.

However, complete reproducibility of every published Velqora PDF 10.3 binary has not yet been verified.

Some third-party development dependencies and resources may need to be obtained separately.

Review the dependency files, build scripts and third-party notices before attempting a build.

---

## Third-party software

Velqora PDF uses third-party software components, including:

| Component | Version | License |
|---|---|---|
| PyMuPDF / MuPDF | 1.24.11 | AGPL-3.0 or commercial |
| PySide6 / Qt / Shiboken | 6.5.3 | Component-specific LGPL/GPL/commercial |
| Pillow | 11.0.0 | HPND |
| NumPy | 1.26.4 | BSD-3-Clause |
| Python | 3.11 | PSF License |
| PyInstaller | 6.11.1 | GPL with bootloader exception |
| Tesseract OCR language data | Pinned upstream version | Apache-2.0 |

Some components are used only during development or packaging.

All third-party components retain their applicable copyright notices and license terms.

**Licensing notice:** PyMuPDF/MuPDF is available under the AGPL or a commercial license. AGPL obligations may affect the combined application, including redistribution and source-code rights. Compatibility with the custom Velqora PDF license has not yet been independently established.

---

## Licensing

Velqora PDF uses the **Velqora PDF Source-Available License 1.0** for independently licensable material owned by Cheesy Studios.

**Source-available is not the same as OSI-approved open source.**

The intended permissions for Cheesy Studios-owned material are:

| Activity | Permission |
|---|---|
| View and download source code | Allowed |
| Use the software for personal or internal purposes | Allowed |
| Modify source code privately | Allowed |
| Study and experiment with source code | Allowed |
| Publish modified versions | Written permission required |
| Redistribute Cheesy Studios-owned source code | Written permission required |
| Incorporate Cheesy Studios-owned code into publicly distributed products | Written permission required |

These restrictions apply only to the extent permitted by law and other applicable licenses.

Third-party open-source rights and obligations remain in effect and may also apply to the combined application.

See the complete [LICENSE](https://github.com/Kaasplank1234/Velquorapdf/blob/main/LICENSE) for the custom license terms.

---

## Known limitations

Velqora PDF continues to evolve as an independent project.

- Complex PDF layouts may not always preserve their original formatting during editing.
- OCR accuracy depends on document quality.
- macOS builds are currently unsigned and not notarized.
- Direct testing on macOS 11 Big Sur remains pending.
- Linux compatibility may vary between distributions.
- Full reproducibility of the published binaries from the available source has not yet been verified.
- Third-party licensing compatibility requires further review.

---

## Support and feedback

Need assistance or found a bug?

Please include your operating system, processor architecture, Velqora PDF version and the exact error message when reporting an issue.

- [Official Website](https://velqorapdf.pages.dev/)
- [Official Downloads](https://github.com/Kaasplank1234/Velquorapdf/releases)
- [Report an Issue](https://github.com/Kaasplank1234/Velquorapdf/issues)
- [Contact Cheesy Studios](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)

---

## About Cheesy Studios

Velqora PDF is an independent hobby project developed under **Cheesy Studios**.

I created Velqora PDF because useful PDF editing tools should be accessible without expensive subscriptions, unnecessary restrictions on everyday functionality or mandatory online services.

My goal is to create practical software that combines modern design, useful features and respect for users' privacy.

I continue improving Velqora PDF's usability, performance and cross-platform support.

**Made independently. Built with curiosity.**

---

**Velqora PDF 10.3 — Your PDFs. Your Freedom.**

© 2026 Cheesy Studios.

See `LICENSE` and the applicable third-party license notices for legal terms.

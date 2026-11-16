# Velqora PDF 10.3

**Your PDFs. Your Freedom.**

**A free, powerful and offline PDF editor for Windows, macOS and Linux.** Edit existing PDF text, annotate documents, organize pages and make scanned PDFs searchable — without subscriptions, accounts, OCR credits or mandatory cloud services.

[**Download Velqora PDF**](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download) · [**Official website**](https://velqorapdf.pages.dev/) · [**Get support**](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)

> **Free to use · Source-available · Local document processing**
>
> Velqora PDF's source code is available for inspection and private modification. Publishing or distributing modified versions of Cheesy Studios-owned code requires written permission, subject to applicable third-party licenses. **Source-available is not the same as OSI-approved open source.**

## Why Velqora PDF?

PDF editing should be straightforward, accessible and free.

Velqora PDF combines text editing, annotations, page management and optical character recognition (OCR) in one modern desktop application. Whether you're editing a document, reviewing a PDF or making scanned pages searchable, Velqora PDF provides essential tools without requiring an online account.

Supported document-processing features work locally, so you don't have to upload your PDFs to an online editor.

**What makes Velqora PDF different?**

- **Completely free:** No subscriptions, premium editing tools or OCR credits.
- **Offline-first:** Edit PDFs and recognize scanned text without an internet connection.
- **Privacy-focused:** Supported document-processing operations run locally.
- **Cross-platform:** Available for Windows, macOS Intel, macOS Apple Silicon and Linux.
- **Modern workspace:** Convenient editing, annotation and navigation tools.
- **Source-available:** Explore the code and make private modifications under the applicable license terms.

## Features

### Edit text and images

- Edit existing PDF text, retaining original formatting and fonts where possible.
- Change text colors and choose alternative fonts when needed.
- Add text, movable text boxes and images.
- Adjust font families, sizes, colors and image positions.
- Work directly with existing PDF documents without converting them to another format first.

Some complex PDF layouts or embedded fonts may limit how accurately original formatting can be preserved.

### Annotate and draw

- Highlight text in **yellow, green, blue, pink or orange**.
- Strike through text while preserving its original color, including multicolored selections.
- Draw directly on pages using a **pen, marker or brush**.
- Customize drawing colors and line thickness.
- Add notes, underlines and shapes.
- Undo edits or remove individual annotations.
- Find drawing and highlighting controls together in the redesigned **Comments** panel.

### Offline OCR

- Recognize text in scanned PDF pages locally, including background recognition.
- Search, select and copy recognized text.
- Rerun OCR on an individual page or an entire document.
- Make scanned documents easier to search and work with.
- Supported languages: **Dutch, English, German, French, Spanish and Turkish**.

**No OCR credits, external account or additional OCR payment required.**

OCR accuracy depends on scan quality, document layout and language.

### Manage pages

- Add, delete, rotate and reorder pages.
- Merge multiple PDFs and extract selected pages.
- Navigate with thumbnails, continuous scrolling and page jumping.
- Organize documents without relying on external online services.

### Learn as you go

- Interactive welcome tour.
- Built-in, searchable Help Center with offline guides.
- Helpful explanations for common editing and document-management tasks.

## Downloads

Download official builds directly from [GitHub Releases](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download). Choose the version for your operating system below.

| Platform | Direct download | Architecture |
| --- | --- | --- |
| Windows | [Download Windows ZIP](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Windows-x64.zip) | x86-64 (Intel / AMD) |
| macOS — Intel | [Download Intel DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-Intel.dmg) | Intel 64-bit |
| macOS — Apple Silicon | [Download Apple Silicon DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-AppleSilicon.dmg) | Apple M-series |
| Linux | [Download Linux AppImage](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Linux-x86_64.AppImage) | x86-64 (Intel / AMD) |

All four files are distributed through the official [Velqora PDF 10.3 GitHub release](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download).

**GitHub Releases is the official download source for Velqora PDF.**

### Windows

1. Download the Windows ZIP and select **Extract All**.
2. Open the extracted folder and run `Velqora PDF.exe`.
3. Keep the extracted application files together; don't run the executable directly from inside the ZIP.

Windows may show a SmartScreen warning for independently distributed software. Verify that your download came from the official GitHub release before deciding whether to proceed.

### macOS

1. Download the DMG matching your Mac's processor (**Apple menu → About This Mac**).
2. Open the DMG and drag **Velqora PDF** into **Applications**.
3. Open the application from Finder.

**Unsigned / not notarized:** macOS may block the first launch. After verifying the download, check **System Settings → Privacy & Security** for an **Open Anyway** option. On older macOS versions, look under **System Preferences → Security & Privacy**.

See [Apple's guidance on opening Mac apps safely](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac).

**Compatibility:** The Intel build targets macOS 11 Big Sur or later and has been tested on macOS 15. Direct testing on macOS 11.7.11 is still pending. The Apple Silicon build is intended for compatible Apple Silicon Macs.

### Linux

Download the AppImage, then run:

```bash
cd ~/Downloads
chmod +x Velqora-PDF-10.3-Linux-x86_64.AppImage
./Velqora-PDF-10.3-Linux-x86_64.AppImage
```

Alternatively, use your file manager to mark the AppImage executable and launch it, if your desktop environment supports this.

**Troubleshooting:**

- **Permission denied:** Run the `chmod +x` command above.
- **FUSE-related error:** Try `./Velqora-PDF-10.3-Linux-x86_64.AppImage --appimage-extract-and-run` (if supported by the AppImage).
- **Exec format error:** Run `uname -m` and confirm it reports `x86_64`.
- **Nothing happens / missing libraries:** Launch from a terminal, read the error output and check for distribution-specific dependencies.

**Compatibility:** The Linux AppImage passed 75 automated checks in a test environment. Direct GUI testing on Ubuntu and Manjaro is still pending; compatibility across distributions is not guaranteed.

## Privacy and offline use

Velqora PDF is designed for local document processing:

- PDF editing and OCR do not require cloud uploads.
- No account or subscription is required.
- No OCR credits or additional processing fees are required.
- Core document-processing features work without an internet connection.
- The built-in help content is available offline.

**Your documents remain on your computer during supported offline operations.**

These statements describe Velqora PDF's intended document-processing behavior and do not imply that every operating-system or third-party component is incapable of network activity.

## Source code and development

Velqora PDF's source code is publicly available on GitHub for inspection, learning and private experimentation under the applicable licenses.

The repository currently contains extracted source-code directories rather than downloadable source archives.

**[Browse the Python source code](https://github.com/Kaasplank1234/Velquorapdf/tree/main/Velqora-PDF-10.3-Cheesy-Studios-Source-Available/src)** · **[View additional project files](https://github.com/Kaasplank1234/Velquorapdf/tree/main/Velqora-PDF-10.3-Remaining-Project-Files)**

### Repository structure

| Directory or file | Description |
| --- | --- |
| `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/` | Python application source, tests, scripts and build configurations |
| `Velqora-PDF-10.3-Remaining-Project-Files/` | Additional application assets and project documentation |
| `Velqora-PDF-10.3-License-*/` | Third-party license texts and notices |
| `README.md` | Project overview and installation instructions |
| `LICENSE` | Velqora PDF Source-Available License 1.0 |

The repository includes source files and build-related resources for Velqora PDF 10.3. However, complete reproducibility of every published binary from these files has not yet been verified.

Some third-party dependencies or resources may need to be obtained separately.

## Source availability and licensing

Velqora PDF is **source-available**, **not open source** under the Open Source Initiative definition.

The intended permissions for independently licensable Cheesy Studios-owned code are:

| Activity | Permission |
| --- | --- |
| View and download source code | Allowed |
| Use the software for personal or internal purposes | Allowed |
| Modify source code privately | Allowed |
| Study and experiment with source code | Allowed |
| Publish or distribute modified versions | **Not allowed without written permission** |
| Redistribute Cheesy Studios-owned source code or reuse it in another publicly distributed product | **Not allowed without written permission** |

**The actual [LICENSE](https://github.com/Kaasplank1234/Velquorapdf/blob/main/LICENSE) file controls the custom license terms.** This README is only a summary.

Third-party components remain subject to their respective licenses. These licenses may grant additional rights or impose obligations affecting the combined application.

### Third-party dependencies

Velqora PDF uses several third-party software components.

| Component | Version | License |
| --- | --- | --- |
| PyMuPDF / MuPDF | 1.24.11 | AGPL-3.0 or commercial |
| PySide6 / Qt / Shiboken | 6.5.3 | Component-specific LGPL/GPL/commercial |
| Pillow | 11.0.0 | HPND |
| NumPy | 1.26.4 | BSD-3-Clause |
| Python | 3.11 | PSF License |
| PyInstaller | 6.11.1 | GPL with bootloader exception |
| Tesseract OCR language data | Pinned upstream version | Apache-2.0 |

Some dependencies are used during development or packaging and may not be included in every application build.

**Important licensing notice:** PyMuPDF/MuPDF is available under the AGPL or a commercial license. AGPL obligations may affect the combined application, including source-code availability and redistribution rights. Compatibility with Velqora PDF's custom Source-Available License has not yet been independently established.

Separating third-party licensing materials into different directories does not remove applicable license obligations.

## Known limitations

Velqora PDF continues to evolve as an independent project.

- Complex PDF layouts and embedded fonts may limit text-editing accuracy.
- OCR results depend on document quality and language.
- macOS builds are currently unsigned and not notarized.
- Direct testing on macOS 11 Big Sur remains pending.
- Linux compatibility may vary between distributions.
- Complete reproducibility of the published binaries has not yet been established.
- Third-party licensing compatibility requires further review.

## Support and feedback

Found a bug or need help getting started? Please include your **operating system/version**, **processor architecture**, **Velqora PDF version**, and any **exact error message**.

- [Official Velqora PDF website](https://velqorapdf.pages.dev/)
- [Download Velqora PDF](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download)
- [Report a bug or request a feature](https://github.com/Kaasplank1234/Velquorapdf/issues)
- [Contact Cheesy Studios](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)

## About

Velqora PDF is an independent hobby project by **Cheesy Studios**.

I created it to make useful PDF tools more accessible without recurring fees, unnecessary online services or restrictions on essential editing features.

My goal is to develop practical, modern software that combines useful functionality, straightforward design and respect for users' privacy.

I continue to improve Velqora PDF's editing experience, offline functionality, performance and platform support.

**Made independently. Built with curiosity.**

© 2026 Cheesy Studios. See `LICENSE` and the applicable third-party license notices for legal terms.

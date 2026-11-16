# Velqora PDF 10.3

**Your PDFs. Your Freedom.**

**A free, powerful and offline PDF editor for Windows, macOS and Linux.** Edit existing PDF text, annotate documents, organize pages and make scanned PDFs searchable — without subscriptions, accounts, OCR credits or mandatory cloud services.

[**Download Velqora PDF**](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download) · [**Official website**](https://velqorapdf.pages.dev/) · [**Get support**](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)

> **Free to use · Source-available · Local document processing**
>
> Velqora PDF is designed to make everyday PDF editing accessible without recurring fees or unnecessary online services. Its source code is available for inspection and private modification under the applicable licenses. Restrictions on redistributing Cheesy Studios-owned code apply only to the extent permitted by applicable third-party licenses.

## Why Velqora PDF?

PDF editing should be simple, accessible and affordable.

Velqora PDF brings essential editing, annotation, page-management and OCR tools together in one modern desktop application.

Whether you're editing a document, highlighting important information, reorganizing pages or working with scanned PDFs, Velqora PDF gives you the tools to get things done without relying on an online editor.

**What makes Velqora PDF different?**

- **Completely free:** No subscriptions, premium editing features or OCR credits.
- **Offline-first:** Core editing and OCR tools work without an internet connection.
- **Privacy-focused:** Supported document-processing operations take place locally.
- **Cross-platform:** Available for Windows, macOS Intel, macOS Apple Silicon and Linux.
- **Modern workspace:** Organized editing tools, convenient navigation and a dedicated Comments panel.
- **Source-available:** Inspect the application code and experiment privately under the applicable license terms.

## Features

### Edit text and images

- Edit existing PDF text while retaining original formatting and fonts where possible.
- Change text colors and select alternative fonts.
- Add new text and movable text boxes.
- Insert images and adjust their positions.
- Customize font families, sizes and colors.
- Make changes directly to supported PDF content without converting the document first.

Complex layouts, embedded fonts and certain PDF structures may limit how accurately existing formatting can be preserved.

### Annotate and draw

- Highlight text in **yellow, green, blue, pink or orange**.
- Strike through text while preserving its original color, including multicolored selections.
- Draw directly on pages with a **pen, marker or brush**.
- Choose custom drawing colors and line thicknesses.
- Add notes, underlines and shapes.
- Undo changes or remove individual annotations.
- Access highlighting and drawing controls through the redesigned **Comments** panel.

### Offline OCR

Make scanned PDF documents searchable without uploading them to an external server.

- Recognize text in scanned PDF pages locally, including background recognition.
- Search, select and copy recognized text.
- Rerun OCR on individual pages or entire documents.
- Work with scanned documents without an online OCR service.
- Supported languages: **Dutch, English, German, French, Spanish and Turkish**.

**No OCR credits, external account or additional OCR payment required.**

OCR accuracy depends on scan quality, document layout and language.

### Manage pages

- Add, delete, rotate and reorder pages.
- Merge multiple PDF documents.
- Extract selected pages into separate PDFs.
- Navigate using page thumbnails.
- Use continuous scrolling and direct page navigation.

### Learn as you go

- Interactive welcome tour.
- Built-in, searchable Help Center.
- Offline guides and explanations.
- Helpful instructions for common PDF editing tasks.

## Downloads

Download official builds directly from [GitHub Releases](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download). Choose the version that matches your operating system and processor.

| Platform | Direct download | Architecture |
| --- | --- | --- |
| Windows | [Download Windows ZIP](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Windows-x64.zip) | x86-64 (Intel / AMD) |
| macOS — Intel | [Download Intel DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-Intel.dmg) | Intel 64-bit |
| macOS — Apple Silicon | [Download Apple Silicon DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-AppleSilicon.dmg) | Apple M-series |
| Linux | [Download Linux AppImage](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Linux-x86_64.AppImage) | x86-64 (Intel / AMD) |

All four builds are distributed through the official [Velqora PDF 10.3 GitHub release](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download).

**GitHub Releases is the official download source for Velqora PDF.**

### Windows

1. Download the Windows ZIP and select **Extract All**.
2. Open the extracted folder.
3. Run `Velqora PDF.exe`.
4. Keep the extracted application files together.

Do not launch the executable directly from inside the ZIP archive.

**Windows SmartScreen:** Windows may display a warning for independently distributed software. Verify that the download came from the official GitHub release before deciding whether to proceed.

### macOS

1. Download the DMG matching your Mac's processor (**Apple menu → About This Mac**).
2. Open the downloaded DMG.
3. Drag **Velqora PDF** into **Applications**.
4. Launch the application from Finder.

**Unsigned / not notarized:** Velqora PDF is not currently notarized by Apple. macOS may block the initial launch.

After verifying the download, check **System Settings → Privacy & Security** for an **Open Anyway** option.

On older macOS versions, look under **System Preferences → Security & Privacy**.

See [Apple's official guidance on opening Mac apps safely](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac).

**Compatibility:** The Intel build targets macOS 11 Big Sur or later and has been tested on macOS 15. Direct testing on macOS 11.7.11 remains pending. The Apple Silicon build is intended for compatible Apple Silicon Macs.

### Linux

Download the AppImage, then run:

```bash
cd ~/Downloads
chmod +x Velqora-PDF-10.3-Linux-x86_64.AppImage
./Velqora-PDF-10.3-Linux-x86_64.AppImage
```

Alternatively, use your file manager to mark the AppImage as executable, if supported by your desktop environment.

**Troubleshooting:**

- **Permission denied:** Run the `chmod +x` command above.
- **FUSE-related error:** Try `./Velqora-PDF-10.3-Linux-x86_64.AppImage --appimage-extract-and-run` if supported.
- **Exec format error:** Run `uname -m` and confirm that your system reports `x86_64`.
- **Application does not open:** Launch it from a terminal and inspect the error output for missing dependencies.

**Compatibility:** The Linux AppImage passed 75 automated checks in a test environment. Direct GUI testing on Ubuntu and Manjaro is still pending; compatibility across distributions is not guaranteed.

## Privacy and offline use

Velqora PDF is designed around local document processing.

- PDF editing and OCR do not require cloud uploads.
- No account or subscription is required.
- No OCR credits or external processing payments are necessary.
- Core document-processing features work offline.
- Built-in help documentation is available offline.

**Your documents remain on your computer during supported offline operations.**

These statements describe Velqora PDF's intended document-processing behavior and do not imply that every operating-system component or third-party dependency is incapable of network activity.

## Source code and development

Velqora PDF's source code is publicly available for inspection and private experimentation under the applicable licenses.

The repository includes Python application modules, supporting resources, development documentation and third-party licensing information.

**[Browse the application source code](https://github.com/Kaasplank1234/Velquorapdf/tree/main/src)** · **[View additional project files](https://github.com/Kaasplank1234/Velquorapdf/tree/main/Velqora-PDF-10.3-Remaining-Project-Files)**

### Repository structure

| Directory or file | Description |
| --- | --- |
| [`src/`](https://github.com/Kaasplank1234/Velquorapdf/tree/main/src) | Application source code |
| [`assets/`](https://github.com/Kaasplank1234/Velquorapdf/tree/main/assets) | Application assets and resources |
| [`linux-build/`](https://github.com/Kaasplank1234/Velquorapdf/tree/main/linux-build) | Linux-related build resources |
| `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/` | Preserved original source package and development files |
| `Velqora-PDF-10.3-Remaining-Project-Files/` | Additional project resources and documentation |
| `Velqora-PDF-10.3-License-*/` | Preserved third-party licensing materials |
| [`THIRD_PARTY.md`](https://github.com/Kaasplank1234/Velquorapdf/blob/main/THIRD_PARTY.md) | Third-party licensing information |
| [`LICENSE`](https://github.com/Kaasplank1234/Velquorapdf/blob/main/LICENSE) | Velqora PDF Source-Available License 1.0 |

The original extracted source directories are preserved alongside the reorganized project files.

### Building from source

The repository contains Python source files, dependency specifications and platform-specific build resources.

However, complete reproducibility of every published Velqora PDF 10.3 binary from the currently available files has not yet been verified.

Developers should review the source package's requirements files, scripts and build documentation before attempting a local build.

Some third-party dependencies and resources may need to be obtained separately.

## Source availability and licensing

Velqora PDF is **source-available**, **not open source** under the Open Source Initiative definition.

The intended permissions for independently licensable Cheesy Studios-owned code are:

| Activity | Permission |
| --- | --- |
| View and download source code | Allowed |
| Use the software for personal or internal purposes | Allowed |
| Modify source code privately | Allowed |
| Study and experiment with source code | Allowed |
| Publish or distribute modified versions of Cheesy Studios-owned code | **Written permission required** |
| Redistribute Cheesy Studios-owned source code or reuse it in another publicly distributed product | **Written permission required** |

These restrictions apply only to the extent legally permitted and do not override applicable third-party licenses.

**The actual [LICENSE](https://github.com/Kaasplank1234/Velquorapdf/blob/main/LICENSE) file controls the custom license terms.** This README is only a summary.

Third-party software remains subject to its original licenses, which may grant additional rights or impose obligations affecting the combined application.

### Third-party dependencies

Velqora PDF uses third-party software components, including:

| Component | Version | License |
| --- | --- | --- |
| PyMuPDF / MuPDF | 1.24.11 | AGPL-3.0 or commercial |
| PySide6 / Qt / Shiboken | 6.5.3 | Component-specific LGPL/GPL/commercial |
| Pillow | 11.0.0 | HPND |
| NumPy | 1.26.4 | BSD-3-Clause |
| Python | 3.11 | PSF License |
| PyInstaller | 6.11.1 | GPL with bootloader exception |
| Tesseract OCR language data | Pinned upstream version | Apache-2.0 |

Some dependencies are used only during development or packaging and may not be included in every distributed application build.

**Important licensing notice:** PyMuPDF/MuPDF is available under the AGPL or a commercial license. AGPL obligations may affect the combined application, including redistribution and source-code availability rights. Compatibility with Velqora PDF's custom Source-Available License has not yet been independently established.

See [`THIRD_PARTY.md`](https://github.com/Kaasplank1234/Velquorapdf/blob/main/THIRD_PARTY.md) for additional information.

## Known limitations

Velqora PDF is an independently developed application and continues to evolve.

- Complex PDF layouts and embedded fonts may limit text-editing accuracy.
- OCR accuracy depends on scan quality and language.
- macOS builds are currently unsigned and not notarized.
- Direct testing on macOS 11 Big Sur remains pending.
- Linux compatibility may vary between distributions.
- Complete reproducibility of the published binaries from the available source has not yet been verified.
- Third-party licensing compatibility requires further review.

## Support and feedback

Found a bug or need help getting started?

When reporting a problem, please include your **operating system/version**, **processor architecture**, **Velqora PDF version**, steps to reproduce the issue and any **exact error message**.

- [Official Velqora PDF website](https://velqorapdf.pages.dev/)
- [Download Velqora PDF](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download)
- [Report a bug or request a feature](https://github.com/Kaasplank1234/Velquorapdf/issues)
- [Contact Cheesy Studios](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)

## About

Velqora PDF is an independent hobby project by **Cheesy Studios**.

I created Velqora PDF because useful PDF tools should be accessible without expensive subscriptions, unnecessary online services or restrictions on essential editing features.

My goal is to develop practical software that combines modern design, useful functionality and respect for users' privacy.

I continue improving the editing experience, offline functionality, performance and cross-platform support.

**Made independently. Built with curiosity.**

© 2026 Cheesy Studios. See `LICENSE` and the applicable third-party license notices for legal terms.

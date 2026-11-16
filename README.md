# Velqora PDF 10.3

**Your PDFs. Your Freedom.**

**A free, offline PDF editor for Windows, macOS and Linux.** Edit documents, annotate pages, organize PDFs and make scanned documents searchable — without subscriptions, accounts or OCR credits.

[**Download Velqora PDF**](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download) · [**Official website**](https://velqorapdf.pages.dev/) · [**Get support**](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)

> **Free to use · Source-available · Local document processing**
>
> Velqora PDF's source code is available for inspection and private modification. Publishing or distributing modified versions is **not permitted without written permission**, subject to the terms of the repository's `LICENSE` file and applicable third-party licenses. **Source-available is not the same as OSI-approved open source.**

## Why Velqora PDF?

PDF editing should be straightforward and accessible. Velqora PDF brings essential editing, annotation, page-management and OCR tools into one desktop application. Its supported document-processing features work locally, so you don't have to upload PDFs to an online editor.

## Features

### Edit text and images

- Edit existing PDF text, retaining original formatting and fonts where possible.
- Change text colors and choose alternative fonts when needed.
- Add text, movable text boxes and images.
- Adjust fonts, sizes, colors and image positions.

### Annotate and draw

- Highlight text in **yellow, green, blue, pink or orange**.
- Strike through text while preserving its original color, including multicolored selections.
- Draw with a **pen, marker or brush** and customize colors and line thickness.
- Add notes, underlines and shapes; undo edits or remove individual annotations.
- Find drawing and highlighting controls in the **Comments** panel.

### Offline OCR

- Recognize text in scanned PDF pages locally, including background recognition.
- Search, select and copy recognized text.
- Rerun OCR on one page or an entire document.
- Supported languages: **Dutch, English, German, French, Spanish and Turkish**.

**No OCR credits, external account or additional OCR payment required.**

### Manage pages

- Add, delete, rotate and reorder pages.
- Merge multiple PDFs and extract selected pages.
- Navigate with thumbnails, continuous scrolling and page jumping.

### Learn as you go

- Interactive welcome tour.
- Built-in, searchable Help Center with offline guides.

## Downloads

Download official builds directly from [GitHub Releases](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download). Choose the version for your operating system below.

| Platform | Direct download | Architecture |
| --- | --- | --- |
| Windows | [Download Windows ZIP](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Windows-x64.zip) | x86-64 (Intel / AMD) |
| macOS — Intel | [Download Intel DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-Intel.dmg) | Intel 64-bit |
| macOS — Apple Silicon | [Download Apple Silicon DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-AppleSilicon.dmg) | Apple M-series |
| Linux | [Download Linux AppImage](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Linux-x86_64.AppImage) | x86-64 (Intel / AMD) |

All four files are hosted in the official [Velqora PDF 10.3 GitHub release](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download).

### Windows

1. Download the Windows ZIP and select **Extract All**.
2. Open the extracted folder and run `Velqora PDF.exe`.
3. Keep the extracted application files together; don't run the executable directly from inside the ZIP.

Windows may show a SmartScreen warning for independently distributed software. Verify that your download came from the official page before deciding whether to proceed.

### macOS

1. Download the DMG matching your Mac's processor (**Apple menu → About This Mac**).
2. Open the DMG and drag **Velqora PDF** into **Applications**.
3. Open the application from Finder.

**Unsigned / not notarized:** macOS may block the first launch. After verifying the download, check **System Settings → Privacy & Security** for an **Open Anyway** option. On older macOS versions, look under **System Preferences → Security & Privacy**. See [Apple's guidance on opening Mac apps safely](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac).

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
- The built-in help content is available offline.

Your documents remain on your computer during supported offline operations.

## Source availability and licensing

Velqora PDF is **source-available**, **not open source** under the Open Source Initiative definition.

The intended permissions for the Velqora PDF-owned code are:

| Activity | Permission |
| --- | --- |
| View and download source code | Allowed |
| Modify source code privately | Allowed |
| Publish or distribute modified versions | **Not allowed without written permission** |
| Redistribute source code or reuse it in another product | **Not allowed without written permission** |

**The actual `LICENSE` file controls the legal terms.** This README is only a summary. Third-party components remain subject to their respective licenses; this project's terms do not override them. If the repository still contains AGPL-licensed code or notices, review those rights before replacing any license files or publishing the source.

## Support and feedback

Found a bug or need help getting started? Please include your **operating system/version**, **processor architecture**, **Velqora PDF version**, and any **exact error message**.

- [Official Velqora PDF website](https://velqorapdf.pages.dev/)
- [Download Velqora PDF](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download)
- [Contact Cheesy Studios](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)

## About

Velqora PDF is an independent hobby project by **Cheesy Studios**. I created it to make useful PDF tools more accessible without recurring fees or unnecessary online services. I continue to improve the editing experience, offline features and platform support.

**Made independently. Built with curiosity.**

© 2026 Cheesy Studios. See `LICENSE` for applicable terms.

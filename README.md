# Velqora PDF 10.3

**Your PDFs. Your Freedom.**

Velqora PDF is a free, offline-first PDF editor for Windows, macOS and Linux. I created it to make routine document editing simple without subscriptions, accounts, hidden OCR fees, or cloud-only workflows.

- [Official website](https://velqorapdf.pages.dev/)
- [GitHub Releases](https://github.com/Kaasplank1234/Velquorapdf/releases/tag/Download)
- [Support and feedback](https://www.cheesy-studios.22web.org/neem-contact-met-ons-op-faq)

> Free to use · Source-available · Local document processing
>
> The app is designed to work offline wherever possible, with document processing kept local to the machine.

## Why Velqora PDF?

PDF work should be practical, private, and straightforward. Velqora PDF combines the essentials most people need in a desktop PDF editor: text editing, annotations, page organization, and local OCR for scanned files.

It is built for everyday use on personal documents, forms, scan cleanup, and reference PDFs. Nothing in the app requires a web account or an online OCR service to complete core editing tasks.

## Features

### Edit text and images

- Edit existing PDF text and change its color.
- Add movable text boxes and images.
- Customize fonts, sizes, and colors.
- Replace or update text directly in supported PDF content.

### Annotate and draw

- Highlight text in yellow, green, blue, pink, and orange.
- Strike through text while preserving the original text color.
- Draw with pens, markers, and brushes.
- Add notes, underlines, and shapes.
- Use the Comments panel for quick annotation workflows.

### Offline OCR

- Offline OCR with Dutch, English, German, French, Spanish, and Turkish.
- Search, select, and copy recognized text.
- Run OCR in the background and revisit results later.

### Page organization

- Add, delete, rotate, and reorder PDF pages.
- Merge PDFs and extract selected pages.
- Browse pages using thumbnails and quick navigation.

### Onboarding and help

- Interactive welcome tour.
- Built-in offline Help Center.

## Downloads

The official release assets are published on GitHub Releases only.

| Platform | Direct download | Architecture |
| --- | --- | --- |
| Windows x64 | [Download Windows ZIP](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Windows-x64.zip) | x86-64 |
| macOS Intel | [Download Intel DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-Intel.dmg) | Intel 64-bit |
| macOS Apple Silicon | [Download Apple Silicon DMG](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-macOS-AppleSilicon.dmg) | Apple Silicon |
| Linux x86-64 | [Download Linux AppImage](https://github.com/Kaasplank1234/Velquorapdf/releases/download/Download/Velqora-PDF-10.3-Linux-x86_64.AppImage) | x86-64 |

## Windows installation

1. Download the Windows ZIP from the official release.
2. Extract the ZIP to a location of your choice.
3. Open the extracted folder and launch `Velqora PDF.exe`.
4. Keep the extracted folder together; the app expects its bundled files alongside the executable.

## macOS installation

1. Check whether your Mac is Intel or Apple Silicon.
2. Download the matching DMG from the release list.
3. Open the DMG and drag `Velqora PDF.app` into Applications.
4. Launch the app from Applications.

macOS builds may be unsigned and may not be notarized by Apple. Follow Apple's official guidance before opening a downloaded app for the first time: https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac

Do not disable Gatekeeper broadly as a workaround.

## Linux installation

The Linux release is distributed as an AppImage.

```bash
cd ~/Downloads
chmod +x Velqora-PDF-10.3-Linux-x86_64.AppImage
./Velqora-PDF-10.3-Linux-x86_64.AppImage
```

If the AppImage fails on a system without FUSE support, try:

```bash
cd ~/Downloads
./Velqora-PDF-10.3-Linux-x86_64.AppImage --appimage-extract-and-run
```

## Privacy and offline use

Velqora PDF is intended to be local-first. The app can work without a cloud OCR service and without an online account. PDF editing and recognition functions are designed to run on the local machine, which keeps documents in the user's control.

This does not guarantee every workflow is 100% offline in all environments, but the app is built around local processing rather than mandatory online services.

## Source code and development

The full source package for the 10.3 release is preserved in:

- `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/`

The application entry point is:

- `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/src/main.py`

For platform-specific build and development steps, see `DEVELOPMENT.md`.

## Source availability and licensing

- The project-owned license is the root `LICENSE` file.
- Third-party dependency notices are recorded in `THIRD_PARTY.md`.
- Preserved license archives and provenance files remain in the repository for legal review.

This project uses a custom source-available license for Cheesy Studios-owned material. Third-party components, especially AGPL-licensed software such as PyMuPDF/MuPDF, retain their own licensing obligations. The repo preserves those notices and does not silently relicense them.

## Known limitations

- Text replacement can be limited by embedded fonts, PDF structures, and layout complexity.
- Some advanced editing and form operations remain constrained by the underlying PDF engine.
- The app is designed for practical desktop editing, not exhaustive Acrobat parity.
- OCR quality depends on scan quality, page layout, and language selection.

## Support and feedback

If you run into a bug or want to send feedback, use the support page linked above or the release discussion thread for the current version.

Please include the OS version, architecture, application version, and a short description of the problem when reporting issues.

## About

I created Velqora PDF as an independent hobby project. My goal was to make a capable, private, and approachable PDF editor that stays useful without subscriptions or unnecessary online dependencies.

I continue improving it with a focus on local workflows, document reliability, and a clean user experience.

Made independently. Built with curiosity.


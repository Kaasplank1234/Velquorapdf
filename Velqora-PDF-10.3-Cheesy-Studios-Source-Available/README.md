# Velqora PDF 3.0
Native offline PDF editor, continuing the existing LibrePDF Pro sources. AGPL-3.0-or-later; no account, ads, subscription or web server.

## Install
Open Velqora-PDF-3.0-macOS-Intel.dmg and drag Velqora PDF.app to Applications. End users need no Python. The app is ad-hoc signed, NOT Developer ID signed or notarized. Follow macOS's normal security interface; do not disable Gatekeeper.

Target: Intel x86_64 and macOS 11+. Build script checks the minimum OS load commands and linked libraries of every Mach-O binary. Passing these static checks is not proof of Big Sur runtime compatibility. Native execution is tested on the GitHub runner OS, reported in reports/build-host.txt. No physical 2013 Mac or Big Sur test has been performed here.

## What's new in 2.6

- After OCR, the Document Text window shows recognized text from every page. Use **Copy All Text** to copy it, or select and copy part of it. The **Document** menu has both text commands for reopened PDFs as well.
- OCR results opened from password-protected PDFs keep the source password when saved.
- The installed macOS app asks once if you want Velqora to open PDFs by default. You can decline or return to **Document → Set as Default PDF App**. If macOS cannot apply the change, the app shows the equivalent Finder steps.
- Finder requests to open a PDF during startup are queued until the window is ready.

## Working features
- Own coral/graphite identity, original icons, light/dark theme, native menus, document tabs, recent documents and workspace preferences.
- Open/save/password PDFs, drag files, zoom/Ctrl-wheel/fit width, selected-page thumbnail and drag page ordering, search, bookmarks, links, properties, printing.
- Add/replace/delete/move text; double-click a text line to edit. Choose standard font, size, color and paragraph alignment. Replacement removes old characters and reconstructs the region, rather than covering the old text.
- Add/move/scale/replace/delete/rotate/export images. Shared image resources are refused to prevent editing other occurrences. Movement preserves soft-mask transparency.
- Rotate/duplicate/delete/insert/crop pages, insert another PDF, extract selected pages, split into groups.
- Six built-in offline OCR languages: Dutch, English, German, French, Spanish, Turkish. Runs in a separate process with progress and cancellation. Creates a new rasterized searchable PDF at 150 dpi; save it separately.
- Highlight, underline, strikeout, notes, rectangle, circle, arrow, delete page annotations and export annotation JSON.
- Fill basic PDF fields; draw a visual signature and place as an image; edit title/author/subject/keywords; watermarks and page numbers.
- TXT/HTML/PNG/text-only DOCX export; images to PDF; AES-256 password save, retained encryption on subsequent save; actual redaction; lossless cleanup/deflation on save.
- Atomic saves, transactional rollback, bounded undo/redo, Save/Discard/Cancel on close.

## Limits
This is not complete Acrobat parity. Text replacement uses a chosen base font and does not preserve original PDF operators, embedded fonts, exact layout or text flow across paragraphs. Standard-font coverage is limited. Redaction should be inspected in a saved copy before distribution; previous originals and undo history may retain sensitive content until closed.
No certified digital signatures, PDF/A, DOCX import, precise Word layout/table conversion, automatic OCR language detection, batch interface, autosave/recovery, image crop, ink annotation or visual document comparison. Comparison is extracted text only. Radio buttons and multi-select forms have limited support. Printing rasterizes pages.
Rendering and large document mutations still run on the UI thread and may pause on complex/large files; only the selected page is rendered, capped at 6 million pixels. OCR is isolated in a child process, not a MuPDF thread. Undo snapshots can use up to ~48 MiB plus the live document (one large transient snapshot can exceed this).

## Source run
Python 3.11: `python -m venv .venv`, activate, `pip install -r requirements.txt`, then `python src/main.py`.
The source ZIP already includes six tessdata_fast models (Apache-2.0) pinned to upstream commit 87416418657359cb625c412a48b6e1d6d41c29bd, hashes in assets/tessdata/manifest.json.

## Build and tests
`bash scripts/build_macos.sh` on an Intel Mac with Python 3.11.9. Dependencies and hashes are pinned in requirements-macos.lock (PySide6 6.5.3 and PyMuPDF 1.24.11). The CI wrapper in the existing repository extracts the source ZIP and invokes this script on macos-15-intel.
Tests: `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v` and `python src/main.py --self-test --report report.json`.
Build verifies architecture/dependencies, runs frozen app offscreen and Cocoa tests, creates an HFS+ DMG, mounts read-only, checks app/Applications link, repeats binary audit and runs the mounted standalone application.
Authoritative results are in the accompanying build reports; do not interpret this README as proof a build passed.

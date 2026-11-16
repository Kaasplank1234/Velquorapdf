# Velqora PDF 2.3 verification

All 16 unit tests and 16 integrated app checks passed on Linux x86_64 with Python 3.12.14, Qt 6.6.3 and PyMuPDF 1.24.11. The new checks cover cross-page search, persistent highlighting, ordered page extraction, encryption retention and checkbox save/reopen. Manual smoke checks also verified dropdown values and mixed English–Dutch OCR.

The page-range checks cover undo, password retention when splitting, refusal to overwrite outputs, and cleanup after a simulated write failure.

The macOS build runs the same tests with the pinned native dependencies. See the build reports for the runner version and mounted DMG verification. macOS Big Sur runtime verification is pending.

The Linux app check copied recognized text from two pages in order. The Launch Services lookup is exercised by the frozen macOS self-test. Changing the system default is an interactive macOS action.

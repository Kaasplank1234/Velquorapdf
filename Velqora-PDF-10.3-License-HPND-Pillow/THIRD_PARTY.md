# Afhankelijkheden

| Bibliotheek | Versie | Licentie / bron |
| --- | --- | --- |
| PyMuPDF / MuPDF | 1.24.11 | AGPL-3.0; https://github.com/pymupdf/PyMuPDF/tree/1.24.11 |
| PySide6 / Qt / Shiboken | 6.5.3 | LGPLv3/GPLv3/commerciële keuzelicenties per component; LGPL-route; https://code.qt.io/cgit/pyside/pyside-setup.git/ en https://www.qt.io/licensing/open-source-lgpl-obligations |
| Pillow | 11.0.0 | HPND/Pillow notices; https://github.com/python-pillow/Pillow/tree/11.0.0 |
| NumPy | 1.26.4 | BSD-3-Clause; https://github.com/numpy/numpy/tree/v1.26.4; workaround voor Qt bindings; niet nodig in frozen app |
| CPython | 3.11 | PSF License; https://www.python.org/downloads/ |
| PyInstaller (buildtool) | 6.11.1 | GPL met bootloader-uitzondering; https://pyinstaller.org/en/v6.11.1/license.html |
| Tesseract (optioneel, niet gebundeld) | lokaal geïnstalleerd | Apache-2.0; https://github.com/tesseract-ocr/tesseract |

De editor gebruikt geen qpdf, Poppler, OCRmyPDF of pypdf. Voeg geen ongebruikte afhankelijkheden toe alleen omdat ze in het oorspronkelijke wensenpakket stonden.

De macOS-build neemt licentieteksten en package metadata mee via PyInstaller. De bron-ZIP bevat de eigen AGPL-licentie en dependencyversies; upstream-broncode is via bovenstaande links beschikbaar en niet volledig in dit kleine projectarchief opgenomen. Bij een daadwerkelijke binaryrelease moeten notices en corresponderende dependencybronnen blijvend beschikbaar worden gesteld. LGPL-bibliotheken blijven dynamisch; geen restrictie op vervanging of reverse engineering voor debugging van wijzigingen toevoegen.

Velqora 2.0 bundles tessdata_fast language data nld/eng/deu/fra/spa/tur under Apache-2.0; license in assets/tessdata/LICENSE. Pinned source: https://github.com/tesseract-ocr/tessdata_fast/tree/87416418657359cb625c412a48b6e1d6d41c29bd . MuPDF's integrated Tesseract is used instead of a required external executable. Original icons drawn in workspace.py and make_icon.py.

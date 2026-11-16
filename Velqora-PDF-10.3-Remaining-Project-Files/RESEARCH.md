# Technische keuze en verificatie — 10 november 2026

Beschikbare host: Linux x86_64. Geen macOS SDK/runtime, geen echte Intel Mac, geen ingelogde gh CLI. De GitHub-koppeling herkent het account en kan bestaande repositories lezen, maar biedt hier geen repositoryaanmaak of dispatch van nieuwe workflowruns. De browser toont GitHub-sign-in. Beschikbare GitHub-connectoracties bevatten repositorybestanden en workflowresultaten, maar geen mogelijkheid om hier een macOS-host te provisionen of een nieuwe workflowrun te starten. Daarom geen macOS-binary of DMG geclaimd.

Gekozen: CPython 3.11, PySide6 6.5.3, PyMuPDF 1.24.11. Qt 6.5 ondersteunt macOS 11 en Intel. De PySide6 6.5.3-wheel is macosx_11_0_universal2. De PyMuPDF 1.24.11-wheel heeft een macosx_10_9_x86_64-tag. Tags en ondersteunde platforms zijn aanwijzingen, geen runtimebewijs; de uiteindelijke gebundelde bestanden moeten de audit en een Big Sur-test doorstaan.

Primaire bronnen:

- https://doc.qt.io/qt-6.5/supported-platforms.html
- https://pypi.org/project/PySide6/6.5.3/
- https://pypi.org/project/PyMuPDF/1.24.11/
- https://github.com/pymupdf/PyMuPDF
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
- https://github.com/actions/runner-images/issues/13045
- https://pyinstaller.org/en/v6.11.1/usage.html#building-macos-app-bundles

Een echte externe Intel-build is technisch mogelijk via GitHub Actions `macos-15-intel`. Dat is opgenomen als workflow; niet daadwerkelijk uitgevoerd. Runnerbeschikbaarheid kan veranderen. De compatibiliteitsaudit weigert een te hoge deployment target in afhankelijkheden, in plaats van uitsluitend Info.plist op 11.0 te zetten.

OCR is optioneel via een lokale Tesseract-subprocess. Er is nog geen compatibele, volledig meegenomen macOS-Tesseractdistributie onderzocht/gebouwd. qpdf, OCRmyPDF en Poppler zouden extra distributie- en licentiewerk vragen en zijn niet geïntegreerd.

Geen uitspraak dat alle oudere dependencyversies tegenwoordig de veiligste keuzes zijn. Versies zijn hier gekozen voor het expliciete oude besturingssysteem en moeten voor een publiek verspreide release opnieuw worden onderhouden en gecontroleerd.


Vervolg: echte macOS-wheels en het CPython 3.11.9-macos11.pkg uit de setup-python-release zijn statisch onderzocht op Linux. Rapporten met wheelhashes, onderzochte Intel-binaries en minimumtargets staan in verification/. Dit is headeronderzoek, geen uitvoering van macOS-code. De nieuwe workflow bevat een dependency-hashlock, blijvende foutlogs en read-only DMG-mountcontroles. Er is nog geen GitHub-run gestart.

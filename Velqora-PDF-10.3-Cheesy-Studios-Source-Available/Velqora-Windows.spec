# Native Windows x64 build. Keep the executable with its _internal folder.
from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata

root = Path(SPECPATH)
notices = []
for package in ('PyMuPDF', 'PySide6', 'PySide6-Essentials', 'PySide6-Addons', 'shiboken6', 'Pillow'):
    notices.extend(copy_metadata(package))

analysis = Analysis(
    [str(root / 'src/main.py')],
    pathex=[str(root / 'src')],
    datas=[(str(root / 'assets'), 'assets')] + [
        (str(root / name), '.') for name in ('LICENSE', 'THIRD_PARTY.md', 'WINDOWS.md')
    ] + notices,
    hiddenimports=['fitz', 'pymupdf'],
    excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'numpy', 'tkinter'],
)
archive = PYZ(analysis.pure)
executable = EXE(
    archive, analysis.scripts, [], exclude_binaries=True,
    name='Velqora PDF', console=False, icon=str(root / 'assets/icon.png'),
)
distribution = COLLECT(executable, analysis.binaries, analysis.datas, name='Velqora PDF')

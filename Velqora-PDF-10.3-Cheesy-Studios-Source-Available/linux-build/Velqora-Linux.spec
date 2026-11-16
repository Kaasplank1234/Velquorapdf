from pathlib import Path

root = Path(SPECPATH).parent / 'project'
app = Analysis(
    [str(root / 'src/main.py')],
    pathex=[str(root / 'src')],
    datas=[(str(root / 'assets'), 'assets'),
           *[(str(root / name), '.') for name in ('README.md', 'LICENSE', 'THIRD_PARTY.md')]],
    hiddenimports=['fitz', 'pymupdf', 'PySide6.QtSvg'],
    excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'numpy', 'tkinter'],
)
app.exclude_system_libraries()
archive = PYZ(app.pure)
program = EXE(archive, app.scripts, [], exclude_binaries=True, name='velqora-pdf', console=True)
bundle = COLLECT(program, app.binaries, app.datas, name='velqora-pdf')

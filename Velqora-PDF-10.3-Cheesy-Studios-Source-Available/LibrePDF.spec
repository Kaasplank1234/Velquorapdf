# PyInstaller build for the native macOS host architecture.
import platform
from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata
root=Path(SPECPATH)
notices=[]
for name in ['PyMuPDF','PySide6','PySide6-Essentials','PySide6-Addons','shiboken6','Pillow']:
    notices+=copy_metadata(name)
a=Analysis([str(root/'src/main.py')],pathex=[str(root/'src')],
    datas=[(str(root/'assets'),'assets'),(str(root/'README.md'),'.'),(str(root/'LICENSE'),'.'),(str(root/'THIRD_PARTY.md'),'.')]+notices,
    hiddenimports=['fitz','pymupdf'],excludes=['PySide6.QtWebEngineCore','PySide6.QtWebEngineWidgets','numpy','tkinter'],noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='Velqora PDF',console=False,target_arch=platform.machine())
coll=COLLECT(exe,a.binaries,a.datas,name='Velqora PDF')
app=BUNDLE(coll,name='Velqora PDF.app',icon=str(root/'assets/icon.icns'),bundle_identifier='org.velqora.pdf',
 info_plist={'CFBundleShortVersionString':'10.3.0','CFBundleVersion':'1030', 'LSMinimumSystemVersion':'11.0',
 'CFBundleDevelopmentRegion':'en','NSHighResolutionCapable':True,'CFBundleDocumentTypes':[{'CFBundleTypeName':'PDF document','CFBundleTypeRole':'Editor','LSItemContentTypes':['com.adobe.pdf'],'LSHandlerRank':'Alternate'}]})

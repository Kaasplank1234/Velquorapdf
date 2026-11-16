"""Offline fonts packaged with Velqora, plus the standard PDF families."""
from functools import lru_cache
from pathlib import Path
import os
import re
import sys

STANDARD = {'Helvetica': 'helv', 'Times': 'tiro', 'Courier': 'cour'}

@lru_cache(maxsize=1)
def bundled_fonts():
    assets = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1])) / 'assets/fonts'
    entries = {}
    for metadata in sorted(assets.glob('*/METADATA.pb')):
        label = re.search(r'^name: "([^"]+)"', metadata.read_text(encoding='utf-8'), re.M)
        path = next(metadata.parent.glob('*.ttf'), None)
        if label and path:
            entries[label[1]] = path
    return dict(sorted(entries.items(), key=lambda item: item[0].casefold()))

@lru_cache(maxsize=1)
def available_fonts():
    fonts = dict(bundled_fonts())
    local = {'Arial': ('arial.ttf', 'Arial.ttf'), 'Times New Roman': ('times.ttf', 'Times New Roman.ttf'), 'Verdana': ('verdana.ttf', 'Verdana.ttf'), 'Georgia': ('georgia.ttf', 'Georgia.ttf'), 'Calibri': ('calibri.ttf', 'Calibri.ttf')}
    roots = [Path('/System/Library/Fonts/Supplemental'), Path('/Library/Fonts'), Path.home() / 'Library/Fonts']
    if sys.platform == 'win32':
        roots = [Path(os.environ.get('WINDIR', r'C:\Windows')) / 'Fonts']
    for name, filenames in local.items():
        path = next((folder / filename for folder in roots for filename in filenames if (folder / filename).is_file()), None)
        if path:
            fonts[name] = path
    return fonts

import sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from main import App,Window
import fitz

def exercise(window):
    e=window.current()
    e.doc.add_text(0,fitz.Rect(30,30,350,110),'GUI persistence test',16)
    e.refresh(); e.blank(); e.rotate(); e.doc.undo(); e.refresh()
    with tempfile.TemporaryDirectory() as temp:
        path=str(Path(temp)/'roundtrip.pdf')
        e.doc.save(path); window.open(path)
        assert 'GUI persistence test' in window.current().doc.pdf[0].get_text()
        assert len(window.current().doc.pdf)==2
        image=window.grab(); assert not image.isNull()
        if '--screenshot' in sys.argv:image.save(str(Path(__file__).resolve().parents[1]/'preview.png'))
        window.close_tab(window.tabs.currentIndex())
    # Avoid prompting at teardown.
    for i in range(window.tabs.count()):window.tabs.widget(i).doc.dirty=False
    print('GUI_START_OPEN_EDIT_SAVE_REOPEN_OK',flush=True)

if __name__=='__main__':
    app=App([]); win=Window(); app.window=win; win.show(); app.processEvents(); exercise(win); win.close()

import os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import fitz
from engine import Document

class Tools(unittest.TestCase):
    def test_annotations_forms_metadata(self):
        d=Document()
        def op(pdf):
            p=pdf[0]
            p.add_highlight_annot(fitz.Rect(10,10,100,40))
            w=fitz.Widget(); w.field_name='Name'; w.field_type=fitz.PDF_WIDGET_TYPE_TEXT; w.rect=fitz.Rect(40,100,200,140); w.field_value='Arda'; p.add_widget(w)
            pdf.set_metadata({'title':'Editor test'})
        d.change(op)
        with tempfile.TemporaryDirectory() as tmp:
            path=str(Path(tmp)/'form.pdf');d.save(path)
            r=fitz.open(path)
            self.assertEqual(r.metadata['title'],'Editor test')
            self.assertEqual(next(r[0].widgets()).field_value,'Arda')
            self.assertEqual(len(list(r[0].annots())),1);r.close()
    def test_ui_tools(self):
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        from main import App,Window
        from PySide6.QtWidgets import QInputDialog
        from unittest.mock import patch
        app=App.instance() or App([]); window=Window(); app.window=window
        e=window.current()
        e.mode='Add text'
        with patch.object(QInputDialog,'getMultiLineText',return_value=('Inserted through GUI',True)):
            e.apply_tool(fitz.Rect(30,30,400,100),fitz.Point(30,30))
        e.mode='Replace text'
        with patch.object(QInputDialog,'getMultiLineText',return_value=('Changed through GUI',True)):
            e.apply_tool(fitz.Rect(29,29,401,101),fitz.Point(29,29))
        self.assertNotIn('Inserted',e.doc.pdf[0].get_text())
        self.assertIn('Changed',e.doc.pdf[0].get_text())
        for mode in ['Highlight','Underline','Strike through','Rectangle','Circle','Arrow']:
            e.mode=mode;e.apply_tool(fitz.Rect(30,150,150,200),fitz.Point(30,150))
        self.assertEqual(len(list(e.doc.pdf[0].annots())),6)
        e.blank();e.duplicate();self.assertEqual(len(e.doc.pdf),3)
        e.delete();self.assertEqual(len(e.doc.pdf),2)
        e.doc.dirty=False;window.close()

if __name__=='__main__':unittest.main(verbosity=2)

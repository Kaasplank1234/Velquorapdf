import unittest, tempfile, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from engine import Document
import fitz
from PIL import Image

class RoundTrip(unittest.TestCase):
    def test_edit_save_reopen(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); d=Document()
            d.add_text(0,(40,40,300,90),'ORIGINAL SECRET',14)
            d.replace_text(0,fitz.Rect(39,39,301,91),'REPLACED',14)
            self.assertNotIn('ORIGINAL',d.pdf[0].get_text())
            self.assertIn('REPLACED',d.pdf[0].get_text())
            image=root/'image.png'; Image.new('RGB',(40,30),'red').save(image)
            d.image(0,fitz.Rect(50,150,150,250),str(image))
            info=d.pdf[0].get_image_info(xrefs=True)[0]
            d.move_image(0,info,fitz.Rect(200,150,300,250))
            d.change(lambda pdf:pdf.new_page())
            d.change(lambda pdf:pdf.select([1,0]))
            d.undo(); self.assertIn('REPLACED',d.pdf[0].get_text())
            d.undo(True); self.assertIn('REPLACED',d.pdf[1].get_text())
            path=root/'edited.pdf'; d.save(str(path))
            check=fitz.open(path)
            self.assertEqual(len(check),2)
            self.assertIn('REPLACED',check[1].get_text())
            self.assertNotIn('SECRET',check[1].get_text())
            self.assertTrue(any(fitz.Rect(i['bbox']).x0==200 for i in check[1].get_image_info()))
            check.close()
            d.save(str(root/'locked.pdf'),'strong-password')
            locked=fitz.open(root/'locked.pdf'); self.assertTrue(locked.needs_pass); self.assertTrue(locked.authenticate('strong-password')); locked.close()
    def test_redaction_and_transaction(self):
        d=Document(); d.add_text(0,(30,30,300,80),'REMOVE ME',14)
        before=d.pdf[0].get_text()
        with self.assertRaises(ValueError): d.replace_text(0,fitz.Rect(30,30,31,31),'Too long',144)
        self.assertEqual(before,d.pdf[0].get_text())
        d.redact(0,fitz.Rect(29,29,301,81))
        reopened=fitz.open(stream=d.snapshot(),filetype='pdf')
        self.assertNotIn('REMOVE',reopened[0].get_text()); reopened.close()

if __name__=='__main__':unittest.main(verbosity=2)

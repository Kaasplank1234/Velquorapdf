import unittest,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import fitz
from engine import Document
from worker_engine import recognize

class Upgrade(unittest.TestCase):
    def test_move_text(self):
        d=Document();d.add_text(0,(40,40,400,100),'Moving text',14)
        rect=d.pdf[0].search_for('Moving text')[0];d.relocate_text(0,rect,fitz.Rect(40,180,400,250),'Moving text',14)
        with fitz.open(stream=d.snapshot(),filetype='pdf') as p:
            self.assertEqual(len(p[0].search_for('Moving text')),1);self.assertGreater(p[0].search_for('Moving text')[0].y0,170)
    def test_encryption_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=str(Path(tmp)/'locked.pdf');d=Document();d.save(path,'secret');d=Document(path,'secret');d.add_text(0,(30,30,300,100),'Protected');d.save(path)
            with fitz.open(path) as p:self.assertTrue(p.needs_pass);self.assertTrue(p.authenticate('secret'))
    def test_all_ocr_models(self):
        d=Document();d.add_text(0,(30,30,450,100),'HELLO WORLD 123',28)
        for lang in ['eng','nld','deu','fra','spa','tur']:
            with self.subTest(lang=lang),fitz.open(stream=recognize(d.pdf,lang),filetype='pdf') as p:self.assertIn('123',p[0].get_text())

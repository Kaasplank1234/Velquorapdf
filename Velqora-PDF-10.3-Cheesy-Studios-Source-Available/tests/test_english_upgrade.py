import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import fitz
from PySide6.QtWidgets import QInputDialog
from engine import Document, parse_page_ranges
from main import App, Window


class EnglishUpgrade(unittest.TestCase):
    def setUp(self):
        self.app = App.instance() or App([])
        self.window = Window()
        self.app.window = self.window
        self.editor = self.window.current()

    def tearDown(self):
        self.editor.doc.dirty = False
        self.window.close()

    def test_find_across_pages_and_wrap(self):
        for text in ('Find this phrase', 'Find this phrase twice: phrase'):
            page = self.editor.doc.pdf[0] if len(self.editor.doc.pdf) == 1 and not self.editor.doc.pdf[0].get_text() else self.editor.doc.pdf.new_page()
            page.insert_text((50, 60), text)
        self.editor.refresh()
        self.window.search()
        self.editor.find_input.setText('phrase')
        self.editor.find()
        self.assertEqual(self.editor.find_status.text(), '1 of 3')
        self.editor.find(-1)
        self.assertEqual(self.editor.page, 1)
        self.assertEqual(self.editor.find_status.text(), '3 of 3')
        self.editor.zoom(.8)
        self.assertEqual(len(self.editor.search_hits), 3)
        self.editor.find()
        self.assertEqual(self.editor.page, 0)
        self.editor.close_find()
        self.assertEqual(self.editor.search_hits, [])

    def test_extract_order_and_password(self):
        doc = Document()
        for number in range(1, 5):
            page = doc.pdf[0] if number == 1 else doc.pdf.new_page()
            page.insert_text((50, 60), f'Page {number}')
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'source.pdf'
            result = Path(folder) / 'extracted.pdf'
            doc.save(source, 'test password')
            doc.extract_pages(parse_page_ranges('4, 1-2, 2', 4), result)
            with fitz.open(result) as output:
                self.assertTrue(output.needs_pass)
                self.assertTrue(output.authenticate('test password'))
                self.assertEqual([p.get_text().strip() for p in output], ['Page 4', 'Page 1', 'Page 2'])
            with self.assertRaises(ValueError):
                doc.extract_pages([0], source)
        for invalid in ('', '0', '4-2', '5', '1,,2'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_page_ranges(invalid, 4)
        doc.pdf.close()

    def test_checkbox_roundtrip(self):
        page = self.editor.doc.pdf[0]
        field = fitz.Widget()
        field.field_name = 'Accept'
        field.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
        field.rect = fitz.Rect(50, 50, 70, 70)
        page.add_widget(field)
        for option, expected in [('Checked', 'Yes'), ('Unchecked', 'Off')]:
            with patch.object(QInputDialog, 'getItem', side_effect=[('1: Accept', True), (option, True)]):
                self.editor.form()
            with fitz.open(stream=self.editor.doc.snapshot(), filetype='pdf') as output:
                self.assertEqual(next(output[0].widgets()).field_value, expected)

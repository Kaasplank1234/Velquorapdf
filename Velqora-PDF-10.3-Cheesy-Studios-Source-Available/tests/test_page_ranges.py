import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import fitz
from engine import Document, parse_page_ranges


class PageRanges(unittest.TestCase):
    def setUp(self):
        self.document = Document()
        for number in range(1, 6):
            page = self.document.pdf[0] if number == 1 else self.document.pdf.new_page()
            page.insert_text((50, 60), f'Page {number}')

    def tearDown(self):
        self.document.pdf.close()

    def test_range_edits_are_undoable(self):
        doc = self.document
        doc.edit_page_range(parse_page_ranges('2, 4-5', 5), 'counterclockwise')
        self.assertEqual([p.rotation for p in doc.pdf], [0, 270, 0, 270, 270])
        doc.edit_page_range([1, 3], 'delete')
        self.assertEqual([p.get_text().strip() for p in doc.pdf], ['Page 1', 'Page 3', 'Page 5'])
        doc.undo()
        self.assertEqual(len(doc.pdf), 5)
        doc.undo()
        self.assertEqual([p.rotation for p in doc.pdf], [0] * 5)
        with self.assertRaises(ValueError):
            doc.edit_page_range(range(5), 'delete')
        self.assertEqual(len(doc.pdf), 5)

    def test_split_preserves_password_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            doc = self.document
            doc.save(Path(folder) / 'Protected.pdf', 'sample password')
            paths = doc.split(folder, 2)
            self.assertEqual([p.name for p in paths], [
                'Protected-pages-1-2.pdf', 'Protected-pages-3-4.pdf', 'Protected-pages-5-5.pdf',
            ])
            result = []
            for path in paths:
                with fitz.open(path) as part:
                    self.assertTrue(part.needs_pass)
                    self.assertTrue(part.authenticate('sample password'))
                    result.extend(p.get_text().strip() for p in part)
            self.assertEqual(result, [f'Page {n}' for n in range(1, 6)])
            before = paths[0].read_bytes()
            with self.assertRaises(ValueError):
                doc.split(folder, 2)
            self.assertEqual(paths[0].read_bytes(), before)

    def test_failed_split_removes_partial_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch('engine.shutil.copyfileobj', side_effect=OSError('Disk full')):
                with self.assertRaises(OSError):
                    self.document.split(folder, 2)
            self.assertEqual(list(Path(folder).iterdir()), [])

"""Real GUI/document roundtrip, also shipped inside the frozen executable."""
import json,platform,sys,tempfile,traceback
from pathlib import Path
import fitz
from engine import Document

def run(window, report_path=None):
    report={'status':'failed','system':platform.system(),'macos':platform.mac_ver()[0],
            'machine':platform.machine(),'frozen':bool(getattr(sys,'frozen',False)),
            'python':platform.python_version(),'pymupdf':fitz.VersionBind,'checks':[],
            'big_sur_runtime_verified':platform.system()=='Darwin' and platform.mac_ver()[0].startswith('11.')}
    def check(condition,name):
        if not condition:raise RuntimeError('Self-test failed: '+name)
        report['checks'].append(name)
    try:
        from PySide6.QtCore import qVersion, Qt, QPoint, QPointF
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication
        from PIL import Image
        report['qt']=qVersion()
        if platform.system() == 'Darwin' and report['frozen']:
            from macos_defaults import pdf_handler
            check(isinstance(pdf_handler(), bool), 'macOS PDF handler lookup')
        check(window.tabs.count() == 0, 'home opens without creating a blank document')
        e=window.current()
        from PySide6.QtWidgets import QPushButton
        QApplication.processEvents()
        check(e.tool_panel.isHidden(), 'PDF opens in a clear reading workspace')
        check(e.split.indexOf(e.pages) == 2 and e.split.indexOf(e.tool_panel) == 0,
              'tools on the left and page thumbnails on the right')
        QTest.mouseClick(e.mode_buttons[0], Qt.LeftButton)
        check(not e.tool_panel.isHidden() and e.mode_buttons[0].isChecked(),
              'labeled Edit PDF action opens the editing tools')
        e.choose_mode('Replace text')
        check(e.tool_status.text() == 'Replace text', 'active editing mode is visible in the toolbar')
        check(not window.tabs.tabBar().drawBase(), 'document tabs omit the native base border')
        e.open_tool_category(2)
        e.brush.showPopup()
        QApplication.processEvents()
        check(e.brush.view().isVisible(), 'styled drawing dropdown opens')
        QTest.keyClick(e.brush.view(), Qt.Key_Down)
        QTest.keyClick(e.brush.view(), Qt.Key_Return)
        check(e.brush.currentText() == 'Marker' and e.ink_width.value() == 12,
              'keyboard selection in drawing dropdown updates stroke width')
        QTest.keyClick(e.ink_width, Qt.Key_Up)
        check(e.ink_width.value() == 13, 'styled stroke width input responds to keyboard')
        e.brush.setCurrentText('Pen')
        e.open_tool_category(0)
        e.choose_mode('Select')
        e.doc.add_text(0,fitz.Rect(30,30,350,110),'Original self-test text',16)
        e.doc.replace_text(0,fitz.Rect(29,29,351,111),'Saved replacement text',16)
        e.doc.add_text(0,fitz.Rect(30,300,350,370),'SECRET FOR REDACTION',16)
        e.doc.redact(0,fitz.Rect(29,299,351,371))
        with tempfile.TemporaryDirectory() as temp:
            temp=Path(temp)
            image=temp/'image.png'; Image.new('RGB',(40,30),'red').save(image)
            e.doc.image(0,fitz.Rect(50,150,150,225),str(image))
            info=e.doc.pdf[0].get_image_info(xrefs=True)[0]
            e.doc.move_image(0,info,fitz.Rect(220,150,320,225))
            e.doc.change(lambda d:d.new_page());e.refresh()
            QApplication.processEvents()
            check(not window.grab().isNull(),'GUI render')
            path=temp/'roundtrip.pdf';e.doc.save(str(path))
            window.open(str(path)); opened=window.current()
            check(len(opened.doc.pdf)==2,'page insertion and reopen')
            text=opened.doc.pdf[0].get_text()
            check('Saved replacement text' in text,'replacement saved')
            check('Original self-test text' not in text,'original text removed')
            check('SECRET' not in text,'redaction saved')
            check(any(abs(fitz.Rect(i['bbox']).x0-220)<.1 for i in opened.doc.pdf[0].get_image_info()),'image movement saved')
            locked=temp/'locked.pdf';opened.doc.save(str(locked),'test-password')
            encrypted=Document(str(locked),'test-password')
            check(encrypted.pdf.is_pdf,'encrypted PDF reopened'); encrypted.pdf.close()
            canvas = opened.canvas
            QApplication.processEvents()
            canvas.verticalScrollBar().setValue(canvas.verticalScrollBar().maximum())
            check(opened.page == 1, 'continuous scroll reaches second page')
            canvas.scroll_to_page(0)
            opened.choose_mode('Replace text')
            bounds = opened.doc.pdf[0].search_for('Saved replacement text')[0]
            hit = canvas.mapFromScene(canvas.pdf_rect_to_scene(0, bounds).center())
            QTest.mouseClick(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, hit)
            check(canvas.inline is not None, 'click opens inline text editor')
            field = canvas.inline
            field.setText('Inline edit saved')
            QTest.keyClick(field, Qt.Key_Return)
            check('Inline edit saved' in opened.doc.pdf[0].get_text(), 'inline edit committed')
            opened.doc.undo()
            opened.refresh()
            check('Saved replacement text' in opened.doc.pdf[0].get_text(), 'undo inline edit')
            QApplication.processEvents()
            bounds = opened.doc.pdf[0].search_for('Saved replacement text')[0]
            hit = canvas.mapFromScene(canvas.pdf_rect_to_scene(0, bounds).center())
            QTest.mouseClick(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, hit)
            field = canvas.inline
            check(field is not None, 'reopen inline editor after undo')
            from PySide6.QtWidgets import QComboBox
            picker = canvas.draft_panel.findChild(QComboBox)
            field.setText('Unsupported 😀')
            QTest.keyClick(field, Qt.Key_Return)
            check(canvas.inline is field and 'Saved replacement text' in opened.doc.pdf[0].get_text(),
                  'unsupported character preserves both draft and original text')
            picker.setCurrentText('Times')
            field.setText('Gewijzigd: Değişiklik')
            QTest.keyClick(field, Qt.Key_Return)
            check(canvas.inline is None and 'Gewijzigd: Değişiklik' in opened.doc.pdf[0].get_text(),
                  'font switch saves Unicode replacement')
            reopened = fitz.open(stream=opened.doc.snapshot(), filetype='pdf')
            with reopened:
                check('Gewijzigd: Değişiklik' in reopened[0].get_text(), 'Unicode replacement survives reopen')
            opened.doc.undo()
            opened.refresh()
            opened.doc.change(lambda pdf: pdf[0].add_ink_annot([[(70, 130), (110, 145), (140, 130)]]))
            opened.refresh()
            opened.choose_mode('Select')
            page = opened.doc.pdf[0]
            ink = page.first_annot
            hit = canvas.mapFromScene(canvas.pdf_rect_to_scene(0, ink.rect).center())
            QTest.mouseClick(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, hit)
            QTest.keyClick(canvas, Qt.Key_Delete)
            check(opened.doc.pdf[0].first_annot is None, 'click and Delete remove ink annotation')
            opened.doc.undo()
            opened.refresh()
            check(opened.doc.pdf[0].first_annot is not None, 'undo restores deleted drawing')
            embedded = fitz.Font('cjk').buffer
            def add_embedded(pdf):
                page = pdf[0]
                page.insert_font(fontname='TestEmbedded', fontbuffer=embedded)
                page.insert_text((65, 95), 'Original embedded', fontname='TestEmbedded', fontsize=13)
            opened.doc.change(add_embedded)
            opened.refresh()
            def click_pdf(point):
                rect = fitz.Rect(point, point)
                hit = canvas.mapFromScene(canvas.pdf_rect_to_scene(0, rect).center())
                QTest.mouseClick(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, hit)
            page = opened.doc.pdf[0]
            spans = [span for block in page.get_text('dict')['blocks']
                     for line in block.get('lines', []) for span in line['spans']]
            name = next(span['font'] for span in spans if span['text'] == 'Original embedded')
            opened.choose_mode('Replace text')
            click_pdf(page.search_for('Original embedded')[0].tl + (12, 5))
            check(canvas.inline is not None, 'embedded font inline editing')
            field = canvas.inline
            field.setText('Embedded updated')
            QTest.keyClick(field, Qt.Key_Return)
            page = opened.doc.pdf[0]
            spans = [span for block in page.get_text('dict')['blocks']
                     for line in block.get('lines', []) for span in line['spans']]
            check(any(span['text'] == 'Embedded updated' and span['font'] == name for span in spans),
                  'replacement keeps exact embedded font')
            edge_target, wrapped = opened.doc.fit_text_box(opened.doc.pdf[0], fitz.Point(580, 825),
                'A long text box near the page edge must wrap and stay inside the document. ' * 3,
                12, 'helv', None)
            check(edge_target in opened.doc.pdf[0].rect and '\n' in wrapped,
                  'long text box wraps and fits near a page edge')
            opened.choose_mode('Add text box')
            if report['frozen']:
                check(opened.font.findText('Arimo') >= 0, 'Arimo is available for text boxes')
                opened.font.setCurrentText('Arimo')
            click_pdf(fitz.Point(65, 170))
            check(canvas.inline is not None, 'click opens text box editor')
            box = canvas.inline
            box.setPlainText('First line\nSecond line')
            from PySide6.QtWidgets import QPushButton
            place = next(button for button in canvas.draft_panel.findChildren(QPushButton)
                         if button.text() == 'Place text box')
            check(place.isVisible(), 'native draft placement control is visible')
            QTest.mouseClick(place, Qt.LeftButton)
            QApplication.processEvents()
            check(canvas.inline is None, 'visible text box placement button commits the draft')
            opened.choose_mode('Select')
            canvas.signature_strokes = [[QPointF(0, 20), QPointF(25, 0), QPointF(90, 18)]]
            click_pdf(fitz.Point(65, 260))
            def overlays(page):
                return {item.info['subject']: (item.rect, item.info['content'])
                        for item in page.annots() if item.info['subject'].startswith('Velqora ')}
            before = overlays(opened.doc.pdf[0])
            for name in ('Velqora Text Box', 'Velqora Signature'):
                check(name in before, 'placed ' + name)
                hit = canvas.mapFromScene(canvas.pdf_rect_to_scene(0, before[name][0]).center())
                finish = hit + QPoint(45, 15)
                QTest.mousePress(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, hit)
                QTest.mouseMove(canvas.viewport(), finish)
                QTest.mouseRelease(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, finish)
                after = overlays(opened.doc.pdf[0])
                check(after[name][0].x0 > before[name][0].x0 + 20, 'dragged ' + name)
            opened.choose_mode('Select')
            def drag_word(word):
                page = opened.doc.pdf[0]
                bounds = canvas.pdf_rect_to_scene(0, page.search_for(word)[0])
                left = canvas.mapFromScene(bounds.center()) - QPoint(round(bounds.width()/2), 0)
                right = canvas.mapFromScene(bounds.center()) + QPoint(round(bounds.width()/2), 0)
                QTest.mousePress(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, left)
                QTest.mouseMove(canvas.viewport(), right)
                QTest.mouseRelease(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, right)
            for mode, subtype in [('Highlight', fitz.PDF_ANNOT_HIGHLIGHT),
                                  ('Underline', fitz.PDF_ANNOT_UNDERLINE),
                                  ('Strike through', fitz.PDF_ANNOT_STRIKE_OUT)]:
                opened.choose_mode('Select')
                drag_word('replacement')
                check(''.join(value for _, value, _ in canvas.selected_text()) == 'replacement',
                      'precise character selection for ' + mode)
                canvas.copy_selection()
                check(QApplication.clipboard().text() == 'replacement', 'copy exact selection for ' + mode)
                opened.choose_mode(mode)
                page = opened.doc.pdf[0]
                check(any(annot.type[0] == subtype for annot in page.annots()), 'saved ' + mode)
            from PySide6.QtGui import QColor
            from PySide6.QtWidgets import QColorDialog
            opened.doc.change(lambda pdf: pdf[0].insert_text((65, 310), 'Color sample', fontsize=13,
                                                              color=(1, 0, 0)))
            opened.refresh()
            opened.choose_mode('Replace text')
            page = opened.doc.pdf[0]
            click_pdf(page.search_for('Color sample')[0].tl + (6, 4))
            color_button = next(button for button in canvas.draft_panel.findChildren(QPushButton)
                                if button.text() == 'Text color')
            original_picker = QColorDialog.getColor
            try:
                QColorDialog.getColor = lambda *args: QColor('#008000')
                color_button.click()
            finally:
                QColorDialog.getColor = original_picker
            QTest.keyClick(canvas.inline, Qt.Key_Return)
            page = opened.doc.pdf[0]
            spans = [span for block in page.get_text('dict')['blocks']
                     for line in block.get('lines', []) for span in line['spans']]
            check(any(span['text'] == 'Color sample' and span['color'] == 0x008000 for span in spans),
                  'existing PDF text can be recolored without changing the words')
            opened.choose_mode('Select')
            drag_word('Color sample')
            opened.choose_mode('Strike through')
            page = opened.doc.pdf[0]
            check(any(a.type[0] == fitz.PDF_ANNOT_STRIKE_OUT and a.colors['stroke'][1] > .49
                      for a in page.annots()), 'strikeout follows the original text color')
            opened.choose_mode('Select')
            drag_word('Color sample')
            opened.highlight_color = (.3, .6, 1)
            opened.choose_mode('Highlight')
            page = opened.doc.pdf[0]
            check(any(a.type[0] == fitz.PDF_ANNOT_HIGHLIGHT and a.colors['stroke'][2] > .99
                      for a in page.annots()), 'highlight honors the selected color')
            opened.choose_mode('Draw')
            opened.brush.setCurrentIndex(1)
            opened.ink_width.setValue(9)
            opened.ink_color = (.1, .3, .8)
            start = canvas.mapFromScene(canvas.pdf_rect_to_scene(0, fitz.Rect(80, 350, 81, 351)).center())
            finish = start + QPoint(60, 20)
            QTest.mousePress(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, start)
            QTest.mouseMove(canvas.viewport(), finish)
            QTest.mouseRelease(canvas.viewport(), Qt.LeftButton, Qt.NoModifier, finish)
            page = opened.doc.pdf[0]
            check(any(a.type[0] == fitz.PDF_ANNOT_INK and a.border['width'] == 9
                      and abs(a.opacity - .45) < .01 for a in page.annots()),
                  'freehand marker saves width and opacity')
            opened.choose_mode('Select')
            finished = temp / 'placed.pdf'
            opened.doc.save(str(finished))
            with fitz.open(finished) as saved:
                if saved.needs_pass: saved.authenticate('test-password')
                check(overlays(saved[0]) == after, 'moved signature and text box survive reopening')
                if report['frozen']:
                    saved_page = saved[0]
                    item = next(a for a in saved_page.annots() if a.info['subject'] == 'Velqora Text Box')
                    image = item.get_pixmap(alpha=True)
                    check(saved.xref_get_key(item.xref, 'VelqoraFontAppearance') == ('bool', 'true')
                          and len(set(image.samples)) > 10, 'embedded text box appearance survives drag and save')
                page = saved[0]
                check({fitz.PDF_ANNOT_HIGHLIGHT, fitz.PDF_ANNOT_UNDERLINE, fitz.PDF_ANNOT_STRIKE_OUT}
                      <= {annot.type[0] for annot in page.annots()}, 'all three markup types survive reopening')
            opened.doc.dirty = False
            window.close_tab(window.tabs.currentIndex())
        from worker_engine import recognize
        sample=Document();sample.add_text(0,(30,30,450,100),'HELLO WORLD 123',28)
        for language in ['nld','eng','deu','fra','spa','tur']:
            with fitz.open(stream=recognize(sample.pdf,language),filetype='pdf') as result:
                check('123' in result[0].get_text(),'bundled OCR '+language)
        from advanced import OCRWorker
        from PySide6.QtCore import QEventLoop,QTimer
        sample.pdf.new_page().insert_text((40, 80), 'SECOND PAGE 456', fontsize=28)
        worker=OCRWorker(sample.snapshot(),'eng');loop=QEventLoop();ocr_result=[];ocr_error=[]
        worker.completed.connect(ocr_result.append);worker.failed.connect(ocr_error.append);worker.finished.connect(loop.quit)
        QTimer.singleShot(60000,loop.quit);worker.start();loop.exec()
        if worker.isRunning():worker.requestInterruption();worker.wait(5000)
        check(bool(ocr_result) and not ocr_error,'OCR bundled child process')
        recognized = Document()
        recognized.pdf.close()
        recognized.pdf = fitz.open(stream=ocr_result[0], filetype='pdf')
        window.add(recognized)
        window.copy_all_text()
        copied = QApplication.clipboard().text()
        check('123' in copied and '456' in copied and copied.index('123') < copied.index('456'),
              'OCR copy all pages in order')
        recognized_canvas = window.current().canvas
        from PySide6.QtGui import QKeySequence
        shortcut = QKeySequence(QKeySequence.SelectAll)[0]
        QTest.keyClick(recognized_canvas, shortcut.key(), shortcut.keyboardModifiers())
        selected_pages = list(recognized_canvas.selected_text())
        check(len(selected_pages) == 2 and '123' in selected_pages[0][1]
              and '456' in selected_pages[1][1] and all(quads for _, _, quads in selected_pages),
              'OCR text supports cross-page selection and markup')
        with tempfile.TemporaryDirectory() as scan_folder:
            scan_path = Path(scan_folder) / 'scan.pdf'
            with fitz.open() as scanned:
                source = sample.pdf[0]
                target = scanned.new_page(width=source.rect.width, height=source.rect.height)
                target.insert_image(target.rect, pixmap=source.get_pixmap())
                target.add_text_annot((50, 180), 'Preserve this comment')
                scanned.new_page().insert_text((40, 80), 'Native text remains')
                scanned.save(scan_path)
            setting = window.settings.value('automaticOcr', True, type=bool)
            window.settings.setValue('automaticOcr', True)
            window.open(str(scan_path))
            window.settings.setValue('automaticOcr', setting)
            opened_scan = window.current()
            loop = QEventLoop()
            poll = QTimer()
            poll.setInterval(50)
            poll.timeout.connect(lambda: loop.quit() if '123' in opened_scan.doc.pdf[0].get_text() else None)
            QTimer.singleShot(35000, loop.quit)
            poll.start()
            loop.exec()
            poll.stop()
            check(window.current() is opened_scan and '123' in opened_scan.doc.pdf[0].get_text(),
                  'automatic OCR updates the same PDF tab')
            page = opened_scan.doc.pdf[0]
            check(page.first_annot is not None and len(page.get_image_info()) == 1
                  and 'Native text remains' in opened_scan.doc.pdf[1].get_text(), 'OCR preserves existing PDF content')
            canvas = opened_scan.canvas
            for key in (QKeySequence.SelectAll, QKeySequence.Copy):
                shortcut = QKeySequence(key)[0]
                QTest.keyClick(canvas, shortcut.key(), shortcut.keyboardModifiers())
            check('123' in QApplication.clipboard().text(), 'copy automatic OCR with the native keyboard shortcut')
            from worker_engine import add_text_layer, ocr_stream
            with fitz.open(stream=opened_scan.doc.snapshot(), filetype='pdf') as copied_scan:
                check(bool(ocr_stream(copied_scan[0])), 'completed OCR status is embedded in the PDF')
                repeated = add_text_layer(copied_scan, 'eng', lambda _: None, repeat=True)
                with fitz.open(stream=repeated, filetype='pdf') as refreshed:
                    check(refreshed[0].get_text().count('123') == 1 and bool(ocr_stream(refreshed[0])),
                          'repeat OCR replaces its text layer without duplication')
            QApplication.processEvents()
            opened_scan.ocr()
            check(opened_scan.ocr_panel.run.text() == 'Run again' and
                  'Text layer available' in opened_scan.ocr_panel.status.text(),
                  'OCR panel reports the completed text layer')
            opened_scan.ocr_panel.close()
            with fitz.open(stream=opened_scan.doc.snapshot(), filetype='pdf') as scanned:
                isolated = add_text_layer(scanned, 'eng', lambda _: None, repeat=True, page_index=0)
                with fitz.open(stream=isolated, filetype='pdf') as result:
                    check('123' in result[0].get_text() and 'Native text remains' in result[1].get_text(),
                          'OCR can refresh only the selected page')
            opened_scan.start_ocr(repeat=True)
            opened_scan.cancel_ocr()
            cancel_loop = QEventLoop()
            opened_scan.worker.finished.connect(cancel_loop.quit)
            QTimer.singleShot(6000, cancel_loop.quit)
            cancel_loop.exec()
            check(not opened_scan.ocr_busy and opened_scan.ocr_message == 'Recognition cancelled.'
                  and opened_scan.doc.pdf[0].get_text().count('123') == 1,
                  'OCR cancellation retains the last valid text layer')
            opened_scan.doc.dirty = False
            window.close_tab(window.tabs.currentIndex())
        if report['frozen']:
            from font_catalog import bundled_fonts
            families = bundled_fonts()
            check(len(families) == 200, '200 offline font families')
            chosen = families.get('Inter') or next(iter(families.values()))
            example = Document()
            example.edit_line(0, None, fitz.Point(50, 80), 'Font preview', 16, 'helv',
                              (0, 0, 0), font_data=chosen.read_bytes())
            check('Font preview' in example.pdf[0].get_text(), 'offline font embeds in the PDF')
        from help_center import show_help_center
        from PySide6.QtWidgets import QLineEdit, QListWidget, QTextBrowser
        help_dialog = show_help_center(window)
        articles = help_dialog.findChild(QListWidget)
        check(articles.count() == 10, 'offline help center has ten articles')
        help_dialog.findChild(QLineEdit).setText('handwritten')
        check(articles.count() == 1 and 'OCR and scanned PDFs' in
              help_dialog.findChild(QTextBrowser).toPlainText(), 'offline help search opens the matching article')
        help_dialog.close()
        from workspace import SignaturePad
        pad=SignaturePad()
        pad.strokes=[[QPointF(10,10),QPointF(120,80)]]
        check(not pad.image().isNull(),'signature drawing')
        report['status']='passed' 
    except Exception:
        report['error']=traceback.format_exc()
    finally:
        for i in range(window.tabs.count()):window.tabs.widget(i).doc.dirty=False
        if report_path:
            target=Path(report_path);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(report,indent=2),encoding='utf-8')
        if sys.stdout:print(json.dumps(report),flush=True)
    return 0 if report['status']=='passed' else 1

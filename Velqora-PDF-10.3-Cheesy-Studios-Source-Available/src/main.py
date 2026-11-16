"""Velqora PDF — native Qt desktop editor, AGPL-3.0-or-later."""
import sys, os, json
if __name__=="__main__" and "--velqora-worker" in sys.argv:
    from worker_engine import cli
    sys.exit(cli(sys.argv[sys.argv.index("--velqora-worker")+1]))
from pathlib import Path
import fitz
from PySide6.QtCore import Qt, QRectF, QTimer, QSize, QUrl
from PySide6.QtGui import QAction, QImage, QPixmap, QColor, QPainter, QPainterPath, QPen, QKeySequence, QIcon, QDesktopServices
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,
    QFileDialog,QMessageBox,QInputDialog,QTabWidget,QSplitter,QListWidget,QListWidgetItem,
    QGraphicsView,QGraphicsScene,QMenu,QToolBar,QComboBox,QLabel,QPushButton,QAbstractItemView,
    QScrollArea,QColorDialog,QDialog,QDialogButtonBox,QFormLayout,QLineEdit,QSpinBox,QPlainTextEdit)
from PySide6.QtPrintSupport import QPrinter,QPrintDialog
from engine import Document, parse_page_ranges
from text_selection import MARKUP, PageText
from font_catalog import STANDARD, available_fonts

from bisect import bisect_right
from collections import OrderedDict

class InlineText(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancel()
        else:
            super().keyPressEvent(event)


class InlineBox(QPlainTextEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancel()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & (Qt.ControlModifier | Qt.MetaModifier):
            self.commit()
        else:
            super().keyPressEvent(event)


class Canvas(QGraphicsView):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QColor('#eceef1'))
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumWidth(350)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.rects = []
        self.tops = []
        self.cache = OrderedDict()
        self.cache_bytes = 0
        self.text_cache = OrderedDict()
        self.text_anchor = None
        self.text_selection = None
        self.start = None
        self.rubber = None
        self.inline = None
        self.draft_panel = None
        self.selected_annotation = None
        self.pending_target = None
        self.signature_strokes = None
        self.overlay_drag = None
        self.ink = None
        self.updating_layout = False
        self.verticalScrollBar().valueChanged.connect(self.sync_visible_page)

    def rebuild(self):
        old_rect = self.rects[self.editor.page] if self.editor.page < len(self.rects) else None
        old_top = self.mapToScene(self.viewport().rect().topLeft()).y()
        relative_top = (old_top - old_rect.top()) / old_rect.height() if old_rect else 0
        self.updating_layout = True
        try:
            self.cancel_inline(focus=False)
            self.ink = None
            self.scene().clear()
            self.rubber = self.start = self.selected_annotation = self.pending_target = self.overlay_drag = None
            self.text_cache.clear()
            self.text_anchor = self.text_selection = None
            self.cache.clear()
            self.cache_bytes = 0
            scale = self.editor.scale
            sizes = [(page.rect.width * scale, page.rect.height * scale) for page in self.editor.doc.pdf]
            width = max(w for w, _ in sizes)
            self.rects = []
            top = 22
            for w, h in sizes:
                self.rects.append(QRectF(44 + (width-w)/2, top, w, h))
                top += h + 18
            self.tops = [r.top() for r in self.rects]
            self.setSceneRect(0, 0, width + 88, top + 58)
            active = self.rects[self.editor.page]
            self.verticalScrollBar().setValue(round(active.top() + relative_top * active.height()))
            if old_rect is None:
                self.scroll_to_page(self.editor.page)
        finally:
            self.updating_layout = False
        self.viewport().update()

    def page_pixmap(self, index):
        if index in self.cache:
            self.cache.move_to_end(index)
            return self.cache[index][0]
        page = self.editor.doc.pdf[index]
        scale = min(self.editor.scale, (3_200_000 / page.rect.get_area()) ** .5)
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        rendered = QPixmap.fromImage(image)
        cost = pix.width * pix.height * 4
        while self.cache and self.cache_bytes + cost > 24 * 1024 * 1024:
            _, (_, removed) = self.cache.popitem(last=False)
            self.cache_bytes -= removed
        self.cache[index] = (rendered, cost)
        self.cache_bytes += cost
        return rendered

    def drawBackground(self, painter, exposed):
        super().drawBackground(painter, exposed)
        if not self.rects:
            return
        first = max(0, bisect_right(self.tops, exposed.top()) - 1)
        for index in range(first, len(self.rects)):
            bounds = self.rects[index]
            if bounds.top() > exposed.bottom():
                break
            if not bounds.intersects(exposed):
                continue
            painter.fillRect(bounds.translated(2, 3), QColor(0, 0, 0, 32))
            pixmap = self.page_pixmap(index)
            painter.drawPixmap(bounds, pixmap, QRectF(pixmap.rect()))
        for hit, (index, rect) in enumerate(self.editor.search_hits):
            if first <= index < len(self.rects) and self.rects[index].intersects(exposed):
                bounds = self.pdf_rect_to_scene(index, rect)
                painter.fillRect(bounds, QColor(255, 147, 25, 100 if hit == self.editor.search_index else 50))

        if self.text_selection:
            (first_page, first_char), (last_page, last_char) = self.text_selection
            for index in range(max(first, first_page), last_page + 1):
                if self.rects[index].top() > exposed.bottom():
                    break
                text = self.page_text(index)
                _, quads = text.extract(first_char if index == first_page else 0,
                                        last_char if index == last_page else text.count)
                for quad in quads:
                    painter.fillRect(self.pdf_rect_to_scene(index, quad.rect), QColor(43, 113, 235, 88))

    def page_text(self, index):
        if index not in self.text_cache:
            self.text_cache[index] = PageText(self.editor.doc.pdf[index])
            if len(self.text_cache) > 8:
                self.text_cache.popitem(last=False)
        self.text_cache.move_to_end(index)
        return self.text_cache[index]

    def text_position(self, scene_point):
        index = min(len(self.tops) - 1, max(0, bisect_right(self.tops, scene_point.y()) - 1))
        page = self.editor.doc.pdf[index]
        point = self.page_point(index, scene_point) * page.derotation_matrix
        return index, self.page_text(index).caret(point)

    def select_text_to(self, point):
        end = self.text_position(point)
        self.text_selection = tuple(sorted((self.text_anchor, end))) if end != self.text_anchor else None
        self.viewport().update()

    def selected_text(self, with_color=False):
        if not self.text_selection:
            return
        (first, start), (last, stop) = self.text_selection
        for index in range(first, last + 1):
            page = self.page_text(index)
            value, quads = page.extract(start if index == first else 0, stop if index == last else page.count, with_color=with_color)
            if value:
                yield index, value, quads

    def copy_selection(self):
        text = '\n'.join(text for _, text, _ in self.selected_text())
        if text:
            QApplication.clipboard().setText(text)

    def apply_markup(self, mode):
        selections = [(index, quads) for index, _, quads in self.selected_text(with_color=True) if quads]
        if selections:
            def annotate(pdf):
                for index, quads in selections:
                    page = pdf[index]
                    groups = {}
                    for quad, rgb in quads:
                        color = ((rgb >> 16 & 255)/255, (rgb >> 8 & 255)/255, (rgb & 255)/255)
                        if mode != 'Strike through':
                            color = self.editor.highlight_color if mode == 'Highlight' else (0, .35, .7)
                        groups.setdefault(color, []).append(quad)
                    for color, rectangles in groups.items():
                        item = getattr(page, MARKUP[mode])(rectangles)
                        item.set_colors(stroke=color)
                        item.update()
            self.editor.mutate(annotate)

    def start_ink(self, index, position):
        color, width, opacity = self.editor.ink_style()
        path = QPainterPath(position)
        pen = QPen(QColor.fromRgbF(*color), width * self.editor.scale)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        item = self.scene().addPath(path, pen)
        item.setOpacity(opacity)
        item.setZValue(2)
        self.ink = (index, [position], path, item, color, width, opacity)

    def extend_ink(self, position):
        index, points, path, item, *_ = self.ink
        bounds = self.rects[index]
        position.setX(min(bounds.right(), max(bounds.left(), position.x())))
        position.setY(min(bounds.bottom(), max(bounds.top(), position.y())))
        if (position - points[-1]).manhattanLength() >= 2:
            points.append(position)
            path.lineTo(position)
            item.setPath(path)

    def finish_ink(self, position):
        self.extend_ink(position)
        index, points, _, item, color, width, opacity = self.ink
        self.ink = None
        self.scene().removeItem(item)
        if len(points) < 2:
            return
        page = self.editor.doc.pdf[index]
        matrix = page.derotation_matrix
        stroke = [tuple(self.page_point(index, point) * matrix) for point in points]
        def annotate(pdf):
            target = pdf[index]
            ink = target.add_ink_annot([stroke])
            ink.set_colors(stroke=color)
            ink.set_border(width=width)
            ink.update(opacity=opacity)
        self.editor.safe(lambda: self.editor.mutate(annotate))

    def pdf_rect_to_scene(self, index, rect):
        page = self.editor.doc.pdf[index]
        rect = rect * page.rotation_matrix
        origin = self.rects[index]
        scale = self.editor.scale
        return QRectF(origin.x()+rect.x0*scale, origin.y()+rect.y0*scale,
                      rect.width*scale, rect.height*scale)

    def sync_visible_page(self):
        if self.updating_layout or not self.tops:
            return
        middle = self.mapToScene(self.viewport().rect().center()).y()
        index = max(0, bisect_right(self.tops, middle) - 1)
        self.editor.set_active_page(index)

    def scroll_to_page(self, index):
        self.updating_layout = True
        try:
            self.verticalScrollBar().setValue(round(self.rects[index].top()) - 18)
        finally:
            self.updating_layout = False
        self.editor.set_active_page(index)

    def page_at(self, point):
        index = bisect_right(self.tops, point.y()) - 1
        return index if index >= 0 and self.rects[index].contains(point) else None

    def page_point(self, index, point):
        origin = self.rects[index]
        return fitz.Point((point.x()-origin.x())/self.editor.scale,
                          (point.y()-origin.y())/self.editor.scale)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier and event.angleDelta().y():
            self.editor.zoom(1.1 if event.angleDelta().y() > 0 else 1/1.1)
            event.accept()
        else:
            super().wheelEvent(event)

    def cancel_inline(self, focus=True):
        if self.draft_panel is not None:
            panel = self.draft_panel
            self.inline = self.draft_panel = None
            panel.hide()
            self.editor.layout().removeWidget(panel)
            panel.deleteLater()
            if focus:
                self.setFocus()

    def edit_inline(self, index, point, add=False, note=False, box=False):
        self.cancel_inline()
        doc = self.editor.doc
        page = doc.pdf[index]
        point = point * page.derotation_matrix
        original_name = None
        chosen_font = None
        if add or note or box:
            size = self.editor.size.value()
            origin = fitz.Point(point.x, min(point.y + size, page.cropbox.height - 2))
            rect = None
            original = ''
            color = self.editor.color
            family = self.editor.font.currentText()
            font = STANDARD.get(family, 'helv')
            chosen_font = available_fonts().get(family)
            if (add or box) and family not in STANDARD and not chosen_font:
                self.editor.owner.statusBar().showMessage('Choose a font from the list.', 5000)
                return
        else:
            line = next((line for block in page.get_text('dict', flags=fitz.TEXTFLAGS_TEXT)['blocks']
                         for line in block.get('lines', []) if point in fitz.Rect(line['bbox'])), None)
            if not line:
                return
            spans = line['spans']
            styles = {(span['font'], span['size'], span['color']) for span in spans}
            if len(styles) > 1:
                spans = [next((span for span in spans if point in fitz.Rect(span['bbox'])), spans[0])]
            if abs(line['dir'][1]) > .01 or line['dir'][0] < 0:
                self.editor.owner.statusBar().showMessage('Editing requires horizontal left-to-right text.', 6000)
                return
            original = ''.join(span['text'] for span in spans)
            rect = fitz.Rect(spans[0]['bbox'])
            for span in spans[1:]:
                rect |= fitz.Rect(span['bbox'])
            original_name = spans[0]['font']
            origin = fitz.Point(spans[0]['origin'])
            size = spans[0]['size']
            flags = spans[0]['flags']
            family = 'ti' if flags & 4 else 'co' if flags & 8 else 'he'
            variant = ('bi' if flags & 2 and flags & 16 else 'it' if flags & 2
                       else 'bo' if flags & 16 else '')
            font = family + variant if variant else {'ti':'tiro','co':'cour','he':'helv'}[family]
            rgb = spans[0]['color']
            color = tuple(((rgb >> shift) & 255)/255 for shift in (16, 8, 0))
        panel = QWidget(self.editor)
        panel.setObjectName('draftPanel')
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)
        caption = QLabel(('New text box' if box else 'Edit text') + f' · Page {index + 1}')
        caption.setObjectName('draftCaption')
        layout.addWidget(caption)
        field = InlineBox(original, panel) if box else InlineText(original, panel)
        field.cancel = self.cancel_inline
        field.setAccessibleName('Add comment' if note else 'Edit PDF text')
        field.setPlaceholderText('Type your text')
        if box:
            field.setFixedHeight(76)
        layout.addWidget(field, 1)
        self.inline = field
        self.draft_panel = panel

        original_color = color

        def commit():
            replacement = field.toPlainText() if box else field.text()
            family = font_choice.currentText() if original_name and font_choice.currentIndex() else None
            if (replacement == original and color == original_color and not family) or (box and not replacement.strip()):
                self.cancel_inline()
                return
            try:
                if note:
                    doc.change(lambda pdf: pdf[index].add_text_annot(point, replacement))
                elif box:
                    font_data = chosen_font.read_bytes() if chosen_font else None
                    target, wrapped = doc.fit_text_box(doc.pdf[index], point, replacement, size, font, font_data)
                    doc.add_text_box(index, target, wrapped, size, color, font,
                                     self.editor.align.currentIndex(), font_data)
                else:
                    replacement_font = available_fonts().get(family) if family else chosen_font
                    doc.edit_line(index, rect, origin, replacement, size,
                                  STANDARD.get(family, 'helv') if family else font, color,
                                  None if family else original_name,
                                  replacement_font.read_bytes() if replacement_font else None)
            except (ValueError, RuntimeError, OSError) as ex:
                error.setText(str(ex))
                error.show()
                return
            self.cancel_inline()
            self.editor.refresh()

        if original_name:
            font_choice = QComboBox(panel)
            font_choice.setAccessibleName('Replacement font')
            font_choice.addItem('Original font')
            font_choice.addItems([*STANDARD, *available_fonts()])
            font_choice.setMaximumWidth(150)
            layout.addWidget(font_choice)

        if not note:
            color_button = QPushButton('Text color', panel)
            def choose_color():
                nonlocal color
                chosen = QColorDialog.getColor(QColor.fromRgbF(*color), panel, 'Text color')
                if chosen.isValid():
                    color = (chosen.redF(), chosen.greenF(), chosen.blueF())
                    field.setStyleSheet(f'color: {chosen.name()};')
                    color_button.setText(chosen.name().upper())
            color_button.clicked.connect(choose_color)
            layout.addWidget(color_button)
        cancel = QPushButton('Cancel', panel)
        cancel.clicked.connect(lambda: self.cancel_inline())
        place = QPushButton('Place text box' if box else 'Apply', panel)
        place.setObjectName('accent')
        place.clicked.connect(commit)
        layout.addWidget(cancel)
        layout.addWidget(place)
        if box:
            field.commit = commit
        else:
            field.returnPressed.connect(commit)
        error = QLabel(panel)
        error.setObjectName('draftError')
        error.setWordWrap(True)
        error.setMaximumWidth(245)
        error.hide()
        layout.insertWidget(2, error)
        self.editor.layout().addWidget(panel)
        panel.show()
        field.setFocus()
        field.selectAll()
        self.editor.owner.statusBar().showMessage(
            'Ctrl/⌘ + Enter to apply text box · Esc to cancel' if box else
            f"{original_name or 'Edit text'} · Enter to apply · Esc to cancel", 6000)

    def clear_annotation(self):
        if self.selected_annotation:
            _, _, item = self.selected_annotation
            self.scene().removeItem(item)
            self.selected_annotation = None

    def select_annotation(self, index, point):
        self.clear_annotation()
        page = self.editor.doc.pdf[index]
        point = point * page.derotation_matrix
        hits = [a for a in page.annots() or [] if point in a.rect + (-3,-3,3,3)]
        if not hits:
            return False
        annotation = min(hits, key=lambda a: a.rect.get_area())
        outline = self.scene().addRect(self.pdf_rect_to_scene(index, annotation.rect),
                                       QPen(QColor('#2467d6'), 2, Qt.DashLine))
        self.selected_annotation = (index, annotation.xref, outline)
        self.editor.owner.statusBar().showMessage('Annotation selected · Delete or Backspace to remove', 6000)
        return True

    def delete_annotation(self):
        if not self.selected_annotation:
            return
        index, xref, _ = self.selected_annotation

        def remove(pdf):
            page = pdf[index]
            annotation = page.load_annot(xref)
            if annotation:
                page.delete_annot(annotation)

        self.editor.mutate(remove)

    def keyPressEvent(self, event):
        if not self.inline and self.editor.mode == 'Select' and event.matches(QKeySequence.SelectAll):
            self.clear_annotation()
            last = len(self.rects) - 1
            self.text_selection = ((0, 0), (last, self.page_text(last).count))
            self.viewport().update()
            event.accept()
            return
        if not self.inline and self.text_selection and event.matches(QKeySequence.Copy):
            self.copy_selection()
            event.accept()
            return
        if not self.inline and event.key() in (Qt.Key_Delete, Qt.Key_Backspace) and self.selected_annotation:
            self.editor.safe(self.delete_annotation)
            event.accept()
            return
        if not self.inline and event.key() == Qt.Key_Escape:
            self.clear_annotation()
            self.text_selection = self.text_anchor = None
            self.viewport().update()
            if self.ink:
                self.scene().removeItem(self.ink[3])
                self.ink = None
            self.pending_target = self.overlay_drag = self.signature_strokes = None
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        position = self.mapToScene(event.position().toPoint())
        index = self.page_at(position)
        if index is not None and event.button() in (Qt.LeftButton, Qt.RightButton):
            if isinstance(self.inline, InlineBox) and self.inline.toPlainText().strip():
                self.editor.owner.statusBar().showMessage('Place or cancel the draft text box first.', 5000)
                event.accept()
                return
            self.cancel_inline()
            self.editor.set_active_page(index)
            self.setFocus()
            point = self.page_point(index, position)
            if event.button() == Qt.RightButton:
                if self.text_selection:
                    menu = QMenu(self)
                    menu.addAction('Copy', self.copy_selection)
                    for label in MARKUP:
                        menu.addAction(label, lambda checked=False, mode=label:
                                       self.editor.safe(lambda: self.apply_markup(mode)))
                    menu.exec(event.globalPosition().toPoint())
                    event.accept()
                    return
                if self.select_annotation(index, point):
                    menu = QMenu(self)
                    menu.addAction('Delete annotation', lambda: self.editor.safe(self.delete_annotation))
                    menu.exec(event.globalPosition().toPoint())
                event.accept()
                return
            self.text_selection = self.text_anchor = None
            self.viewport().update()
            mode = self.editor.mode
            if mode == 'Draw':
                self.start_ink(index, position)
                event.accept()
                return
            if self.signature_strokes and self.editor.mode == 'Select':
                self.editor.safe(lambda: self.place_signature(index, point))
                event.accept()
                return
            if mode in ('Replace text', 'Add text', 'Note', 'Add text box'):
                self.edit_inline(index, point, add=mode == 'Add text', note=mode == 'Note', box=mode == 'Add text box')
                event.accept()
                return
            if mode in ('Move image', 'Resize image', 'Move text'):
                self.editor.safe(lambda: self.place_selected(index, point, mode))
                event.accept()
                return
            if mode in ('Rotate image', 'Delete image', 'Replace image', 'Delete text'):
                self.editor.handle(fitz.Rect(point, point), point)
                event.accept()
                return
            if mode == 'Select' and self.select_annotation(index, point):
                page = self.editor.doc.pdf[index]
                _, xref, outline = self.selected_annotation
                annotation = page.load_annot(xref)
                if annotation.info['subject'] in ('Velqora Signature', 'Velqora Text Box'):
                    self.overlay_drag = (index, xref, position, outline)
                    self.editor.owner.statusBar().showMessage('Drag to reposition · Delete to remove', 6000)
                    event.accept()
                    return
            if mode == 'Select' or mode in MARKUP:
                self.text_anchor = self.text_position(position)
            self.start = (index, position)
        super().mousePressEvent(event)

    def place_signature(self, index, point):
        page = self.editor.doc.pdf[index]
        point = point * page.derotation_matrix
        strokes = self.signature_strokes
        all_points = [p for stroke in strokes for p in stroke]
        left, top = min(p.x() for p in all_points), min(p.y() for p in all_points)
        width = max(1, max(p.x() for p in all_points) - left)
        height = max(1, max(p.y() for p in all_points) - top)
        factor = min(170 / width, 64 / height)
        x = max(4, min(point.x, page.cropbox.width - width * factor - 4))
        y = max(4, min(point.y, page.cropbox.height - height * factor - 4))
        paths = [[(x + (p.x() - left) * factor, y + (p.y() - top) * factor) for p in stroke]
                 for stroke in strokes]
        def insert(pdf):
            target = pdf[index]
            item = target.add_ink_annot(paths)
            item.set_info(title='Velqora PDF', subject='Velqora Signature')
            item.set_colors(stroke=(.08, .13, .22))
            item.set_border(width=1.5)
            item.update()
        self.editor.mutate(insert)
        self.signature_strokes = None

    def place_selected(self, index, point, mode):
        page = self.editor.doc.pdf[index]
        unrotated = point * page.derotation_matrix
        selected = self.pending_target
        if selected and selected[:2] == (index, mode):
            self.pending_target = None
            _, _, source, bounds = selected
            self.editor.drag_end = point
            target = fitz.Rect(bounds.tl, unrotated).normalize() if mode == 'Resize image' else fitz.Rect(source, point).normalize()
            if mode == 'Resize image':
                self.editor.handle(target * page.rotation_matrix, source)
            else:
                self.editor.handle(target, source)
            return
        self.pending_target = None
        if mode == 'Move text':
            bounds = next((fitz.Rect(line['bbox']) for block in page.get_text('dict', flags=fitz.TEXTFLAGS_TEXT)['blocks']
                           for line in block.get('lines', []) if unrotated in fitz.Rect(line['bbox'])), None)
        else:
            bounds = next((fitz.Rect(image['bbox']) for image in page.get_image_info(xrefs=True)
                           if image['xref'] and unrotated in fitz.Rect(image['bbox'])), None)
        if bounds is not None:
            self.pending_target = (index, mode, point, bounds)
            hint = 'Click the new bottom-right corner' if mode == 'Resize image' else 'Click the new position'
            self.editor.owner.statusBar().showMessage(hint + ' · Esc to cancel', 6000)

    def mouseDoubleClickEvent(self, event):
        if self.inline:
            super().mouseDoubleClickEvent(event)
            return
        if event.button() == Qt.LeftButton and self.editor.mode == 'Select':
            position = self.mapToScene(event.position().toPoint())
            index = self.page_at(position)
            if index is not None:
                self.clear_drag()
                self.text_anchor = self.text_selection = None
                self.edit_inline(index, self.page_point(index, position))
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def clear_drag(self):
        self.start = None
        if self.rubber:
            self.scene().removeItem(self.rubber)
            self.rubber = None

    def mouseMoveEvent(self, event):
        if self.ink:
            self.extend_ink(self.mapToScene(event.position().toPoint()))
            return
        if self.overlay_drag:
            _, _, start, outline = self.overlay_drag
            outline.setPos(self.mapToScene(event.position().toPoint()) - start)
            return
        if self.text_anchor is not None:
            self.select_text_to(self.mapToScene(event.position().toPoint()))
            return
        if self.start:
            index, start = self.start
            end = self.mapToScene(event.position().toPoint())
            if self.rubber:
                self.scene().removeItem(self.rubber)
            area = QRectF(start, end).normalized().intersected(self.rects[index])
            self.rubber = self.scene().addRect(area, QPen(QColor('#2467d6'), 1.5), QColor(36,103,214,25))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.ink and event.button() == Qt.LeftButton:
            self.finish_ink(self.mapToScene(event.position().toPoint()))
            event.accept()
            return
        if self.overlay_drag and event.button() == Qt.LeftButton:
            index, xref, start, outline = self.overlay_drag
            self.overlay_drag = None
            end = self.mapToScene(event.position().toPoint())
            outline.setPos(0, 0)
            if (end - start).manhattanLength() >= 3:
                page = self.editor.doc.pdf[index]
                matrix = page.derotation_matrix
                delta = self.page_point(index, end) * matrix - self.page_point(index, start) * matrix
                def move():
                    self.editor.doc.move_overlay(index, xref, delta.x, delta.y)
                    self.editor.refresh()
                self.editor.safe(move)
            event.accept()
            return
        if event.button() == Qt.LeftButton and self.start:
            index, start = self.start
            end = self.mapToScene(event.position().toPoint())
            if self.text_anchor is not None:
                if (end - start).manhattanLength() >= 3:
                    self.select_text_to(end)
                self.text_anchor = None
                mode = self.editor.mode
                if self.text_selection:
                    self.clear_annotation()
                    if mode in MARKUP:
                        self.editor.safe(lambda: self.apply_markup(mode))
                    else:
                        self.editor.owner.statusBar().showMessage(
                            'Text selected · Copy or right-click for markup', 6000)
                self.clear_drag()
                if self.text_selection or mode in MARKUP or self.selected_annotation:
                    event.accept()
                    return
            bounds = self.rects[index]
            end.setX(max(bounds.left(), min(bounds.right(), end.x())))
            end.setY(max(bounds.top(), min(bounds.bottom(), end.y())))
            p0, p1 = self.page_point(index, start), self.page_point(index, end)
            self.clear_drag()
            self.editor.set_active_page(index)
            self.editor.drag_end = p1
            self.editor.handle(fitz.Rect(p0, p1).normalize(), p0)
            event.accept()
            return
        super().mouseReleaseEvent(event)

class Editor(QWidget):
    def __init__(self, owner, document):
        super().__init__()
        from workspace import init_editor
        init_editor(self,owner,document)
    def open_tool_category(self, index):
        self.tool_panel.show()
        self.category.setCurrentIndex(index)
        self.panel_title.setText(self.category.itemText(index))
        for category, button in self.mode_buttons.items():
            button.setChecked(category == index)

    def choose_mode(self, mode):
        if mode != 'Select':
            self.open_tool_category(2 if mode in ('Note', 'Draw', *MARKUP) else 0)
        if self.modes.currentText() == mode:
            self.modes.currentTextChanged.emit(mode)
        else:
            self.modes.setCurrentText(mode)

    def safe(self,fn):
        try: fn()
        except Exception as ex: QMessageBox.warning(self,'Edit failed',str(ex))
    def ink_style(self):
        return (self.ink_color, self.ink_width.value(),
                self.brush.currentData())

    def pick_color(self):
        c=QColorDialog.getColor();
        if c.isValid(): self.color=(c.redF(),c.greenF(),c.blueF())
    def refresh(self):
        self.search_hits = []
        self.search_index = -1
        self.find_status.clear()
        self.pages.blockSignals(True); self.pages.clear()
        for n in range(len(self.doc.pdf)):
            item=QListWidgetItem(f'Page {n+1}'); item.setData(Qt.UserRole,n); self.pages.addItem(item)
        self.page=min(self.page,len(self.doc.pdf)-1); self.pages.setCurrentRow(self.page); self.pages.blockSignals(False); self.render()
        self.owner.title_tab(self)
    def render(self):
        self.canvas.rebuild()
        self.update_counter()

    def update_counter(self):
        self.counter.setText(f'{self.page+1} / {len(self.doc.pdf)} · {round(self.scale*100)}%')
        self.undo_button.setEnabled(bool(self.doc.undo_stack))
        self.redo_button.setEnabled(bool(self.doc.redo_stack))
        if not self.pages.isHidden():
            self.thumbnail_timer.start(80)

    def update_thumbnails(self):
        self.pages.setIconSize(QSize(63, 86))
        if self.pages.isHidden():
            return
        for index in range(max(0, self.page-1), min(len(self.doc.pdf), self.page+2)):
            item = self.pages.item(index)
            if item.icon().isNull():
                page = self.doc.pdf[index]
                scale = min(80/page.rect.width, 110/page.rect.height)
                pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
                image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                item.setIcon(QIcon(QPixmap.fromImage(image)))

    def set_active_page(self, index):
        self.page = index
        previous = self.pages.blockSignals(True)
        self.pages.setCurrentRow(index)
        self.pages.blockSignals(previous)
        self.update_counter()

    def toggle_pages(self):
        self.pages.setVisible(self.pages.isHidden())
        if not self.pages.isHidden():
            self.update_thumbnails()

    def find(self, direction=1):
        term = self.find_input.text().strip()
        if not term:
            return
        if term != self.search_term or self.search_index < 0:
            self.search_term = term
            self.search_hits = [
                (page.number, rect)
                for page in self.doc.pdf
                for rect in page.search_for(term)
            ]
            if direction > 0:
                self.search_index = next((i for i, hit in enumerate(self.search_hits)
                                          if hit[0] >= self.page), 0)
            else:
                self.search_index = next((i for i in range(len(self.search_hits)-1, -1, -1)
                                          if self.search_hits[i][0] <= self.page),
                                         len(self.search_hits)-1)
        elif self.search_hits:
            self.search_index = (self.search_index + direction) % len(self.search_hits)
        if not self.search_hits:
            self.search_index = -1
            self.find_status.setText('No matches')
            self.render()
            return
        self.find_status.setText(f'{self.search_index + 1} of {len(self.search_hits)}')
        page_number, rect = self.search_hits[self.search_index]
        self.canvas.scroll_to_page(page_number)
        self.canvas.updating_layout = True
        try:
            self.canvas.ensureVisible(self.canvas.pdf_rect_to_scene(page_number, rect), 35, 35)
        finally:
            self.canvas.updating_layout = False
        self.canvas.viewport().update()

    def clear_find(self):
        self.search_hits = []
        self.search_index = -1
        self.find_status.clear()
        self.render()

    def close_find(self):
        self.find_bar.hide()
        self.clear_find()
        self.canvas.setFocus()

    def select_page(self,n):
        if n>=0: self.canvas.scroll_to_page(n)
    def navigate(self,delta): self.pages.setCurrentRow(max(0,min(len(self.doc.pdf)-1,self.page+delta)))
    def zoom(self,factor): self.scale=max(.25,min(2.6,self.scale*factor)); self.render()
    def reorder(self,*args):
        order=[self.pages.item(i).data(Qt.UserRole) for i in range(self.pages.count())]
        QTimer.singleShot(0,lambda:self.safe(lambda:self.mutate(lambda d:d.select(order))))
    def mutate(self,fn): self.doc.change(fn); self.refresh()
    def rotate(self): self.mutate(lambda d:d[self.page].set_rotation((d[self.page].rotation+90)%360))
    def blank(self): self.mutate(lambda d:d.new_page(pno=self.page+1))
    def duplicate(self): self.mutate(lambda d:d.fullcopy_page(self.page,to=self.page+1))
    def delete(self):
        if len(self.doc.pdf)==1: raise ValueError('A document must contain at least one page.')
        self.mutate(lambda d:d.delete_page(self.page))
    def manage_page_range(self):
        actions = {
            'Rotate clockwise': 'clockwise',
            'Rotate counterclockwise': 'counterclockwise',
            'Delete pages': 'delete',
        }
        label, accepted = QInputDialog.getItem(
            self, 'Manage page range', 'Action', list(actions), 0, False,
        )
        if not accepted:
            return
        selection, accepted = QInputDialog.getText(
            self, label, 'Page numbers and ranges, e.g. 1, 3-5',
            text=str(self.page + 1),
        )
        if not accepted:
            return
        pages = parse_page_ranges(selection, len(self.doc.pdf))
        action = actions[label]
        if action == 'delete' and QMessageBox.question(
            self, label, f'Delete {len(pages)} selected page(s)?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        ) != QMessageBox.Yes:
            return
        self.doc.edit_page_range(pages, action)
        if action == 'delete':
            self.page -= sum(index < self.page for index in pages)
        self.refresh()
        self.owner.statusBar().showMessage(f'Updated {len(pages)} page(s)', 5000)

    def merge(self):
        path,_=QFileDialog.getOpenFileName(self,'Insert PDF','','PDF (*.pdf)')
        if path:
            with fitz.open(path) as other:
                if other.needs_pass:
                    password, accepted = QInputDialog.getText(
                        self, 'Protected PDF', 'Password', QLineEdit.Password,
                    )
                    if not accepted:
                        return
                    if not other.authenticate(password):
                        raise ValueError('The password is missing or incorrect.')
                self.mutate(lambda pdf: pdf.insert_pdf(other, start_at=self.page + 1))
    def extract(self):
        selection, accepted = QInputDialog.getText(
            self, 'Extract pages', 'Page numbers and ranges, e.g. 1, 3-5',
            text=str(self.page + 1),
        )
        if not accepted:
            return
        pages = parse_page_ranges(selection, len(self.doc.pdf))
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save extracted pages', 'extracted.pdf', 'PDF (*.pdf)',
        )
        if path:
            self.doc.extract_pages(pages, path)
            self.owner.statusBar().showMessage(f'Saved {len(pages)} extracted pages', 5000)
    def bookmarks(self):
        toc=self.doc.pdf.get_toc(); choices=[f'{i+1}. {x[1]} (p. {x[2]})' for i,x in enumerate(toc)]
        if not choices: QMessageBox.information(self,'Bookmarks','This document has no bookmarks.'); return
        choice,ok=QInputDialog.getItem(self,'Bookmarks','Go to',choices,0,False)
        if ok:self.pages.setCurrentRow(toc[choices.index(choice)][2]-1)
    def properties(self):
        text=json.dumps(self.doc.pdf.metadata,ensure_ascii=False,indent=2)
        QMessageBox.information(self,'Document properties',f'{len(self.doc.pdf)} pages\n\n{text}')
    def form(self):
        widgets=list(self.doc.pdf[self.page].widgets() or [])
        if not widgets: QMessageBox.information(self,'Forms','This page has no form fields.'); return
        choices=[f'{i+1}: {w.field_name}' for i,w in enumerate(widgets)]
        choice,ok=QInputDialog.getItem(self,'Field','Choose a field',choices,0,False)
        if not ok:return
        w=widgets[choices.index(choice)]
        if w.field_type==fitz.PDF_WIDGET_TYPE_SIGNATURE: raise ValueError('Certificate signatures are unsupported.')
        if w.field_flags & fitz.PDF_FIELD_IS_READ_ONLY:
            raise ValueError('This field is read-only.')
        if w.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
            choices = ['Unchecked', 'Checked']
            value, ok = QInputDialog.getItem(
                self, 'Fill form', w.field_name, choices,
                int(w.field_value == w.on_state()), False,
            )
            value = w.on_state() if value == 'Checked' else 'Off'
        elif w.field_type in (fitz.PDF_WIDGET_TYPE_COMBOBOX, fitz.PDF_WIDGET_TYPE_LISTBOX) and w.choice_values:
            choices = list(w.choice_values)
            selected = choices.index(w.field_value) if w.field_value in choices else 0
            value, ok = QInputDialog.getItem(self, 'Fill form', w.field_name, choices, selected, False)
        elif w.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
            value, ok = QInputDialog.getMultiLineText(
                self, 'Fill form', w.field_name, str(w.field_value or ''),
            )
        else:
            raise ValueError('This form field type is unsupported.')
        if ok:
            xref = w.xref

            def update_field(pdf):
                page = pdf[self.page]
                field = page.load_widget(xref)
                field.field_value = value
                field.update()

            self.mutate(update_field)
    def metadata(self):
        title,ok=QInputDialog.getText(self,'Metadata','Title',text=self.doc.pdf.metadata.get('title',''))
        if ok:
            metadata=dict(self.doc.pdf.metadata); metadata['title']=title
            self.mutate(lambda d:d.set_metadata(metadata))
    def decorate(self):
        text,ok=QInputDialog.getText(self,'Watermark / page numbers','Text on every page ({page} inserts the page number)')
        if ok:
            def op(d):
                for n,p in enumerate(d):p.insert_text((36,p.rect.height-30),text.replace('{page}',str(n+1)),fontsize=11,color=self.color)
            self.mutate(op)
    def remove_annotations(self):
        if QMessageBox.question(self,'Annotations','Delete all annotations on this page?')==QMessageBox.Yes:
            def op(d):
                p=d[self.page]
                for a in list(p.annots() or []):p.delete_annot(a)
            self.mutate(op)
    def export_image(self):
        infos = [info for info in self.doc.pdf[self.page].get_image_info(xrefs=True) if info['xref']]
        choices=[str(i+1) for i in range(len(infos))]
        if not choices:raise ValueError('This page has no images.')
        choice,ok=QInputDialog.getItem(self,'Image','Image number (PDF order)',choices,0,False)
        if ok:
            data=self.doc.pdf.extract_image(infos[int(choice)-1]['xref'])
            path,_=QFileDialog.getSaveFileName(self,'Export image','image.'+data['ext'])
            if path:Path(path).write_bytes(data['image'])
    def signature(self):
        QMessageBox.information(self,'Drawn signature','Choose Add image and draw a box for the signature image.')
        self.modes.setCurrentText('Add image')
    def has_ocr_layer(self):
        from worker_engine import ocr_stream
        return any(ocr_stream(page) for page in self.doc.pdf)

    def ocr(self):
        from ocr_panel import OCRPanel
        if not hasattr(self, 'ocr_panel'):
            self.ocr_panel = OCRPanel(self)
        if not self.ocr_busy:
            self.ocr_completed = self.has_ocr_layer()
            if self.ocr_completed:
                self.ocr_message = 'Text layer available. Select and copy from the PDF page.'
        self.update_ocr_panel()
        self.ocr_panel.show()
        self.ocr_panel.raise_()

    def update_ocr_panel(self):
        if hasattr(self, 'ocr_panel'):
            self.ocr_panel.update_status(self.ocr_message, self.ocr_checked,
                                         getattr(self, 'ocr_total', len(self.doc.pdf)),
                                         self.ocr_busy, self.ocr_completed)
        self.ocr_button.setText('Scanning…' if self.ocr_busy else 'Scan text')
        self.ocr_button.setToolTip(self.ocr_message)

    def queue_ocr(self, delay=200):
        if not hasattr(self, 'ocr_timer'):
            self.ocr_timer = QTimer(self)
            self.ocr_timer.setSingleShot(True)
            self.ocr_timer.timeout.connect(lambda: self.start_ocr(automatic=True))
        self.ocr_timer.start(delay)

    def cancel_ocr(self):
        worker = getattr(self, 'worker', None)
        if worker and worker.isRunning():
            self.ocr_cancelled = True
            self.ocr_message = 'Cancelling recognition…'
            worker.requestInterruption()
            self.update_ocr_panel()

    def start_ocr(self, language='eng+nld', automatic=False, repeat=False, page_index=None):
        from advanced import OCRWorker
        if self.owner.tabs.indexOf(self) < 0:
            return
        if self.ocr_busy:
            return
        if automatic and self.canvas.inline:
            self.queue_ocr(1000)
            return
        if any(self.owner.tabs.widget(i).ocr_busy for i in range(self.owner.tabs.count())):
            if automatic:
                self.queue_ocr(1000)
            else:
                self.ocr_message = 'Another PDF is being recognized. Try again when it finishes.'
                self.update_ocr_panel()
            return
        if hasattr(self, 'ocr_timer'):
            self.ocr_timer.stop()
        source = self.doc.pdf
        worker = OCRWorker(self.doc.snapshot(), language, preserve_pages=True, repeat=repeat, page_index=page_index)
        self.worker = worker
        self.ocr_busy = True
        self.ocr_checked = 0
        self.ocr_total = len(self.doc.pdf) if page_index is None else 1
        self.ocr_cancelled = False

        def status(message):
            self.ocr_message = message
            self.update_ocr_panel()
            if self.owner.current() is self:
                self.owner.statusBar().showMessage(message, 7000)

        def completed(data):
            if self.owner.tabs.indexOf(self) < 0 or self.ocr_cancelled:
                return
            if self.canvas.inline:
                if automatic:
                    self.queue_ocr(1200)
                status('Recognition postponed while a text edit is open.')
                return
            if self.doc.pdf is not source:
                status('The PDF changed during OCR. Run recognition again to include the latest changes.')
                return
            if not data:
                self.ocr_completed = self.has_ocr_layer()
                status('No additional text was recognized.' if self.ocr_completed else
                       'No new text found. Digital text can be selected directly. For scans, try the document language.')
                return
            before = self.doc.snapshot()
            result = fitz.open(stream=data, filetype='pdf')
            source.close()
            self.doc.pdf = result
            self.doc.record_change(before)
            self.ocr_completed = True
            self.refresh()
            status('Text layer ready. Select text on the page and save the PDF to keep it.')

        def progress(number):
            self.ocr_checked = number
            if not self.ocr_cancelled:
                status(f'Checking pages · {number} of {self.ocr_total}')

        def ended():
            if self.owner.tabs.indexOf(self) < 0:
                return
            self.ocr_busy = False
            if self.ocr_cancelled:
                status('Recognition cancelled.')
            self.update_ocr_panel()

        worker.progress.connect(progress)
        worker.failed.connect(lambda error: status('OCR failed. ' + error))
        worker.completed.connect(completed)
        worker.finished.connect(ended)
        status('Checking PDF for scanned pages…')
        worker.start()

    def handle(self,rect,start): self.safe(lambda:self.apply_tool(rect,start))
    def apply_tool(self,rect,start):
        p=self.doc.pdf[self.page]
        # Convert displayed coordinates back to unrotated PDF coordinates.
        rect=rect*p.derotation_matrix; start=start*p.derotation_matrix
        if self.mode=='Select':
            if rect.width<4 and rect.height<4:
                link=next((link for link in p.get_links() if start in fitz.Rect(link['from'])),None)
                if link and link.get('uri'):
                    uri=link['uri']
                    if QUrl(uri).scheme() in ('http','https','mailto') and QMessageBox.question(self,'Open external link',uri)==QMessageBox.Yes:QDesktopServices.openUrl(QUrl(uri))
                elif link and link.get('page',-1)>=0:self.pages.setCurrentRow(link['page'])
            else:QApplication.clipboard().setText(p.get_textbox(rect))
            self.canvas.viewport().update(); return
        if self.mode in ('Add text','Replace text','Delete text','Move text'):
            if self.mode == 'Delete text' and rect.is_empty:
                rect = next((fitz.Rect(line['bbox']) for block in p.get_text('dict', flags=fitz.TEXTFLAGS_TEXT)['blocks']
                             for line in block.get('lines', []) if start in fitz.Rect(line['bbox'])), None)
                if rect is None:
                    return
            if self.mode != 'Move text' and (rect.width<5 or rect.height<5):
                raise ValueError('Select a text line or area.')
            old=p.get_textbox(rect) if self.mode!='Add text' else ''
            if self.mode=='Move text':
                line=next((fitz.Rect(line['bbox']) for block in p.get_text('dict')['blocks'] if 'lines' in block for line in block['lines'] if start in fitz.Rect(line['bbox'])),None)
                if line is None:raise ValueError('Drag from inside a line of text to move it.')
                text=p.get_textbox(line);delta=(self.drag_end*p.derotation_matrix)-start
                target=line+(delta.x,delta.y,delta.x,delta.y+12)
                self.doc.relocate_text(self.page,line,target,text,self.size.value(),self.color)
                self.refresh();return
            if self.mode=='Delete text':
                self.doc.replace_text(self.page,rect,'');self.refresh();return
            text,ok=QInputDialog.getMultiLineText(self,'Text','Enter the text',old)
            if ok:
                fn=self.doc.replace_text if self.mode=='Replace text' else self.doc.add_text
                fn(self.page,rect,text,self.size.value(),self.color,STANDARD.get(self.font.currentText(), 'helv'),self.align.currentIndex())
        elif self.mode=='Add image':
            path,_=QFileDialog.getOpenFileName(self,'Image','','Images (*.png *.jpg *.jpeg)')
            if path:self.doc.image(self.page,rect,path)
        elif self.mode.endswith(' image'):
            found=next((i for i in p.get_image_info(xrefs=True) if start in fitz.Rect(i['bbox']) and i['xref']),None)
            if not found: raise ValueError('Start the selection inside an image.')
            old=fitz.Rect(found['bbox'])
            if self.mode=='Delete image':
                self.doc.edit_image(self.page,found,remove=True); self.refresh(); return
            if self.mode=='Rotate image':
                self.doc.edit_image(self.page,found,angle=90); self.refresh(); return
            if self.mode=='Replace image':
                path,_=QFileDialog.getOpenFileName(self,'Replace image','','Images (*.png *.jpg *.jpeg)')
                if path:self.doc.edit_image(self.page,found,path=path)
                self.refresh(); return
            if self.mode=='Move image':
                delta=(self.drag_end*p.derotation_matrix)-start; target=old+ (delta.x,delta.y,delta.x,delta.y)
            else: target=rect
            self.doc.move_image(self.page,found,target)
        elif self.mode=='Redact':
            if QMessageBox.question(self,'Permanent redaction','Permanently remove content inside this area?')==QMessageBox.Yes:self.doc.redact(self.page,rect)
        elif self.mode=='Crop': self.doc.change(lambda d:d[self.page].set_cropbox(rect))
        elif self.mode=='Note':
            text,ok=QInputDialog.getMultiLineText(self,'Note','Comment')
            if ok:self.doc.change(lambda d:d[self.page].add_text_annot(start,text))
        else:
            def op(d):
                page=d[self.page]
                methods={'Highlight':page.add_highlight_annot,'Underline':page.add_underline_annot,'Strike through':page.add_strikeout_annot,'Rectangle':page.add_rect_annot,'Circle':page.add_circle_annot}
                if self.mode=='Arrow':
                    a=page.add_line_annot(rect.tl,rect.br); a.set_line_ends(0,4); a.update()
                else: methods[self.mode](rect)
            self.doc.change(op)
        self.refresh()

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        from workspace import init_window
        init_window(self)
    def safe(self,fn):
        try:fn()
        except Exception as ex:QMessageBox.warning(self,'Error',str(ex))
    def offer_default_pdf_app(self):
        from macos_defaults import app_bundle, pdf_handler

        key = 'defaultPdfPromptShown'
        bundle = app_bundle()
        if bundle is None or bundle.is_relative_to('/Volumes') or self.settings.value(key, False, type=bool):
            return
        self.settings.setValue(key, True)
        try:
            if pdf_handler():
                return
        except (OSError, RuntimeError, AttributeError):
            pass
        self.ask_default_pdf_app()

    def ask_default_pdf_app(self):
        from macos_defaults import app_bundle, pdf_handler

        bundle = app_bundle()
        if bundle is None:
            return
        if bundle.is_relative_to('/Volumes'):
            QMessageBox.information(
                self, 'Default PDF app',
                'Copy Velqora PDF to Applications and open that copy to set it as the default.',
            )
            return
        dialog = QMessageBox(self)
        dialog.setWindowTitle('Default PDF app')
        dialog.setText('Open PDFs with Velqora PDF by default?')
        set_default = dialog.addButton('Set as Default', QMessageBox.AcceptRole)
        later = dialog.addButton('Not Now', QMessageBox.RejectRole)
        dialog.setDefaultButton(later)
        dialog.exec()
        if dialog.clickedButton() != set_default:
            return
        try:
            if pdf_handler(make_default=True):
                self.statusBar().showMessage('Velqora PDF is now the default PDF app.', 8000)
                return
        except (OSError, RuntimeError, AttributeError):
            pass
        QMessageBox.information(
            self, 'Default PDF app',
            'In Finder, select a PDF and choose File → Get Info. Under Open with, '
            'select Velqora PDF and click Change All.',
        )

    def copy_all_text(self):
        text = self.current().doc.document_text()
        if not text:
            self.statusBar().showMessage('No text found. Run Offline OCR for scanned PDFs.', 7000)
            return
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage('All document text copied.', 5000)

    def show_document_text(self):
        from PySide6.QtWidgets import QPlainTextEdit

        text = self.current().doc.document_text()
        if not text:
            QMessageBox.information(self, 'Document text', 'No text found. Run Offline OCR for scanned PDFs.')
            return
        dialog = QDialog(self)
        dialog.setWindowTitle('Document text')
        dialog.resize(700, 520)
        layout = QVBoxLayout(dialog)
        preview = QPlainTextEdit(text, dialog)
        preview.setReadOnly(True)
        layout.addWidget(preview)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        copy = buttons.addButton('Copy All Text', QDialogButtonBox.ActionRole)

        def copy_preview():
            QApplication.clipboard().setText(text)
            self.statusBar().showMessage('All document text copied.', 5000)

        copy.clicked.connect(copy_preview)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def current(self):
        if not self.tabs.count():self.new()
        return self.tabs.currentWidget()
    def title_tab(self,e):
        i=self.tabs.indexOf(e)
        if i>=0:self.tabs.setTabText(i,('* ' if e.doc.dirty else '')+ (Path(e.doc.path).name if e.doc.path else 'New document'))
    def new(self):self.add(Document())
    def add(self,doc):
        e=Editor(self,doc); self.tabs.addTab(e,''); self.tabs.setCurrentWidget(e); self.title_tab(e); self.stack.setCurrentIndex(1)
        return e
    def open(self,path=None):
        if not path:path,_=QFileDialog.getOpenFileName(self,'Open PDF','','PDF (*.pdf)')
        if not path:return
        try:doc=Document(path)
        except ValueError:
            pw,ok=QInputDialog.getText(self,'Protected PDF','Password',QLineEdit.Password)
            if not ok:return
            doc=Document(path,pw)
        editor = self.add(doc)
        if self.settings.value('automaticOcr', True, type=bool):
            editor.queue_ocr()
        from workspace import remember
        remember(self,path)
    def from_images(self):
        paths,_=QFileDialog.getOpenFileNames(self,'Images to PDF','','Images (*.png *.jpg *.jpeg)')
        if not paths:return
        doc=Document()
        for i,path in enumerate(paths):
            image=fitz.open(path)
            converted=fitz.open(stream=image.convert_to_pdf(),filetype='pdf')
            if i==0:doc.pdf.delete_page(0)
            doc.pdf.insert_pdf(converted); converted.close(); image.close()
        doc.dirty=True; self.add(doc)
    def save(self,as_new=False,password=None):
        e=self.current(); path=e.doc.path
        if as_new or not path:path,_=QFileDialog.getSaveFileName(self,'Save PDF',path or 'document.pdf','PDF (*.pdf)')
        if path:
            e.doc.save(path,password); self.title_tab(e)
            from workspace import remember
            remember(self,path)
            return True
        return False
    def encrypt(self):
        pw,ok=QInputDialog.getText(self,'Encrypt','New password',QLineEdit.Password)
        if ok and pw:self.save(True,pw)
    def history(self,redo):e=self.current(); e.doc.undo(redo); e.refresh()
    def search(self):
        editor = self.current()
        self.stack.setCurrentIndex(1)
        editor.find_bar.show()
        editor.find_input.setFocus()
        editor.find_input.selectAll()

    def find_again(self, direction):
        editor = self.current()
        self.stack.setCurrentIndex(1)
        editor.find_bar.show()
        if editor.find_input.text().strip():
            editor.find(direction)
        else:
            editor.find_input.setFocus()
    def export(self):
        fmt,ok=QInputDialog.getItem(self,'Export','Format',['TXT','HTML','DOCX (text)','PNG (current page)','Annotations JSON'],0,False)
        if not ok:return
        extensions = {'TXT': 'txt', 'HTML': 'html', 'DOCX (text)': 'docx',
                      'PNG (current page)': 'png', 'Annotations JSON': 'json'}
        suffix = extensions[fmt]
        path, _ = QFileDialog.getSaveFileName(
            self, 'Export', f'document.{suffix}', f'{suffix.upper()} (*.{suffix})',
        )
        if not path:return
        e=self.current()
        if fmt=='DOCX (text)':
            from conversions import export_docx
            export_docx(e.doc.pdf,path);return
        if fmt.startswith('PNG'):e.doc.pdf[e.page].get_pixmap(matrix=fitz.Matrix(2,2)).save(path)
        else:
            if fmt=='Annotations JSON':data=json.dumps([{'page':n+1,'type':a.type,'info':a.info,'rect':list(a.rect)} for n,p in enumerate(e.doc.pdf) for a in p.annots() or []],ensure_ascii=False,indent=2)
            else:data='\n'.join(p.get_text('html' if fmt=='HTML' else 'text') for p in e.doc.pdf)
            Path(path).write_text(data,encoding='utf-8')
    def print_pdf(self):
        printer=QPrinter(QPrinter.HighResolution)
        if QPrintDialog(printer,self).exec()!=QDialog.Accepted:return
        painter=QPainter(printer)
        try:
            for n,p in enumerate(self.current().doc.pdf):
                if n:printer.newPage()
                pix=p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
                img=QImage(pix.samples,pix.width,pix.height,pix.stride,QImage.Format_RGB888).copy()
                target=printer.pageRect(QPrinter.DevicePixel); scaled=QSize(pix.width,pix.height).scaled(target.size().toSize(),Qt.KeepAspectRatio)
                painter.drawImage(QRectF(target.x(),target.y(),scaled.width(),scaled.height()),img)
        finally:painter.end()
    def theme(self):
        from workspace import apply_theme
        self.dark=not self.dark;apply_theme(self)
    def fullscreen(self): self.showNormal() if self.isFullScreen() else self.showFullScreen()
    def close_tab(self,i):
        e=self.tabs.widget(i)
        if e.doc.dirty:
            answer=QMessageBox.question(self,'Unsaved changes','Save changes?',QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel)
            if answer==QMessageBox.Cancel:return False
            if answer==QMessageBox.Save:
                self.tabs.setCurrentIndex(i)
                if not self.save():return False
        if getattr(e, 'worker', None) and e.worker.isRunning():
            e.cancel_ocr()
            if not e.worker.wait(1600):
                self.statusBar().showMessage('OCR is stopping. Close the tab again in a moment.', 5000)
                return False
        if hasattr(e, 'ocr_timer'):
            e.ocr_timer.stop()
        self.tabs.removeTab(i); e.doc.pdf.close(); e.deleteLater()
        if not self.tabs.count():self.stack.setCurrentIndex(0)
        return True
    def closeEvent(self,event):
        for i in reversed(range(self.tabs.count())):
            if not self.close_tab(i):event.ignore();return
        event.accept()
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls():event.acceptProposedAction()
    def dropEvent(self,event):
        for u in event.mimeData().urls():self.safe(lambda:self.open(u.toLocalFile()))

class App(QApplication):
    def event(self,event):
        from PySide6.QtCore import QEvent
        if event.type()==QEvent.FileOpen:
            path = event.file()
            if path:
                if hasattr(self, 'window'):
                    self.window.safe(lambda: self.window.open(path))
                else:
                    pending = getattr(self, 'pending_files', [])
                    pending.append(path)
                    self.pending_files = pending
            return True
        return super().event(event)

def main():
    from PySide6.QtCore import QLocale
    QLocale.setDefault(QLocale(QLocale.English))
    app=App(sys.argv); app.setApplicationName('Velqora PDF'); app.setApplicationVersion('10.3.0'); app.setStyle('Fusion')
    window=Window(); app.window=window; window.show()
    if '--self-test' in sys.argv:
        from selftest import run
        report_path=None
        if '--report' in sys.argv:
            report_path=sys.argv[sys.argv.index('--report')+1]
        # Run after the platform event loop starts, including cocoa on macOS CI.
        QTimer.singleShot(0,lambda:app.exit(run(window,report_path)))
        return app.exec()
    paths = dict.fromkeys([*getattr(app, 'pending_files', []), *sys.argv[1:]])
    for path in paths:
        if path.lower().endswith('.pdf'):
            window.safe(lambda p=path: window.open(p))
    from workspace import show_tour
    def welcome():
        if not window.settings.value('tourSeen', False, type=bool):
            show_tour(window)
        window.offer_default_pdf_app()
    QTimer.singleShot(0, welcome)
    return app.exec()
if __name__=='__main__':sys.exit(main())

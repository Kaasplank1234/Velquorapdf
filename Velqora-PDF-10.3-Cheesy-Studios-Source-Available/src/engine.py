"""Offline PDF operations. AGPL-3.0-or-later."""
import os
from pathlib import Path
import shutil
import tempfile
import fitz

class Document:
    def __init__(self, path=None, password=None):
        self.pdf = fitz.open(path) if path else fitz.open()
        if self.pdf.needs_pass and not self.pdf.authenticate(password or ''):
            self.pdf.close()
            raise ValueError('The password is missing or incorrect.')
        if not path:
            self.pdf.new_page()
        self.password=password
        self.path = path
        self.undo_stack, self.redo_stack = [], []
        self.dirty = False

    def document_text(self):
        pages = (page.get_text('text', sort=True).strip() for page in self.pdf)
        return '\n\n'.join(text for text in pages if text)

    def snapshot(self):
        return self.pdf.tobytes(garbage=0)

    def change(self, operation):
        before = self.snapshot()
        try:
            operation(self.pdf)
            # Reopen after edits to invalidate MuPDF page/annotation caches.
            updated=self.pdf.tobytes(garbage=1)
            self.pdf.close()
            self.pdf=fitz.open(stream=updated,filetype="pdf")
        except Exception:
            self.pdf.close()
            self.pdf = fitz.open(stream=before, filetype='pdf')
            raise
        self.record_change(before)

    def record_change(self, before):
        # Bound undo by both count and byte size for low-memory machines.
        self.undo_stack.append(before)
        while len(self.undo_stack)>10 or sum(map(len,self.undo_stack))>48*1024*1024:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.dirty = True

    def undo(self, redo=False):
        source, target = (self.redo_stack,self.undo_stack) if redo else (self.undo_stack,self.redo_stack)
        if source:
            target.append(self.snapshot())
            self.pdf.close()
            self.pdf = fitz.open(stream=source.pop(), filetype='pdf')
            self.dirty=True

    def save(self, path, password=None):
        password = password or self.password
        # Windows can lock the source until MuPDF closes its file handle.
        source = self.pdf.name
        if os.name == 'nt' and source and os.path.normcase(os.path.realpath(source)) == os.path.normcase(os.path.realpath(path)):
            detached = fitz.open(stream=self.snapshot(), filetype='pdf')
            self.pdf.close()
            self.pdf = detached
        self.write_pdf(self.pdf, path, password)
        self.password = password
        self.path = path
        self.dirty = False

    @staticmethod
    def write_pdf(pdf, path, password=None):
        options = dict(garbage=4, deflate=True)
        if password:
            options.update(encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw=password, user_pw=password)
        fd, tmp = tempfile.mkstemp(suffix='.pdf',dir=os.path.dirname(os.path.abspath(path)))
        os.close(fd)
        try:
            pdf.save(tmp, **options)
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    def add_text(self, page, rect, text, size=12, color=(0,0,0), font='helv', align=0):
        def op(pdf):
            if pdf[page].insert_textbox(fitz.Rect(rect),text,fontsize=size,fontname=font,color=color,align=align)<0:
                raise ValueError('The text does not fit. Enlarge the box or use a smaller font.')
        self.change(op)

    def replace_text(self, page, rect, text, size=12, color=(0,0,0), font='helv', align=0):
        # Actually remove old characters; keep overlapping images and line art.
        def op(pdf):
            p=pdf[page]
            p.add_redact_annot(rect,fill=False)
            p.apply_redactions(images=0,graphics=0)
            if text and p.insert_textbox(rect,text,fontsize=size,fontname=font,color=color,align=align)<0:
                raise ValueError('The replacement text does not fit. The original text was restored.')
        self.change(op)

    @staticmethod
    def original_font(page, name):
        def normalize(value):
            return ''.join(ch for ch in value.split('+')[-1].lower() if ch.isalnum())

        for xref, _, _, base, _, *_ in page.get_fonts(full=True):
            if normalize(base) == normalize(name):
                data = page.parent.extract_font(xref)[3]
                if data:
                    return data
        return None

    def edit_line(self, index, original, origin, text, size, font, color, original_name=None, font_data=None):
        page = self.pdf[index]
        embedded = self.original_font(page, original_name) if original_name and text else font_data
        if text and original_name and not embedded:
            base_name = fitz.Font(font).name
            if original_name.replace(' ', '').lower() != base_name.replace(' ', '').lower():
                raise ValueError(f'The font {original_name} is unavailable. Choose another font and apply again.')
        face = (fitz.Font(fontbuffer=embedded) if embedded else fitz.Font(font)) if text else None
        if face and any(not face.has_glyph(ord(char), fallback=False) for char in set(text)):
            raise ValueError('This font is missing a character. Choose another font and apply again.')
        if face and not embedded:
            try:
                text.encode('cp1252')
            except UnicodeEncodeError:
                embedded = face.buffer
        if face and face.text_length(text, fontsize=size) > page.cropbox.width - origin.x:
            raise ValueError('Text is too long for this line. Shorten it and press Enter.')

        def change(pdf):
            page = pdf[index]
            if original is not None:
                page.add_redact_annot(original, fill=False)
                page.apply_redactions(images=0, graphics=0)
            if text:
                if embedded:
                    from hashlib import sha256
                    font_name = 'VQ' + sha256(embedded).hexdigest()[:16]
                    page.insert_font(fontname=font_name, fontbuffer=embedded)
                else:
                    font_name = font
                if page.insert_text(origin, text, fontsize=size, fontname=font_name, color=color) < 1:
                    raise ValueError('Text does not fit at this position.')

        self.change(change)

    @staticmethod
    def fit_text_box(page, point, text, size, font, font_data):
        bounds = page.rect * page.derotation_matrix
        width = min(320, bounds.width - 12)
        face = fitz.Font(fontbuffer=font_data) if font_data else fitz.Font(font)
        if width <= size:
            raise ValueError('The page is too narrow for this font size.')
        lines = []
        for paragraph in text.split('\n'):
            remaining = paragraph.rstrip()
            while face.text_length(remaining, fontsize=size) > width - 12:
                lengths = face.char_lengths(remaining, fontsize=size)
                consumed = 0
                for count, advance in enumerate(lengths):
                    consumed += advance
                    if consumed > width - 12:
                        break
                cut = max(1, count)
                space = remaining.rfind(' ', 0, cut + 1)
                cut = space if space > 0 else cut
                lines.append(remaining[:cut].rstrip())
                remaining = remaining[cut:].lstrip()
            lines.append(remaining)
        height = max(44, size * (len(lines) + 1) * 1.45 + 8)
        if height > bounds.height - 12:
            raise ValueError('This text exceeds the page height. Reduce the font size or use multiple boxes.')
        x = min(max(point.x, bounds.x0 + 6), bounds.x1 - width - 6)
        y = min(max(point.y, bounds.y0 + 6), bounds.y1 - height - 6)
        return fitz.Rect(x, y, x + width, y + height), '\n'.join(lines)

    def add_text_box(self, index, target, text, size, color, font, align, font_data=None):
        def insert(pdf):
            page = pdf[index]
            if not font_data:
                if any(fitz.get_text_length(line, fontname=font, fontsize=size) > target.width - 6
                       for line in text.splitlines()):
                    raise ValueError('Add a line break so the text fits inside the box.')
                item = page.add_freetext_annot(target, text, fontsize=size, fontname=font,
                                               text_color=color, align=min(align, 2))
                item.set_info(title='Velqora PDF', subject='Velqora Text Box')
                item.update()
                return
            face = fitz.Font(fontbuffer=font_data)
            if any(not face.has_glyph(ord(char), fallback=False) for char in set(text) - {'\n'}):
                raise ValueError('The selected font does not contain one or more characters.')
            with fitz.open() as appearance:
                drawing = appearance.new_page(width=target.width, height=target.height)
                drawing.insert_font(fontname='VelqoraBox', fontbuffer=font_data)
                inset = drawing.rect + (3, 2, -3, -2)
                if drawing.insert_textbox(inset, text, fontname='VelqoraBox', fontsize=size,
                                          color=color, align=align) < 0:
                    raise ValueError('The text does not fit. Try a smaller size or move the box away from the page edge.')
                # Import a reusable vector Form, then remove its temporary host page.
                host = pdf.new_page(width=target.width, height=target.height)
                form = host.show_pdf_page(host.rect, appearance, 0)
                pdf.delete_page(-1)
            page = pdf[index]
            item = page.add_freetext_annot(target, text, fontsize=size, text_color=color)
            item.set_info(title='Velqora PDF', subject='Velqora Text Box')
            item.update()
            pdf.xref_set_key(item.xref, 'AP', f'<< /N {form} 0 R >>')
            pdf.xref_set_key(item.xref, 'VelqoraFontAppearance', 'true')

        self.change(insert)

    def move_overlay(self, index, xref, dx, dy):
        def move(pdf):
            page = pdf[index]
            item = page.load_annot(xref)
            old = item.rect
            bounds = page.rect * page.derotation_matrix
            dx_clamped = min(max(dx, bounds.x0 - old.x0), bounds.x1 - old.x1)
            dy_clamped = min(max(dy, bounds.y0 - old.y0), bounds.y1 - old.y1)
            if item.info['subject'] == 'Velqora Signature':
                strokes = [[(x + dx_clamped, y + dy_clamped) for x, y in stroke]
                           for stroke in item.vertices]
                updated = page.add_ink_annot(strokes)
                updated.set_info(title='Velqora PDF', subject='Velqora Signature')
                updated.set_colors(stroke=(.08, .13, .22))
                updated.set_border(width=1.5)
                updated.update()
                page.delete_annot(item)
            else:
                item.set_rect(old + (dx_clamped, dy_clamped, dx_clamped, dy_clamped))
                if pdf.xref_get_key(item.xref, 'VelqoraFontAppearance') != ('bool', 'true'):
                    item.update()

        self.change(move)

    def image(self,page,rect,path):
        self.change(lambda pdf: pdf[page].insert_image(rect,filename=path))

    def move_image(self,page,info,rect):
        def op(pdf):
            p=pdf[page]
            # Removing an xref affects all its occurrences: refuse ambiguous cases.
            if sum(len(pg.get_image_rects(info['xref'])) for pg in pdf)!=1:
                raise ValueError('This image appears more than once. Moving it would affect other copies.')
            data=self.image_bytes(pdf,info['xref'])
            p.delete_image(info['xref'])
            p.insert_image(rect,stream=data)
        self.change(op)

    def redact(self,page,rect):
        def op(pdf):
            p=pdf[page]; p.add_redact_annot(rect,fill=(0,0,0)); p.apply_redactions(images=2,graphics=1)
        self.change(op)

    def edit_image(self,page,info,path=None,remove=False,angle=0):
        def op(pdf):
            p=pdf[page]; xref=info['xref']
            if sum(len(pg.get_image_rects(xref)) for pg in pdf)!=1:
                raise ValueError('This image appears more than once. Editing it would affect other copies.')
            if remove:p.delete_image(xref)
            elif path:p.replace_image(xref,filename=path)
            else:
                from PIL import Image
                import io
                original=self.image_bytes(pdf,xref)
                image=Image.open(io.BytesIO(original)).rotate(angle,expand=True)
                data=io.BytesIO(); image.save(data,format='PNG')
                p.replace_image(xref,stream=data.getvalue())
        self.change(op)

    @staticmethod
    def image_bytes(pdf,xref):
        data=pdf.extract_image(xref)
        if data.get('smask'):
            pix=fitz.Pixmap(fitz.Pixmap(pdf,xref),fitz.Pixmap(pdf,data['smask']))
            return pix.tobytes('png')
        return data['image']

    def relocate_text(self,page,old,target,text,size=12,color=(0,0,0)):
        def op(pdf):
            p=pdf[page];p.add_redact_annot(old,fill=False);p.apply_redactions(images=0,graphics=0)
            if p.insert_textbox(target,text,fontsize=size,color=color)<0:raise ValueError('The text does not fit in the destination box.')
        self.change(op)

    def extract_pages(self, pages, path):
        """Export selected pages in the supplied order and retain source encryption."""
        if self.path and os.path.realpath(self.path) == os.path.realpath(path):
            raise ValueError('Choose a different file to avoid replacing the source PDF.')
        with fitz.open() as output:
            for page in pages:
                output.insert_pdf(self.pdf, from_page=page, to_page=page)
            self.write_pdf(output, path, self.password)

    def edit_page_range(self, pages, action):
        selected = set(pages)
        if not selected or any(page < 0 or page >= len(self.pdf) for page in selected):
            raise ValueError('Select at least one valid page.')
        if action == 'delete':
            remaining = [page for page in range(len(self.pdf)) if page not in selected]
            if not remaining:
                raise ValueError('A document must contain at least one page.')
            self.change(lambda pdf: pdf.select(remaining))
            return
        if action not in ('clockwise', 'counterclockwise'):
            raise ValueError('Unknown page action.')
        degrees = 90 if action == 'clockwise' else -90

        def rotate(pdf):
            for index in selected:
                page = pdf[index]
                page.set_rotation((page.rotation + degrees) % 360)

        self.change(rotate)

    def split(self, folder, pages_per_file):
        """Write protected parts when the source is protected."""
        if pages_per_file < 1:
            raise ValueError('Choose at least one page per file.')
        folder = Path(folder)
        stem = Path(self.path).stem if self.path else 'document'
        ranges = [
            (start, min(start + pages_per_file, len(self.pdf)))
            for start in range(0, len(self.pdf), pages_per_file)
        ]
        destinations = [folder / f'{stem}-pages-{start + 1}-{end}.pdf' for start, end in ranges]
        if any(os.path.lexists(path) for path in destinations):
            raise ValueError('Output files already exist. Choose another folder.')

        created = []
        with tempfile.TemporaryDirectory(dir=folder) as staging:
            try:
                for (start, end), path in zip(ranges, destinations):
                    staged = Path(staging) / path.name
                    with fitz.open() as part:
                        part.insert_pdf(self.pdf, from_page=start, to_page=end - 1)
                        self.write_pdf(part, staged, self.password)
                    # Exclusive creation prevents overwriting files added during export.
                    with staged.open('rb') as source, open(
                        path, 'xb', opener=lambda name, flags: os.open(name, flags, 0o600),
                    ) as target:
                        created.append(path)
                        shutil.copyfileobj(source, target)
                    staged.unlink()
            except Exception:
                for path in created:
                    path.unlink(missing_ok=True)
                raise
        return destinations


def parse_page_ranges(selection, page_count):
    """Convert comma-separated, one-based page ranges to ordered page indices."""
    import re

    pages = {}
    for part in selection.split(','):
        match = re.fullmatch(r'\s*([0-9]+)(?:\s*-\s*([0-9]+))?\s*', part)
        if not match:
            raise ValueError('Enter page numbers or ranges, for example 1, 3-5.')
        first = int(match[1])
        last = int(match[2] or first)
        if not 1 <= first <= last <= page_count:
            raise ValueError(f'Use ascending page ranges between 1 and {page_count}.')
        for page in range(first - 1, last):
            pages[page] = None
    return list(pages)

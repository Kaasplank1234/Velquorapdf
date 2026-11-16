"""Isolated MuPDF/Tesseract OCR, with bundled offline language models."""
import sys,json
from pathlib import Path
import fitz

def recognize(source,language,progress=lambda n:None):
    data=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[1]))/'assets/tessdata'
    for lang in language.split('+'):
        if lang not in ('nld','eng','deu','fra','spa','tur') or not (data/(lang+'.traineddata')).is_file():raise ValueError('Missing language pack: '+lang)
    out=fitz.open()
    try:
        for n,page in enumerate(source):
            pix=page.get_pixmap(dpi=150,colorspace=fitz.csRGB,alpha=False)
            with fitz.open(stream=pix.pdfocr_tobytes(language=language,tessdata=str(data)),filetype='pdf') as one:out.insert_pdf(one)
            progress(n+1)
        return out.tobytes(garbage=4,deflate=True)
    finally:out.close()

OCR_START = b'% Velqora OCR start\n'
OCR_END = b'\n% Velqora OCR end'


def ocr_stream(page):
    kind, ref = page.parent.xref_get_key(page.xref, 'VelqoraOCR')
    if kind == 'xref':
        xref = int(ref.split()[0])
        if xref in page.get_contents():
            stream = page.parent.xref_stream(xref)
            if stream.startswith(OCR_START) and stream.endswith(OCR_END):
                return xref
    return None


def add_text_layer(source, language, progress, repeat=False, page_index=None):
    """Recognize image-only pages while preserving the original PDF page objects."""
    data = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1])) / 'assets/tessdata'
    font = fitz.Font('cjk')
    changed = False
    pages = source if page_index is None else (source[page_index],)
    for number, page in enumerate(pages, 1):
        previous = ocr_stream(page)
        has_image = bool(page.get_image_info())
        if previous and repeat and has_image:
            remaining = [ref for ref in page.get_contents() if ref != previous]
            contents = ' '.join(f'{ref} 0 R' for ref in remaining)
            source.xref_set_key(page.xref, 'Contents', f'[{contents}]')
            page = source.reload_page(page)
        if has_image and (previous and repeat or not page.get_text().strip()):
            rotation = page.rotation
            page.set_rotation(0)
            try:
                dpi = min(220, max(36, int(72 * (9_000_000 / page.rect.get_area()) ** .5)))
                pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False, annots=False)
                with fitz.open(stream=pix.pdfocr_tobytes(language=language, tessdata=str(data)),
                               filetype='pdf') as recognized:
                    scan = recognized[0]
                    writer = fitz.TextWriter(page.rect)
                    sx, sy = page.rect.width / scan.rect.width, page.rect.height / scan.rect.height
                    for block in scan.get_text('dict', flags=fitz.TEXTFLAGS_TEXT)['blocks']:
                        for line in block.get('lines', ()):
                            for span in line['spans']:
                                x, y = span['origin']
                                writer.append((x * sx, y * sy), span['text'], font=font,
                                              fontsize=span['size'] * sy)
                    if not writer.text_rect.is_empty:
                        prior = set(page.get_contents())
                        writer.write_text(page, render_mode=3)
                        new = [ref for ref in page.get_contents() if ref not in prior]
                        if len(new) != 1:
                            raise RuntimeError('Could not isolate the OCR text layer.')
                        xref = new[0]
                        source.update_stream(xref, OCR_START + source.xref_stream(xref) + OCR_END)
                        source.xref_set_key(page.xref, 'VelqoraOCR', f'{xref} 0 R')
                        changed = True
                    elif previous and repeat:
                        restored = ' '.join(f'{ref} 0 R' for ref in (*remaining, previous))
                        source.xref_set_key(page.xref, 'Contents', f'[{restored}]')
            finally:
                page.set_rotation(rotation)
        progress(number)
    return source.tobytes(garbage=3, deflate=True) if changed else b''


def cli(folder):
    folder=Path(folder);request=json.loads((folder/'request.json').read_text())
    def progress(n):
        with (folder/'progress').open('a') as f:f.write(str(n)+'\n')
    try:
        with fitz.open(folder/'input.pdf') as source:
            if request.get('preserve_pages'):
                result = add_text_layer(source, request['language'], progress, repeat=request.get('repeat', False),
                                        page_index=request.get('page_index'))
            else:
                result = recognize(source, request['language'], progress)
        (folder/'output.pdf').write_bytes(result);return 0
    except Exception as ex:(folder/'error.txt').write_text(str(ex));return 1

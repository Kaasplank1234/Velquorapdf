"""Map pointer positions to PDF character ranges and markup quads."""
import fitz

MARKUP = {
    'Highlight': 'add_highlight_annot',
    'Underline': 'add_underline_annot',
    'Strike through': 'add_strikeout_annot',
}


class PageText:
    def __init__(self, page):
        flags = fitz.TEXTFLAGS_RAWDICT & ~fitz.TEXT_PRESERVE_IMAGES & ~fitz.TEXT_PRESERVE_LIGATURES
        raw = page.get_text('rawdict', flags=flags, sort=True)
        self.lines = []
        self.count = 0
        for block in raw['blocks']:
            for line in block.get('lines', ()):
                spans = [span for span in line['spans'] if span['chars']]
                chars = [char for span in spans for char in span['chars']]
                if chars:
                    self.lines.append((self.count, fitz.Rect(line['bbox']), line['dir'], spans, chars))
                    self.count += len(chars)

    def caret(self, point):
        if not self.lines:
            return 0
        def distance(line):
            box = line[1]
            return max(box.x0 - point.x, point.x - box.x1, 0)**2 + max(box.y0 - point.y, point.y - box.y1, 0)**2
        offset, _, direction, _, chars = min(self.lines, key=distance)
        dx, dy = direction
        position = point.x * dx + point.y * dy
        centers = [((c['bbox'][0] + c['bbox'][2]) * dx + (c['bbox'][1] + c['bbox'][3]) * dy)/2 for c in chars]
        rtl = len(centers) > 1 and centers[0] > centers[-1]
        for index, center in enumerate(centers):
            if (position > center) if rtl else (position < center):
                return offset + index
        return offset + len(chars)

    def extract(self, start, stop, with_color=False):
        quads, lines = [], []
        for offset, _, direction, spans, chars in self.lines:
            first = max(0, start - offset)
            last = min(len(chars), stop - offset)
            if first >= last:
                continue
            lines.append(''.join(char['c'] for char in chars[first:last]))
            cursor = 0
            for span in spans:
                length = len(span['chars'])
                lo, hi = max(0, first - cursor), min(length, last - cursor)
                if lo < hi:
                    quad = fitz.recover_span_quad(direction, span, span['chars'][lo:hi])
                    if quad.is_convex and quad.rect.get_area() > 0:
                        quads.append((quad, span['color']) if with_color else quad)
                cursor += length
        return '\n'.join(lines), quads

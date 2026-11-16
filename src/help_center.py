"""Searchable offline documentation for the Velqora workspace."""
from html import escape
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QTextBrowser, QVBoxLayout,
)
from PySide6.QtCore import Qt

ARTICLES = (
    ('Getting started', (
        'Open PDF from Home or drag a PDF into the window. Each document gets its own tab.',
        'Use All tools to switch between editing, comments, page organization and document actions.',
        'Use Save As to make a separate copy, or Help → Welcome tour for a guided introduction.',
    )),
    ('Find, select and copy text', (
        'Choose Select from the quick tools next to the page. Drag over text to select a range.',
        'Press Command+C on Mac or Ctrl+C on Windows to copy. Use Command+A or Ctrl+A to select the document text.',
        'Use the magnifier or Command/Ctrl+F to search. F3 and Shift+F3 navigate matches.',
    )),
    ('OCR and scanned PDFs', (
        'Open a scanned PDF. Velqora checks image-only pages and recognizes them on your device when automatic OCR is enabled.',
        'Open OCR in the top toolbar to see progress, change the language, recognize only the current page or cancel. If recognition already finished, choose Run again and confirm.',
        'When the text layer is ready, close the OCR panel, use Select and copy from the page. Save the PDF to retain the layer.',
        'Choose the scan language for better results. Faint, blurred or handwritten scans can produce mistakes. Pages with existing digital text are skipped.',
    )),
    ('Add and move a text box', (
        'Open Edit → Add text box, choose a font, size, alignment and color, then click the page.',
        'Type your text and click Place text box. Ctrl+Enter or Command+Enter also places it. Press Escape to discard the draft.',
        'Switch to Select and drag the text box to move it. Select it and press Delete to remove it. Undo can reverse either action.',
    )),
    ('Edit existing text and images', (
        'In Edit, choose Edit existing text and click a text line. The line must have a text layer and enough room for the replacement.',
        'Choose Add image to draw a placement rectangle. Choose Move image or Resize image and follow the on-screen instructions.',
        'Use Undo if you want to revert a change. OCR is useful for copying scan text; the scan image itself is still an image.',
    )),
    ('Highlight, underline and comment', (
        'Drag over a text range with Select, then choose Highlight, Underline or Strike through from the right-click menu.',
        'Open Comments to add a note, rectangle, circle or arrow. Select an existing annotation and press Delete to remove it.',
    )),
    ('Organize and extract pages', (
        'Open Organize pages. Use the page thumbnails to reorder pages, or the page controls to rotate, duplicate, crop or remove pages.',
        'Manage page range lets you act on several pages. Extract pages writes the selected pages to a new PDF. Split PDF writes consecutive groups to a folder.',
    )),
    ('Fill forms and sign', (
        'Choose Fill a form for supported PDF form fields. Save to preserve your changes.',
        'Choose Fill & Sign to draw a signature and place it on the page. A drawn signature is a visible annotation and can be moved with Select.',
    )),
    ('Protect, redact and export', (
        'Use Protect a PDF for password protection. Keep the password somewhere you can retrieve it.',
        'For redaction, choose Redact permanently and draw a rectangle over the information. Review the result and save a separate copy.',
        'Use Export for the available file types or Print to send the current document to a printer.',
    )),
    ('Settings and keyboard shortcuts', (
        'Open Document → Settings for appearance, page thumbnails and automatic OCR.',
        'Command/Ctrl+O opens a PDF. Command/Ctrl+S saves. Command/Ctrl+Z undoes a change, and adding Shift redoes it.',
        'Escape cancels inline editing or clears selection. Help → Welcome tour reopens the introduction.',
    )),
)


def show_help_center(window):
    dialog = QDialog(window)
    dialog.setWindowTitle('Velqora PDF Help Center')
    dialog.resize(820, 560)
    dialog.setAttribute(Qt.WA_DeleteOnClose)
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(22, 20, 22, 20)
    title = QLabel('Help Center')
    title.setObjectName('heading')
    layout.addWidget(title)
    search = QLineEdit()
    search.setPlaceholderText('Search articles, tools or shortcuts')
    search.setAccessibleName('Search help articles')
    layout.addWidget(search)
    body = QHBoxLayout()
    layout.addLayout(body, 1)
    topics = QListWidget()
    topics.setAccessibleName('Help articles')
    topics.setFixedWidth(252)
    topics.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    body.addWidget(topics)
    article = QTextBrowser()
    article.setObjectName('helpArticle')
    body.addWidget(article, 1)

    def show_topic(item, _previous):
        if item:
            heading, paragraphs = ARTICLES[item.data(Qt.UserRole)]
            article.setHtml('<h1>' + escape(heading) + '</h1>' +
                            ''.join('<p>' + escape(line) + '</p>' for line in paragraphs))
        else:
            article.setPlainText('No matching articles. Try a different search.')

    def filter_topics(query):
        terms = query.casefold().split()
        topics.clear()
        for index, (heading, paragraphs) in enumerate(ARTICLES):
            content = ' '.join((heading, *paragraphs)).casefold()
            if all(term in content for term in terms):
                item = QListWidgetItem(heading)
                item.setData(Qt.UserRole, index)
                topics.addItem(item)
        if topics.count():
            topics.setCurrentRow(0)
        else:
            show_topic(None, None)

    topics.currentItemChanged.connect(show_topic)
    search.textChanged.connect(filter_topics)
    filter_topics('')
    dialog.show()
    search.setFocus()
    return dialog

"""Document-specific OCR status and controls."""
from PySide6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QMessageBox, QProgressBar,
    QPushButton, QVBoxLayout,
)

LANGUAGES = {
    'English + Dutch': 'eng+nld', 'English': 'eng', 'Dutch': 'nld',
    'German': 'deu', 'French': 'fra', 'Spanish': 'spa', 'Turkish': 'tur',
}


class OCRPanel(QDialog):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setWindowTitle('Scan & OCR')
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)
        title = QLabel('Scan & OCR')
        title.setObjectName('heading')
        layout.addWidget(title)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setAccessibleName('OCR status')
        layout.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setAccessibleName('OCR page progress')
        layout.addWidget(self.progress)
        languages = QHBoxLayout()
        languages.addWidget(QLabel('Scan language'))
        self.language = QComboBox()
        self.language.addItems(LANGUAGES)
        self.language.setAccessibleName('Scan language')
        languages.addWidget(self.language, 1)
        layout.addLayout(languages)
        scope = QHBoxLayout()
        scope.addWidget(QLabel('Pages'))
        self.scope = QComboBox()
        self.scope.addItems(['Entire document', 'Current page'])
        self.scope.setAccessibleName('OCR pages')
        scope.addWidget(self.scope, 1)
        layout.addLayout(scope)
        buttons = QHBoxLayout()
        layout.addLayout(buttons)
        close = QPushButton('Close')
        close.clicked.connect(self.close)
        self.cancel = QPushButton('Cancel OCR')
        self.cancel.clicked.connect(editor.cancel_ocr)
        self.run = QPushButton()
        self.run.setObjectName('accent')
        self.run.clicked.connect(self.start)
        buttons.addWidget(close)
        buttons.addStretch()
        buttons.addWidget(self.cancel)
        buttons.addWidget(self.run)

    def update_status(self, message, checked, total, busy, completed):
        self.status.setText(message)
        self.progress.setRange(0, max(1, total))
        self.progress.setValue(checked)
        self.progress.setVisible(busy)
        self.cancel.setVisible(busy)
        self.run.setEnabled(not busy)
        self.language.setEnabled(not busy)
        self.scope.setEnabled(not busy)
        self.run.setText('Run again' if completed else 'Recognize text')

    def start(self):
        from worker_engine import ocr_stream
        page_index = self.editor.page if self.scope.currentIndex() == 1 else None
        repeat = (self.editor.has_ocr_layer() if page_index is None else
                  bool(ocr_stream(self.editor.doc.pdf[page_index])))
        if repeat and QMessageBox.question(self, 'Repeat OCR?',
                'This PDF already has a Velqora OCR layer. Replace it with a new recognition pass?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        self.editor.safe(lambda: self.editor.start_ocr(LANGUAGES[self.language.currentText()],
                                                              repeat=repeat, page_index=page_index))

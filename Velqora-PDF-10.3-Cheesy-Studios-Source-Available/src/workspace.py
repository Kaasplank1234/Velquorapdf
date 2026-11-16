"""Velqora desktop workspace. Original artwork and native Qt widgets."""
import json, os, sys, tempfile
from pathlib import Path
import fitz
from PySide6.QtCore import Qt, QSize, QSettings, QRectF, QPoint, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QAction
from PySide6.QtWidgets import *

def icon(kind):
    pix=QPixmap(24,24); pix.fill(Qt.transparent)
    p=QPainter(pix);p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor('#7b83a3'), 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    if kind=='open':p.drawRoundedRect(3,7,18,14,3,3);p.drawLine(4,7,10,3);p.drawLine(10,3,17,7)
    elif kind=='save':p.drawRoundedRect(4,3,16,18,2,2);p.drawRect(8,3,8,6);p.drawRect(8,14,8,7)
    elif kind=='home':p.drawLine(3,11,12,3);p.drawLine(12,3,21,11);p.drawRect(6,11,12,10)
    elif kind=='plus':p.drawLine(12,4,12,20);p.drawLine(4,12,20,12)
    elif kind=='clock':p.drawEllipse(3,3,18,18);p.drawLine(12,7,12,12);p.drawLine(12,12,16,14)
    elif kind=='search':p.drawEllipse(3,3,13,13);p.drawLine(15,15,22,22)
    elif kind=='text':p.drawLine(4,4,20,4);p.drawLine(12,4,12,21);p.drawLine(8,21,16,21)
    elif kind=='page':p.drawRoundedRect(5,2,14,20,2,2);p.drawLine(8,8,16,8);p.drawLine(8,12,16,12)
    elif kind=='select':p.drawPolygon([QPoint(5,3),QPoint(18,13),QPoint(12,14),QPoint(10,21)])
    elif kind=='edit':p.drawLine(5,18,17,6);p.drawLine(5,18,4,21);p.drawLine(4,21,8,20);p.drawLine(8,20,20,8)
    elif kind=='draw':p.drawLine(4,19,9,8);p.drawLine(9,8,13,16);p.drawLine(13,16,20,5)
    elif kind=='comment':p.drawRoundedRect(3,4,18,13,3,3);p.drawLine(7,17,7,21);p.drawLine(7,21,12,17)
    elif kind=='sign':p.drawLine(3,17,9,7);p.drawLine(9,7,10,17);p.drawLine(10,17,15,12);p.drawLine(15,12,21,17)
    elif kind=='grid':
        for x in (4, 13):
            for y in (4, 13):
                p.drawRoundedRect(x,y,7,7,1,1)
    elif kind=='close':p.drawLine(7,7,17,17);p.drawLine(17,7,7,17)
    elif kind=='more':
        for x in (5,12,19):p.drawEllipse(x-1,11,2,2)
    elif kind=='image':p.drawRect(3,4,18,16);p.drawEllipse(6,7,4,4);p.drawLine(4,19,13,11);p.drawLine(13,11,20,19)
    else:p.drawEllipse(4,4,16,16);p.drawLine(7,12,11,16);p.drawLine(11,16,18,8)
    p.end();return QIcon(pix)

def button(label,fn,kind='page'):
    b=QPushButton(icon(kind),label);b.setMinimumHeight(34);b.clicked.connect(lambda checked=False:fn());return b

def icon_button(label, kind, callback):
    widget = QToolButton()
    widget.setObjectName('railButton')
    widget.setIcon(icon(kind))
    widget.setToolTip(label)
    widget.setAccessibleName(label)
    widget.setFixedSize(32, 32)
    widget.clicked.connect(lambda checked=False: callback())
    return widget


def apply_theme(window):
    dark=window.dark
    bg,panel,fg,muted,line=('#101521','#192132','#f2f5ff','#b9c4db','#303d55') if dark else ('#f4f6fb','#ffffff','#202942','#53627d','#dce3f1')
    accent = '#c6b8ff' if dark else '#5138d4'
    accent_text = '#161c35' if dark else '#ffffff'
    tint = '#343052' if dark else '#eeebff'
    canvas = '#111725' if dark else '#e3e9f4'
    ui = (Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1])) / 'assets/ui').as_posix()
    mode = 'dark' if dark else 'light'
    field = '#202a3d' if dark else '#fafbfe'
    QApplication.instance().setStyleSheet(f'''
    QWidget {{font-family: "Inter", ".AppleSystemUIFont", "DejaVu Sans"; font-size:13px;color:{fg};}}
    QMainWindow,QDialog,QWidget#workspace {{background:{bg};}}
    QToolBar {{background:{panel};border:0;border-bottom:1px solid {line};spacing:6px;padding:9px;}}
    QToolButton {{padding:7px;border:0;border-radius:7px;}} QToolButton:hover {{background:{bg};}}
    QToolTip {{color:{fg};background:{panel};border:1px solid {line};padding:5px;}}
    QPushButton {{background:{panel};border:1px solid {line};border-radius:7px;padding:6px 11px;text-align:left;}}
    QPushButton:hover {{border-color:{accent};background:{bg};}} QPushButton:pressed {{background:{accent};color:{accent_text};}}
    QPushButton#accent {{background:{accent};color:{accent_text};border:0;}}
    QLineEdit,QComboBox,QSpinBox,QTextEdit,QPlainTextEdit,QTextBrowser,QListWidget {{
        background:{field};border:1px solid {line};border-radius:9px;padding:7px 10px;
        selection-background-color:{accent};selection-color:{accent_text};
    }}
    QLineEdit:hover,QComboBox:hover,QSpinBox:hover {{border-color:{muted};}}
    QLineEdit:focus,QComboBox:focus,QSpinBox:focus,QTextEdit:focus,QPlainTextEdit:focus {{border-color:{accent};background:{panel};}}
    QComboBox,QSpinBox {{padding-right:29px;min-height:20px;}}
    QComboBox {{combobox-popup:0;}}
    QComboBox QLineEdit,QSpinBox QLineEdit {{background:transparent;border:0;padding:0;}}
    QComboBox::drop-down {{
        subcontrol-origin:padding;subcontrol-position:top right;width:28px;border:0;
        background:transparent;border-top-right-radius:8px;border-bottom-right-radius:8px;
    }}
    QComboBox::drop-down:hover {{background:{tint};}}
    QComboBox::down-arrow,QPushButton::menu-indicator {{image:url("{ui}/down-{mode}.svg");width:14px;height:14px;}}
    QPushButton::menu-indicator {{subcontrol-origin:padding;subcontrol-position:right center;}}
    QComboBox QAbstractItemView {{
        background:{panel};color:{fg};border:1px solid {line};border-radius:8px;
        padding:4px;outline:0;selection-background-color:{tint};selection-color:{fg};show-decoration-selected:1;
    }}
    QComboBox QAbstractItemView::item {{min-height:27px;padding:3px 8px;border-radius:5px;}}
    QSpinBox::up-button,QSpinBox::down-button {{
        subcontrol-origin:border;width:25px;height:15px;border:0;background:transparent;
    }}
    QSpinBox::up-button {{subcontrol-position:top right;margin-top:3px;border-top-right-radius:7px;}}
    QSpinBox::down-button {{subcontrol-position:bottom right;margin-bottom:3px;border-bottom-right-radius:7px;}}
    QSpinBox::up-button:hover,QSpinBox::down-button:hover {{background:{tint};}}
    QSpinBox::up-arrow {{image:url("{ui}/up-{mode}.svg");width:12px;height:12px;}}
    QSpinBox::down-arrow {{image:url("{ui}/down-{mode}.svg");width:12px;height:12px;}}
    QListWidget::item {{padding:8px;border-radius:5px;}} QListWidget::item:selected {{background:{accent};color:{accent_text};}}
    QTabWidget::pane {{border:0;}}
    QWidget#tabCorner,QTabBar {{background:{bg};border:0;}}
    QTabBar::tab {{
        margin:5px 3px;padding:6px 11px;min-height:21px;background:transparent;
        border:1px solid transparent;border-radius:8px;color:{muted};
    }}
    QTabBar::tab:hover {{background:{field};color:{fg};}}
    QTabBar::tab:selected {{background:{panel};border-color:{line};color:{fg};}}
    QTabBar::tab:focus {{border-color:{accent};}}
    QTabBar::close-button {{
        image:url("{ui}/close-{mode}.svg");width:14px;height:14px;border:0;border-radius:4px;
    }}
    QTabBar::close-button:hover {{background:{tint};}}
    QWidget#documentNav {{background:{panel};border-bottom:1px solid {line};}}
    QWidget#documentNav QPushButton {{min-height:25px;}}
    QWidget#taskBar {{background:{panel};border-bottom:1px solid {line};}}
    QPushButton#taskButton {{background:transparent;border:1px solid transparent;font-weight:650;padding:5px 12px;}}
    QPushButton#taskButton:hover {{background:{bg};}}
    QPushButton#taskButton:checked {{color:{accent};background:{tint};border-color:{line};}}
    QLabel#toolStatus {{background:{tint};color:{fg};padding:8px 12px;border-radius:8px;}}
    QWidget#readerControls QPushButton {{min-height:23px;padding:4px 7px;}}
    QWidget#documentNav QPushButton#saveButton {{background:{accent};color:{accent_text};font-weight:700;}}
    QWidget#documentNav QPushButton#saveButton:hover {{border-color:{fg};}}
    QWidget#toolpanel QPushButton#toolEntry {{border:1px solid {line};background:{panel};}}
    QWidget#toolpanel QPushButton#toolEntry:hover {{background:{tint};}}
    QWidget#toolpanel QPushButton#toolEntry:checked {{background:{tint};border-color:{accent};}}
    QWidget#toolpanel QLabel#eyebrow {{font-size:12px;font-weight:700;padding-top:8px;}}
    QWidget#toolpanel QPushButton#accent {{background:{accent};color:{accent_text};border:0;padding:7px 10px;}}

    QPushButton#modeTab {{border:0;border-radius:8px;padding:6px 12px;font-weight:650;}}
    QPushButton#modeTab:checked {{color:{accent};background:{tint};}}
    QWidget#toolpanel QComboBox, QWidget#toolpanel QSpinBox {{min-height:22px;}}
    QWidget#toolRail, QWidget#readerControls {{background:{panel};border:1px solid {line};border-radius:9px;}}
    QToolButton#railButton {{padding:5px;border-radius:6px;}}
    QToolButton#railButton:checked {{background:{tint};border:1px solid {accent};}}
    QLabel#panelTitle {{font-size:20px;font-weight:750;}}
    QLabel#brandBadge {{background:#5142dc;color:white;padding:6px 9px;border-radius:7px;font-weight:750;}}
    QWidget#homeCard {{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #181638,stop:1 #49358c);border-radius:24px;}}
    QWidget#homeCard QLabel {{color:#ffffff;}}
    QWidget#homeCard QLabel#homeSubtitle {{color:#ddd7f6;}}
    QWidget#homeCard QLabel#homeBadge {{background:#ffffff;color:#442a9b;border-radius:10px;font-size:21px;font-weight:750;}}
    QLabel#draftError {{color:{fg};background:{tint};padding:5px;border-radius:6px;}}
    QLabel#counter {{color:{muted};padding:0 10px;font-weight:650;}}
    QPushButton:disabled {{color:{muted};}}
    QPushButton:focus,QToolButton:focus {{border:1px solid {accent};}}
    QListWidget#recentDocuments {{padding:8px;border-radius:14px;}}
    QLabel#homeTitle {{font-size:44px;font-weight:750;}}
    QLabel#homeSubtitle {{font-size:15px;color:{muted};}}
    QWidget#draftPanel,QWidget#readerFooter {{background:{panel};border-top:1px solid {line};}}
    QWidget#quickRail {{background:{panel};border-right:1px solid {line};}}
    QLabel#draftCaption {{font-weight:700;color:{accent};}}
    QWidget#draftPanel QPlainTextEdit {{border:1px solid {accent};border-radius:9px;}}

    QPushButton#homeAction[primary="true"] {{background:{accent};color:{accent_text};border:0;}}
    QPushButton#homeAction {{padding:12px 16px;font-size:14px;font-weight:650;}}

    QListWidget#pageThumbnails {{border:0;border-left:1px solid {line};border-radius:0;padding:8px;}}
    QWidget#searchBar {{background:{panel};border-bottom:1px solid {line};}}
    QWidget#toolpanel QPushButton#toolEntry {{min-height:31px;font-size:13px;padding:5px 8px;border-radius:7px;}}
    QWidget#toolpanel QPushButton#toolEntry:checked {{background:{tint};color:{accent};font-weight:650;}}
    QPushButton#ocrButton {{background:{tint};color:{fg};border-color:{line};font-weight:650;}}
    QLabel#toolHint {{color:{muted};background:{tint};padding:8px;border-radius:8px;}}
    QTextBrowser#helpArticle {{padding:14px;}}
    QProgressBar {{border:1px solid {line};background:{bg};border-radius:5px;text-align:center;}}
    QProgressBar::chunk {{background:{accent};border-radius:4px;}}
    QFrame#panelRule {{background:{line};max-height:1px;}}
    QGraphicsView {{border:0;}}
    QStatusBar {{border-top:1px solid {line};}}
    QWidget#toolpanel QPushButton {{border:0;background:transparent;padding:5px 7px;}}
    QWidget#toolpanel QPushButton:hover {{background:{bg};}}
    QWidget#toolpanel QPushButton#toolEntry:focus {{border-color:{accent};}}
    QScrollArea {{border:0;background:{panel};}} QWidget#toolpanel {{background:{panel};}}
    QLabel#eyebrow {{color:{muted};font-size:11px;font-weight:600;}}
    QLabel#heading {{font-size:24px;font-weight:700;}} QLabel#brand {{font-size:18px;font-weight:700;}}
    QMenuBar,QMenu,QStatusBar {{background:{panel};color:{fg};}} QMenu::item:selected {{background:{accent};color:{accent_text};}}
    QSplitter::handle {{background:{line};width:1px;}}
    QScrollBar:vertical {{width:10px;background:transparent;margin:2px;}}
    QScrollBar:horizontal {{height:10px;background:transparent;margin:2px;}}
    QScrollBar::handle {{background:{line};border-radius:3px;min-height:24px;min-width:24px;}}
    QScrollBar::handle:hover {{background:{muted};}}
    QScrollBar::add-line,QScrollBar::sub-line {{height:0;width:0;background:transparent;border:0;}}
    QScrollBar::add-page,QScrollBar::sub-page {{background:transparent;}}
    QAbstractScrollArea::corner {{background:transparent;border:0;}}
    ''')
    window.settings.setValue('dark',dark)
    for i in range(window.tabs.count()):window.tabs.widget(i).canvas.setBackgroundBrush(QColor(canvas))

def init_window(w):
    w.setWindowTitle('Velqora PDF');w.resize(1240,770);w.setMinimumSize(840,560);w.setAcceptDrops(True)
    w.settings=QSettings('Velqora','PDF');w.dark=w.settings.value('dark',False,type=bool)
    root=QWidget();root.setObjectName('workspace');layout=QVBoxLayout(root);layout.setContentsMargins(0,0,0,0);layout.setSpacing(0)
    w.tabs=QTabWidget();w.tabs.setTabsClosable(True);w.tabs.tabCloseRequested.connect(w.close_tab)
    w.stack=QStackedWidget();layout.addWidget(w.stack);w.setCentralWidget(root)
    home=QWidget();hl=QVBoxLayout(home);hl.setContentsMargins(72,55,72,45);hl.setSpacing(20)
    welcome = QWidget()
    welcome.setObjectName('homeCard')
    welcome_layout = QVBoxLayout(welcome)
    welcome_layout.setContentsMargins(36, 29, 36, 34)
    welcome_layout.setSpacing(14)
    badge = QLabel('V')
    badge.setObjectName('homeBadge')
    badge.setAlignment(Qt.AlignCenter)
    badge.setFixedSize(43, 43)
    badge.setAccessibleName('Velqora PDF')
    welcome_layout.addWidget(badge)
    title = QLabel('Velqora PDF')
    title.setObjectName('homeTitle')
    welcome_layout.addWidget(title)
    subtitle = QLabel('Read, edit and scan your PDFs offline.')
    subtitle.setObjectName('homeSubtitle')
    welcome_layout.addWidget(subtitle)
    cards=QHBoxLayout();cards.setSpacing(12);welcome_layout.addLayout(cards)
    hl.addWidget(welcome)
    for label,fn,k in [('Open PDF',w.open,'open'),('New document',w.new,'plus'),('Images to PDF',w.from_images,'image')]:
        b=button(label,lambda f=fn:w.safe(f),k);b.setObjectName('homeAction');b.setProperty('primary', label == 'Open PDF');b.setMinimumHeight(52);cards.addWidget(b)
    recent_heading = QLabel('Recent documents')
    recent_heading.setObjectName('panelTitle')
    hl.addWidget(recent_heading)
    w.recent = QListWidget()
    w.recent.setAccessibleName('Recent documents')
    w.recent.setObjectName('recentDocuments')
    hl.addWidget(w.recent)
    w.recent.itemActivated.connect(lambda item:w.safe(lambda:w.open(item.data(Qt.UserRole))) if item.data(Qt.UserRole) else None)
    w.stack.addWidget(home);w.stack.addWidget(w.tabs)
    corner = QWidget(w.tabs)
    corner.setObjectName('tabCorner')
    corner_layout = QHBoxLayout(corner)
    corner_layout.setContentsMargins(9, 0, 6, 0)
    brand = QLabel('V')
    brand.setAccessibleName('Velqora PDF')
    brand.setObjectName('brandBadge')
    corner_layout.addWidget(brand)
    for label, kind, callback in [('Home', 'home', lambda: w.stack.setCurrentIndex(0)),
                                   ('Open PDF', 'open', w.open)]:
        corner_layout.addWidget(icon_button(label, kind, lambda fn=callback: w.safe(fn)))
    w.tabs.setCornerWidget(corner, Qt.TopLeftCorner)
    w.tabs.setDocumentMode(False)
    w.tabs.tabBar().setDrawBase(False)
    w.tabs.tabBar().setElideMode(Qt.ElideMiddle)
    w.tabs.setMovable(True)
    w.tabs.tabBar().setAccessibleName('Open PDFs')
    actions=[('Home',lambda:w.stack.setCurrentIndex(0),'home',None),('Open',w.open,'open','Ctrl+O'),('New',w.new,'plus','Ctrl+N'),('Save',w.save,'save','Ctrl+S'),('Save As',lambda:w.save(True),'save','Ctrl+Shift+S'),('Undo',lambda:w.history(False),'other','Ctrl+Z'),('Redo',lambda:w.history(True),'other','Ctrl+Shift+Z'),('Find',w.search,'search','Ctrl+F')]
    menu=w.menuBar().addMenu('Document')
    for title,fn,k,key in actions:
        a=QAction(icon(k),title,w);a.triggered.connect(lambda checked=False,f=fn:w.safe(f))
        if key:a.setShortcut(key)
        menu.addAction(a)
    for title,fn,key in [('Find Next',lambda:w.find_again(1),'F3'),('Find Previous',lambda:w.find_again(-1),'Shift+F3'),('Export',w.export,None),('Encrypt',w.encrypt,None),('Print',w.print_pdf,'Ctrl+P'),('Settings',lambda:preferences(w),None),('Full Screen',w.fullscreen,'Ctrl+Meta+F')]:
        a=QAction(title,w);a.triggered.connect(lambda checked=False,f=fn:w.safe(f))
        if key:a.setShortcut(key)
        menu.addAction(a)
    for title, callback, shortcut in [
        ('View Document Text', w.show_document_text, None),
        ('Copy All Text', w.copy_all_text, 'Ctrl+Shift+C'),
    ]:
        action = QAction(title, w)
        action.triggered.connect(lambda checked=False, fn=callback: w.safe(fn))
        if shortcut:
            action.setShortcut(shortcut)
        menu.addAction(action)
    from macos_defaults import app_bundle
    if app_bundle() is not None:
        action = QAction('Set as Default PDF App', w)
        action.triggered.connect(w.ask_default_pdf_app)
        menu.addAction(action)
    from help_center import show_help_center
    help_menu = w.menuBar().addMenu('Help')
    help_menu.addAction('Help Center', lambda: show_help_center(w))
    help_menu.addAction('Welcome tour', lambda: show_tour(w))
    w.statusBar().showMessage('Offline workspace')
    refresh_recent(w);apply_theme(w);w.stack.setCurrentIndex(0)

def show_tour(window):
    steps = (
        ('Welcome to Velqora PDF', 'Open a PDF or start a blank document. Use All tools to find editing, page organization, comments and signatures.'),
        ('Edit directly on the page', 'Under Edit, choose Add text box and a font. Click the page, type, then confirm with Ctrl or Command + Enter. Use Select to drag the finished box.'),
        ('Copy text from scans', 'Scans are recognized offline in the background. Drag over the text and press Ctrl or Command + C. Use the clock button to check or repeat OCR.'),
    )
    dialog = QDialog(window)
    dialog.setWindowTitle('Welcome to Velqora PDF')
    dialog.setMinimumWidth(460)
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(26, 24, 26, 22)
    layout.setSpacing(14)
    title = QLabel()
    title.setObjectName('heading')
    copy = QLabel()
    copy.setWordWrap(True)
    copy.setMinimumHeight(62)
    count = QLabel()
    count.setObjectName('eyebrow')
    for label in (count, title, copy):
        layout.addWidget(label)
    actions = QHBoxLayout()
    layout.addLayout(actions)
    step = 0
    def update():
        count.setText(f'{step + 1} / {len(steps)}')
        title.setText(steps[step][0])
        copy.setText(steps[step][1])
        back.setEnabled(step > 0)
        forward.setText('Get started' if step == len(steps) - 1 else 'Next')
    def advance(delta):
        nonlocal step
        if step + delta == len(steps):
            dialog.accept()
        else:
            step += delta
            update()
    actions.addWidget(button('Skip tour', dialog.reject, 'close'))
    actions.addStretch()
    back = button('Back', lambda: advance(-1))
    forward = button('Next', lambda: advance(1))
    forward.setObjectName('accent')
    actions.addWidget(back)
    actions.addWidget(forward)
    update()
    dialog.exec()
    window.settings.setValue('tourSeen', True)


def refresh_recent(w):
    w.recent.clear()
    for path in w.settings.value('recent', [], type=list):
        if not Path(path).is_file():
            continue
        item = QListWidgetItem(f'{Path(path).name}\n{Path(path).parent}')
        item.setData(Qt.UserRole, path)
        item.setIcon(icon('page'))
        item.setToolTip(path)
        w.recent.addItem(item)
    if not w.recent.count():
        item = QListWidgetItem('Recently opened PDFs will appear here.')
        item.setFlags(Qt.NoItemFlags)
        w.recent.addItem(item)

def remember(w,path):
    paths=w.settings.value('recent',[],type=list);paths=[str(path)]+[p for p in paths if p!=str(path)]
    w.settings.setValue('recent',paths[:20]);refresh_recent(w)

def preferences(w):
    d=QDialog(w);d.setWindowTitle('Workspace');l=QFormLayout(d)
    dark=QCheckBox('Dark mode');dark.setChecked(w.dark);l.addRow(dark)
    automatic_ocr=QCheckBox('Recognize scanned PDF pages automatically')
    automatic_ocr.setChecked(w.settings.value('automaticOcr', True, type=bool))
    l.addRow(automatic_ocr)
    thumbs = QCheckBox('Show page navigation')
    active = w.tabs.currentWidget()
    thumbs.setChecked(not active.pages.isHidden() if active else
                      w.settings.value('pageNavigation', False, type=bool))
    l.addRow(thumbs)
    buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);l.addRow(buttons);buttons.accepted.connect(d.accept);buttons.rejected.connect(d.reject)
    if d.exec()==QDialog.Accepted:
        w.dark=dark.isChecked();apply_theme(w)
        w.settings.setValue('automaticOcr', automatic_ocr.isChecked())
        w.settings.setValue('pageNavigation', thumbs.isChecked())
        for i in range(w.tabs.count()):
            editor = w.tabs.widget(i)
            editor.pages.setVisible(thumbs.isChecked())
            if thumbs.isChecked():
                editor.update_thumbnails()

def init_editor(e,owner,doc):
    from main import Canvas
    e.owner=owner;e.doc=doc;e.page=0;e.scale=1.15;e.mode='Select';e.color=(0,0,0)
    e.highlight_color = (1, .82, .16)
    e.ink_color = (.25, .18, .71)
    l=QVBoxLayout(e);l.setContentsMargins(0,0,0,0);l.setSpacing(0)
    nav_widget = QWidget()
    nav_widget.setObjectName('documentNav')
    nav = QHBoxLayout(nav_widget)
    nav.setContentsMargins(12, 7, 12, 7)
    nav.setSpacing(4)
    l.addWidget(nav_widget)
    e.mode_buttons = {}
    nav.addWidget(button('Find text', owner.search, 'search'))
    nav.addWidget(button('Thumbnails', e.toggle_pages, 'page'))
    nav.addStretch()
    e.ocr_message = 'Recognize scanned text offline.'
    e.ocr_busy = e.ocr_completed = False
    e.ocr_checked = 0
    e.ocr_button = button('Scan text', e.ocr, 'clock')
    e.ocr_button.setObjectName('ocrButton')
    e.ocr_button.setToolTip(e.ocr_message)
    nav.addWidget(e.ocr_button)
    e.undo_button = button('Undo', lambda: owner.safe(lambda: owner.history(False)), 'other')
    e.redo_button = button('Redo', lambda: owner.safe(lambda: owner.history(True)), 'other')
    nav.addWidget(e.undo_button)
    nav.addWidget(e.redo_button)
    save = button('Save PDF', owner.save, 'save')
    save.setObjectName('saveButton')
    nav.addWidget(save)
    more = icon_button('More document actions', 'more', lambda: None)
    more_menu = QMenu(more)
    for label, callback in [('Undo', lambda: owner.history(False)), ('Redo', lambda: owner.history(True)),
                             ('Export', owner.export), ('Print', owner.print_pdf),
                             ('Settings', lambda: preferences(owner))]:
        more_menu.addAction(label, lambda fn=callback: owner.safe(fn))
    more.setMenu(more_menu)
    more.setPopupMode(QToolButton.InstantPopup)
    nav.addWidget(more)
    tasks = QWidget()
    tasks.setObjectName('taskBar')
    task_layout = QHBoxLayout(tasks)
    task_layout.setContentsMargins(12, 5, 12, 5)
    task_layout.setSpacing(4)
    l.addWidget(tasks)
    for label, kind, index in [('Edit PDF', 'edit', 0), ('Pages', 'grid', 1),
                               ('Comments', 'comment', 2), ('All tools', 'more', 4)]:
        task = button(label, lambda category=index: e.open_tool_category(category), kind)
        task.setObjectName('taskButton')
        task.setCheckable(True)
        task_layout.addWidget(task)
        e.mode_buttons[index] = task
    task_layout.addWidget(button('Sign', lambda: e.safe(lambda: signature(e)), 'sign'))
    task_layout.addStretch()
    e.tool_status = QLabel('Select')
    e.tool_status.setObjectName('toolStatus')
    e.tool_status.setAccessibleName('Current tool')
    task_layout.addWidget(e.tool_status)
    e.find_bar = QWidget()
    e.find_bar.setObjectName('searchBar')
    find_layout = QHBoxLayout(e.find_bar)
    e.find_input = QLineEdit()
    e.find_input.setPlaceholderText('Find text in this PDF')
    e.find_input.setAccessibleName('Search text')
    e.find_input.returnPressed.connect(lambda: e.safe(e.find))
    e.find_status = QLabel()
    e.search_term = ''
    e.search_hits = []
    e.search_index = -1
    e.find_input.textChanged.connect(lambda: e.clear_find() if e.search_hits or e.find_status.text() else None)
    find_layout.addWidget(e.find_input, 1)
    find_layout.addWidget(e.find_status)
    find_layout.addWidget(button('Previous match', lambda: e.safe(lambda: e.find(-1)), 'search'))
    find_layout.addWidget(button('Next match', lambda: e.safe(e.find), 'search'))
    find_layout.addWidget(button('Close search', e.close_find))
    e.find_bar.hide()
    l.addWidget(e.find_bar)
    e.split=QSplitter();l.addWidget(e.split,1)
    e.pages=QListWidget();e.pages.setMinimumWidth(130);e.pages.setMaximumWidth(240);e.pages.setDragDropMode(QAbstractItemView.InternalMove);e.pages.setDefaultDropAction(Qt.MoveAction)
    e.thumbnail_timer = QTimer(e)
    e.thumbnail_timer.setSingleShot(True)
    e.thumbnail_timer.timeout.connect(e.update_thumbnails)
    e.pages.setObjectName('pageThumbnails')
    e.pages.setAccessibleName('Page thumbnails')
    e.pages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    e.pages.setMinimumWidth(166)
    e.pages.currentRowChanged.connect(e.select_page);e.pages.model().rowsMoved.connect(e.reorder)
    document = QWidget()
    document_layout = QGridLayout(document)
    document_layout.setContentsMargins(0, 0, 0, 0)
    document_layout.setSpacing(0)
    e.canvas = Canvas(e)
    document_layout.addWidget(e.canvas, 0, 1)
    document_layout.setColumnStretch(1, 1)
    e.canvas.setBackgroundBrush(QColor('#111725' if owner.dark else '#e3e9f4'))

    rail = QWidget()
    rail.setObjectName('toolRail')
    rail_layout = QVBoxLayout(rail)
    rail_layout.setContentsMargins(4, 4, 4, 4)
    rail_layout.setSpacing(2)
    rail_host = QWidget()
    host_layout = QVBoxLayout(rail_host)
    host_layout.setContentsMargins(7, 10, 7, 0)
    rail_host.setObjectName('quickRail')
    host_layout.addWidget(rail)
    host_layout.addStretch()
    document_layout.addWidget(rail_host, 0, 0)

    controls = QWidget()
    controls.setObjectName('readerControls')
    controls_layout = QHBoxLayout(controls)
    controls_layout.setContentsMargins(5, 3, 5, 3)
    controls_layout.setSpacing(3)
    e.counter = QLabel()
    e.counter.setObjectName('counter')
    for title, name, callback in [
        ('‹', 'Previous page', lambda: e.navigate(-1)),
        ('›', 'Next page', lambda: e.navigate(1)),
        ('−', 'Zoom out', lambda: e.zoom(.8)),
        ('+', 'Zoom in', lambda: e.zoom(1.25)),
    ]:
        control = QPushButton(title)
        control.setAccessibleName(name)
        control.setToolTip(name)
        control.clicked.connect(lambda checked=False, fn=callback: e.safe(fn))
        controls_layout.addWidget(control)
    fit = QPushButton('Fit')
    fit.setAccessibleName('Fit page or width')
    fit.setMinimumWidth(61)
    fit_options = QMenu(fit)
    fit_options.addAction('Fit page', lambda: fit_page(e))
    fit_options.addAction('Fit width', lambda: fit_width(e))
    fit.setMenu(fit_options)
    controls_layout.addWidget(fit)
    controls_layout.addWidget(e.counter)
    controls_host = QWidget()
    controls_outer = QHBoxLayout(controls_host)
    controls_host.setObjectName('readerFooter')
    controls_outer.setContentsMargins(9, 5, 9, 5)
    controls_outer.addStretch()
    controls_outer.addWidget(controls)
    controls_outer.addStretch()
    document_layout.addWidget(controls_host, 1, 0, 1, 2)

    panel = QWidget()
    panel.setObjectName('toolpanel')
    tl = QVBoxLayout(panel)
    tl.setContentsMargins(15, 14, 15, 12)
    tl.setSpacing(9)
    heading_row = QHBoxLayout()
    e.panel_title = QLabel('All tools')
    e.panel_title.setObjectName('panelTitle')
    heading_row.addWidget(e.panel_title, 1)
    def hide_tools():
        e.tool_panel.hide()
        for task in e.mode_buttons.values():
            task.setChecked(False)
    heading_row.addWidget(icon_button('Hide tools', 'close', hide_tools))
    tl.addLayout(heading_row)
    rule = QFrame()
    rule.setObjectName('panelRule')
    rule.setFixedHeight(1)
    tl.addWidget(rule)
    e.category = QComboBox()
    e.category.addItems(['Edit PDF', 'Organize pages', 'Comments', 'Document', 'All tools'])
    e.category.hide()
    e.tools_stack = QStackedWidget()
    tl.addWidget(e.tools_stack, 1)
    e.category.currentIndexChanged.connect(e.tools_stack.setCurrentIndex)
    edit = QWidget()
    el = QVBoxLayout(edit)
    el.setContentsMargins(0, 4, 0, 0)
    e.modes=QComboBox();e.modes.addItems(['Select','Add text','Add text box','Replace text','Delete text','Move text','Add image','Move image','Resize image','Replace image','Delete image','Rotate image','Highlight','Underline','Strike through','Draw','Note','Rectangle','Circle','Arrow','Redact','Crop'])
    def change_mode(mode):
        e.mode = mode
        from text_selection import MARKUP
        if mode in MARKUP and e.canvas.text_selection:
            e.safe(lambda: e.canvas.apply_markup(mode))
    e.modes.currentTextChanged.connect(change_mode)
    e.modes.setAccessibleName('Active editing tool')
    e.modes.currentTextChanged.connect(e.tool_status.setText)
    el.addWidget(e.modes)
    hint = QLabel('Drag across page text to select it.')
    hint.setObjectName('toolHint')
    hint.setWordWrap(True)
    el.addWidget(hint)
    tips = {
        'Select': 'Drag across page text to select it.',
        'Add text': 'Click the page and type. Press Enter to place the text.',
        'Add text box': 'Click the page to type in a movable box.',
        'Replace text': 'Click an existing text line to edit it.',
        'Delete text': 'Click the text you want to remove.',
        'Move text': 'Click existing text, then click its new position.',
        'Add image': 'Draw a rectangle on the page to place an image.',
        'Move image': 'Click the image, then click its new position.',
        'Resize image': 'Click the image, then click its new bottom-right corner.',
        'Crop': 'Draw the rectangle you want to keep.',
        'Redact': 'Draw over the information you want to redact.',
        'Highlight': 'Drag across text to highlight it.',
        'Underline': 'Drag across text to underline it.',
        'Strike through': 'Drag across text to cross it out.',
        'Draw': 'Drag on the page to draw a stroke.',
        'Note': 'Click the page to add a comment.',
    }
    def describe_mode(mode):
        tip = tips.get(mode, mode)
        hint.setText(tip)
        e.tool_status.setToolTip(tip)
    e.modes.currentTextChanged.connect(describe_mode)
    describe_mode(e.mode)
    from font_catalog import STANDARD, available_fonts
    el.addWidget(QLabel('TEXT STYLE'))
    e.font = QComboBox()
    e.font.setEditable(True)
    e.font.setInsertPolicy(QComboBox.NoInsert)
    e.font.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    e.font.setMinimumContentsLength(13)
    fonts = available_fonts()
    favorites = ('Arial', 'Times New Roman', 'Verdana', 'Georgia', 'Calibri', 'Arimo', 'Inter', 'Roboto', 'Open Sans', 'Lato', 'Montserrat', 'Poppins',
                 'Source Sans 3', 'Noto Sans', 'Nunito', 'Raleway', 'Work Sans', 'DM Sans',
                 'Manrope', 'Rubik', 'Ubuntu', 'Carlito', 'Tinos', 'Cousine', 'Lora',
                 'Merriweather', 'Playfair Display', 'Libre Baskerville', 'Crimson Text',
                 'Cormorant Garamond', 'EB Garamond', 'Fira Code', 'JetBrains Mono',
                 'Space Mono', 'Inconsolata')
    ordered = dict.fromkeys((*STANDARD, *(family for family in favorites if family in fonts), *fonts))
    e.font.addItems(list(ordered))
    e.font.setAccessibleName('Font family')
    e.font.setToolTip('Type a font name to find it. Arimo is an Arial-compatible choice. Fonts work for text boxes and text lines.')
    el.addWidget(e.font)
    e.size=QSpinBox();e.size.setRange(4,144);e.size.setValue(12);e.size.setSuffix(' pt');e.size.setAccessibleName('Font size');el.addWidget(e.size)
    e.align=QComboBox();e.align.addItems(['Left','Center','Right','Justify']);e.align.setAccessibleName('Text alignment');el.addWidget(e.align)
    el.addWidget(button('Text color',e.pick_color,'text'))
    entries = []
    for section, options in (
        ('Text', [('Add text box', 'Add text box', 'text'),
                  ('Add text line', 'Add text', 'text'),
                  ('Edit existing text', 'Replace text', 'edit')]),
        ('Images', [('Add image', 'Add image', 'image'),
                    ('Move image', 'Move image', 'image')]),
    ):
        heading = QLabel(section)
        heading.setObjectName('eyebrow')
        el.addWidget(heading)
        for label, mode, kind in options:
            entry = button(label, lambda value=mode: e.modes.setCurrentText(value), kind)
            entry.setObjectName('toolEntry')
            entry.setCheckable(True)
            entry.setChecked(e.mode == mode)
            entries.append((mode, entry))
            el.addWidget(entry)
    def sync_edit_entries(mode):
        for value, entry in entries:
            entry.setChecked(value == mode)
    e.modes.currentTextChanged.connect(sync_edit_entries)
    for value, entry in entries:
        entry.clicked.connect(lambda checked=False: sync_edit_entries(e.mode))
    export_image = button('Export image', lambda: e.safe(e.export_image), 'image')
    export_image.setObjectName('toolEntry')
    el.addWidget(export_image)
    el.addStretch()
    e.tools_stack.addWidget(edit)
    groups=[
      [('Manage page range',e.manage_page_range),('Rotate',e.rotate),('Blank page',e.blank),('Duplicate',e.duplicate),('Delete',e.delete),('Insert PDF',e.merge),('Extract pages',e.extract),('Split PDF',lambda:split_pdf(e)),('Crop page',lambda:e.modes.setCurrentText('Crop'))],
      [('Highlight',lambda:e.modes.setCurrentText('Highlight')),('Underline',lambda:e.modes.setCurrentText('Underline')),('Strike through',lambda:e.modes.setCurrentText('Strike through')),('Note',lambda:e.modes.setCurrentText('Note')),('Rectangle',lambda:e.modes.setCurrentText('Rectangle')),('Circle',lambda:e.modes.setCurrentText('Circle')),('Arrow',lambda:e.modes.setCurrentText('Arrow')),('Remove annotations',e.remove_annotations)],
      [('Bookmarks',e.bookmarks),('Properties',e.properties),('Metadata',lambda:metadata(e)),('Watermark / page numbers',e.decorate),('Fill form',e.form),('Draw signature',lambda:signature(e)),('Offline OCR',e.ocr),('Redact permanently',lambda:e.modes.setCurrentText('Redact')),('Compare text',lambda:compare(e))]]
    for category_index, group in enumerate(groups):
        page=QWidget();pl=QVBoxLayout(page);pl.setContentsMargins(0,4,0,0)
        if category_index == 1:
            markup_heading = QLabel('Text markup')
            markup_heading.setObjectName('eyebrow')
            pl.addWidget(markup_heading)
            palette = QHBoxLayout()
            pl.addLayout(palette)
            for label, shade in [('Yellow', '#ffd229'), ('Green', '#68d88c'),
                                 ('Blue', '#72c5ff'), ('Pink', '#f58ac3'), ('Orange', '#ffa252')]:
                swatch = QPushButton()
                swatch.setAccessibleName(f'{label} highlight')
                swatch.setToolTip(f'{label} highlight')
                swatch.setFixedSize(25, 25)
                swatch.setStyleSheet(f'background:{shade};border-radius:6px;')
                def highlight(checked=False, value=shade):
                    color = QColor(value)
                    e.highlight_color = (color.redF(), color.greenF(), color.blueF())
                    e.choose_mode('Highlight')
                swatch.clicked.connect(highlight)
                palette.addWidget(swatch)
            palette.addStretch()
            drawing_heading = QLabel('Freehand drawing')
            drawing_heading.setObjectName('eyebrow')
            pl.addWidget(drawing_heading)
            e.brush = QComboBox()
            for label, opacity in [('Pen', 1.0), ('Marker', .45), ('Brush', .78)]:
                e.brush.addItem(label, opacity)
            e.brush.setAccessibleName('Brush preset')
            e.ink_width = QSpinBox()
            e.ink_width.setRange(1, 32)
            e.ink_width.setValue(3)
            e.ink_width.setSuffix(' pt')
            e.ink_width.setAccessibleName('Stroke width')
            e.brush.currentIndexChanged.connect(lambda index: e.ink_width.setValue((3, 12, 7)[index]))
            drawing_row = QHBoxLayout()
            drawing_row.addWidget(e.brush, 1)
            drawing_row.addWidget(e.ink_width)
            pl.addLayout(drawing_row)
            def pick_ink():
                color = QColorDialog.getColor(QColor.fromRgbF(*e.ink_color), e, 'Drawing color')
                if color.isValid():
                    e.ink_color = (color.redF(), color.greenF(), color.blueF())
                    ink_button.setText('Color · ' + color.name().upper())
            ink_button = button('Drawing color', pick_ink, 'draw')
            pl.addWidget(ink_button)
            draw_button = button('Draw on page', lambda: e.choose_mode('Draw'), 'draw')
            draw_button.setObjectName('accent')
            pl.addWidget(draw_button)
        for title, fn in group:
            entry = button(title, lambda callback=fn: e.safe(callback))
            entry.setObjectName('toolEntry')
            pl.addWidget(entry)
        pl.addStretch();e.tools_stack.addWidget(page)
    gallery = QWidget()
    gallery_layout = QVBoxLayout(gallery)
    gallery_layout.setContentsMargins(0, 3, 0, 0)
    gallery_layout.setSpacing(4)
    for title, kind, callback in [
        ('Edit a PDF', 'edit', lambda: e.open_tool_category(0)),
        ('Organize pages', 'grid', lambda: e.open_tool_category(1)),
        ('Comments and drawing', 'comment', lambda: e.open_tool_category(2)),
        ('Export a PDF', 'page', owner.export),
        ('Scan && OCR', 'search', e.ocr),
        ('Fill a form', 'text', e.form),
        ('Draw a signature', 'sign', lambda: signature(e)),
        ('Protect a PDF', 'save', owner.encrypt),
        ('Document tools', 'more', lambda: e.open_tool_category(3)),
    ]:
        entry = button(title, lambda fn=callback: e.safe(fn), kind)
        entry.setObjectName('toolEntry')
        gallery_layout.addWidget(entry)
    gallery_layout.addStretch()
    e.tools_stack.addWidget(gallery)
    rail_buttons = {}
    for title, kind in [('Select', 'select'), ('Replace text', 'edit'), ('Add text box', 'text'),
                        ('Draw', 'draw'), ('Note', 'comment'), ('Add image', 'image')]:
        shortcut = QToolButton(rail)
        shortcut.setObjectName('railButton')
        shortcut.setIcon(icon(kind))
        shortcut.setToolTip(title)
        shortcut.setAccessibleName(title)
        shortcut.setFixedSize(32, 32)
        shortcut.setCheckable(True)
        shortcut.clicked.connect(lambda checked=False, mode=title: e.choose_mode(mode))
        rail_layout.addWidget(shortcut)
        rail_buttons[title] = shortcut

    def sync_rail(mode):
        for name, shortcut in rail_buttons.items():
            shortcut.setChecked(name == mode)

    e.modes.currentTextChanged.connect(sync_rail)
    sync_rail(e.mode)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(panel)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setMinimumWidth(254)
    scroll.setMaximumWidth(290)
    e.tool_panel = scroll
    e.split.addWidget(scroll)
    e.split.addWidget(document)
    e.split.addWidget(e.pages)
    e.split.setChildrenCollapsible(False)
    e.split.setStretchFactor(1, 1)
    e.split.setSizes([266, 870, 170])
    e.pages.setVisible(owner.settings.value('pageNavigation', False, type=bool))
    e.open_tool_category(0)
    hide_tools()
    e.refresh()

def fit_page(e):
    bounds = e.doc.pdf[e.page].rect
    viewport = e.canvas.viewport()
    e.scale = max(.1, min((viewport.width()-90)/bounds.width,
                          (viewport.height()-50)/bounds.height))
    e.render()


def fit_width(e):
    e.scale=max(.1,min(3,(e.canvas.viewport().width()-38)/e.doc.pdf[e.page].rect.width));e.render()

def metadata(e):
    d=QDialog(e);d.setWindowTitle('Edit metadata');l=QFormLayout(d);fields={}
    for name,title in [('title','Title'),('author','Author'),('subject','Subject'),('keywords','Keywords')]:
        fields[name]=QLineEdit(e.doc.pdf.metadata.get(name) or '');l.addRow(title,fields[name])
    b=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);l.addRow(b);b.accepted.connect(d.accept);b.rejected.connect(d.reject)
    if d.exec()==QDialog.Accepted:
        m=dict(e.doc.pdf.metadata);m.update({k:v.text() for k,v in fields.items()});e.mutate(lambda pdf:pdf.set_metadata(m))

def split_pdf(e):
    count,ok=QInputDialog.getInt(e,'Split PDF','Pages per file',1,1,len(e.doc.pdf))
    if not ok:return
    folder=QFileDialog.getExistingDirectory(e,'Destination folder')
    if not folder:return
    targets = e.doc.split(folder, count)
    e.owner.statusBar().showMessage(f'{len(targets)} PDF files saved')

def compare(e):
    import difflib
    path,_=QFileDialog.getOpenFileName(e,'Compare text','','PDF (*.pdf)')
    if not path:return
    with fitz.open(path) as other:
        a='\n'.join(p.get_text() for p in e.doc.pdf).splitlines();b='\n'.join(p.get_text() for p in other).splitlines()
    diff='\n'.join(difflib.unified_diff(a,b,fromfile='Current',tofile=Path(path).name))
    d=QDialog(e);d.setWindowTitle('Text comparison');d.resize(750,550);l=QVBoxLayout(d);t=QPlainTextEdit(diff or 'No text differences.');t.setReadOnly(True);l.addWidget(t);d.exec()

class SignaturePad(QWidget):
    def __init__(self):
        super().__init__();self.setMinimumSize(540,200);self.strokes=[];self.setAutoFillBackground(True)
    def mousePressEvent(self,event):self.strokes.append([event.position()]);self.update()
    def mouseMoveEvent(self,event):
        if event.buttons()&Qt.LeftButton and self.strokes:self.strokes[-1].append(event.position());self.update()
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),QColor('white'));self.draw(p);p.end()
    def draw(self,p):
        p.setRenderHint(QPainter.Antialiasing);p.setPen(QPen(QColor('#172333'),2.5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        for stroke in self.strokes:
            for a,b in zip(stroke,stroke[1:]):p.drawLine(a,b)
    def image(self):
        from PySide6.QtGui import QImage
        im=QImage(self.size(),QImage.Format_ARGB32);im.fill(Qt.transparent);p=QPainter(im);self.draw(p);p.end();return im

def signature(e):
    d=QDialog(e);d.setWindowTitle('Draw signature');l=QVBoxLayout(d);pad=SignaturePad();l.addWidget(pad)
    l.addWidget(button('Clear',lambda:(pad.strokes.clear(),pad.update())))
    b=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);l.addWidget(b);b.accepted.connect(d.accept);b.rejected.connect(d.reject)
    if d.exec()==QDialog.Accepted and any(len(s)>1 for s in pad.strokes):
        e.canvas.signature_strokes = [stroke for stroke in pad.strokes if len(stroke) > 1]
        e.choose_mode('Select')
        e.canvas.setFocus()
        e.owner.statusBar().showMessage('Click the page to place your signature. Drag it to reposition.', 8000)

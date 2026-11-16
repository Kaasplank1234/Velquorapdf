"""OCR runs as a child process; MuPDF is never invoked in a GUI worker thread."""
import sys,json,subprocess,tempfile
from pathlib import Path
from PySide6.QtCore import QThread,Signal

class OCRWorker(QThread):
    completed=Signal(bytes)
    failed=Signal(str)
    progress=Signal(int)
    def __init__(self,data,language,preserve_pages=False,repeat=False,page_index=None):
        super().__init__();self.data=data;self.language=language;self.preserve_pages=preserve_pages;self.repeat=repeat;self.page_index=page_index
    def run(self):
        try:
            with tempfile.TemporaryDirectory(prefix='velqora-ocr-') as temp:
                root=Path(temp);(root/'input.pdf').write_bytes(self.data);(root/'request.json').write_text(json.dumps({'language':self.language,'preserve_pages':self.preserve_pages,'repeat':self.repeat,'page_index':self.page_index}))
                command=[sys.executable]
                if not getattr(sys,'frozen',False):command.append(str(Path(__file__).with_name('main.py')))
                command+=['--velqora-worker',temp]
                with (root/'stderr.log').open('w') as log:
                    creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                    process=subprocess.Popen(command,stdout=log,stderr=log,creationflags=creation_flags);previous=0
                    while process.poll() is None:
                        if self.isInterruptionRequested():
                            process.terminate()
                            try:
                                process.wait(timeout=.7)
                            except subprocess.TimeoutExpired:
                                process.kill()
                                process.wait()
                            return
                        if (root/'progress').exists():
                            lines=(root/'progress').read_text().splitlines()
                            if len(lines)>previous and lines[-1].isdigit():self.progress.emit(int(lines[-1]));previous=len(lines)
                        self.msleep(100)
                    if process.returncode:raise RuntimeError((root/'error.txt').read_text() if (root/'error.txt').exists() else (root/'stderr.log').read_text()[-2000:])
                if not self.isInterruptionRequested():
                    self.completed.emit((root/'output.pdf').read_bytes())
        except Exception as ex:self.failed.emit(str(ex))

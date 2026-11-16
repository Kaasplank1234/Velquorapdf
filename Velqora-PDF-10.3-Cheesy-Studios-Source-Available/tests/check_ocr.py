"""Optional integration test: requires local Tesseract + eng traineddata."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import fitz
from advanced import OCRWorker
from PySide6.QtCore import QCoreApplication
app=QCoreApplication([])
d=fitz.open();p=d.new_page();p.insert_text((60,150),'OFFLINE OCR TEST',fontsize=28)
scan=fitz.open();s=scan.new_page();s.insert_image(s.rect,stream=p.get_pixmap(dpi=150).tobytes('png'))
worker=OCRWorker(scan.tobytes(),'eng'); results=[]; errors=[]
worker.completed.connect(lambda data:results.append(data));worker.failed.connect(lambda error:errors.append(error))
worker.run();app.processEvents()
assert not errors, errors
assert results
result=fitz.open(stream=results[0],filetype='pdf')
assert 'OFFLINE OCR TEST' in result[0].get_text(),result[0].get_text()
print('OCR_SCANNED_IMAGE_TO_SEARCHABLE_PDF_OK')

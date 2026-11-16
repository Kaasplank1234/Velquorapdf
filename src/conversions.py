"""Minimal standards-based text DOCX export. No promise of layout preservation."""
from zipfile import ZipFile,ZIP_DEFLATED
from xml.sax.saxutils import escape

def export_docx(pdf,path):
    body=[]
    for n,page in enumerate(pdf):
        if n:body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        for line in page.get_text().splitlines():body.append('<w:p><w:r><w:t xml:space="preserve">'+escape(line)+'</w:t></w:r></w:p>')
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml','<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join(body)+'<w:sectPr/></w:body></w:document>')

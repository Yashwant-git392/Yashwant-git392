#!/usr/bin/env python3
"""Basic structural checks for all PDF and Word companion files."""
from pathlib import Path
from zipfile import ZipFile
import re

from docx import Document
import pymupdf
from build_report import INDEX_ITEMS

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / 'report' / 'CampusShikayatSetu_MCA-Mini-Project_Report.docx'


def main():
    pdfs = sorted(ROOT.rglob('*.pdf'))
    assert pdfs
    for pdf in pdfs:
        word = pdf.with_suffix('.docx')
        assert word.is_file(), f'Missing Word companion: {word}'
        assert ZipFile(word).testzip() is None, word
        Document(word)  # valid editable package
    doc = Document(REPORT)
    assert len(doc.sections) == 2
    for section in doc.sections:
        for actual, expected in ((section.left_margin.inches, 2), (section.right_margin.inches, 1.5),
                                 (section.top_margin.inches, 2), (section.bottom_margin.inches, 1.5)):
            assert abs(actual - expected) < .01
    paragraphs = [p.text for p in doc.paragraphs]
    text = ' '.join(paragraphs + [cell.text for table in doc.tables for row in table.rows for cell in row.cells])
    for forbidden in ('github', 'review 3', 'review schedule', 'draft:', 'before final submission'):
        assert forbidden not in text.lower(), forbidden
    assert len(doc.inline_shapes) == 48  # logo + all 47 numbered figures
    assert text.count('Description:') == 47
    for number in ['1.1'] + [f'3.1{c}' for c in 'abc'] + [f'3.2{c}' for c in 'abcd'] + [f'3.3{c}' for c in 'ab'] + [f'3.4{c}' for c in 'abcde'] + [f'3.{n}' for n in range(5, 12)] + [f'10.{n}' for n in range(1, 26)]:
        assert re.search(r'Figure ' + re.escape(number) + r'(?![\da-z])', text), number
    with ZipFile(REPORT) as z:
        xml = z.read('word/document.xml').decode()
        assert xml.count('PAGEREF ') == len(INDEX_ITEMS)
        assert xml.count('<w:bookmarkStart ') == len(INDEX_ITEMS)
        assert xml.count('w:type="page"') >= 2
        assert 'w:updateFields' in z.read('word/settings.xml').decode()
    diagram_pdf = ROOT / 'report' / 'Campus_Shikayat_Setu_Use_Case_Diagrams.pdf'
    diagram_doc = Document(diagram_pdf.with_suffix('.docx'))
    assert len(diagram_doc.inline_shapes) == len(pymupdf.open(diagram_pdf)) == 4
    print(f'Validated {len(pdfs)} PDF/DOCX pairs, {len(doc.inline_shapes)-1} report figures and {len(INDEX_ITEMS)} page-reference fields.')


if __name__ == '__main__':
    main()

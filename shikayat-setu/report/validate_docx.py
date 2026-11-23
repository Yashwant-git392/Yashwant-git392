#!/usr/bin/env python3
"""Basic structural checks for all PDF and Word companion files."""
from pathlib import Path
from zipfile import ZipFile
import re

from docx import Document
import pymupdf
from build_report import INDEX_ITEMS, LEFT, RIGHT, TOP, BOTTOM, OFFICIAL_FRONT

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
    front, body = doc.sections
    assert all(abs(m.mm) < .1 for m in (front.left_margin, front.right_margin, front.top_margin, front.bottom_margin))
    for section in (body,):
        for actual, expected in ((section.left_margin.mm, LEFT), (section.right_margin.mm, RIGHT),
                                 (section.top_margin.mm, TOP), (section.bottom_margin.mm, BOTTOM)):
            assert abs(actual - expected) < .1
    paragraphs = [p.text for p in doc.paragraphs]
    front_images = list(doc.inline_shapes)[:4]
    assert [shape._inline.docPr.get('descr') for shape in front_images] == [f'Official supplied page {i}' for i in range(1,5)]
    assert all(doc.paragraphs[i].paragraph_format.page_break_before == (i > 0) for i in range(4))
    assert 'CHAPTER 1' in paragraphs[5]
    assert abs(doc.styles['Normal'].paragraph_format.line_spacing - 1.5) < .01
    text = ' '.join(paragraphs + [cell.text for table in doc.tables for row in table.rows for cell in row.cells])
    for forbidden in ('github', 'review 3', 'review schedule', 'draft:', 'before final submission'):
        assert forbidden not in text.lower(), forbidden
    assert len(doc.inline_shapes) == 51  # four supplied pages + 47 report figures
    assert text.count('Description:') == 47
    # The document requests an explicit page break before each screenshot:
    # on the image for chapter 3, or on the corresponding manual heading.
    image_starts = 0
    manual_starts = 0
    for i, paragraph in enumerate(doc.paragraphs):
        if re.match(r'Figure 3\.(?:7|8|9|10|11)(?!\d)', paragraph.text):
            assert i > 0 and doc.paragraphs[i-1].paragraph_format.page_break_before, paragraph.text
            image_starts += 1
        if re.match(r'10\.3\.\d+\s', paragraph.text):
            assert paragraph.paragraph_format.page_break_before, paragraph.text
            manual_starts += 1
    assert image_starts == 5 and manual_starts == 25
    for number in ['1.1'] + [f'3.1{c}' for c in 'abc'] + [f'3.2{c}' for c in 'abcd'] + [f'3.3{c}' for c in 'ab'] + [f'3.4{c}' for c in 'abcde'] + [f'3.{n}' for n in range(5, 12)] + [f'10.{n}' for n in range(1, 26)]:
        assert re.search(r'Figure ' + re.escape(number) + r'(?![\da-z])', text), number
    with ZipFile(REPORT) as z:
        xml = z.read('word/document.xml').decode()
        assert xml.count('PAGEREF ') == 0  # official blank index is a page image
        assert xml.count('<w:bookmarkStart ') == len(INDEX_ITEMS)
        assert 'w:updateFields' in z.read('word/settings.xml').decode()
    official_doc = Document(OFFICIAL_FRONT.with_suffix('.docx'))
    assert len(official_doc.inline_shapes) == 4
    diagram_pdf = ROOT / 'report' / 'Campus_Shikayat_Setu_Use_Case_Diagrams.pdf'
    diagram_doc = Document(diagram_pdf.with_suffix('.docx'))
    assert len(diagram_doc.inline_shapes) == len(pymupdf.open(diagram_pdf)) == 4
    print(f'Validated {len(pdfs)} PDF/DOCX pairs, four official page images and {len(doc.inline_shapes)-4} report figures.')


if __name__ == '__main__':
    main()

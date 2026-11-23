"""Render the supplied image-only official pages into Word documents.

The PDF source is sanitized only for document metadata; the visible pages are
preserved. Word receives page images because the upload has no text layer.
"""
from io import BytesIO
from pathlib import Path
import pymupdf
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

HERE = Path(__file__).resolve().parent
OFFICIAL = HERE / 'reference' / 'PROJECT REPORT Sequence Yashwant.pdf'


def add_official_pages(doc):
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Mm(0)
    with pymupdf.open(OFFICIAL) as source:
        if len(source) != 4:
            raise ValueError('The supplied official front matter must have four pages.')
        for index, page in enumerate(source):
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5), alpha=False)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.page_break_before = index > 0
            p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1
            run = p.add_run()
            run.font.size = Pt(1)
            picture = run.add_picture(BytesIO(pix.tobytes('png')), width=Mm(205))
            picture._inline.docPr.set('descr', f'Official supplied page {index+1}')


def build_reference_docx():
    doc = Document()
    add_official_pages(doc)
    doc.core_properties.title = 'Supplied official front matter — Campus Shikayat Setu'
    doc.save(OFFICIAL.with_suffix('.docx'))


if __name__ == '__main__':
    build_reference_docx()

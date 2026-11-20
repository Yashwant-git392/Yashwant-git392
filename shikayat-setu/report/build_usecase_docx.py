#!/usr/bin/env python3
"""Make a Word companion to the four-page landscape use-case diagram PDF."""
from io import BytesIO
from pathlib import Path

import pymupdf
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

HERE = Path(__file__).resolve().parent
PDF = HERE / 'Campus_Shikayat_Setu_Use_Case_Diagrams.pdf'
OUT = PDF.with_suffix('.docx')


def main():
    pdf = pymupdf.open(PDF)
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = Mm(297), Mm(210)
    section.left_margin = section.right_margin = Mm(27)
    section.top_margin = section.bottom_margin = Mm(11)
    labels = ['Student', 'Department officer', 'Administrator', 'Public visitor']
    assert len(pdf) == len(labels)
    for i, label in enumerate(labels):
        page = pdf[i]
        images = page.get_images(full=True)
        assert len(images) == 1
        image = pdf.extract_image(images[0][0])['image']
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1
        p.paragraph_format.page_break_before = i > 0
        run = p.add_run(); run.font.size = Pt(1)
        picture = run.add_picture(BytesIO(image), width=Mm(242.7))
        picture._inline.docPr.set('descr', f'{label} use-case diagram')
    doc.core_properties.title = 'Campus Shikayat Setu — Use-Case Diagrams'
    doc.save(OUT)
    print('Word diagrams:', OUT)


if __name__ == '__main__':
    main()

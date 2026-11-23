#!/usr/bin/env python3
"""Build an editable Word version from the report's shared content functions.

The supplied image-only official pages are inserted as images. The remaining
report text and tables are editable; Word computes pagination itself.
"""
from pathlib import Path
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor
from PIL import Image

import build_report as source
from official_front import add_official_pages, build_reference_docx

OUT = source.REPORT_DIR / 'CampusShikayatSetu_MCA-Mini-Project_Report.docx'
NAVY = RGBColor(22, 36, 61)
GOLD = RGBColor(190, 146, 47)
CONTENT_MM = source.CONTENT_W


def style_run(run, size=13, bold=False, color=None):
    run.font.name = 'Times New Roman'
    run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    return run


def keep(paragraph, next_=False):
    paragraph.paragraph_format.keep_together = True
    paragraph.paragraph_format.keep_with_next = next_


def field(paragraph, instruction, cached='—'):
    run = paragraph.add_run()
    style_run(run)
    begin = OxmlElement('w:fldChar'); begin.set(qn('w:fldCharType'), 'begin')
    begin.set(qn('w:dirty'), 'true')
    text = OxmlElement('w:instrText'); text.set(qn('xml:space'), 'preserve'); text.text = ' ' + instruction + ' '
    separate = OxmlElement('w:fldChar'); separate.set(qn('w:fldCharType'), 'separate')
    value = OxmlElement('w:t'); value.text = cached
    end = OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'), 'end')
    for element in (begin, text, separate, value, end):
        run._r.append(element)


def bookmark_name(key):
    return 'r_' + re.sub('[^a-zA-Z0-9_]', '_', key)


def shade(cell, color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), color); tc_pr.append(shd)


class DocxReport:
    def __init__(self):
        self.doc = Document()
        self.bookmark_id = 0
        self.expected_keys = {key for _, _, key in source.INDEX_ITEMS if key != 'certificate'}
        self.first_body_heading = True
        self.written_keys = set()
        normal = self.doc.styles['Normal']
        normal.font.name = 'Times New Roman'
        normal._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
        normal.font.size = Pt(13)
        normal.paragraph_format.line_spacing = 1.5
        normal.paragraph_format.space_after = Pt(7)
        sec = self.doc.sections[0]
        self.section_layout(sec)
        settings = self.doc.settings._element
        update = OxmlElement('w:updateFields'); update.set(qn('w:val'), 'true'); settings.append(update)
        self.doc.core_properties.title = 'Campus Shikayat Setu — Mini Project Report'
        self.doc.core_properties.author = 'Yashwant Santosh Ahire'

    def section_layout(self, sec):
        sec.page_width, sec.page_height = Mm(210), Mm(297)
        sec.left_margin, sec.right_margin = Mm(source.LEFT), Mm(source.RIGHT)
        sec.top_margin, sec.bottom_margin = Mm(source.TOP), Mm(source.BOTTOM)
        sec.header_distance, sec.footer_distance = Mm(14), Mm(14)

    def mark(self, paragraph, key):
        if key not in self.expected_keys or key in self.written_keys:
            return
        self.bookmark_id += 1
        start = OxmlElement('w:bookmarkStart')
        start.set(qn('w:id'), str(self.bookmark_id)); start.set(qn('w:name'), bookmark_name(key))
        end = OxmlElement('w:bookmarkEnd'); end.set(qn('w:id'), str(self.bookmark_id))
        # Paragraph properties must remain the first child in WordprocessingML.
        paragraph._p.insert(1 if paragraph._p.pPr is not None else 0, start)
        paragraph._p.append(end)
        self.written_keys.add(key)

    def cover(self):
        # The uploaded PDF has no text layer; these four Word pages are
        # faithful page images, not editable transcription.
        add_official_pages(self.doc)
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        # Keep the section break tiny enough to remain after the fourth page.
        separator = self.doc.paragraphs[-1]
        separator.paragraph_format.space_before = separator.paragraph_format.space_after = Pt(0)
        separator.paragraph_format.line_spacing = Pt(1)
        style_run(separator.add_run(), 1)
        self.section_layout(sec)
        sec.header.is_linked_to_previous = False
        sec.footer.is_linked_to_previous = False
        header = sec.header.paragraphs[0]; header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        style_run(header.add_run('Campus Shikayat Setu'), color=NAVY)
        footer = sec.footer.paragraphs[0]
        footer.paragraph_format.tab_stops.add_tab_stop(Mm(CONTENT_MM - 4), WD_TAB_ALIGNMENT.RIGHT)
        style_run(footer.add_run('Dr. B. V. Hiray College of\t'), color=NAVY)
        field(footer, 'PAGE', '—')
        style_run(footer.add_run('\nManagement & Research Centre'), color=NAVY)

    def h1(self, key, text, kicker=None):
        p = self.doc.add_paragraph()
        p.paragraph_format.page_break_before = not self.first_body_heading
        self.first_body_heading = False
        p.paragraph_format.space_after = Pt(6)
        keep(p, True)
        if kicker:
            style_run(p.add_run(kicker.upper() + '\n'), 16, True, NAVY)
        style_run(p.add_run(source._plain(text)), 16, True, NAVY)
        self.mark(p, key)

    def h2(self, text, reserve=20, new_page=False):
        self.heading(text, 'Heading 2', new_page)

    def h3(self, text, reserve=16, new_page=False):
        self.heading(text, 'Heading 3', new_page)

    def heading(self, text, style, new_page=False):
        p = self.doc.add_paragraph(style=style); keep(p, True)
        p.paragraph_format.page_break_before = new_page
        p.paragraph_format.space_after = Pt(4)
        style_run(p.add_run(source._plain(text)), 15, True, NAVY)
        self.mark(p, 'section:' + text.split(' ', 1)[0])

    def p(self, text):
        p = self.doc.add_paragraph(); style_run(p.add_run(source._plain(text)))
        return p

    def bullets(self, items, indent=6):
        for item in items:
            self.p('•  ' + source._plain(item))

    def note(self, text):
        self.p(text)

    def figure(self, path, width_mm, caption_text, description=None, new_page=False):
        description = description or source.FIGURE_DESCRIPTIONS.get(Path(path).name)
        if not description:
            raise ValueError(f'No description for {path}')
        with Image.open(path) as image:
            width, height = image.size
        image_width = min(width_mm, CONTENT_MM, 190 * width / height)
        p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1
        p.paragraph_format.page_break_before = new_page
        keep(p, True); p.add_run().add_picture(str(path), width=Mm(image_width))
        p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(3); keep(p, True)
        style_run(p.add_run(source._plain(caption_text)), 13, True, NAVY)
        p = self.p('Description: ' + source._plain(description)); keep(p)

    def table(self, headers, rows, widths, **kwargs):
        if not rows:
            self.p('No records.')
            return
        headers, rows, widths_mm = source.table_layout(headers, rows, widths)
        table = self.doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        table.style = 'Table Grid'
        for col, width in zip(table.columns, widths_mm):
            col.width = Mm(width)
        # Word repeats the header when a table runs across pages.
        tr_pr = table.rows[0]._tr.get_or_add_trPr()
        tr_pr.append(OxmlElement('w:tblHeader'))
        for row_index, values in enumerate([headers] + rows):
            cells = table.rows[0].cells if row_index == 0 else table.add_row().cells
            for cell, value, width in zip(cells, values, widths_mm):
                cell.width = Mm(width); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
                if row_index == 0:
                    shade(cell, '16243D')
                p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
                style_run(p.add_run(source._plain(value)), 13, row_index == 0,
                          RGBColor(255,255,255) if row_index == 0 else None)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(0)

    def code(self, code_text, title=None):
        if title:
            self.h3(title)
        # Preserve whitespace and source lines as editable text.
        p = self.doc.add_paragraph(); p.paragraph_format.space_after = Pt(5)
        style_run(p.add_run(code_text))


def keep_subtopic_paragraphs_together(doc):
    """Word may split a group longer than a page; tables/figures break groups."""
    paragraphs = doc.paragraphs
    in_topic = False
    for index, p in enumerate(paragraphs):
        if p.style.name in ('Heading 2','Heading 3'):
            in_topic=True
            continue
        if not in_topic or index+1 >= len(paragraphs):
            continue
        next_p=paragraphs[index+1]
        # Only chain consecutive text paragraphs, never across a table, image,
        # or the next heading/chapter. Word can then pack short topics together.
        if p._p.getnext() is next_p._p and next_p.style.name not in ('Heading 2','Heading 3') and not p._p.xpath('.//w:drawing') and not next_p._p.xpath('.//w:drawing') and not next_p.paragraph_format.page_break_before:
            p.paragraph_format.keep_with_next=True
        if next_p.paragraph_format.page_break_before:
            in_topic=False


def main():
    pdf = DocxReport()
    pdf.cover()
    for fn in (source.ch1, source.ch2, source.ch3, source.ch4, source.ch5,
               source.ch6, source.ch7, source.ch8, source.ch9, source.ch10,
               source.appa, source.appb, source.appc):
        fn(pdf)
    keep_subtopic_paragraphs_together(pdf.doc)
    assert pdf.written_keys == pdf.expected_keys, ('Missing bookmarks', pdf.expected_keys-pdf.written_keys)
    pdf.doc.save(OUT)
    build_reference_docx()
    print('Editable report:', OUT)


if __name__ == '__main__':
    main()

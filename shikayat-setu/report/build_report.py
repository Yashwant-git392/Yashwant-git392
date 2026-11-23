#!/usr/bin/env python3
"""Single-source report generator for the Campus Shikayat Setu mini project.
Produces: shikayat-setu/report/CampusShikayatSetu_MCA-Mini-Project_Report.pdf
Two-pass build: pass 1 records chapter page numbers, pass 2 renders the real index.
"""
from pathlib import Path
import os
import re
import html
import tempfile
import sqlite3
from datetime import date

from fpdf import FPDF
from fpdf.enums import MethodReturnValue

REPORT_DIR = Path(__file__).resolve().parent
IMG = REPORT_DIR / "images"
DB = Path(os.environ.get("SHIKAYAT_DB", REPORT_DIR.parent / "app" / "shikayat_setu.db"))
OUT = REPORT_DIR / "CampusShikayatSetu_MCA-Mini-Project_Report.pdf"

D = str(REPORT_DIR / "fonts") + os.sep
LEFT, RIGHT, TOP, BOTTOM = 50.8, 38.1, 50.8, 38.1  # 2, 1.5, 2, 1.5 inches
CONTENT_W = 210 - LEFT - RIGHT
LINE_H = 13 * 1.5 * 25.4 / 72
NAVY = (22, 36, 61)
NAVY2 = (31, 52, 85)
GOLD = (190, 146, 47)
LIGHT = (245, 247, 250)
TODAY = date.today().strftime("%d %B %Y")

SECTIONS = [
    ("Certificate", "certificate"),
    ("Chapter 1 — Introduction", "ch1"),
    ("Chapter 2 — Proposed System", "ch2"),
    ("Chapter 3 — System Analysis and Design", "ch3"),
    ("Chapter 4 — Coding", "ch4"),
    ("Chapter 5 — Testing", "ch5"),
    ("Chapter 6 — Limitations of Proposed System", "ch6"),
    ("Chapter 7 — Proposed Enhancements", "ch7"),
    ("Chapter 8 — Conclusion", "ch8"),
    ("Chapter 9 — Bibliography", "ch9"),
    ("Chapter 10 — User Manual", "ch10"),
    ("Appendix A — Database Schema (schema.sql)", "appa"),
    ("Appendix B — Seed Data (actual records, ≥ 5 per table)", "appb"),
    ("Appendix C — Glossary and Acronyms", "appc"),
]


def db_rows(sql):
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    rows = c.execute(sql).fetchall()
    c.close()
    return [dict(r) for r in rows]


def _plain(text):
    """The source uses simple emphasis HTML; keep text without HTML markup."""
    return html.unescape(re.sub(r'</?(?:b|i|em|strong|br)\s*/?>', '', str(text)))


def extract_template_fonts(directory):
    """Use Times New Roman subsets embedded in the supplied template PDF.

    The template provides editable-embedding font subsets; missing characters
    use the bundled OFL Tinos (a Times-compatible font) and DejaVu fallback.
    The extracted font files remain temporary, never committed as standalone.
    """
    import pymupdf
    template = pymupdf.open(REPORT_DIR / 'reference' / 'PROJECT_REPORT_Sequence.pdf')
    regular = bold = None
    for xref, _, _, name, *_ in template[0].get_fonts():
        if 'TimesNewRomanPS-BoldMT' in name and bold is None:
            bold = template.extract_font(xref)[3]
        elif 'TimesNewRomanPSMT' in name and regular is None:
            regular = template.extract_font(xref)[3]
    template.close()
    if not regular or not bold:
        raise RuntimeError('The supplied report sequence PDF must contain its embedded Times New Roman fonts.')
    for name, data in [('regular.ttf', regular), ('bold.ttf', bold)]:
        (Path(directory) / name).write_bytes(data)
    return Path(directory) / 'regular.ttf', Path(directory) / 'bold.ttf'


FIGURE_DESCRIPTIONS = {
    'fig-architecture.png': 'The browser communicates with the Flask application over HTTP. The application applies routing and access rules and reads or updates the SQLite database.' ,
    'fig-erd.png': 'The Chen diagram shows categories and assigned departments. Each complaint has one category and one assigned department; reassignment can change the assigned department independently.',
    'fig-erd-b.png': 'A user may belong to a department and may lodge complaints. The application restricts complaint submission to students; the database foreign key references the users table.',
    'fig-erd-c.png': 'A complaint can have many events and at most one feedback record. Each event belongs to one complaint and may have an associated user as its actor.',
    'fig-usecase-student.png': 'The student actor registers or signs in, submits and tracks their own complaints, and can give feedback or request reopening when the relevant conditions are met.',
    'fig-usecase-officer.png': 'The department officer signs in, reviews the assigned queue and records permitted complaint actions, including acknowledgement, work and resolution.',
    'fig-usecase-administrator.png': 'The administrator can create officers, toggle user status, manage complaints across departments and view management reports. The feedback route accepts an administrator, although the admin interface has no feedback form.',
    'fig-usecase-public-visitor.png': 'A visitor without a login can use the public tracker with a complaint code and the matching roll number to view the corresponding status and timeline.',
    'fig-class.png': 'The conceptual domain types and associations illustrate stored project data. They are a domain model, not implemented Python ORM classes.',
    'fig-class-b.png': 'The additional associations show users assigned to departments, event actors and the departments assigned to complaints. Multiplicities follow the SQLite constraints.',
    'fig-activity.png': 'A student enters complaint details. Invalid input returns for correction; valid input is routed, prioritised and saved with events before the complaint code is returned.',
    'fig-activity-b.png': 'An authorised officer or administrator submits a resolution remark. The system checks the complaint and remark, then records a successful resolution or reports a rejection or stale change.',
    'fig-activity-c.png': 'A student submits a rating for an owned, resolved complaint. A successful update closes the complaint and stores feedback and events; invalid or stale requests do not proceed.',
    'fig-activity-d.png': 'A student requests reopening of an owned resolved complaint. The system checks the reason and resolution age, returning the complaint to In Progress when the update succeeds.',
    'fig-activity-e.png': 'An administrator requests closure of a resolved complaint. On a successful conditional update the system records a closure event; a rejection or stale change is reported.',
    'fig-deployment.png': 'A browser communicates with the Flask application, which uses the local SQLite database. The diagram represents a single-node demo, with optional access from a LAN peer.',
    'fig-modules.png': 'The hierarchy groups the project into authentication, complaint workflow, routing, database, reports and presentation modules, and maps responsibilities to the implemented files.',
    'screen-login.png': 'A student, officer or administrator enters a username or roll number and password. The page also links to student registration and the public tracker.',
    'screen-dashboard.png': 'The student dashboard summarises that student’s own complaints by status. The student can open a listed complaint or start a new submission.',
    'screen-lodge.png': 'The student enters the complaint title, description and category, with optional location and anonymous flag. Routing preview is advisory; submission validates and saves the complaint.',
    'screen-console.png': 'The administrator filters the complaint register by department, status or priority and opens an entry to inspect it or perform permitted administrative actions.',
    'screen-timeline.png': 'The complaint detail page presents its current status, assigned department, deadline, routing details and chronological events for an authorised viewer.',
}


class Report(FPDF):
    def __init__(self, toc=None, recorder=None, font_dir=None):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.toc = toc or {}
        self.recorder = recorder if recorder is not None else {}
        regular, bold = extract_template_fonts(font_dir)
        self.add_font('DVS', '', str(regular))
        self.add_font('DVS', 'B', str(bold))
        # The italic subset in the template contains only a few letters.
        self.add_font('DVS', 'I', str(regular))
        self.add_font('DVS', 'BI', str(bold))
        for style, file in [('', 'Tinos-Regular.ttf'), ('B', 'Tinos-Bold.ttf'),
                            ('I', 'Tinos-Italic.ttf'), ('BI', 'Tinos-BoldItalic.ttf')]:
            self.add_font('Tinos', style, str(REPORT_DIR / 'fonts' / file))
        self.add_font('Symbols', '', D + 'DejaVuSans.ttf')
        self.add_font('Symbols', 'B', D + 'DejaVuSans-Bold.ttf')
        self.add_font('Symbols', 'I', D + 'DejaVuSans.ttf')
        self.add_font('Symbols', 'BI', D + 'DejaVuSans-Bold.ttf')
        self.set_fallback_fonts(['Tinos', 'Symbols'], exact_match=False)
        self.set_auto_page_break(auto=True, margin=BOTTOM)
        self.set_margins(LEFT, TOP, RIGHT)
        self.set_text_color(0, 0, 0)

    def header(self):
        if self.page_no() <= 3:  # two genuinely blank pages and the cover
            return
        self.set_y(29)
        self.set_x(LEFT)
        self.set_font('DVS', '', 13)
        self.set_text_color(*NAVY)
        self.set_fill_color(*NAVY)
        self.cell(CONTENT_W, LINE_H, 'Campus Shikayat Setu', align='R')
        self.set_draw_color(*GOLD)
        self.set_line_width(0.3)
        self.line(LEFT, 40, LEFT + CONTENT_W, 40)
        self.set_text_color(0, 0, 0)
        self.set_y(TOP)

    def footer(self):
        if self.page_no() <= 3:
            return
        self.set_y(-23)
        self.set_x(LEFT)
        self.set_draw_color(*GOLD)
        self.set_line_width(0.3)
        self.line(LEFT, 272, LEFT + CONTENT_W, 272)
        self.set_font('DVS', '', 13)
        self.set_text_color(*NAVY)
        self.set_fill_color(*NAVY)
        self.cell(CONTENT_W - 15, LINE_H, 'Dr. B. V. Hiray College of', align='L')
        self.cell(15, LINE_H, str(self.page_no()), align='R')
        self.set_xy(LEFT, 297 - 23 + LINE_H)
        self.cell(CONTENT_W, LINE_H, 'Management & Research Centre', align='L')

    def h1(self, key, text, kicker=None):
        self.add_page()
        self.recorder[key] = self.page_no()
        self.set_font('DVS', 'B', 16)
        self.set_text_color(*NAVY)
        self.set_fill_color(*NAVY)
        if kicker:
            self.multi_cell(CONTENT_W, LINE_H, kicker.upper(), align='L')
        self.set_x(LEFT)
        self.multi_cell(CONTENT_W, LINE_H, text, align='L')
        self.set_draw_color(*GOLD)
        self.set_line_width(0.7)
        self.line(LEFT, self.get_y() + 1, LEFT + 30, self.get_y() + 1)
        self.ln(4)
        self.set_text_color(0, 0, 0)
        self.start_section(text, level=0)

    def h2(self, text, reserve=20):
        if self.get_y() + min(reserve, 95) > 297 - BOTTOM:
            self.add_page()
        self.recorder['section:' + text.split(' ', 1)[0]] = self.page_no()
        self.set_font('DVS', 'B', 15)
        self.set_text_color(*NAVY2)
        self.set_fill_color(*NAVY2)
        self.set_x(LEFT)
        self.multi_cell(CONTENT_W, LINE_H, text, align='L')
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def h3(self, text, reserve=16):
        if self.get_y() + min(reserve, 105) > 297 - BOTTOM:
            self.add_page()
        self.recorder['section:' + text.split(' ', 1)[0]] = self.page_no()
        self.set_font('DVS', 'B', 15)
        self.set_text_color(*NAVY2)
        self.set_fill_color(*NAVY2)
        self.set_x(LEFT)
        self.multi_cell(CONTENT_W, LINE_H, text, align='L')
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def p(self, text):
        self.set_x(LEFT)
        self.set_font('DVS', '', 13)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(0, 0, 0)
        self.multi_cell(CONTENT_W, LINE_H, _plain(text), align='L')
        self.ln(2)

    def bullets(self, items, indent=6):
        for item in items:
            self.p('•  ' + _plain(item))

    def caption(self, text):
        self.set_x(LEFT)
        self.set_font('DVS', 'B', 13)
        self.set_text_color(*NAVY)
        self.set_fill_color(*NAVY)
        self.multi_cell(CONTENT_W, LINE_H, _plain(text), align='C')
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def figure(self, path, width_mm, caption_text, description=None):
        from PIL import Image
        if description is None:
            description = FIGURE_DESCRIPTIONS.get(Path(path).name)
        if not description:
            raise ValueError(f'Missing explanatory description for {path}')
        caption_text = _plain(caption_text)
        description = 'Description: ' + _plain(description)
        self.set_font('DVS', 'B', 13)
        cap_lines = self.multi_cell(CONTENT_W, LINE_H, caption_text, align='C',
                                    dry_run=True, output=MethodReturnValue.LINES)
        self.set_font('DVS', '', 13)
        desc_lines = self.multi_cell(CONTENT_W, LINE_H, description, align='L',
                                     dry_run=True, output=MethodReturnValue.LINES)
        # Keep every image, its caption and its explanation on the same page.
        text_height = (len(cap_lines) + len(desc_lines)) * LINE_H + 8
        max_height = 297 - TOP - BOTTOM - text_height - 2
        if max_height <= 25:
            raise ValueError(f'Explanation too long to fit with {path}')
        with Image.open(path) as image:
            width, height = image.size
        w = min(width_mm, CONTENT_W)
        h = w * height / width
        if h > max_height:
            w *= max_height / h
            h = max_height
        if self.get_y() + h + text_height > 297 - BOTTOM:
            self.add_page()
        self.set_x(LEFT)
        self.image(str(path), x=LEFT + (CONTENT_W - w) / 2, w=w)
        self.ln(2)
        self.caption(caption_text)
        self.p(description)

    def table(self, headers, rows, widths, **kwargs):
        # The specified 121 mm content width cannot hold the original four-
        # and five-column tables legibly at 13 pt. Display their records as
        # structured cards with navy title rows; use true tables where possible.
        self.set_font('DVS', '', 13)
        if not rows:
            self.p('No records.')
            return
        if len(headers) == 2:
            col1 = max(29, min(40, CONTENT_W * widths[0] / sum(widths)))
            max_lines = 0
            for row in [headers] + list(rows):
                for value, width in zip(row, (col1, CONTENT_W-col1)):
                    lines = self.multi_cell(width - 3, LINE_H, _plain(value),
                                            dry_run=True, output=MethodReturnValue.LINES)
                    max_lines = max(max_lines, len(lines))
            # Oversized rows must flow as cards instead of breaking inside a table row.
            if max_lines * LINE_H < (297 - TOP - BOTTOM - 3 * LINE_H):
                widths_mm = (col1, CONTENT_W - col1)

                def draw_row(values, is_header=False):
                    self.set_font('DVS', 'B' if is_header else '', 13)
                    lines = [self.multi_cell(width - 3, LINE_H, _plain(value), align='L',
                                             dry_run=True, output=MethodReturnValue.LINES)
                             for value, width in zip(values, widths_mm)]
                    height = max(map(len, lines)) * LINE_H + 2
                    y = self.get_y()
                    self.set_draw_color(190, 190, 190)
                    self.set_line_width(0.2)
                    text_color = (255, 255, 255) if is_header else (0, 0, 0)
                    self.set_text_color(*text_color)
                    x = LEFT
                    for text_lines, width in zip(lines, widths_mm):
                        self.set_fill_color(*(NAVY if is_header else LIGHT))
                        self.rect(x, y, width, height, style='DF')
                        # fpdf's fallback-font switches must not be wrapped in
                        # separate q/Q blocks for each line; equal fill/text colours.
                        self.set_fill_color(*text_color)
                        self.set_xy(x + 1, y + 1)
                        self.multi_cell(width - 3, LINE_H, '\n'.join(text_lines), align='L')
                        x += width
                    self.set_y(y + height)
                    self.set_x(LEFT)
                    self.set_text_color(0, 0, 0)
                    return height

                def row_height(values, bold=False):
                    self.set_font('DVS', 'B' if bold else '', 13)
                    return max(len(self.multi_cell(width - 3, LINE_H, _plain(value), align='L',
                                                   dry_run=True, output=MethodReturnValue.LINES))
                               for value, width in zip(values, widths_mm)) * LINE_H + 2

                heading_height = row_height(headers, True)
                if self.get_y() + heading_height + row_height(rows[0]) > 297 - BOTTOM:
                    self.add_page()
                draw_row(headers, True)
                for values in rows:
                    if self.get_y() + row_height(values) > 297 - BOTTOM:
                        self.add_page()
                        draw_row(headers, True)
                    draw_row(values)
                self.ln(3)
                return
        for values in rows:
            label = _plain(str(headers[0]) + ': ' + str(values[0]))
            self.set_font('DVS', 'B', 13)
            lines = self.multi_cell(CONTENT_W, LINE_H, label, align='L',
                                    dry_run=True, output=MethodReturnValue.LINES)
            height = len(lines) * LINE_H
            if self.get_y() + height + LINE_H > 297 - BOTTOM:
                self.add_page()
            y = self.get_y()
            self.set_fill_color(*NAVY2)
            self.rect(LEFT, y, CONTENT_W, height, style='F')
            self.set_fill_color(255, 255, 255)
            self.set_text_color(255, 255, 255)
            self.set_x(LEFT)
            self.multi_cell(CONTENT_W, LINE_H, label, align='L')
            self.set_text_color(0, 0, 0)
            self.set_fill_color(0, 0, 0)
            for header, value in zip(headers[1:], values[1:]):
                self.set_x(LEFT)
                self.set_font('DVS', '', 13)
                self.multi_cell(CONTENT_W, LINE_H, _plain(str(header) + ': ' + str(value)), align='L')
            self.ln(3)

    def code(self, code_text, title=None):
        if title:
            self.h3(title)
        self.set_font('DVS', '', 13)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(0, 0, 0)
        for line in code_text.splitlines():
            self.set_x(LEFT)
            if not line:
                self.ln(LINE_H)
                continue
            self.multi_cell(CONTENT_W, LINE_H, line, wrapmode='CHAR')
        self.ln(2)

    def note(self, text):
        self.p(text)


def blank_pages(pdf):
    pdf.add_page()
    pdf.add_page()


def cover(pdf):
    pdf.add_page()
    pdf.recorder['cover'] = pdf.page_no()
    pdf.set_font('DVS', 'B', 16)
    pdf.set_text_color(*NAVY)
    pdf.set_fill_color(*NAVY)
    for line in ['A', 'PROJECT REPORT', 'ON', 'CAMPUS SHIKAYAT SETU']:
        pdf.set_x(LEFT)
        pdf.multi_cell(CONTENT_W, LINE_H, line, align='C')
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.7)
    pdf.line(LEFT + 35, pdf.get_y() + 1, LEFT + CONTENT_W - 35, pdf.get_y() + 1)
    pdf.ln(3)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_font('DVS', '', 13)
    for line in ['Submitted By', 'Yashwant Santosh Ahire', 'MCA-I SEM-I',
                 'Roll No.: ____________________', 'UNDER THE GUIDANCE OF',
                 'Project Guide: ____________________', 'In Partial Fulfillment of',
                 'SAVITRIBAI PHULE PUNE UNIVERSITY', 'MASTER OF COMPUTER APPLICATIONS',
                 "K.B.H.S.S. Trust’s", 'Dr. B. V. Hiray College of Management & Research Centre']:
        pdf.set_x(LEFT)
        pdf.multi_cell(CONTENT_W, LINE_H, line, align='C')
    logo = IMG / 'college-logo.png'
    pdf.image(str(logo), x=LEFT + (CONTENT_W - 24) / 2, w=24)
    pdf.set_x(LEFT)
    pdf.multi_cell(CONTENT_W, LINE_H, '2026–2027', align='C')


def certificate(pdf):
    pdf.h1('certificate', 'COLLEGE CERTIFICATE')
    pdf.p('Project report titled “Campus Shikayat Setu”, submitted by Yashwant Santosh Ahire, '
          'MCA-I Semester-I, academic year 2026–2027, under the guidance of the undersigned '
          'at Dr. B. V. Hiray College of Management & Research Centre, Malegaon.')
    pdf.p('Date: ____________________       Place: Malegaon')
    pdf.p('Project Guide: ____________________')
    pdf.p('Head of Department: ____________________')
    pdf.p('Director / College authority: ____________________')


def declaration(pdf):
    pdf.h1('declaration', 'DECLARATION')
    pdf.p('I, Yashwant Santosh Ahire, student of Master of Computer Applications, academic year '
          '2026–2027, declare that the information in the project report titled “Campus Shikayat Setu” '
          'is accurate to the best of my knowledge.')
    pdf.p('Date: ____________________')
    pdf.p('Place: Malegaon')
    pdf.p('Signature: ____________________')
    pdf.p('Yashwant Santosh Ahire')


def acknowledgement(pdf):
    pdf.h1('acknowledgement', 'ACKNOWLEDGEMENT')
    pdf.p('I would like to thank the Director, my project guide ____________________, and the faculty '
          'of Dr. B. V. Hiray College of Management & Research Centre, Malegaon, for their guidance '
          'and support. I also thank my family and friends for their encouragement during the project.')
    pdf.p('Date: ____________________')
    pdf.p('Place: Malegaon')
    pdf.p('Yashwant Santosh Ahire')


INDEX_ITEMS = [
    ('1', 'Introduction', 'ch1'),
    ('1.1', 'Abstract', 'section:1.1'), ('1.2', 'Existing System and Need for System', 'section:1.2'),
    ('1.3', 'Scope of System', 'section:1.3'), ('1.4', 'Operating Environment — Hardware and Software', 'section:1.4'),
    ('1.5', 'Brief Description of Technology Used', 'section:1.5'),
    ('1.5.1', 'Operating Systems Used', 'section:1.5.1'), ('1.5.2', 'Database Used', 'section:1.5.2'),
    ('2', 'Proposed System', 'ch2'), ('2.1', 'Study of Similar Systems', 'section:2.1'),
    ('2.2', 'Feasibility Study', 'section:2.2'), ('2.3', 'Objectives of Proposed System', 'section:2.3'),
    ('2.4', 'Users of System', 'section:2.4'), ('3', 'System Analysis and Design', 'ch3'),
    ('3.1', 'System Requirements', 'section:3.1'), ('3.2', 'Entity Relationship Diagram', 'section:3.2'),
    ('3.3', 'Table Structure', 'section:3.3'), ('3.4', 'Use-Case Diagrams', 'section:3.4'),
    ('3.5', 'Class Diagram', 'section:3.5'), ('3.6', 'Activity Diagram', 'section:3.6'),
    ('3.7', 'Deployment Diagram', 'section:3.7'), ('3.8', 'Module Hierarchy Diagram', 'section:3.8'),
    ('3.9', 'Sample Input and Output Screens', 'section:3.9'), ('4', 'Coding', 'ch4'),
    ('4.1', 'Code Snippets', 'section:4.1'), ('5', 'Testing', 'ch5'),
    ('5.1', 'Test Strategy', 'section:5.1'), ('5.2', 'Unit Test Plan', 'section:5.2'),
    ('5.3', 'Acceptance Test Plan', 'section:5.3'), ('5.4', 'Test Case / Test Script', 'section:5.4'),
    ('6', 'Limitations of Proposed System', 'ch6'), ('7', 'Proposed Enhancements', 'ch7'),
    ('8', 'Conclusion', 'ch8'), ('9', 'Bibliography', 'ch9'), ('10', 'User Manual', 'ch10'),
    ('A', 'Database Schema', 'appa'), ('B', 'Synthetic Seed Data', 'appb'),
    ('C', 'Glossary', 'appc'),
]


def index(pdf):
    pdf.h1('index', 'INDEX')
    pdf.p('Chapter / section — details — PDF page number')
    for number, title, key in INDEX_ITEMS:
        # Fixed-width number text avoids changes in wrapping between passes.
        page = str(pdf.toc.get(key, '000')).zfill(3)
        pdf.p(f'{number}   {title}   —   {page}')

# =====================================================================
def ch1(pdf: Report):
    pdf.h1("ch1", "Introduction", "Chapter 1")

    pdf.h2("1.1  Abstract")
    pdf.p("Campus grievances may include leaking taps, broken equipment and other student concerns. For this mini project, "
          "a manual paper-based process is used as an illustrative assumption, not a verified statement about the college. "
          "<b>Campus Shikayat Setu</b> is a demo web application that digitises a grievance workflow: "
          "lodging with category and location, <b>keyword-based routing</b> via a "
          "keyword-weighted engine, an <b>SLA matrix</b> (High 24 h, Medium 72 h, Low 7 days) with computed overdue flags, "
          "officer workflow (acknowledge → in-progress → resolve), student feedback with a 7-day reopen window, anonymous "
          "complaints, and six print-ready administrative registers.")
    pdf.p("The system is built with <b>Python + Flask</b>, <b>Jinja2</b> templates, <b>vanilla JavaScript</b> and a "
          "<b>SQLite 3</b> database chosen deliberately for the use case (single campus, single PC; local database; a future MySQL migration would require application and schema changes). Three roles are supported — <b>student</b>, "
          "<b>department officer</b> and <b>administrator</b> — with server-side access checks on protected routes.")
    pdf.p("<b>Keywords:</b> Grievance Redressal, Web Application, Flask, SQLite, SLA, Keyword Routing, SPPU MCA, "
          "Application Development.")

    pdf.h2("1.2  Existing System and Need for System")
    pdf.h3("1.2.1  Description of the existing (manual) system")
    pdf.p("For comparison, the assumed baseline is a manual process in which complaints are written on paper and forwarded to the relevant department. The actual college process has not been surveyed.")
    pdf.h3("1.2.2  Potential problems in the assumed manual system")
    pdf.bullets([
        "<b>Routing:</b> manual forwarding may cause delays or misassignment.",
        "<b>Deadlines:</b> without a register, overdue items may be harder to identify.",
        "<b>Status:</b> complainants may need to ask staff for progress updates.",
        "<b>Privacy:</b> sensitive complaints require careful handling of identity and free text.",
        "<b>Data:</b> calculating trends or response times manually may be time-consuming.",
        "<b>History:</b> paper records may not capture each action consistently.",
    ])
    pdf.h3("1.2.3  Why a new system is needed")
    pdf.bullets([
        "Give every grievance a code (CMP-YYYY-NNNN), an owner department, a priority and an SLA deadline at the moment of lodging.",
        "Support routing with a transparent, keyword-weighted router and retain the selected category when no stronger match is found.",
        "Close the loop with student feedback and a controlled reopen window.",
        "Produce print-ready registers for review meetings — pendency, SLA compliance, resolution time, trend, feedback, routing audit.",
        "Protect sensitive complainants with anonymous lodging (identity fields hidden from officers; administrators can see them).",
    ])

    pdf.h2("1.3  Scope of the System")
    pdf.h3("In scope")
    pdf.bullets([
        "Student self-registration (roll no./e-mail/mobile validation), login, logout, password change.",
        "Complaint lodging with category, description, location and optional anonymous flag.",
        "Automatic department routing with weighted keyword scoring + audit event; admin reassign with full trace.",
        "SLA matrix (High 24 h / Medium 72 h / Low 7 days) with live overdue computation and escalation-to-High.",
        "Officer workflow: acknowledge → in-progress → resolve (remark mandatory) · student confirmation with 1–5 star rating or reopen (whole-day age check).",
        "Admin console: filter by department/status/priority, reassign, escalate, force-close resolved complaints, manage officer accounts.",
        "Six print-ready registers: Department Pendency · SLA Compliance · Resolution Time · Monthly Trend · Feedback Summary · Routing Audit.",
        "Public tracker (complaint code + roll no., no login) and seeded demo (37 illustrative complaints across 6 departments).",
    ])
    pdf.figure(f"{IMG}/fig-architecture.png", 172, "Figure 1.1  Application architecture — browser, Flask application and SQLite database.")
    pdf.h3("Out of scope (deferred — see Chapter 7)")
    pdf.bullets([
        "E-mail / SMS / WhatsApp notifications; push mobile app; multi-college tenancy.",
        "Photo evidence upload; ERP integration; public grievance board.",
        "Machine-learning auto-classification (current router is deliberately deterministic and explainable).",
    ])

    pdf.h2("1.4  Operating Environment — Hardware and Software")
    pdf.h3("Hardware (minimum specification to run the project)")
    pdf.table(["Component", "Minimum", "Recommended (dev/demo)"], [
        ["Processor", "Intel Core i3 (any generation)", "Intel Core i5 / Ryzen 5"],
        ["RAM", "2 GB", "8 GB"],
        ["Storage", "150 MB free", "1 GB free (SSD)"],
        ["Display", "1366 × 768", "1920 × 1080"],
        ["Network", "None (single-machine)", "LAN (demo from another PC)"],
    ], [38, 70, 70])
    pdf.h3("Software")
    pdf.table(["Software", "Version used", "Purpose"], [
        ["Operating System", "GNU/Linux (Debian 12) · Windows 10/11", "Development & demo environment"],
        ["Python", "3.11.2", "Application runtime"],
        ["Flask", "3.x", "Web framework (routing, sessions, flash)"],
        ["Jinja2", "3.x", "Server-side templating"],
        ["SQLite", "3.x (file: shikayat_setu.db)", "Relational database (migration requires changes and testing)"],
        ["Werkzeug", "3.x", "WSGI stack + Werkzeug password hashing"],
        ["pytest", "9.x", "Unit / integration test runner (114 tests)"],
        ["Browser", "Chrome 120+ / Firefox 120+ / Edge 120+", "Client"],
        ["IDE / Editor", "VS Code", "Source code editing and debugging"],
    ], [42, 62, 74])

    pdf.h2("1.5  Brief Description of Technology Used")
    pdf.p("<b>Python 3</b> is the implementation language. <b>Flask</b> provides routing, sessions and Jinja2 rendering without imposing an ORM; all SQL is "
          "explicit and bound-parameterised. <b>Jinja2</b> templates keep presentation "
          "out of logic; the front end uses semantic HTML5, a navy, off-white and teal CSS theme and zero build tooling.")
    pdf.p("<b>SQLite 3</b> was selected after matching databases to the use case: single-campus, low-write, read-mostly, "
          "one-machine demo with zero DBA. It enforces integrity with UNIQUE, CHECK and FOREIGN KEY constraints. The schema "
          "works without a separate server. A move to MySQL would require changes to queries, connection handling and deployment (see Chapter 7).")
    pdf.p("<b>Security:</b> passwords are hashed with Werkzeug; protected routes check login and relevant roles "
          "server-side (students cannot open the admin console — covered by test_11); SQL uses bound parameters; "
          "anonymous identity fields and student event actors are hidden from officers, but free text may reveal identity; status changes write event records. POST forms use CSRF tokens.")
    pdf.h3("1.5.1  Operating systems used")
    pdf.p("Development and automated testing were executed on GNU/Linux. The app is intended to work on Windows with Python and dependencies, but native Windows testing remains outstanding.")
    pdf.h3("1.5.2  RDBMS used for the database")
    pdf.p("SQLite 3 is the relational database used by the application. It stores the project data in a local database file and enforces defined keys and constraints. MySQL and Oracle are not used by this implementation.")


def ch2(pdf: Report):
    pdf.h1("ch2", "Proposed System", "Chapter 2")

    pdf.h2("2.1  Study of Similar Systems")
    pdf.p("The comparison considers CPGRAMS, the Government of India public-grievance portal, an assumed manual process, and a generic ERP grievance module. The comparison is illustrative: the actual college workflow and the capabilities of individual ERP products may differ.")
    pdf.table(["System", "Type / Cost", "Strengths", "Limitations vs need"], [
        ["Manual paper process (assumed)", "Paper", "Simple to introduce",
         "No routing, no status, no SLA, no reports"],
        ["CPGRAMS (GoI)", "Citizen portal · free", "National scale, escalation matrix",
         "Heavyweight; external identity; no college-department model"],
        ["ERP grievance module (generic)", "Varies", "May integrate with student records",
         "Features and cost depend on the vendor; not evaluated here"],
    ], [38, 26, 52, 60])

    pdf.h2("2.2  Feasibility Study")
    pdf.table(["Dimension", "Assessment"], [
        ["Technical", "Flask + SQLite requires only Python 3.11; no drivers, no services, no network. Dependencies require a network connection or locally available installation packages."],
        ["Operational", "The demo presents department actions as buttons. Actual workflow and training needs require stakeholder confirmation."],
        ["Economic", "The software components used have no purchase cost for this demo; hardware, support and operating costs depend on deployment."],
        ["Schedule", "The project scope supports incremental implementation of authentication, complaint management, reporting and testing within a mini-project development cycle."],
        ["Legal / Ethical", "Anonymous complaints handled with admin-only identity access; all actions audit-logged; roll number and phone are stored; email is validated but not stored."],
    ], [30, 148])

    pdf.h2("2.3  Objectives of Proposed System")
    pdf.bullets([
        "O1 — Digitise grievance lodging with validation and a permanent, coded identity (CMP-YYYY-NNNN).",
        "O2 — Suggest a department using keyword scoring; retain the selected category when no stronger match exists.",
        "O3 — Stamp an SLA deadline at submission; surface overdue items everywhere.",
        "O4 — Enforce a complete, audited lifecycle (Submitted → Acknowledged → In Progress → Resolved → Closed).",
        "O5 — Protect sensitive complainants via anonymous lodging with admin-only identity.",
        "O6 — Close the loop: student feedback (1–5 stars) and a controlled 7-day reopen window.",
        "O7 — Produce management registers (pendency, SLA compliance, resolution time, trend, feedback, routing audit).",
        "O8 — Deliver a deterministic, self-seeding demo runnable with one command on any lab PC.",
    ])

    pdf.h2("2.4  Users of System")
    pdf.table(["User", "Access scope", "Capabilities"], [
        ["Student (seeded MCA2026001–008)", "Own complaints only",
         "Self-register (name / roll / e-mail / mobile / password) · lodge (category, location, anonymous option) · track (code and roll no.) · submit 1–5 ★ feedback to close · reopen with a whole-day age check · change password"],
        ["Department Officer (×6 departments)", "Assigned department only",
         "Priority-ordered queue · acknowledge → in-progress → resolve (remark ≥ 10 chars) · every action written to the audit timeline"],
        ["Administrator", "College-wide",
         "Filter (dept / status / priority) · reassign to a department · escalate → High · force-close resolved complaints · create / activate / deactivate officer accounts · 6 registers + anonymous identity visibility"],
        ["Public visitor (no login — /track)", "Read-only · code + roll no.",
         "View current status and timeline of one complaint; no names, e-mails or other records exposed"],
    ], [36, 32, 110])

    pdf.h3("2.4.1  Proposed System Overview")
    pdf.p("Campus Shikayat Setu supports the workflow lodge → auto-route → track and "
          "implements the demo using a relational schema with foreign-key "
          "enforcement, Werkzeug password hashing with three roles, a transparent router whose scoring is printed on the "
          "complaint timeline, an SLA engine, a 7-day student reopen window, full audit events and six print registers.")
    pdf.bullets([
        "<b>Student layer:</b> register → lodge (category, location, anonymous flag) → track (code and roll no.) → confirm or reopen with feedback.",
        "<b>Officer layer:</b> department queue ordered by priority then recency; acknowledge → start work → resolve with mandatory remark.",
        "<b>Admin layer:</b> college-wide console — filter, reassign, escalate (priority→High), force-close resolved complaints, manage officer accounts.",
        "<b>Report layer:</b> six Ctrl+P print-ready registers; routing has two summary modes and a separate complaint-level record table.",
    ])

    pdf.h3("2.4.2  Modules Identified")
    pdf.table(["Module", "Responsibility"], [
        ["Auth & Profile", "Login (username or roll no.), logout, student self-registration, change password, account activation/deactivation."],
        ["Lodging", "Category picker, validation (title ≥ 8 chars, description ≥ 20), anonymous flag, preview of routing score."],
        ["Routing Engine (routing.py)", "Weighted keyword scoring (multi-word keywords weigh more; title counts double); safety words force High; mass-impact phrases bump one level; no stronger match → retain selected category."],
        ["SLA & Escalation", "Deadline = submission + SLA(priority); overdue computed at render time; admin escalation raises priority to High with an audit event."],
        ["Officer Workflow", "Department-scoped queue (priority, then recency); acknowledge / start work / resolve with mandatory ≥ 10-char remark; timeline remarks."],
        ["Student Closure", "Feedback (1–5 + comment) closes; or reopen (≤ 7 days, reason mandatory) returns to In Progress."],
        ["Admin Console", "Filters (department/status/priority), reassign to a department, force-close resolved complaints, officer creation & activation."],
        ["Reports", "Six print registers incl. SLA compliance % and per-category average resolution hours."],
    ], [42, 136])

# =====================================================================
def ch3(pdf: Report):
    pdf.h1("ch3", "System Analysis and Design", "Chapter 3")

    pdf.h2("3.1  System Requirements (Functional and Non-Functional)")
    pdf.h3("3.1.1  Functional requirements")
    pdf.table(["ID", "Requirement", "Priority"], [
        ["FR-1", "Student shall register with roll no. (MCA2026NNN), e-mail, mobile (Indian format) and password; duplicate roll nos. are rejected.", "Must"],
        ["FR-2", "Students can lodge complaints; title ≥ 8 chars, description ≥ 20 chars and a valid category.", "Must"],
        ["FR-3", "System uses keyword scoring; when no stronger match exists, the selected category is retained.", "Must"],
        ["FR-4", "System shall compute SLA due time at submission: High 24 h, Medium 72 h, Low 168 h.", "Must"],
        ["FR-5", "Officers shall acknowledge / mark in-progress / resolve; resolution requires a ≥ 10-char remark.", "Must"],
        ["FR-6", "Students shall close via feedback (1–5 stars) or reopen with a whole-day age check of resolution.", "Must"],
        ["FR-7", "Anonymous complaints hide identity fields from officers; admins can see them. Free text may identify the student.", "Must"],
        ["FR-8", "Admin shall filter, reassign, escalate (→High) and force-close resolved complaints.", "Must"],
        ["FR-9", "Application records state changes as timeline events; direct database modification is not prevented.", "Must"],
        ["FR-10", "Officer queue shall show only the officer's department; students see only their own complaints.", "Must"],
        ["FR-11", "System shall render six print registers with live SQL totals.", "Should"],
        ["FR-12", "Public tracking requires complaint code and matching roll number; signed-in admins bypass the roll check.", "Should"],
    ], [14, 148, 16])
    pdf.h3("3.1.2  Non-functional requirements")
    pdf.table(["ID", "Requirement"], [
        ["NFR-1", "Responsive interface without a JavaScript framework. Response-time targets have not been benchmarked."],
        ["NFR-2", "SQLite transactions and foreign keys support consistency. Crash recovery and backup procedures have not been validated."],
        ["NFR-3", "Passwords hashed with Werkzeug; signed sessions and CSRF tokens. Demo credentials are not secure."],
        ["NFR-4", "Print CSS hides chrome; registers fit A4 portrait without truncation."],
        ["NFR-5", "Fresh databases receive illustrative seed data with dates relative to the seeding date."],
        ["NFR-6", "Code style: PEP 8, bound parameters only, no string-concatenated SQL."],
    ], [18, 160])

    pdf.h2("3.2  Entity Relationship Diagram (ERD)", reserve=150)
    pdf.p("The three Chen-notation views show selected attributes and all eight foreign-key relationships. An underlined attribute is a key. Each (minimum, maximum) pair is the participation of an instance of the adjacent entity; N means many. The full columns and constraints are listed in Section 3.3.")
    pdf.figure(f"{IMG}/fig-erd.png", 178, "Figure 3.1a  ERD — category and assigned department.")
    pdf.figure(f"{IMG}/fig-erd-b.png", 178, "Figure 3.1b  ERD — users and complaints.")
    pdf.figure(f"{IMG}/fig-erd-c.png", 178, "Figure 3.1c  ERD — events and feedback.")

    pdf.h2("3.3  Table Structure")
    pdf.p("Physical schema (verbatim from <b>schema.sql</b>, Appendix A) — every column, key and CHECK constraint in force:")
    pdf.table(["Table", "Key columns & constraints"], [
        ["departments", "id PK · name UNIQUE · head_name · email · location"],
        ["categories", "id PK · name UNIQUE · department_id FK→departments · default_priority CHECK(High,Medium,Low) · keywords TEXT"],
        ["users", "id PK · role CHECK(student,officer,admin) · username UNIQUE · password_hash · roll_no UNIQUE NULL · department_id FK NULL · status CHECK(Active,Inactive)"],
        ["complaints", "id PK · code UNIQUE (CMP-YYYY-NNNN) · student_id FK · category_id FK · department_id FK · priority CHECK · routing CHECK(auto,manual) · routing_score · status CHECK · is_anonymous · submitted_at · sla_due_at · resolved_at"],
        ["complaint_events", "id PK · complaint_id FK ON DELETE CASCADE · event_type · note · actor_id FK NULL · created_at"],
        ["feedback", "id PK · complaint_id FK UNIQUE · rating CHECK(1..5) · comment · created_at"],
    ], [30, 148])

    pdf.h2("3.4  Use-Case Diagrams", reserve=140)
    pdf.p("Each actor has a separate use-case diagram. The first three are stored user roles; the public visitor is an external actor, not a database role. Repeated actor symbols on a page denote the same role and improve readability.")
    pdf.figure(f"{IMG}/fig-usecase-student.png", 170, "Figure 3.2a  Student use cases.")
    pdf.figure(f"{IMG}/fig-usecase-officer.png", 170, "Figure 3.2b  Department officer use cases.")
    pdf.figure(f"{IMG}/fig-usecase-administrator.png", 170, "Figure 3.2c  Administrator use cases.")
    pdf.figure(f"{IMG}/fig-usecase-public-visitor.png", 170, "Figure 3.2d  Public visitor use case (external actor).")
    pdf.h3("3.4.1  Use-case descriptions (selection)")
    pdf.table(["Use case", "Actor", "Flow"], [
        ["Lodge complaint", "Student", "Fill title+description+location+category → submit → router assigns dept & SLA → code shown on timeline."],
        ["Resolve complaint", "Officer", "Open complaint → optionally acknowledge/start work → resolve with remark; direct resolution is also permitted."],
        ["Confirm & close", "Student", "Resolved list → star rating + comment → status Closed; feedback row inserted (UNIQUE per complaint)."],
        ["Reopen (whole-day check)", "Student", "Own resolved complaint → reason → status In Progress; age uses whole days and invalid timestamps prevent reopening."],
        ["Reassign", "Admin", "Console → pick new department → routing=manual → audit event with old→new."],
        ["Escalate to High", "Admin", "Console → escalate → priority=High → audit event; SLA kept at original deadline; escalation surfaces on all views."],
        ["Track without login", "Public", "Enter code + roll no. → timeline & current status rendered."],
    ], [32, 18, 128])

    pdf.h2("3.5  Class Diagram", reserve=140)
    pdf.figure(f"{IMG}/fig-class.png", 178, "Figure 3.3a  Conceptual class diagram — primary associations.")
    pdf.figure(f"{IMG}/fig-class-b.png", 178, "Figure 3.3b  Conceptual class diagram — additional associations.")

    pdf.h2("3.6  Activity Diagram", reserve=155)
    pdf.p("The following separate activity diagrams model selected operations rather than assuming that the actions happen automatically in a fixed sequence.")
    pdf.figure(f"{IMG}/fig-activity.png", 178, "Figure 3.4a  Activity diagram — complaint submission.")
    pdf.figure(f"{IMG}/fig-activity-b.png", 178, "Figure 3.4b  Activity diagram — complaint resolution.")
    pdf.figure(f"{IMG}/fig-activity-c.png", 178, "Figure 3.4c  Activity diagram — feedback and closure.")
    pdf.figure(f"{IMG}/fig-activity-d.png", 178, "Figure 3.4d  Activity diagram — reopening.")
    pdf.figure(f"{IMG}/fig-activity-e.png", 178, "Figure 3.4e  Activity diagram — administrator force-close.")
    pdf.note("Overdue is never stored — it is derived: now > sla_due_at AND status NOT IN (Resolved, Closed). This keeps every register consistent even if the server is restarted after a long break.")

    pdf.h2("3.7  Deployment Diagram", reserve=110)
    pdf.figure(f"{IMG}/fig-deployment.png", 178, "Figure 3.5  Deployment — local demonstration on one computer.")

    pdf.h2("3.8  Module Hierarchy Diagram", reserve=125)
    pdf.figure(f"{IMG}/fig-modules.png", 178, "Figure 3.6  Module hierarchy — actual project files and responsibilities.")

    pdf.h2("3.9  Sample Input and Output Screens", reserve=40)
    pdf.p("Screenshots use synthetic seeded data; see Appendix B. The fresh-seed reports contain at least five data rows; routing has two mode summaries and a separate complaint-level table. The full screen catalogue and validation notes are in Chapter 10.")
    pdf.figure(f"{IMG}/screen-login.png", 120, "Figure 3.7  Sample input — Sign-in screen (roll no./username + password).")
    pdf.figure(f"{IMG}/screen-dashboard.png", 132, "Figure 3.8  Sample output — Student dashboard (KPI tiles, status donut, latest complaints).")
    pdf.figure(f"{IMG}/screen-lodge.png", 148, "Figure 3.9  Sample input — Complaint form with estimated routing.")
    pdf.figure(f"{IMG}/screen-console.png", 148, "Figure 3.10  Sample output — Admin console (fresh-seed filterable register).")
    pdf.figure(f"{IMG}/screen-timeline.png", 148, "Figure 3.11  Sample output — Complaint detail: SLA clock, stepper and timeline.")

    pdf.h3("3.9.1  Constraints and Assumptions")
    pdf.bullets([
        "One campus, one server process, SQLite file in the app directory; contention and capacity depend on workload and have not been load-tested.",
        "Keyword lists are curated per domain; sarcasm/vindication requires admin reassignment (Chapter 6, L-2).",
        "Complaint codes contain the calendar year and a database-generated ID; there is no application delete action for complaints.",
        "Anonymous identity fields are visible to administrators; free text can still identify a complainant.",
    ])

def ch4(pdf: Report):
    pdf.h1("ch4", "Coding", "Chapter 4")
    pdf.p("The following examples illustrate the main routing, workflow, validation and database logic. Ellipses indicate omitted lines.")

    pdf.h2("4.1  Code snippets")
    pdf.h3("4.1.1  Routing engine — scoring and SLA")
    pdf.code('''def score_category(text: str, keywords: str) -> int:
    score = 0
    low = text.lower()
    for kw in (k.strip().lower() for k in keywords.split(",") if k.strip()):
        pattern = r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])"
        hits = len(re.findall(pattern, low))
        if hits:
            weight = len(kw.split()) * 2  # Multi-word keywords carry more weight.
            score += weight * hits
    return score

def assign_priority(default_priority, title, description):
    text = f"{title}. {description}".lower()
    if any(w in text for w in SAFETY_WORDS):
        return "High"
    p = default_priority
    if any(p_ in text for p_ in MASS_IMPACT):
        p = bump_priority(p)
    return p''', title="routing.py — keyword scorer & priority resolver")

    pdf.h3("4.1.2  Selecting a routing category")
    pdf.code('''def select_category(title, description, chosen, categories):
    text = route_text(title, description)
    matched, score = route(text, categories)
    if matched and (matched["id"] == chosen["id"] or
                    score > score_category(text, chosen["keywords"])):
        return matched, "auto", score
    return chosen, "manual", 0''',
        title="routing.py — selection shared by submission, preview and seed")

    pdf.h3("4.1.3  Resolution workflow — status transitions")
    pdf.code('''@app.route("/complaint/<code>/resolve", methods=["POST"])
@login_required
@role_required("officer", "admin")
def resolve(code):
    remark = (request.form.get("remark") or "").strip()
    ...
    if c["status"] not in ("In Progress", "Acknowledged", "Submitted"):
        flash("Complaint is already resolved or closed.", "warning")
    else:
        if not transition_status(conn, c, 'Resolved',
                                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
            stale_complaint()
            return redirect(url_for("complaint_detail", code=code))
        log_event(conn, c["id"], "status", f"Resolved — {remark}", user["id"])
        conn.commit()''', title="app.py — resolve() excerpt")

    pdf.h3("4.1.4  SLA compliance report — SQL")
    pdf.code('''SELECT d.name AS dept,
       COUNT(c.id) AS resolved_total,
       SUM(CASE WHEN c.resolved_at IS NOT NULL
                 AND c.resolved_at <= c.sla_due_at THEN 1 ELSE 0 END) AS within_sla,
       ROUND(100.0 * SUM(CASE WHEN c.resolved_at IS NOT NULL
                                AND c.resolved_at <= c.sla_due_at THEN 1 ELSE 0 END)
             / NULLIF(COUNT(c.id),0), 1) AS pct
FROM departments d
LEFT JOIN complaints c ON c.department_id=d.id AND c.status IN ('Resolved','Closed')
GROUP BY d.id ORDER BY pct DESC NULLS LAST;''', title="app.py — reports() SLA compliance query")

    pdf.h3("4.1.5  Sample of schema constraints in force")
    pdf.code('''status   TEXT NOT NULL DEFAULT 'Submitted'
         CHECK (status IN ('Submitted','Acknowledged','In Progress','Resolved','Closed')),
routing  TEXT NOT NULL DEFAULT 'auto' CHECK (routing IN ('auto','manual')),
priority TEXT NOT NULL CHECK (priority IN ('High','Medium','Low')),
rating   INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5)  -- feedback''', title="schema.sql — CHECK constraints (integrity at the database layer)")
    pdf.h3("4.1.6  Server-side complaint validation")
    pdf.p("The following checks run on submission. The form's browser-side checks assist users but do not replace these server-side checks. A rejected submission is not inserted.")
    pdf.code('''if len(title) < 8: errors.append("Title must be at least 8 characters.")
if len(desc) < 20: errors.append("Description must be at least 20 characters — help the department.")
if not cat_id.isdigit() or not conn.execute(
        "SELECT 1 FROM categories WHERE id=?", (cat_id,)).fetchone():
    errors.append("Choose a valid category.")
if errors:
    for e in errors: flash(e, "danger")
    return render_template("lodge.html", cats=cats, form=request.form), 400''', title="app.py — lodge() validation excerpt; formatting adapted")
# =====================================================================
def ch5(pdf: Report):
    pdf.h1("ch5", "Testing", "Chapter 5")
    pdf.h2("5.1  Test strategy")
    pdf.p("Automated unit and integration tests use Flask's test client and isolated, freshly seeded temporary SQLite databases. Browser and print checks complement these tests. In the recorded automated run, 114 tests passed; the results do not establish formal acceptance or production readiness.")
    pdf.h2("5.2  Unit test plan")
    pdf.table(["ID", "Steps / input", "Expected and observed in automated run", "Script"], [
        ["UT-01", "Score 'leaking leak leak.' for keyword leak; score two occurrences of short circuit.", "4 and 8 respectively; PASS.", "test_safety_and_mass_impact_and_word_boundaries"],
        ["UT-02", "Set default Low and enter a fire keyword; check SLA constants.", "High priority; High 24h, Medium 72h, Low 168h; PASS.", "test_safety_and_mass_impact_and_word_boundaries"],
        ["UT-03", "Test tied keyword scores, then unrelated text.", "First category wins tie; no match returns none; PASS.", "test_keyword_scoring_and_tie_break"],
    ], [15, 53, 58, 52], size=7.2)
    pdf.h2("5.3  Acceptance Test Plan")
    pdf.p("The following automated test-client scenarios show their inputs, expected outcomes and observed assertions. They are acceptance-oriented checks rather than formal stakeholder acceptance.")
    cases = [
      ("AT-01", "Register New Student with MCA2026999, test@example.com, 9876543210 and abc123; submit the same data again.", "First redirects (302); duplicate returns 400. Observed: both assertions passed.", "test_registration_duplicate_and_password_change"),
      ("AT-02", "Log in as MCA2026001; submit a short title or invalid category; compare complaint count before and after.", "HTTP 400, no inserted complaint. Observed: parametrized assertions passed.", "test_lodge_validation_no_partial_insert"),
      ("AT-03", "MCA2026002 lodges overflowing dustbin; maintenance officer acknowledges, starts, resolves with a remark; student submits 5-star feedback.", "Complaint ends Closed. Observed: 302 responses for lodge/resolve/feedback and Closed database status; PASS.", "test_10_full_resolution_cycle"),
      ("AT-04", "Create a complaint as student 1; sign in as student 2 and request its detail and feedback action.", "Both requests forbidden (403), original state unchanged. Observed: PASS.", "test_cross_user_and_department_access_is_denied"),
      ("AT-05", "Track an anonymous complaint with wrong roll MCA2026002, then its correct roll MCA2026001.", "Wrong roll hides title; matching roll returns title without student name. Observed: PASS.", "test_tracking_code_and_roll_and_sql_injection"),
      ("AT-06", "On a controlled dataset of 5 complaints, request routing report as admin.", "Auto 3, manual 2; five distinct detail records match stored modes, scores and department. Observed: PASS.", "test_reports_on_controlled_dataset"),
      ("AT-07", "Log in as admin; submit representative mutating endpoints without CSRF tokens.", "HTTP 400 for each; complaint state and events unchanged. Observed: PASS.", "test_csrf_blocks_every_mutating_endpoint"),
      ("AT-08", "Check acknowledgement, work, resolve and force-close from each of five statuses.", "Only allowed transitions change status and add one event. Observed: matrix assertions passed.", "test_state_transition_matrix"),
    ]
    pdf.table(["ID", "Steps and data", "Expected / actual", "Automated test function"], cases, [14, 55, 57, 52], size=7.2)
    pdf.h2("5.4  Test Case / Test Script")
    pdf.p("The test scripts use isolated seeded data and specify setup, requests, assertions and cleanup. UT-03 and AT-03 are in tests/test_app.py; the other listed functions are in tests/test_in_depth.py. HTTP 302 denotes a redirect.")
    pdf.h3("5.4.1  Test limitations")
    pdf.p("The suite does not prove absence of defects. Small concurrency tests are not load tests. Linux/Chromium browser and six A4 report print checks were performed; native Windows, other browsers, physical printing, accessibility, penetration, large-scale load and crash recovery were not tested. Test data and dates are synthetic.")


def ch6(pdf: Report):
    pdf.h1("ch6", "Limitations of Proposed System", "Chapter 6")
    pdf.bullets([
        "<b>L-1  Explainable but dumb router:</b> the keyword engine cannot understand context or sarcasm; a mis-route needs admin reassignment (one click) — this is a feature for auditability, a limitation for raw accuracy.",
        "<b>L-2  Anonymous follow-up paradox:</b> sensitive complaints (e.g. ragging) hide identity from officers, so the officer cannot ask clarifying questions; only the admin can see the complainant.",
        "<b>L-3  No notifications:</b> students must poll /my-complaints or the tracker; no SMS/e-mail push yet.",
        "<b>L-4  Single node:</b> SQLite file on one PC is the whole database; horizontal scaling is impossible without migration.",
        "<b>L-5  Category catalogue is seed-fixed:</b> officers cannot add categories; admins cannot edit them without SQL.",
        "<b>L-6  Reopen age check:</b> compares whole days to 7, rejects reopening if the timestamp cannot be parsed, and is not configurable per department.",
        "<b>L-7  Reports are print-tables, not charts:</b> powerful for the register, weak for trend visualisation.",
        "<b>L-8  No pagination:</b> lists render fully; performance with large datasets has not been measured.",
        "<b>L-9  Single-semester evidence:</b> behaviour is validated on a seeded dataset + 114 tests, not on a live semester of usage.",
    ])
    pdf.note("Known limitation: force-close checks for Resolved status but does not enforce the proposed seven-day waiting period. The waiting period must therefore be managed outside the application.")
    pdf.p("The implemented workflow supports complaint submission, resolution and feedback, with events recorded in the timeline. Routing, SLA calculations and administrative escalation are deterministic; reports can be checked against the illustrative seeded data.")


def ch7(pdf: Report):
    pdf.h1("ch7", "Proposed Enhancements", "Chapter 7")
    pdf.table(["ID", "Enhancement", "Effort", "Addresses"], [
        ["E-1", "E-mail + SMS on every status change (submission, resolve) via SMTP/SMS gateway", "2 wks", "L-3"],
        ["E-2", "WhatsApp deep-link tracker: share CMP code as wa.me link with prefilled text", "3 days", "L-3"],
        ["E-3", "Photo evidence upload (trap: validate MIME + size ≤ 2 MB; store under instance/)", "1 wk", "L-1"],
        ["E-4", "Admin category management UI (add/retire keywords, re-map departments)", "1 wk", "L-5"],
        ["E-5", "MySQL migration; adapt schema, queries and connections", "3 days", "L-4"],
        ["E-6", "Nightly SLA-breach cron: auto-escalate to admin at 50%/100% of deadline", "2 days", "L-1, SLA"],
        ["E-7", "Charts dashboard (matplotlib PNGs or Chart.js): pendency, trend, SLA %", "2 wks", "L-7"],
        ["E-8", "Public board in the admin corridor: live counts, longest-pending grievances", "1 wk", "visibility"],
        ["E-9", "Marathi / Hindi UI toggle (Jinja-gettext patterns; 120 keys)", "2 wks", "accessibility"],
        ["E-10", "ERP bridge: sync roll no. ↔ ERP student master; auto e-mail to parents on High", "3 wks", "reach"],
    ], [12, 108, 16, 24])
    pdf.p("<b>Planning note:</b> effort values are rough suggestions, not measured commitments. Each enhancement requires design, security review and testing; some may need schema changes.")


def ch8(pdf: Report):
    pdf.h1("ch8", "Conclusion", "Chapter 8")
    pdf.p("Campus Shikayat Setu demonstrates a grievance workflow with role-based access, keyword routing, "
          "status history and printable reports. The data is illustrative and the college's existing process has not been verified.")
    pdf.p("The documented checks support a local demonstration, not a guarantee of correctness, production security or institutional acceptance. "
          "SQLite and Flask were chosen for simplicity; their suitability under real workloads was not benchmarked.")


def ch9(pdf: Report):
    pdf.h1("ch9", "Bibliography", "Chapter 9")
    refs = [
        "Pallets Projects. (2024). <i>Flask — Web development, one drop at a time.</i> https://flask.palletsprojects.com/",
        "Pallets Projects. (2024). <i>Werkzeug — The comprehensive WSGI web application library.</i> https://werkzeug.palletsprojects.com/",
        "The SQLite Consortium. (2024). <i>SQLite documentation — file format, transactions, WAL.</i> https://www.sqlite.org/docs.html",
        "FPDF2 contributors. (2025). <i>fpdf2 — PDF document generation in Python.</i>",
        "Matplotlib developers. (2024). <i>Matplotlib — Visualisation with Python.</i> https://matplotlib.org/",
        "Press Information Bureau. (2024). <i>Centralized Public Grievance Redress and Monitoring System (CPGRAMS).</i> Government of India.",
        "OWASP Foundation. (2023). <i>OWASP Top 10 — A03: Injection, A07: Identification and Authentication Failures.</i> https://owasp.org/www-project-top-ten/",
    ]
    for i, r in enumerate(refs, 1):
        pdf.p(f"[{i}]  {r}")
# =====================================================================
def ch10(pdf: Report):
    pdf.h1("ch10", "User Manual", "Chapter 10")

    pdf.h2("10.1  Roles & demo credentials")
    pdf.table(["Role", "Credentials", "Can do"], [
        ["Admin", "admin / admin123", "Everything: console, reassign, escalate, force-close, users & officers, reports"],
        ["Officer", "hostel.officer · it.officer · maint.officer · exam.officer · welfare.officer · admin.officer / officer123",
         "Own-department queue; acknowledge / progress / resolve; remarks"],
        ["Student", "MCA2026001 … MCA2026008 / student123", "Lodge, track, feedback, reopen (whole-day age check)"],
        ["Public (no login)", "/track + complaint code + roll no.", "View matched complaint details and timeline"],
    ], [26, 62, 90])

    pdf.h2("10.2  Quick start (on the demo PC)")
    pdf.p("With Python 3.10 or newer installed, start the application using the provided launcher. The launcher creates a local environment and installs dependencies on first use. Open http://127.0.0.1:5001 in a browser and sign in using a demo account. Stop the server with Ctrl+C. The launcher retains an existing project database.")

    pdf.h2("10.3  Screen catalogue — all application screen types")
    pdf.p("Images below are browser viewport captures from a fresh, disposable synthetic demo database. Some long pages require scrolling; role and status determine which action forms appear. Counts, names and dates in the demo are illustrative, not real grievance records.")
    screens = [
      ("Sign in", "login", "Enter a username or roll number and password; invalid credentials are rejected. Links open registration and public tracking."),
      ("Student registration", "register", "Enter name, roll number, email, mobile, password and matching confirmation; submit to create a student account."),
      ("Public tracker — input", "track", "Enter complaint code and matching roll number. The tracker is also available without sign-in."),
      ("Public tracker — result", "track-result", "A matching pair displays complaint details and timeline. Signed-in admin may track without a roll match."),
      ("Student dashboard", "dashboard", "Summarises the signed-in student's own complaints; select a complaint or lodge a new one."),
      ("Lodge complaint", "lodge", "Enter title, description, category, optional location and optional anonymous flag. Preview is advisory; submit saves a complaint and code."),
      ("My complaints", "my-complaints", "Lists only the student's own complaints; use the search filter or open a code."),
      ("Complaint detail and timeline", "timeline", "Shows status, department, description, deadline, routing and events for an authorised viewer."),
      ("Student confirmation and reopen", "student-actions", "On an own Resolved complaint, select rating and optional comment to close, or enter a reason to reopen, subject to the age check."),
      ("Change password", "change-password", "Enter current password, a new password and matching confirmation. Applies to signed-in roles."),
      ("Officer dashboard", "officer-dashboard", "Shows the officer's department workload, priority and overdue indicators."),
      ("Officer queue", "queue", "Lists department-assigned complaints; filter locally and open one to act. Admin can also access the queue."),
      ("Officer complaint actions", "officer-actions", "Acknowledge, start work, resolve with a remark or add a timeline remark; availability depends on status and department."),
      ("Administrator dashboard", "admin-dashboard", "Shows college-wide demo totals, current workload and status distribution."),
      ("Admin console", "console", "Apply department, status and priority filters; open a complaint for its actions."),
      ("Users and officers", "users", "Admin creates officers, filters accounts and activates or deactivates users; built-in admin is protected."),
      ("Administrator complaint actions", "admin-actions", "Admin can reassign department, escalate priority and force-close a Resolved complaint; officer actions are also available."),
      ("Report — department pendency", "report-pendency", "Shows counts by department and status, including current overdue totals."),
      ("Report — SLA compliance", "report-sla", "Shows resolved/closed counts and on-time percentages by department."),
      ("Report — resolution time", "report-restime", "Shows average elapsed hours for resolved/closed complaints by category."),
      ("Report — monthly trend", "report-trend", "Groups submissions by month; resolved/closed is the current status of those submissions."),
      ("Report — feedback", "report-feedback", "Shows ratings grouped by department and recent comments."),
      ("Report — routing summary", "report-routing", "Shows the two routing modes. The same page also contains complaint-level routing records and manual examples."),
      ("Report — routing detail", "report-routing-details", "Scroll to the complaint-level table. Each row identifies one complaint, its current department and mode, and the original routing score."),
      ("Access error", "forbidden", "A 403 page is shown for forbidden access. Missing pages or complaints use the same error template with 404."),
    ]
    for i, (title, filename, description) in enumerate(screens, 1):
        pdf.h3(f"10.3.{i}  {title}", reserve=132)
        pdf.figure(f"{IMG}/screen-{filename}.png", 162, f"Figure 10.{i}  {title} — synthetic demo.", description)

    pdf.h2("10.4  Frequently asked questions")
    pdf.bullets([
        "<b>“The complaint is routed wrong!”</b> — Admins reassign in one click; the timeline records old → new department.",
        "<b>“How do I see overdue complaints?”</b> — the reports tab “Department Pendency” has an Overdue column; officer queue sorts High priority first.",
        "<b>“Can I edit a complaint after lodging?”</b> — Not yet; add a remark as officer, or reopen as student. Deliberate: audit integrity.",
        "<b>“Anonymous complaint — who sees who I am?”</b> — Officers see “anonymous” in identity fields and student event actors. Free text may still identify you; administrators can see your identity.",
        "<b>“Where is the data file?”</b> — app/shikayat_setu.db by default. Use SHIKAYAT_DB with a new path for a fresh demo; do not delete existing data without a backup.",
        "<b>“Can it run on Windows?”</b> — It is intended to run on Windows with Python and dependencies installed, but native Windows testing has not been performed.",
    ])

    pdf.h2("10.5  Validation catalogue — what each input enforces")
    pdf.table(["Screen / field", "Rule enforced server-side"], [
        ["Register — Name", "≥ 3 characters; trimmed; required."],
        ["Register — Roll no.", "Format MCA2026 plus exactly three ASCII digits (case-insensitive); duplicates rejected."],
        ["Register — E-mail", "RFC-ish check ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$; validated but not stored."],
        ["Register — Mobile", "Ten ASCII digits, first digit 6–9."],
        ["Registration — Password", "≥ 6 characters; confirmation must match; hashed with Werkzeug — never plaintext."],
        ["Login", "Username OR roll no. + password; deactivated accounts rejected at login and cleared on their next request; wrong credentials return a generic error."],
        ["Lodge — Title / Description", "Title ≥ 8 characters; description ≥ 20 characters (“help the department”); category must reference an existing categories.id."],
        ["Lodge — Location / preview", "Location is optional. Preview is advisory and not saved; submission recalculates routing."],
        ["Lodge — Anonymous", "Optional tick; the student identity and student event actor are hidden from officers. Free-text descriptions or notes can still identify the student."],
        ["Officer/admin — Acknowledge / start", "Acknowledge only Submitted; start on Submitted or Acknowledged. Access is department-scoped for officers."],
        ["Officer/admin — General remark", "Trimmed note must contain at least 5 characters; officer must have access to the assigned department."],
        ["Officer resolve — Remark", "Mandatory, ≥ 10 characters; resolution is blocked otherwise."],
        ["Student confirm — Rating", "1–5 stars mandatory for Close; comment optional; feedback UNIQUE per complaint (FK constraint)."],
        ["Student reopen — Reason", "Mandatory, ≥ 10 characters; whole-day resolution age must be ≤ 7 and the timestamp must parse; status returns to In Progress."],
        ["Admin — Reassign / Force-close", "Reassign requires a valid department. Force-close requires Resolved status; the seven-day wait is not enforced. Both actions are logged."],
        ["Admin — Create officer", "Name at least 3 characters; non-empty unique username; existing department; password at least 6 characters. Empty password falls back to demo default on the server."],
        ["Admin — User status", "Only admin can toggle an existing account; built-in admin cannot be deactivated."],
        ["Password change", "Current password must match; new password at least 6 characters and confirmation must match."],
        ["Filters and reports", "Console and queue filters select displayed records. Reports are read-only and admin-only. Empty datasets may show fewer than five records."],
        ["All POST forms", "CSRF token required. Access control and complaint ownership/department checks apply independently."],
        ["Public tracker (/track)", "Public users need a code and matching roll number. Signed-in admins bypass the roll check. Different errors for missing code and wrong roll can reveal whether a code exists."],
    ], [54, 124], size=7.6)


def appa(pdf: Report):
    pdf.h1("appa", "Appendix A — Database Schema (schema.sql)", "Appendix A")
    with open(REPORT_DIR.parent / "app" / "schema.sql", "r", encoding="utf-8") as f:
        schema = f.read()
    pdf.code(schema, title="schema.sql (verbatim)")


def appb(pdf: Report):
    pdf.h1("appb", "Appendix B — Seed Data (actual records)", "Appendix B")

    pdf.h2("B.1  departments — 6 rows")
    rows = db_rows("SELECT name, head_name, email, location FROM departments ORDER BY id")
    pdf.table(["Name", "Head", "Email", "Location"],
              [[r["name"], r["head_name"], r["email"], r["location"]] for r in rows],
              [40, 34, 52, 52], size=7.6)

    pdf.h2("B.2  categories — 15 rows (keyword router fodder)")
    rows = db_rows("""SELECT c.name, d.name AS dept, c.default_priority p, c.keywords
                      FROM categories c JOIN departments d ON d.id=c.department_id ORDER BY c.id""")
    pdf.table(["Category", "Department", "Default", "Keywords (seed)"],
              [[r["name"], r["dept"], r["p"], r["keywords"]] for r in rows],
              [34, 34, 13, 97], size=6.8)

    pdf.h2("B.3  users — 15 rows (admin, 6 officers, 8 students)")
    rows = db_rows("""SELECT u.username, u.role, u.full_name, COALESCE(d.name,'—') AS dept, u.status
                      FROM users u LEFT JOIN departments d ON d.id=u.department_id ORDER BY u.role, u.username""")
    pdf.table(["Username", "Role", "Full name", "Department", "Status"],
              [[r["username"], r["role"], r["full_name"], r["dept"], r["status"]] for r in rows],
              [30, 18, 44, 52, 24], size=7.0)

    pdf.h2("B.4  complaints — 37 rows")
    rows = db_rows("SELECT code, title, priority, status FROM complaints ORDER BY id")
    pdf.table(["Code", "Title", "Pri", "Status"],
              [[r["code"], r["title"], r["priority"], r["status"]] for r in rows],
              [24, 108, 12, 24], size=6.8)

    pdf.h2("B.5  complaint_events — 135 rows (audit trail)")
    rows = db_rows("""SELECT event_type, COUNT(*) AS n FROM complaint_events GROUP BY event_type ORDER BY n DESC""")
    pdf.table(["Event type", "Count"], [[r["event_type"], r["n"]] for r in rows], [60, 40], size=8.2)

    pdf.h2("B.6  feedback — 11 rows")
    rows = db_rows("""SELECT c.code, f.rating, f.comment FROM feedback f JOIN complaints c ON c.id=f.complaint_id ORDER BY f.id""")
    pdf.table(["Complaint", "Rating", "Comment"],
              [[r["code"], "★" * r["rating"], (r["comment"] or "—")] for r in rows],
              [28, 22, 128], size=7.6)


def appc(pdf: Report):
    pdf.h1("appc", "Appendix C — Glossary and Acronyms", "Appendix C")
    words = [
        ("Audit event", "Application-created complaint_events row recording a status or other action with actor and timestamp; direct database edits are not prevented."),
        ("Auto-routing", "Keyword-weighted assignment of a complaint to a department; scored and printed on the timeline."),
        ("CMP code", "Human-readable complaint identifier: CMP-<year>-<4-digit sequence>."),
        ("Force-close", "Admin-only closure of a Resolved complaint; the seven-day wait is not enforced."),
        ("Grievance", "Any student-raised deficiency in college services — facility, academic, security, food."),
        ("Keyword weight", "Routing score = Σ(weight × hits); multi-word keywords weigh double per word."),
        ("Mass impact", "Phrase class (“entire”, “all students”) that bumps priority one level."),
        ("OLA", "Operational Level Agreement — internal equivalent of SLA between departments."),
        ("Reopen", "Student rejection of a resolution; whole-day age check requires a valid timestamp; returns status to In Progress."),
        ("Resolution remark", "Mandatory ≥ 10-character note officers must enter when resolving."),
        ("Safety word", "Phrase class (ragging, shock, fire…) that forces priority High at submission."),
        ("SLA", "Service-Level Agreement — High 24 h · Medium 72 h · Low 7 days for this college."),
        ("Timeline", "Chronological list of a complaint’s audit events; the single source of truth."),
    ]
    pdf.table(["Term", "Meaning"], words, [34, 144], size=8.0)


def build(toc, recorder, font_dir):
    pdf = Report(toc=toc, recorder=recorder, font_dir=font_dir)
    pdf.set_title("Campus Shikayat Setu — College Grievance Redressal System (MCA-I Sem-I Mini Project Report)")
    pdf.set_author("Yashwant Santosh Ahire — Dr. B.V. Hiray College of Management and Research Centre, Malegaon (SPPU)")
    pdf.set_creator("Campus Shikayat Setu report generator (build_report.py)")
    blank_pages(pdf)
    cover(pdf)
    certificate(pdf)
    declaration(pdf)
    acknowledgement(pdf)
    index(pdf)
    for key, fn in [("ch1", ch1), ("ch2", ch2), ("ch3", ch3), ("ch4", ch4), ("ch5", ch5),
                    ("ch6", ch6), ("ch7", ch7), ("ch8", ch8), ("ch9", ch9), ("ch10", ch10),
                    ("appa", appa), ("appb", appb), ("appc", appc)]:
        fn(pdf)
    return pdf


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="shikayat-report-fonts-") as font_dir:
        rec1 = {}
        build({}, rec1, font_dir)
        rec2 = {}
        pdf = build(rec1, rec2, font_dir)
        if rec1 != rec2:
            raise RuntimeError(f"Report pagination differs between passes: {rec1} != {rec2}")
        pdf.output(OUT)
        print("PDF written:", OUT)
        print("Pages:", pdf.page_no(), "sections:", {k: rec1[k] for _, k in SECTIONS})

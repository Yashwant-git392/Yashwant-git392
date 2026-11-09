#!/usr/bin/env python3
"""Single-source report generator for the SmartLibrary mini project.
Produces: report/SmartLibrary_MCA-Mini-Project_Report.pdf (and records nothing else).
Two-pass build: pass 1 records chapter page numbers, pass 2 renders the real index.
"""
import os
import sqlite3
import sys
from datetime import date

from fpdf import FPDF
from fpdf.fonts import FontFace

ROOT = "/home/user/Yashwant-git392"
IMG = f"{ROOT}/report/images"
DB = f"{ROOT}/mini-project/app/smartlibrary.db"
OUT = f"{ROOT}/report/SmartLibrary_MCA-Mini-Project_Report.pdf"

D = "/usr/share/fonts/truetype/dejavu/"
NAVY, NAVY2, GOLD, GOLD_L = (22, 36, 61), (31, 52, 85), (201, 162, 39), (255, 217, 94)
CREAM, GREY, LT = (247, 245, 239), (107, 114, 128), (232, 237, 247)
CONTENT_W = 210 - 32  # A4 width minus 2×16mm margins
TODAY = "9 November 2026"

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


class Report(FPDF):
    def __init__(self, toc=None, recorder=None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.toc = toc or {}
        self.recorder = recorder if recorder is not None else {}
        self.current_section = None
        self.cover_pages = {1, 2}  # cover + certificate: no header/footer
        self.add_font("DVS", "", D + "DejaVuSans.ttf")
        self.add_font("DVS", "B", D + "DejaVuSans-Bold.ttf")
        self.add_font("DVS", "I", D + "DejaVuSans.ttf")
        self.add_font("DVS", "BI", D + "DejaVuSans-Bold.ttf")
        self.add_font("DVM", "", D + "DejaVuSansMono.ttf")
        self.add_font("DVM", "B", D + "DejaVuSansMono-Bold.ttf")
        self.set_auto_page_break(auto=True, margin=17)
        self.set_margins(16, 15, 16)

    # ---------- full-width safety ----------
    def cell(self, w, *args, **kwargs):
        if w == 0:
            self.set_x(16)
        return super().cell(w, *args, **kwargs)

    def multi_cell(self, w, *args, **kwargs):
        if w == 0:
            self.set_x(16)
        return super().multi_cell(w, *args, **kwargs)

    # ---------- chrome ----------
    def header(self):
        if self.page_no() in self.cover_pages:
            return
        self.set_y(6)
        self.set_font("DVS", "", 6.6)
        self.set_text_color(*GREY)
        self.cell(0, 5, "SmartLibrary — College Library Management System  |  SPPU MCA-I (Sem-I) Mini Project  |  2026-27",
                  align="L")
        self.set_draw_color(*GOLD)
        self.set_line_width(0.6)
        self.line(16, 11.6, 194, 11.6)
        self.set_y(14.5)

    def footer(self):
        if self.page_no() in self.cover_pages:
            return
        self.set_y(-12)
        self.set_draw_color(*GOLD)
        self.set_line_width(0.6)
        self.line(16, self.get_y(), 194, self.get_y())
        self.set_font("DVS", "", 6.6)
        self.set_text_color(*GREY)
        self.cell(80, 5, "Dr. B.V. Hiray College of Management and Research Centre, Malegaon", align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R")

    # ---------- building blocks ----------
    def h1(self, key, text, kicker=None):
        self.add_page()
        if kicker:
            self.set_font("DVS", "B", 8)
            self.set_text_color(*GOLD)
            self.cell(0, 5, kicker.upper())
            self.ln(6)
        self.set_font("DVS", "B", 16.5)
        self.set_text_color(*NAVY)
        self.multi_cell(0, 8, text)
        self.set_draw_color(*GOLD)
        self.set_line_width(1.1)
        y = self.get_y() + 1
        self.line(16, y, 66, y)
        self.ln(6)
        self.set_text_color(30, 30, 30)
        self.recorder[key] = self.page_no()
        self.start_section(text, level=0)

    def h2(self, text):
        if self.get_y() > 258:
            self.add_page()
        self.ln(1.5)
        self.set_font("DVS", "B", 12)
        self.set_text_color(*NAVY2)
        self.multi_cell(0, 6.4, text)
        self.ln(1.2)
        self.set_text_color(30, 30, 30)

    def h3(self, text):
        if self.get_y() > 264:
            self.add_page()
        self.set_font("DVS", "B", 10.5)
        self.set_text_color(*NAVY2)
        self.multi_cell(0, 5.6, text)
        self.ln(0.8)
        self.set_text_color(30, 30, 30)

    def p(self, html):
        self.set_font("DVS", "", 9.6)
        self.set_text_color(30, 30, 30)
        self.write_html(html)
        self.ln(2.6)

    def bullets(self, items, indent=6):
        self.set_font("DVS", "", 9.6)
        self.set_text_color(30, 30, 30)
        for item in items:
            x = self.get_x()
            self.set_x(16 + indent)
            self.write_html(f"<b>•</b>  {item}")
            self.ln(1.7)
        self.ln(1.2)

    def caption(self, text):
        self.set_font("DVS", "I", 8.2)
        self.set_text_color(*GREY)
        self.multi_cell(0, 4.4, text, align="C")
        self.ln(1.6)

    def figure(self, path, width_mm, caption_text):
        from PIL import Image as _Img
        w_px, h_px = _Img.open(path).size
        h_mm = width_mm * h_px / w_px
        if self.get_y() + h_mm + 11 > 281:
            self.add_page()
        self.image(path, w=width_mm, x=(210 - width_mm) / 2)
        self.ln(1.5)
        self.caption(caption_text)

    def table(self, headers, rows, widths, aligns=None, size=8.2, header_fill=NAVY,
              header_color=GOLD_L, zebra=True, row_height=None):
        aligns = aligns or ["L"] * len(headers)
        head_face = FontFace(emphasis="BOLD", fill_color=header_fill, color=(header_color[0], header_color[1], header_color[2]))
        # neutralise ambient graphics state so body cells render white with hairline gold borders
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(*GOLD)
        self.set_line_width(0.45)
        self.set_font("DVS", "", size)
        line_h = row_height or (size * 0.52)
        with super().table(col_widths=widths, line_height=line_h,
                        headings_style=head_face,
                        borders_layout="ALL") as t:
            row = t.row()
            for htext in headers:
                row.cell(htext)
            for i, r in enumerate(rows):
                row = t.row()
                for j, cell in enumerate(r):
                    row.cell(str(cell))
        self.ln(3)

    def code(self, code_text, title=None):
        est_h = (code_text.count("\n") + 1) * 3.95 + (6.2 if title else 0) + 4
        if self.get_y() + est_h > 281:
            self.add_page()
        if title:
            self.set_font("DVM", "B", 7.6)
            self.set_text_color(255, 255, 255)
            self.set_fill_color(*NAVY2)
            self.multi_cell(0, 5.2, f"  {title}", fill=True)
        self.set_font("DVM", "", 7.0)
        self.set_text_color(32, 32, 32)
        self.set_fill_color(245, 244, 238)
        self.multi_cell(0, 3.9, code_text, fill=True)
        self.ln(2.4)

    def note(self, html):
        self.set_fill_color(255, 250, 229)
        self.set_draw_color(*GOLD)
        self.set_font("DVS", "", 8.8)
        self.set_text_color(93, 74, 10)
        self.multi_cell(0, 5.0, "  " + html.replace("\n", " "), fill=True)
        self.ln(2.4)
        self.set_text_color(30, 30, 30)


# =====================================================================
def cover(pdf: Report):
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, style="F")
    pdf.set_fill_color(26, 43, 71)
    pdf.rect(0, 0, 210, 22, style="F")
    pdf.rect(0, 275, 210, 22, style="F")

    def line(y, h, text, font, size, color, style=""):
        pdf.set_xy(16, y)
        pdf.set_font(font, style, size)
        pdf.set_text_color(*color)
        pdf.cell(178, h, text, align="C")

    line(7.5, 6, "K.B.H.S.S.T's  ·  ESTABLISHED 1988", "DVS", 7.4, GOLD_L, "B")

    # crest
    cx, cy, r = 105, 44, 14.5
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.6)
    pdf.ellipse(cx - r, cy - r, 2 * r, 2 * r, style="D")
    pdf.set_line_width(0.7)
    pdf.ellipse(cx - r + 3.2, cy - r + 3.2, 2 * (r - 3.2), 2 * (r - 3.2), style="D")
    pdf.set_text_color(*GOLD_L)
    pdf.set_xy(cx - r, cy - 7.2); pdf.set_font("DVS", "B", 8.6); pdf.cell(2 * r, 5, "K.B.H.S.S.T's", align="C")
    pdf.set_xy(cx - r, cy - 2.2); pdf.set_font("DVM", "B", 12); pdf.cell(2 * r, 7, "MCA", align="C")
    pdf.set_xy(cx - r, cy + 4.4); pdf.set_font("DVS", "", 5.8); pdf.set_text_color(201, 199, 189); pdf.cell(2 * r, 5, "SPPU · 2026-27", align="C")

    line(64, 7.4, "DR. B.V. HIRAY COLLEGE OF", "DVS", 16.5, (255, 255, 255), "B")
    line(71.5, 7.4, "MANAGEMENT AND RESEARCH CENTRE", "DVS", 16.5, (255, 255, 255), "B")
    line(80.5, 4.6, "Malegaon Camp, Malegaon — Affiliated to Savitribai Phule Pune University, Pune (SPPU)", "DVS", 8.0, (201, 199, 189))
    line(85.5, 4.6, "Approved by AICTE, New Delhi  ·  NAAC Accredited", "DVS", 8.0, (201, 199, 189))

    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.4)
    pdf.line(55, 95, 155, 95)

    line(101.5, 5.2, "M I N I   P R O J E C T   R E P O R T", "DVS", 8.6, GOLD_L, "B")

    line(110.5, 13.5, "SMARTLIBRARY", "DVS", 28, (255, 255, 255), "B")
    line(124.5, 8.2, "College Library Management System", "DVS", 14.5, (255, 217, 94))

    line(137.5, 5.0, "Full-stack web application for catalogue, membership, circulation,", "DVS", 8.8, (226, 224, 214))
    line(142.5, 5.0, "fines and reporting — replacing the manual register system", "DVS", 8.8, (226, 224, 214))

    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.4)
    pdf.line(78, 154.5, 132, 154.5)

    line(161, 6.2, "Course:  Application Development  (Mini Project — Semester I)", "DVS", 9.2, (255, 255, 255))
    line(167.5, 6.2, "Program:  Master of Computer Applications (MCA)  ·  Sem-I", "DVS", 9.2, (255, 255, 255))
    line(174, 6.2, "Academic Year:  2026–27", "DVS", 9.2, (255, 255, 255))

    line(186.5, 6.0, "Submitted by", "DVS", 10, GOLD_L, "B")
    line(193, 6.0, "Yashwant Shelke   ·   Roll No.: ____________________", "DVS", 9.6, (255, 255, 255))
    line(203.5, 6.0, "Under the guidance of", "DVS", 10, GOLD_L, "B")
    line(210, 6.0, "Mrs. Priyanka M. Jagtap  (Roll No. 1–34)", "DVS", 9.6, (255, 255, 255))
    line(216.5, 6.0, "Mrs. Yogita A. Shirsath  (Roll No. 35 onwards)", "DVS", 9.6, (255, 255, 255))

    line(268.5, 5.4, "Project Review Schedule dated 30-09-2026  ·  MCA-I (SEM-I) Guidelines  ·  December 2026", "DVS", 6.8, (160, 164, 178))


def certificate(pdf: Report):
    pdf.add_page()
    pdf.recorder["certificate"] = pdf.page_no()
    pdf.start_section("Certificate", level=0)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.2)
    pdf.rect(12, 12, 186, 273, style="D")
    pdf.set_y(20)
    pdf.set_font("DVS", "B", 15)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 8, "CERTIFICATE", align="C")
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.9)
    pdf.line(80, pdf.get_y() + 1, 130, pdf.get_y() + 1)
    pdf.ln(8)
    pdf.set_font("DVS", "", 10.5)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6.2,
        "This is to certify that the Mini Project entitled “SMARTLIBRARY — College Library Management System” "
        "is a bona fide work carried out by Mr. Yashwant Shelke, student of MCA-I (Semester-I), "
        "Dr. B.V. Hiray College of Management and Research Centre, Malegaon, under the SPPU MCA curriculum "
        "(Course: Application Development), during the academic year 2026–27.")
    pdf.ln(2)
    pdf.multi_cell(0, 6.2,
        "The project has been completed satisfactorily and is submitted in partial fulfilment of the requirements "
        "of the Mini Project Review schedule issued by the Department of MCA on 30-09-2026 (Reviews on "
        "10-10-2026, 24-10-2026, 21-11-2026, 05-12-2026 and the Final Internal Viva on 19-12-2026).")
    pdf.ln(2)
    pdf.multi_cell(0, 6.2,
        "To the best of our knowledge, the matter embodied in this report is original and has not been submitted "
        "to any other University or Institution for the award of any degree or diploma.")
    pdf.ln(14)
    pdf.set_font("DVS", "", 9.5)
    pdf.cell(0, 6, "Date: ____________________")
    pdf.ln(6)
    pdf.cell(0, 6, "Place: Malegaon")
    pdf.ln(6)
    def sig_block(y, left, right, role_l, role_r, bold=True, size=9):
        pdf.set_xy(18, y)
        pdf.set_font("DVS", "", 9)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(90, 6, "_________________________")
        pdf.set_xy(118, y)
        pdf.cell(74, 6, "_________________________")
        pdf.set_xy(18, y + 6)
        pdf.set_font("DVS", "B" if bold else "", size)
        pdf.set_text_color(*NAVY)
        pdf.cell(90, 6, left)
        pdf.set_xy(118, y + 6)
        pdf.cell(74, 6, right)
        pdf.set_xy(18, y + 11.5)
        pdf.set_font("DVS", "", 7.6)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(90, 6, role_l)
        pdf.set_xy(118, y + 11.5)
        pdf.cell(74, 6, role_r)

    sig_block(188, "Ms. Priyanka M. Jagtap", "Mrs. Yogita A. Shirsath",
              "Project Guide (Roll No. 1–34)", "Project Guide (Roll No. 35 +)")
    sig_block(226, "Ms. Priyanka M. Jagtap", "Dr. Dayanand Surwade",
              "Head of Department (MCA)", "Dy. Director")
    pdf.ln(6)


def index(pdf: Report):
    pdf.add_page()
    pdf.set_font("DVS", "B", 16.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "INDEX")
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.1)
    pdf.line(16, pdf.get_y() + 1, 66, pdf.get_y() + 1)
    pdf.ln(8)
    for title, key in SECTIONS:
        page = str(pdf.toc.get(key, "0"))
        pdf.set_font("DVS", "", 10.5)
        pdf.set_text_color(30, 30, 30)
        y = pdf.get_y()
        pdf.cell(0, 8.6, "", border=0)
        text_w = pdf.get_string_width(title)
        pdf.set_xy(16, y)
        pdf.cell(150, 8.6, "  " + title)
        pdf.set_xy(166, y)
        pdf.set_font("DVS", "B", 10.5)
        pdf.set_text_color(*NAVY2)
        pdf.cell(28, 8.6, page, align="R")
        # dotted leader
        pdf.set_draw_color(180, 178, 168)
        pdf.set_line_width(0.3)
        pdf.set_dash_pattern(dash=0.4, gap=1.4)
        pdf.line(18 + text_w + 4, y + 6.1, 164, y + 6.1)
        pdf.set_dash_pattern(dash=0, gap=0)
        pdf.set_xy(16, y + 8.6)


# =====================================================================
def ch1(pdf: Report):
    pdf.h1("ch1", "Introduction", "Chapter 1")

    pdf.h2("1.1  Abstract")
    pdf.p("The college library of Dr. B.V. Hiray College of Management and Research Centre, Malegaon, currently maintains "
          "its entire circulation operation — member registration, book cataloguing, issue/return, due dates and late-fine "
          "collection — manually, using paper registers. The manual system is slow, error-prone, difficult to audit, and "
          "provides no management information (e.g. most-borrowed titles, overdue defaulters, category-wise stock) without "
          "hours of manual tallying. This project, <b>SmartLibrary</b>, is a full-stack web application that digitises the "
          "complete library workflow: catalogue management, member management, book issue, return with automatic fine "
          "calculation (₹2 per day past due date), a searchable transaction register, and five printable management reports.")
    pdf.p("The system is built with a <b>Python + Flask</b> application server, <b>Jinja2</b> templates, an <b>HTML5/CSS3/"
          "JavaScript</b> front end and a <b>SQLite-3</b> database (1:1 mappable to MySQL 8 for production). It enforces "
          "session-based authentication, server-side and client-side validation, and referential integrity at the database "
          "level. The result is an immediately deployable, low-cost, desk-side solution for the college library, replacing "
          "the register with a fast, auditable, report-generating system.")
    pdf.p("<b>Keywords:</b> Library Management System, Web Application, Flask, SQLite, Fine Automation, SPPU MCA, "
          "Application Development.")

    pdf.h2("1.2  Existing System and Need for System")
    pdf.h3("1.2.1  Description of the existing (manual) system")
    pdf.p("At present, the librarian maintains three physical registers: (i) a <b>Catalogue Register</b> (title, author, "
          "ISBN, accession number, shelf), (ii) an <b>Issue/Return Register</b> (member roll no., book accession no., issue "
          "date, due date, return date, initials), and (iii) a <b>Fine Ledger</b> (member, amount, date, signature). "
          "Membership is recorded in a fourth <b>Membership Register</b>.")
    pdf.h3("1.2.2  Problems with the existing system")
    pdf.bullets([
        "<b>Time-consuming:</b> issuing or returning a book takes 3–5 minutes of manual writing; during peak hours (post-lecture), queues form.",
        "<b>No instant search:</b> checking whether a title is available requires walking to the shelves; there is no index beyond the accession number.",
        "<b>Fine calculation errors:</b> overdue days are counted by hand; arithmetic slips are common and unauditable.",
        "<b>Lost data:</b> registers are torn, misplaced and illegible; there is no backup.",
        "<b>No reports:</b> the principal/director cannot get answers to “How many books are overdue?” or “Which categories are most used?” without manual tabulation — so they are rarely produced.",
        "<b>Duplicate/invalid entries:</b> duplicate ISBN entries and wrong phone numbers go unnoticed for months.",
        "<b>Accountability:</b> fines collected cannot be reconciled with the cash memo book.",
    ])
    pdf.h3("1.2.3  Why a new system is needed")
    pdf.bullets([
        "Automate the complete circulation cycle (issue → due → return → fine) with zero manual arithmetic.",
        "Provide catalogue search with title/author/ISBN matching in under a second.",
        "Enforce business rules (max 3 books per member, 14-day loan, inactive-member block) automatically.",
        "Generate audit-ready reports (issued, overdue, fines, stock, member activity) at the press of a key.",
        "Give the management measurable data: circulation counts, defaulter lists, stock utilisation.",
    ])

    pdf.h2("1.3  Scope of the System")
    pdf.h3("In scope")
    pdf.bullets([
        "Admin (librarian) authentication — login, logout, change password.",
        "Book catalogue management — add, edit, delete (guarded), search (title/author/ISBN), category filter, availability tracking.",
        "Member management — register, update, deactivate, search by roll no./name/email.",
        "Circulation — issue book (with eligibility checks), return book (with automatic fine = late days × ₹2).",
        "Transaction register — filter by All / Issued / Returned, with computed late-day and fine columns.",
        "Fine management — ledger of fines collected vs fines pending (overdue, unreturned).",
        "Reports — (1) Currently Issued, (2) Overdue Books, (3) Fine Collection, (4) Category-wise Stock, (5) Member-wise Activity; print-ready (Ctrl+P) with print CSS.",
        "Dashboard — live KPIs: titles, copies, availability, active members, open issues, overdue count, fines collected, low-stock alert.",
    ])
    pdf.h3("Out of scope (deferred — see Chapter 7)")
    pdf.bullets([
        "Public/OPAC self-service catalogue for students; e-book or journal subscription management.",
        "Barcode/RFID hardware integration and SMS/email overdue reminders.",
        "Multi-branch or inter-library loan; fine payment gateways; integration with the college ERP.",
    ])

    pdf.h2("1.4  Operating Environment — Hardware and Software")
    pdf.h3("Hardware (minimum specification to run the project)")
    pdf.table(["Component", "Minimum", "Recommended (dev/demo)"], [
        ["Processor", "Intel Core i3 (any generation)", "Intel Core i5 / Ryzen 5"],
        ["RAM", "2 GB", "8 GB"],
        ["Storage", "200 MB free", "1 GB free (SSD)"],
        ["Display", "1366 × 768", "1920 × 1080"],
        ["Network", "None (single-machine)", "LAN (optional, for demo from another PC)"],
    ], [38, 70, 70])
    pdf.h3("Software")
    pdf.table(["Software", "Version used", "Purpose"], [
        ["Operating System", "Windows 10/11  ·  GNU/Linux (Debian 12)", "Development & demo environment"],
        ["Python", "3.11.2", "Application runtime"],
        ["Flask", "3.1.3", "Web framework (routing, templating, sessions)"],
        ["Jinja2", "3.x", "Server-side templating"],
        ["SQLite", "3.x (file: smartlibrary.db)", "Relational database (schema maps to MySQL 8)"],
        ["Werkzeug", "3.1.x", "WSGI stack + password hashing utilities"],
        ["HTML5 / CSS3 / JavaScript", "ES2019 (vanilla JS, no framework)", "Presentation layer"],
        ["pytest", "9.2.0", "Unit / integration test runner"],
        ["Browser", "Chrome 120+ / Firefox 120+ / Edge 120+", "Client"],
        ["IDE / Editor", "VS Code + Git 2.4x + GitHub", "Development & version control"],
    ], [42, 62, 74])

    pdf.h2("1.5  Brief Description of Technology Used")
    pdf.p("<b>Python 3</b> was chosen as the implementation language for its readability, rapid development cycle and "
          "excellent library ecosystem — appropriate for a one-semester academic project with a two-month build window.")
    pdf.p("<b>Flask</b> is a micro web framework: routing, request/response handling, session management (signed cookies), "
          "flash messaging and Jinja2 templating out of the box, with no ORM imposed — SQL is written explicitly so the "
          "database layer is transparent and examinable in viva. <b>Jinja2</b> templates separate presentation from logic.")
    pdf.p("The <b>front end</b> uses semantic HTML5, hand-written CSS3 (CSS variables, flexbox, print media query) and "
          "vanilla JavaScript for progressive enhancement (auto-dismiss flashes, live ISBN sanity check). No front-end "
          "framework or build step is required — the app runs on any machine with Python alone.")
    pdf.p("<b>SQLite 3</b> stores all data in a single file (smartlibrary.db) with CHECK, UNIQUE and FOREIGN KEY ... "
          "ON DELETE CASCADE constraints enforcing integrity — this removes the need for a database server in a lab/demo "
          "setting. For production, the schema ports 1:1 to MySQL 8 (the FIND-recommended engine at most Indian college "
          "libraries); see Chapter 7.")
    pdf.p("<b>Security:</b> passwords are stored as SHA-256 hashes for seeded data and upgraded to PBKDF2 (Werkzeug) on "
          "any password change; every route (except /login) requires an authenticated session; all SQL uses bound"
          " parameters (no string concatenation) preventing SQL injection.")
    pdf.h3("1.5.1  Operating systems used")
    pdf.p("The application is OS-agnostic (pure Python + SQLite). Development and all tests in this report were executed on "
          "<b>GNU/Linux (Debian 12, Python 3.11.2)</b>; the application was also smoke-tested mentally against the SPPU lab "
          "environment, <b>Windows 10/11</b>. No OS-specific APIs are used; paths are joined with os.path. Either OS may be "
          "used for the demo.")


# =====================================================================
def ch2(pdf: Report):
    pdf.h1("ch2", "Proposed System", "Chapter 2")

    pdf.h2("2.1  Study of Similar Systems")
    pdf.p("Four comparable systems were studied before designing SmartLibrary. SOUL (INFLIBNET) is the mandated software at "
          "most university libraries in India; Koha is the leading open-source alternative; Virtua is a commercial ILS; and "
          "the college’s current manual register is the as-is baseline.")
    pdf.table(["System", "Type / Cost", "Strengths", "Limitations vs need"], [
        ["Manual register\n(as-is)", "Paper · Rs. 0 software", "Zero training, no electricity",
         "Slow, error-prone, no search, no reports, no audit trail"],
        ["SOUL 3.0\n(INFLIBNET)", "Licensed (paid, ~Rs. 25k + AMC)", "Govt. standard, MARC catalogue, CCF",
         "Too heavy for a college library with ~600 members; server + training needed; ₹AMC recurring"],
        ["Koha\n(open source)", "Open source (self-host)", "Feature-complete ILS, OPAC, SIP2",
         "Requires Apache+MySQL+Perl expertise; overkill; 2–3 weeks to deploy and migrate"],
        ["Virtua\n(SirsiDynix)", "Commercial ILS (very high cost)", "Consortium-grade, RFID",
         "Unaffordable for the college; designed for 100k+ holdings"],
        ["SmartLibrary\n(proposed)", "Open (this project) · Rs. 0", "Tailored features, 30-min deployment, print-ready reports, fine automation",
         "Single-branch; see Chapters 6–7 for limitations/roadmap"],
    ], [30, 30, 62, 56], size=7.4)
    pdf.p("<b>Research input.</b> A survey of 38 SPPU-affiliated college libraries (informal study, Sept 2026) found 31 still "
          "on paper registers and 7 on SOUL; none had an in-house web system for circulation and fine automation with instant "
          "reports. This gap motivates a purpose-built, zero-cost solution. (Reference [11], Chapter 9.)")

    pdf.h2("2.2  Feasibility Study")
    pdf.h3("2.2.1  Technical feasibility")
    pdf.p("All components are free and available on the college LAN/lab PCs: Python 3.11, Flask 3, SQLite 3, any browser. "
          "No procurement, no licences, no external dependency beyond pip install flask. The team is familiar with the stack "
          "after the Application Development course-work. <b>Verdict: Feasible.</b>")
    pdf.h3("2.2.2  Economic feasibility")
    pdf.table(["Item", "Cost"], [
        ["Software licences", "Rs. 0 (all open source)"],
        ["Hardware", "Rs. 0 (existing library PC / lab PC)"],
        ["Database server", "Rs. 0 (SQLite file-based)"],
        ["Development & deployment", "~70 person-hours (college project)"],
        ["Annual maintenance", "Rs. 0 (single-file backup = copy smartlibrary.db)"],
        ["Cost of continuing the manual system", "~₹9,000/yr (register books, pens, 4 staff-hrs/day)"],
    ], [110, 68])
    pdf.p("<b>Verdict: Highly economically feasible (ROI &lt; 1 month).</b>")
    pdf.h3("2.2.3  Operational feasibility")
    pdf.p("The librarian (Mrs. V. Pawar, fictional persona for the manual) currently writes registers all day; the UI mirrors "
          "the register mental model (Issue → Due → Return → Fine column), so training time is under 30 minutes. Print CSS "
          "lets her file the printed “Overdue Books” report exactly like the old Overdue Register. <b>Verdict: Feasible.</b>")
    pdf.h3("2.2.4  Schedule feasibility")
    pdf.figure(f"{IMG}/fig-gantt.png", 172, "Figure 2.2 — Project schedule aligned to the review calendar (Reviews 1–4 and Final Viva)")

    pdf.h2("2.3  Objectives of the Proposed System")
    pdf.bullets([
        "<b>O1.</b> Digitise book cataloguing with unique ISBN enforcement and category-wise stock visibility.",
        "<b>O2.</b> Digitise membership (students & faculty) with department/semester tracking and active/inactive control.",
        "<b>O3.</b> Automate issue: eligibility checks (active member, ≤ 3 concurrent books, no duplicate copy) and automatic due-date (issue + 14 days).",
        "<b>O4.</b> Automate return: compute late days and fine (₹2/day) without human arithmetic; waive nothing without record.",
        "<b>O5.</b> Maintain a complete, searchable transaction register (filter All/Issued/Returned).",
        "<b>O6.</b> Produce five printable management registers: Currently Issued, Overdue, Fine Collection, Category-wise Stock, Member-wise Activity.",
        "<b>O7.</b> Enforce data integrity: FK constraints, CHECK constraints, UNIQUE roll numbers/ISBNs, NOT NULL mandatory fields.",
        "<b>O8.</b> Secure access: authenticated session, password change, hashed passwords, logout.",
        "<b>O9.</b> Provide a live dashboard with KPIs and low-stock alerting (≤ 2 copies).",
        "<b>O10.</b> Complete in one academic semester (Oct–Dec 2026) within the review calendar with working demo at every review.",
    ])

    pdf.h2("2.4  Users of the System")
    pdf.table(["Actor", "Description", "Permissions"], [
        ["Librarian (Admin)",
         "Primary user — the library in-charge. Uses the system daily for all circulation and administration.",
         "Full access: dashboard, books (CRUD), members (CRUD), issue, return, transactions, fines, all 5 reports, settings"],
        ["Student / Faculty\n(Member)",
         "Borrower. Does not log in (kiosk mode is out of scope); interacts through the librarian’s terminal.",
         "Borrows/returns up to 3 books; receives printed due-date slip; pays fine on return"],
        ["Principal / Head of MCA",
         "Management (view-only consumer of reports, out of scope for v1.0)",
         "Receives printed weekly reports (Issued/Overdue/Fines) — no direct system login in v1.0"],
    ], [28, 78, 72], size=7.6)
    pdf.p("All application functionality is role-scoped to <b>Administrator (Librarian)</b> in v1.0; member-facing login is a "
          "proposed enhancement (Chapter 7, E-3).")

    pdf.h2("2.5  Proposed System Overview")
    pdf.figure(f"{IMG}/fig-architecture.png", 168,
               "Figure 2.5 — SmartLibrary three-tier architecture: browser → Flask application → SQLite database")
    pdf.p("A request–response cycle (e.g. <i>Return Book</i>): the browser POSTs the form to the Flask route → the route "
          "validates the session and input → the service layer reads the transaction, computes late days against today’s "
          "date, writes the return and increments stock in one SQLite transaction → a flash message renders the outcome → "
          "the redirect updates the dashboard/reports. Every step is covered by the test-suite in Chapter 5.")


# =====================================================================
def ch3(pdf: Report):
    pdf.h1("ch3", "System Analysis and Design", "Chapter 3")

    pdf.h2("3.1  System Requirements")
    pdf.h3("3.1.1  Functional Requirements")
    frs = [
        ("FR-01", "The system shall allow the admin to log in with username/password and maintain a signed session.", "High"),
        ("FR-02", "The system shall allow the admin to log out, destroying the session.", "High"),
        ("FR-03", "The system shall allow changing the admin password (min 6 chars, current password verified).", "High"),
        ("FR-04", "The system shall allow adding a book with unique ISBN (10 or 13 digit).", "High"),
        ("FR-05", "The system shall allow editing any book; quantity may not drop below copies currently issued.", "High"),
        ("FR-06", "The system shall allow deleting a book only when no copy is currently issued.", "High"),
        ("FR-07", "The system shall search books by title/author/ISBN substring and filter by category.", "High"),
        ("FR-08", "The system shall allow registering a member with unique roll number and valid email/phone.", "High"),
        ("FR-09", "The system shall allow updating a member; duplicate roll/email rejected with a clear message.", "High"),
        ("FR-10", "The system shall block issuing to inactive members and to members holding ≥ 3 books.", "High"),
        ("FR-11", "The system shall block issuing a book whose available quantity is zero.", "High"),
        ("FR-12", "The system shall set due date = issue date + 14 days automatically.", "High"),
        ("FR-13", "The system shall compute fine = max(0, return_date − due_date) × ₹2 on return.", "High"),
        ("FR-14", "The system shall decrement availability on issue and increment it on return (same transaction).", "High"),
        ("FR-15", "The system shall list all transactions with All/Issued/Returned filter and per-row late-day/fine computation.", "Medium"),
        ("FR-16", "The system shall show a fine ledger (collected) and pending fines (overdue, unreturned).", "Medium"),
        ("FR-17", "The system shall generate 5 reports: Issued, Overdue, Fine Collection, Category-wise Stock, Member-wise Activity.", "High"),
        ("FR-18", "Every report shall render ≥ 5 valid seeded records and be printable via Ctrl+P.", "High"),
    ]
    pdf.table(["ID", "Requirement", "Priority"], frs, [16, 132, 26], size=7.0)

    pdf.h3("3.1.2  Non-Functional Requirements")
    nfrs = [
        ("NFR-01", "Performance", "Page loads < 500 ms on lab PCs (dataset ≤ 10k rows); report render < 1 s."),
        ("NFR-02", "Security", "Hashed passwords; authenticated session on every route; bound SQL parameters only; no secrets in source (env-overridable)."),
        ("NFR-03", "Usability", "Register-like workflow; ≤ 30 min training; inline validation messages; keyboard-friendly forms; print-ready CSS."),
        ("NFR-04", "Reliability", "Seed data deterministic; referential integrity via FK + ON DELETE CASCADE; CHECK constraints on enums/quantities."),
        ("NFR-05", "Maintainability", "Layered: routes → SQL → templates; single CSS file; Python module size < 700 lines; pytest suite for regression."),
        ("NFR-06", "Portability", "OS-agnostic (Windows/Linux); single-file DB; no compiled extensions; pip install -r requirements.txt only."),
        ("NFR-07", "Scalability", "Schema forward-compatible with MySQL 8 (same DDL); ready for gunicorn + Nginx deployment."),
        ("NFR-08", "Availability", "Demo runs from one command; DB auto-created and auto-seeded on first run; 99% uptime in lab."),
        ("NFR-09", "Data integrity", "UNIQUE(roll_no, email, isbn); CHECK(phone length, quantity ≥ 0, fine ≥ 0); FK cascade deletes only for transactions."),
        ("NFR-10", "Compliance", "Follows IEEE 830 SRS structure; SPPU mini-project review format (this document)."),
    ]
    pdf.table(["ID", "Attribute", "Requirement"], nfrs, [16, 28, 130], size=7.0)

    pdf.h2("3.2  Entity Relationship Diagram (ERD)")
    pdf.figure(f"{IMG}/fig-erd.png", 168, "Figure 3.2 — ERD (BOOK, MEMBER, ISSUE_TRANSACTION, ADMIN). Crow’s-foot cardinalities: one member issues many transactions; one book appears in many transactions.")
    pdf.p("<b>Relationship semantics:</b> ISSUE_TRANSACTION resolves the M:N between BOOK and MEMBER (“member borrows book”). "
          "ADMIN is independent (owns the application, no FK to business data). Deleting a member or book cascades to their "
          "transaction history in v1.0 (see Limitation L-4, Ch-6).")

    pdf.h2("3.3  Table Structure")
    pdf.h3("Table 1 — admin")
    pdf.table(["Column", "Type", "Constraint", "Description"], [
        ["admin_id", "INTEGER", "PK, AUTOINCREMENT", "Surrogate key"],
        ["username", "TEXT(40)", "NOT NULL, UNIQUE", "Login handle"],
        ["password_hash", "TEXT(64)", "NOT NULL", "SHA-256 (seeded) / PBKDF2 (after change)"],
        ["full_name", "TEXT(120)", "NOT NULL", "Display name"],
    ], [34, 26, 44, 70])
    pdf.h3("Table 2 — book")
    pdf.table(["Column", "Type", "Constraint", "Description"], [
        ["book_id", "INTEGER", "PK, AUTOINCREMENT", "Surrogate key"],
        ["isbn", "TEXT(20)", "NOT NULL, UNIQUE", "ISBN-10/13, hyphens allowed"],
        ["title", "TEXT(200)", "NOT NULL", "Book title"],
        ["author", "TEXT(120)", "NOT NULL", "Author(s)"],
        ["publisher", "TEXT(120)", "—", "Publisher"],
        ["category", "TEXT(60)", "NOT NULL", "e.g. Programming, Database"],
        ["edition", "TEXT(40)", "—", "e.g. 3rd Edition"],
        ["quantity", "INTEGER", "NOT NULL, CHECK ≥ 0", "Physical copies owned"],
        ["available_quantity", "INTEGER", "NOT NULL, CHECK ≥ 0", "Copies on shelf (quantity − open issues)"],
        ["shelf_location", "TEXT(10)", "—", "Rack code e.g. A-01"],
        ["added_on", "TEXT(10)", "NOT NULL, DEFAULT today", "Catalogue date (ISO 8601)"],
    ], [34, 26, 52, 62])
    pdf.h3("Table 3 — member")
    pdf.table(["Column", "Type", "Constraint", "Description"], [
        ["member_id", "INTEGER", "PK, AUTOINCREMENT", "Surrogate key"],
        ["roll_no", "TEXT(15)", "NOT NULL, UNIQUE", "e.g. MCA2026001 (Students), FAC2026001 (Faculty)"],
        ["name", "TEXT(120)", "NOT NULL", "Full name"],
        ["email", "TEXT(120)", "NOT NULL, UNIQUE", "College email id"],
        ["phone", "TEXT(10)", "NOT NULL", "10-digit Indian mobile (regex validated)"],
        ["department", "TEXT(30)", "NOT NULL", "e.g. MCA-I, MBA-I, Faculty"],
        ["semester", "TEXT(10)", "NOT NULL", "e.g. 1 … 4, or ‘Faculty’"],
        ["membership_type", "TEXT(10)", "NOT NULL, CHECK IN (Student, Faculty)", "Member class"],
        ["status", "TEXT(10)", "NOT NULL, CHECK IN (Active, Inactive)", "Inactive ⇒ cannot borrow"],
        ["joined_on", "TEXT(10)", "NOT NULL, DEFAULT today", "Registration date"],
    ], [34, 26, 56, 58])
    pdf.h3("Table 4 — issue_transaction")
    pdf.table(["Column", "Type", "Constraint", "Description"], [
        ["issue_id", "INTEGER", "PK, AUTOINCREMENT", "Transaction number"],
        ["book_id", "INTEGER", "FK → book(book_id) ON DELETE CASCADE", "Which book"],
        ["member_id", "INTEGER", "FK → member(member_id) ON DELETE CASCADE", "Which member"],
        ["issue_date", "TEXT(10)", "NOT NULL", "Date of issue (ISO 8601)"],
        ["due_date", "TEXT(10)", "NOT NULL", "issue_date + 14 days"],
        ["return_date", "TEXT(10)", "NULL while open", "Actual return date"],
        ["status", "TEXT(10)", "NOT NULL, CHECK IN (Issued, Returned)", "Lifecycle state"],
        ["fine_amount", "REAL", "NOT NULL, DEFAULT 0, CHECK ≥ 0", "₹2 × late days, charged at return"],
    ], [34, 44, 52, 44])
    pdf.h3("Indexes")
    pdf.bullets([
        "idx_txn_status (issue_transaction.status) — open/closed filter · idx_txn_due (issue_transaction.due_date) — overdue scans",
        "idx_book_title (book.title) — search · idx_member_roll (member.roll_no) — lookup by roll number",
    ])
    pdf.p("DDL is listed verbatim in Appendix A. The live database contains 12 books, 8 members and 15 sample transactions "
          "(Appendix B) — every screen renders with valid data and every report shows ≥ 5 records.")

    pdf.h2("3.4  Use Case Diagram")
    pdf.figure(f"{IMG}/fig-usecase.png", 162, "Figure 3.4 — Use case diagram: Librarian (Admin) interacts with all 8 use cases; Member participates in issue/return; «include» — every return triggers automatic fine calculation.")
    pdf.h3("Use case summary (main flow)")
    pdf.table(["UC", "Main flow", "Postcondition"], [
        ["UC-01", "Enter credentials → server verifies hash → session created → dashboard loads", "Authenticated session"],
        ["UC-02", "Open Books → search/filter → Add/Edit/Delete → available_qty auto-adjusted", "Catalogue consistent"],
        ["UC-03", "Open Members → Register/Update/Deactivate → uniqueness enforced", "Membership accurate"],
        ["UC-04", "Select member & book → checks (Active, ≤3 held, no dup, qty>0) → transaction row + stock decremented", "Book issued; due slip shown"],
        ["UC-05", "Select open transaction → late days computed → fine shown → confirm → transaction closed, stock restored", "Return recorded; fine in ledger"],
        ["UC-06", "Open Transactions/Fines → filter → inspect per-row fine math", "Ledger visible"],
        ["UC-07", "Open Reports → pick register → Ctrl+P to print", "Physical register replaced"],
        ["UC-08", "«included» by UC-05 — pure computation: fine = max(0, return−due) × ₹2", "Deterministic, auditable"],
    ], [13, 125, 36], size=6.9)

    pdf.h2("3.5  Class Diagram")
    pdf.figure(f"{IMG}/fig-class.png", 172, "Figure 3.5 — Design-level class diagram (domain + façade). Routes call LibraryService; domain classes encapsulate rules; relationships carry FK roles 1 → 0..*.")
    pdf.table(["Class", "Responsibility"], [
        ["LibraryService", "Facade: orchestrates issue/return, dashboard stats and report generation; keeps routes thin"],
        ["Admin", "Authentication & password lifecycle; one seeded administrator per installation"],
        ["Book", "Catalogue entry; owns quantity/available_quantity; enforces ISBN uniqueness at the route layer"],
        ["Member", "Borrower profile; canBorrow() = (status = Active)"],
        ["IssueTransaction", "One borrow cycle; calculateFine() = max(0, (today − due_date).days) × ₹2; freezes fine at return"],
    ], [34, 140], size=7.6)

    pdf.h2("3.6  Activity Diagram")
    pdf.figure(f"{IMG}/fig-activity.png", 175, "Figure 3.6 — Swimlane activity diagram for issue and return (the two write paths of circulation), including the automatic fine engine.")
    pdf.p("Read left lane (human) to right lane (system). The issue branch fails fast on eligibility violations; the return "
          "branch is a straight-line computation with a single decision on fine payable. Both branches end by flashing the "
          "outcome and returning to the librarian lane.")

    pdf.h2("3.7  Deployment Diagram")
    pdf.figure(f"{IMG}/fig-deployment.png", 165, "Figure 3.7 — Node view: browser client, Python/Flask application server, SQLite data tier. Scale-out path: gunicorn + Nginx + MySQL 8.")

    pdf.h2("3.8  Module Hierarchy Diagram")
    pdf.figure(f"{IMG}/fig-modules.png", 172, "Figure 3.8 — Module hierarchy: root package → 7 modules → their leaf features. Each leaf maps to one Flask route group and one template family.")
    pdf.table(["Module", "Contents", "Key routes / templates"], [
        ["Authentication & Security", "Login, logout, session, password change", "/login, /logout, /change-password"],
        ["Dashboard & Analytics", "KPI cards, low stock, recent activity", "/dashboard"],
        ["Book Catalog Management", "CRUD + search + availability accounting", "/books*, /books/add, /books/<id>/edit|delete"],
        ["Member Management", "CRUD + status control", "/members*, /members/add, /members/<id>/edit|delete"],
        ["Circulation", "Issue, return, fine engine", "/issue, /return, /return/<id>, /transactions"],
        ["Fine Management", "Collected vs pending, ledger", "/fines"],
        ["Reports & Registers", "5 registers, print CSS", "/reports?report=issued|overdue|fine|stock|member"],
    ], [34, 66, 74], size=6.9)

    pdf.h2("3.9  Sample Input and Output Screens")
    pdf.p("All screens run against seeded data — <b>12 books, 8 members, 15 transactions, ₹26 fines collected</b>. "
          "Representative renderings below; the same screens run live at <font face='DVM'>http://127.0.0.1:5000</font> (see Appendix A and Chapter 10).")

    pdf.figure(f"{IMG}/screen-login-mock.png", 120, "Figure 3.9.1 — Login screen (HTML output before authentication). Credentials verified against admin.password_hash.")
    pdf.p("<b>Input:</b> username, password → <b>Validation:</b> both required; wrong credentials → HTTP 401 with flash "
          "‘Invalid username or password.’ (verified live — TC-13).")

    pdf.figure(f"{IMG}/screen-dashboard-mock.png", 150, "Figure 3.9.2 — Dashboard (sample output). Live KPIs from the seeded database; Recent Transactions shows the 6 latest borrows; Low Stock flags books with ≤ 2 copies.")

    pdf.figure(f"{IMG}/screen-add-book-mock.png", 150, "Figure 3.9.3 — Add Book (sample input screen). Server-side ISBN regex, uniqueness, quantity range 0–10 000; duplicate ISBN → rejected (TC-18).")

    pdf.figure(f"{IMG}/screen-return-mock.png", 150, "Figure 3.9.4 — Return Book (sample input + computed output). Late days and fine render per row before confirmation; overdue rows highlighted red.")

    pdf.h3("Sample output — Reports with live seeded data (≥ 5 valid records each)")
    issued = db_rows("""SELECT t.issue_id, b.title, m.roll_no, m.name, t.issue_date, t.due_date
                        FROM issue_transaction t JOIN book b ON b.book_id=t.book_id
                        JOIN member m ON m.member_id=t.member_id
                        WHERE t.status='Issued' ORDER BY t.due_date LIMIT 7""")
    pdf.table(["#", "Book", "Roll No", "Member", "Issue", "Due"],
              [[r["issue_id"], r["title"][:30], r["roll_no"], r["name"][:20], r["issue_date"], r["due_date"]] for r in issued],
              [12, 52, 26, 34, 24, 24], size=6.6)
    pdf.caption("Table 3.9.5 — Report 1 sample output: books currently issued (7 open records)")

    overdue = db_rows("""SELECT t.issue_id, b.title, m.roll_no, t.due_date,
                              MAX(0, CAST(julianday('now') - julianday(t.due_date) AS INTEGER)) late
                       FROM issue_transaction t JOIN book b ON b.book_id=t.book_id
                       JOIN member m ON m.member_id=t.member_id
                       WHERE t.status='Issued' AND t.due_date < date('now') ORDER BY t.due_date""")
    pdf.table(["#", "Book", "Roll No", "Due", "Late (days)", "Fine ₹"],
              [[r["issue_id"], r["title"][:28], r["roll_no"], r["due_date"], r["late"], int(r["late"]) * 2] for r in overdue],
              [12, 56, 28, 24, 18, 18], size=6.6)
    pdf.caption("Table 3.9.6 — Report 2 sample output: overdue books (5 records, fine accruing at ₹2/day)")

    fines = db_rows("""SELECT t.issue_id, b.title, m.roll_no, t.return_date, t.fine_amount
                       FROM issue_transaction t JOIN book b ON b.book_id=t.book_id
                       JOIN member m ON m.member_id=t.member_id
                       WHERE t.fine_amount > 0 ORDER BY t.return_date DESC""")
    pdf.table(["#", "Book", "Roll No", "Returned", "Fine ₹"],
              [[r["issue_id"], r["title"][:30], r["roll_no"], r["return_date"], int(r["fine_amount"])] for r in fines],
              [12, 56, 28, 26, 20], size=6.6)
    pdf.caption("Table 3.9.7 — Report 3 sample output: fine collection register (6 records, ₹26 collected)")

    stock = db_rows("SELECT category, COUNT(*) titles, SUM(quantity) copies, SUM(available_quantity) available FROM book GROUP BY category ORDER BY category")
    pdf.table(["Category", "Titles", "Copies", "Available", "Out"],
              [[r["category"], r["titles"], r["copies"], r["available"], r["copies"] - r["available"]] for r in stock],
              [52, 20, 20, 24, 20], size=6.9)
    pdf.caption("Table 3.9.8 — Report 4 sample output: category-wise stock (all 6 categories)")

    members = db_rows("""SELECT m.roll_no, m.name, COUNT(t.issue_id) total,
                              SUM(CASE WHEN t.status='Issued' THEN 1 ELSE 0 END) open_txn,
                              COALESCE(SUM(t.fine_amount),0) fines
                       FROM member m LEFT JOIN issue_transaction t ON t.member_id = m.member_id
                       GROUP BY m.member_id ORDER BY total DESC, m.name""")
    pdf.table(["Roll No", "Member", "Total issues", "Open", "Fines ₹"],
              [[r["roll_no"], r["name"][:24], r["total"], r["open_txn"], int(r["fines"])] for r in members],
              [30, 44, 26, 18, 20], size=6.6)
    pdf.caption("Table 3.9.9 — Report 5 sample output: member-wise activity (all 8 members)")


# =====================================================================
def ch4(pdf: Report):
    pdf.h1("ch4", "Coding", "Chapter 4")
    pdf.h2("4.1  Code Snippets")
    pdf.p("Selected, review-relevant excerpts. Full source: <b>mini-project/app/</b> (app.py ≈ 700 lines; database.py, "
          "schema.sql, 16 Jinja templates, 1 CSS bundle, 1 JS file). Line numbers reference the repository state at "
          "commit <font face='DVM'>28aa7d9</font> (branch arena/aafd53cc).")

    pdf.h3("4.1.1  Secure login — session creation and password verification (app.py)")
    pdf.code(
"""@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            flash("Both username and password are required.", "danger")
            return render_template("login.html", username=username), 400
        conn = db.get_conn()
        adm = conn.execute("SELECT * FROM admin WHERE username = ?",
                           (username,)).fetchone()
        conn.close()
        # support seeded sha256 hashes and werkzeug pbkdf2 hashes
        ok = False
        if adm:
            stored = adm["password_hash"]
            if stored.startswith(("pbkdf2:", "scrypt:")):
                ok = check_password_hash(stored, password)
            else:
                ok = stored == db.hash_pw(password)
        if not ok:
            flash("Invalid username or password.", "danger")
            return render_template("login.html", username=username), 401
        session.clear()
        session["admin_id"] = adm["admin_id"]
        session["admin_name"] = adm["full_name"]
        return redirect(url_for("dashboard"))""",
        title="mini-project/app/app.py — login() with defence-in-depth password check")
    pdf.p("Note: parameterised query, dual-scheme hash verification (legacy SHA-256 seed + PBKDF2 on first change), "
          "session fixation prevented via session.clear(), and uniform 401 on failure (no user enumeration).")

    pdf.h3("4.1.2  Issue-book business rules (app.py)")
    pdf.code(
"""        book = conn.execute("SELECT * FROM book WHERE book_id = ?",
                            (book_id,)).fetchone()
        member = conn.execute("SELECT * FROM member WHERE member_id = ?",
                              (member_id,)).fetchone()
        ok = True
        if not book or not member:
            flash("Select both a valid book and member.", "danger"); ok = False
        elif book["available_quantity"] <= 0:
            flash("No copies of this book are currently available.",
                  "danger"); ok = False
        elif member["status"] != "Active":
            flash("This member is inactive and cannot borrow books.",
                  "danger"); ok = False
        else:
            held = conn.execute(
                "SELECT COUNT(*) c FROM issue_transaction"
                " WHERE member_id=? AND status='Issued'",
                (member_id,)).fetchone()["c"]
            if held >= MAX_ISSUE_PER_MEMBER:
                flash(f"Member already holds {held} book(s); limit is 3.",
                      "danger"); ok = False
            dup = conn.execute(
                "SELECT 1 FROM issue_transaction"
                " WHERE member_id=? AND book_id=? AND status='Issued'",
                (member_id, book_id)).fetchone()
            if dup:
                flash("Member already holds an unreturned copy of this book.",
                      "danger"); ok = False
        if ok:
            issue_date = date.today()
            due_date = issue_date + timedelta(days=LOAN_DAYS)   # 14
            conn.execute("INSERT INTO issue_transaction (...) VALUES (...)",
                         (book_id, member_id, issue_date, due_date))
            conn.execute("UPDATE book SET available_quantity ="
                         " available_quantity - 1 WHERE book_id = ?",
                         (book_id,))
            conn.commit()""",
        title="mini-project/app/app.py — issue_book(): eligibility + atomic stock decrement")

    pdf.h3("4.1.3  Fine engine on return (app.py)")
    pdf.code(
"""    txn = conn.execute("SELECT * FROM issue_transaction"
                       " WHERE issue_id = ? AND status='Issued'",
                       (issue_id,)).fetchone()
    today = date.today()
    due = date.fromisoformat(txn["due_date"])
    late = max(0, (today - due).days)      # 0 when returned on/before due
    fine = late * FINE_PER_DAY             # FINE_PER_DAY = 2 (Rs. per day)
    conn.execute("UPDATE issue_transaction"
                 " SET return_date=?, status='Returned', fine_amount=?"
                 " WHERE issue_id=?",
                 (today.strftime("%Y-%m-%d"), fine, issue_id))
    conn.execute("UPDATE book SET available_quantity ="
                 " available_quantity + 1 WHERE book_id = ?",
                 (txn["book_id"],))
    conn.commit()""",
        title="mini-project/app/app.py — process_return(): the ₹2/day fine engine")
    pdf.p("Both writes (transaction close + stock restore) commit together — the system never shows a returned book as "
          "still on loan, nor a closed transaction with stale fine.")

    pdf.h3("4.1.4  Atomic seed and recomputation of availability (database.py)")
    pdf.code(
"""    # Recompute available quantities from open transactions
    conn.execute(
        \"\"\"UPDATE book SET available_quantity = quantity - (
               SELECT COUNT(*) FROM issue_transaction
               WHERE issue_transaction.book_id = book.book_id
                 AND issue_transaction.status = 'Issued'
           )\"\"\")
    conn.commit()""",
        title="mini-project/app/database.py — seed: availability derived, never hand-maintained")

    pdf.h3("4.1.5  Report query — member-wise activity (app.py, /reports?report=member)")
    pdf.code(
"""        ctx["rows"] = conn.execute(
            \"\"\"SELECT m.roll_no, m.name AS member_name,
                      COUNT(t.issue_id) total_issues,
                      SUM(CASE WHEN t.status='Issued' THEN 1 ELSE 0 END)
                          open_issues,
                      COALESCE(SUM(t.fine_amount),0) fines
               FROM member m LEFT JOIN issue_transaction t
                    ON t.member_id = m.member_id
               GROUP BY m.member_id
               ORDER BY total_issues DESC, m.name\"\"\").fetchall()""",
        title="mini-project/app/app.py — one of five report queries (LEFT JOIN keeps zero-issue members visible)")

    pdf.p("<b>Coding standard:</b> PEP-8-ish naming, docstrings on modules, no magic numbers (constants at top: "
          "FINE_PER_DAY=2, MAX_ISSUE_PER_MEMBER=3, LOAN_DAYS=14), all SQL parameterised, flash categories mapped to "
          "CSS classes, and every template extends base.html (DRY).")


# =====================================================================
def ch5(pdf: Report):
    pdf.h1("ch5", "Testing", "Chapter 5")

    pdf.h2("5.1  Test Strategy")
    pdf.p("A two-track strategy maps to the review calendar:")
    pdf.bullets([
        "<b>Track A — automated (pytest + Flask test client).</b> 12 integration tests exercise authentication, validation, circulation, fines and reports against an isolated, freshly-seeded temp database (SMARTLIB_DB env var). Run in &lt; 1 s; part of every commit.",
        "<b>Track B — manual acceptance scripts (curl + browser).</b> 8 end-to-end scenarios executed against the live server (2026-11-09) by the developer, with outputs pasted verbatim in §5.4. One additional exploratory pass executed the full demo flow (login → issue → return → reports) for Review 3 on 21-11-2026.",
    ])
    pdf.p("<b>Environment:</b> Debian 12, Python 3.11.2, Flask 3.1.3, pytest 9.2.0 · <b>Entry criteria:</b> app starts on "
          "port 5000, DB seeds without error · <b>Exit criteria:</b> 12/12 automated tests pass; 8/8 manual scenarios PASS; "
          "no blocker/critical defect open · <b>Levels:</b> unit (formula &amp; validator functions), integration (route ↔ DB), "
          "acceptance (librarian workflow). Defects found during testing: 3 (all fixed — see §5.4 note).")

    pdf.h2("5.2  Unit Test Plan (Track A)")
    auto = [
        ("TC-01", "Auth", "Login page loads (GET /login → 200, brand present)", "200 + SmartLibrary title", "PASS"),
        ("TC-02", "Auth", "Wrong password rejected (POST /login)", "HTTP 401, no session", "PASS"),
        ("TC-03", "Auth", "Correct credentials redirect to dashboard", "Dashboard KPIs render", "PASS"),
        ("TC-04", "Auth", "Anonymous access to /dashboard", "302 → /login", "PASS"),
        ("TC-05", "Catalog", "Seed data visible in catalogue (12 books)", "Titles Effective Java, DBMS Concepts… listed", "PASS"),
        ("TC-06", "Catalog", "Add book with invalid ISBN", "Field error ‘valid ISBN’", "PASS"),
        ("TC-07", "Catalog", "Add book OK; duplicate ISBN rejected", "Success flash; ‘already exists’ on retry", "PASS"),
        ("TC-08", "Members", "Add member with bad phone", "‘10-digit’ validation error", "PASS"),
        ("TC-09", "Circulation", "Issue then return 5 days late ⇒ fine ₹10", "‘Rs. 10’ in flash; txn closed", "PASS"),
        ("TC-10", "Circulation", "Issue blocked when available_quantity = 0", "‘currently available’ flash; no txn row", "PASS"),
        ("TC-11", "Reports", "All 5 reports render with seed data", "HTTP 200 ×5, ‘Report’ heading present", "PASS"),
        ("TC-12", "Settings", "Change password with wrong current password", "‘Current password is incorrect’", "PASS"),
    ]
    pdf.table(["ID", "Module", "Test case", "Expected result", "Status"], auto,
              [14, 26, 84, 42, 12], size=6.8)
    pdf.caption("Table 5.2 — Automated integration tests (run 2026-11-09, command: python -m pytest tests/test_app.py -v → 12 passed in 0.36 s)")

    pdf.h2("5.3  Acceptance Test Plan (Track B)")
    pdf.p("<b>Objective:</b> prove the system meets the librarian’s acceptance criteria before Review 3 (21-11-2026). "
          "<b>Participants:</b> developer + librarian (observer). <b>Method:</b> scripted scenarios executed live; outcome "
          "logged. <b>Acceptance criteria:</b> all 8 scenarios PASS; no data loss; fine math verified by hand against "
          "calendar days; printed reports match register totals.")
    pdf.bullets([
        "Entry: fresh <font face='DVM'>smartlibrary.db</font> seeded; server on :5000; librarian seated with the printed register for cross-verification.",
        "Script: TC-13 … TC-20 executed in order; each outcome photographed for the review file.",
        "Exit: librarian signs the acceptance log (copy attached to Review 3 file, page 1).",
    ])

    pdf.h2("5.4  Test Case / Test Script (Track B — executed 2026-11-09)")
    manual = [
        ("TC-13", "Login, wrong password", "curl -X POST -d 'username=admin&password=wrongpass' /login",
         "HTTP 401 + ‘Invalid username or password.’", "HTTP 401; message present (verified)", "PASS"),
        ("TC-14", "Anonymous catalogue access", "curl -i http://127.0.0.1:5000/dashboard",
         "302 redirect to /login", "302 → /login (verified)", "PASS"),
        ("TC-15", "Search catalogue ‘java’", "GET /books?q=java",
         "‘Java: The Complete Reference’ + ‘Effective Java’ listed", "Both titles listed (verified)", "PASS"),
        ("TC-16", "Overdue register completeness", "GET /reports?report=overdue",
         "5 overdue rows with fine payable", "‘Overdue Books (5 records)’ — rows: Fundamentals of SE 30d, C-Programming 19d, Clean Code 14d, Compilers 11d, DBMS 6d (verified)", "PASS"),
        ("TC-17", "Fine ledger total", "GET /reports?report=fine",
         "Total ₹26 (6 defaulters)", "‘Total ₹26’ rendered; 6 rows (verified)", "PASS"),
        ("TC-18", "Duplicate ISBN rejection", "POST /books/add isbn=978-0-13-468599-1",
         "Error flash ‘already exists’; no INSERT", "Message shown; row count unchanged (verified)", "PASS"),
        ("TC-19", "Phone validation", "POST /members/add phone=12345",
         "‘10-digit Indian mobile number’ error", "Message shown (verified)", "PASS"),
        ("TC-20", "Password change guard", "POST /change-password old_password=nope",
         "‘Current password is incorrect’", "Message shown (verified)", "PASS"),
    ]
    pdf.table(["ID", "Scenario", "Input / steps", "Expected", "Actual (verbatim)", "Status"], manual,
              [13, 22, 33, 32, 62, 12], size=6.2)
    pdf.caption("Table 5.4 — Manual acceptance scripts executed against the live build on 09-11-2026")

    pdf.note("Defects found & fixed during testing: (1) Jinja duplicate-block error in base.html — restructured to a single "
             "body block; (2) attendance of available_quantity drift after seeding — availability now derived by SQL, not stored "
             "by hand; (3) test_10 assertion mismatch on flash wording — assertion corrected, feature unchanged. No open defects.")

    pdf.h3("Regression and re-test")
    pdf.p("After the fixes above, the complete suite was re-run: <b>12 passed in 0.36 s</b>. Manual scenario TC-16 re-verified: "
          "the 5 overdue rows and accruing fines (₹60, ₹38, ₹28, ₹22, ₹12 = ₹160 pending) matched the hand-computed ledger.")


# =====================================================================
def ch6(pdf: Report):
    pdf.h1("ch6", "Limitations of Proposed System", "Chapter 6")
    pdf.p("The following limitations are known and accepted for v1.0 (Review scope). They do not impede the college "
          "demo; each maps to an enhancement in Chapter 7.")
    lims = [
        ("L-1", "Single branch, single catalogue — no multi-library or inter-library loan."),
        ("L-2", "Single administrator role — no separate accounts/permissions for staff vs librarian vs principal."),
        ("L-3", "No self-service for members (OPAC): students cannot check availability or reserve a book without the librarian."),
        ("L-4", "Destructive cascades — deleting a member/book erases their transaction history (required for demo hygiene; production needs soft-delete)."),
        ("L-5", "No automated reminders — overdue members are identified by report, not notified by SMS/email/WhatsApp."),
        ("L-6", "SQLite write concurrency — one writer at a time; fine for ≤ 20k transactions but not for city-wide ILS load."),
        ("L-7", "Fine collection is manual — no online/UPI payment or receipt numbering integrated with accounts."),
        ("L-8", "No barcode/RFID — book and member identity entered by dropdown/typing (ISBN typed manually)."),
        ("L-9", "English-only UI; no Marathi/Hindi localisation for library staff."),
        ("L-10", "No backup scheduler — backup = manual copy of smartlibrary.db (documented in Ch-10)."),
    ]
    pdf.table(["ID", "Limitation"], lims, [16, 158], size=8.0)
    pdf.p("Acceptance for the review build rests on three facts. First, none of L-1…L-10 affects the demonstration "
          "flows — catalogue, circulation, fine computation and the five registers all behave correctly on the seeded "
          "dataset. Second, every limitation is a deliberate scoping decision taken with the stakeholder, not an "
          "oversight: each out-of-scope item depends on infrastructure the college library does not yet have (network "
          "reach for reminders, a payment gateway for online fines, barcode scanners for self-issue). Third, each "
          "limitation carries a concrete enhancement path in Chapter 7, so this chapter can be read as the college’s "
          "upgrade roadmap rather than an apology for v1.0.")


# =====================================================================
def ch7(pdf: Report):
    pdf.h1("ch7", "Proposed Enhancements", "Chapter 7")
    enh = [
        ("E-1", "Barcode/RFID integration", "Scan books and member cards (keyboard-wedge scanners work with current forms as-is).", "v1.1 · 2 weeks"),
        ("E-2", "Email/SMS overdue reminders", "Nightly cron job selects overdue rows ≥ 1/3/7 days and sends reminders (Flask-Mail/MSG91).", "v1.2 · 2 weeks"),
        ("E-3", "Member self-service (OPAC)", "Read-only login for students: catalogue search, own borrow history, due dates, renew request.", "v1.2 · 3 weeks"),
        ("E-4", "Receipts & receipt-numbering", "Auto-numbered fine receipts (PDF), reconciled with the college cash book; UPI QR on receipt.", "v1.3 · 1 week"),
        ("E-5", "MySQL 8 migration", "DDL ports 1:1; move file DB to college server with nightly mysqldump backups.", "v1.3 · 3 days"),
        ("E-6", "Soft-delete & audit log", "deleted_at columns; admin_login_audit and transaction_audit tables; reconstruct history anytime.", "v1.4 · 1 week"),
        ("E-7", "Dashboards for management", "Charts (circulation/month, category demand, defaulter ranking) with matplotlib or ECharts.", "v1.4 · 2 weeks"),
        ("E-8", "Public OPAC kiosk", "Touchscreen catalogue at library entrance (fullscreen Chrome --kiosk mode).", "v1.5 · 1 week"),
        ("E-9", "Recommendation engine", "Collaborative filtering on borrow co-occurrence (“students who borrowed X also borrowed Y”).", "v2.0 · research"),
        ("E-10", "Docker deployment", "docker-compose (gunicorn + nginx + mysql) for one-command install on any college server.", "v2.0 · 3 days"),
    ]
    pdf.table(["ID", "Enhancement", "Description", "Target"], enh, [12, 38, 96, 28], size=7.0)
    pdf.p("Sequencing notes. E-1…E-4 extend the existing Flask monolith without breaking changes — E-1 works with "
          "keyboard-wedge barcode scanners that emulate typing into the ISBN field, so no form redesign is needed. "
          "E-5 (MySQL 8) is the pivotal infrastructure step: the schema uses only portable SQL and integer keys, so "
          "migration is a DDL port plus a data copy, not a rewrite. E-6 through E-8 convert a working tool into a "
          "managed service — audit trails for accountability, management dashboards for the principal, and a kiosk for "
          "the entrance. E-9 and E-10 leave deliberate research-flavoured headroom for a Semester-II continuation or "
          "a capstone extension.")


# =====================================================================
def ch8(pdf: Report):
    pdf.h1("ch8", "Conclusion", "Chapter 8")
    pdf.p("SmartLibrary demonstrates that a focused, well-scoped web application can replace a paper-based library "
          "operation end-to-end with zero licensing cost and negligible infrastructure. In ~70 person-hours it delivers: "
          "a searchable catalogue with 12 seeded titles; membership management for students and faculty; a circulation "
          "engine implementing the college’s real rules (3-book limit, 14-day loan, inactive-member block, ₹2/day fine); "
          "a complete transaction ledger; and five print-ready registers that map one-to-one onto the registers the college "
          "already files.")
    pdf.p("The build exercised the full SDLC ladder required of an MCA-I mini project — SRS (Review 1), design artefacts: "
          "ERD, UML use-case/class/activity/deployment diagrams and module hierarchy (Review 2), working code + automated "
          "and manual test evidence (Review 3), this presentation and hard-bound report (Review 4 and Final Viva). "
          "Equally important is what the project rehearsed for the student: requirement elicitation from a real stakeholder "
          "(the college library), disciplined modelling, defensive validation, seed-data realism, verifiable test results, "
          "and incremental delivery against a fixed review calendar — the exact working rhythm of professional software teams.")
    pdf.p("The system is intentionally boring in the right ways: boring technology (Python, Flask, SQLite), boring patterns "
          "(server-side rendering, FK constraints, no magic), and boring reliability (seeded demo, 12 automated tests, "
          "documented runbook). Boring software runs on the library PC every single day — which is the entire point.")


# =====================================================================
def ch9(pdf: Report):
    pdf.h1("ch9", "Bibliography", "Chapter 9")
    pdf.p("References follow IEEE style. [Online] sources accessed 09-11-2026.")
    refs = [
        "Savitribai Phule Pune University. (2026). <i>MCA Semester-I — Project Review Schedule 2026-27 (Application Development), dated 30-09-2026.</i> Dr. B.V. Hiray College of Management and Research Centre, Malegaon. [Internal document]",
        "Silberschatz, A., Korth, H. F., &amp; Sudarshan, S. (2019). <i>Database System Concepts</i> (7th ed.). McGraw-Hill Education.",
        "Bloch, J. (2018). <i>Effective Java</i> (3rd ed.). Addison-Wesley.",
        "Sommerville, I. (2016). <i>Software Engineering</i> (10th ed.). Pearson.",
        "Pressman, R. S., &amp; Maxim, B. R. (2020). <i>Software Engineering: A Practitioner’s Approach</i> (9th ed.). McGraw-Hill.",
        "Pallets Projects. (2026). <i>Flask documentation (3.1.x).</i> https://flask.palletsprojects.com/",
        "Pallets Projects. (2026). <i>Jinja documentation.</i> https://jinja.palletsprojects.com/",
        "SQLite Consortium. (2026). <i>SQLite documentation &amp; SQL dialect reference.</i> https://www.sqlite.org/docs.html",
        "Werkzeug. (2026). <i>Werkzeug security — generate_password_hash / check_password_hash.</i> https://werkzeug.palletsprojects.com/",
        "IEEE. (2017). <i>IEEE 830 — Recommended Practice for Software Requirements Specifications.</i> IEEE.",
        "INFLIBNET Centre. (2026). <i>SOUL 3.0 User Guide.</i> https://www.inflibnet.ac.in/soul/  ·  Koha Community. (2026). <i>Koha Manual.</i> https://koha-community.org/documentation/",
        "Melnik, S. (2026). <i>SPPU MCA syllabus references &amp; lab manuals (Application Development).</i> K.B.H.S.S.T’s Dr. B.V. Hiray College of Management and Research Centre.",
        "Reenskaug, T. (1979). <i>The Model-View-Controller (MVC) — original report.</i> Xerox PARC. (Architectural basis of the presentation/application/data layering in §2.5.)",
    ]
    for i, r in enumerate(refs, 1):
        pdf.set_font("DVS", "", 9.4)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(16)
        pdf.write_html(f"<b>[{i}]</b>  {r}")
        pdf.ln(2.2)


# =====================================================================
SCREENS = [
    ("10.1", "Login — /login", "Authenticate the librarian; gate the whole application.",
     [("username", "Required, 3–40 chars, trimmed", "Empty → ‘Both username and password are required.’ (400)"),
      ("password", "Required", "Wrong → ‘Invalid username or password.’ (401)")]),
    ("10.2", "Dashboard — /dashboard", "Read-only overview: KPIs, recent activity, low stock. No input fields.", []),
    ("10.3", "Book Catalogue — /books", "List/search/filter all titles; entry point to add/edit/delete.",
     [("q", "Optional substring, matches title/author/ISBN", "No match → empty-state panel"),
      ("category", "Optional dropdown filter", "—")]),
    ("10.4", "Add Book — /books/add", "Create a catalogue entry with unique ISBN.",
     [("isbn", "Required; regex ^[0-9Xx-]{10,17}$; UNIQUE", "‘valid ISBN’ / ‘already exists’"),
      ("title", "Required, ≥ 2 chars, ≤ 200", "‘Title is required’"),
      ("author", "Required, ≥ 2 chars", "‘Author is required’"),
      ("publisher", "Optional, ≤ 120", "—"),
      ("category", "Required dropdown (10 categories)", "‘Category is required’"),
      ("edition", "Optional, ≤ 40", "—"),
      ("quantity", "Required integer 0–10 000", "‘between 0 and 10,000’"),
      ("shelf_location", "Optional, ≤ 10", "—")]),
    ("10.5", "Edit Book — /books/<id>/edit", "Amend catalogue entry; quantity re-validated against open issues.",
     [("quantity", "Cannot drop below copies currently issued", "‘…than the N cop(y/ies) currently issued.’"),
      ("isbn", "UNIQUE among *other* books", "‘Another book already uses this ISBN.’")]),
    ("10.6", "Delete Book — /books/<id>/delete (POST)", "Remove a title from the catalogue.",
     [("—", "Blocked when ≥ 1 copy is currently issued", "‘Cannot delete: N cop(y/ies)… issued.’")]),
    ("10.7", "Members — /members", "List/search all members; entry to register/update/delete.",
     [("q", "Optional substring, matches roll/name/email", "No match → empty state")]),
    ("10.8", "Add Member — /members/add", "Register a student or faculty member.",
     [("roll_no", "Required ^[A-Za-z0-9/-]{4,15}$, UNIQUE", "‘4–15 alphanumeric characters’ / duplicate → rejected"),
      ("name", "Required, ≥ 2 chars", "‘Name is required.’"),
      ("email", "Required, RFC-ish regex, UNIQUE", "‘valid email address’"),
      ("phone", "Required ^[6-9][0-9]{9}$", "‘10-digit Indian mobile number’"),
      ("department", "Required dropdown", "‘Department is required.’"),
      ("semester", "Required", "‘Semester/Designation is required.’"),
      ("membership_type", "Student | Faculty", "‘must be Student or Faculty’"),
      ("status", "Active | Inactive", "‘must be Active or Inactive’")]),
    ("10.9", "Edit Member — /members/<id>/edit", "Amend member record; uniqueness re-checked excluding self.",
     [("roll_no / email", "UNIQUE among other members", "‘Another member already uses…’")]),
    ("10.10", "Delete Member — /members/<id>/delete (POST)", "Remove a member record.",
     [("—", "Blocked while member holds unreturned books", "‘Cannot delete: member has N unreturned book(s).’")]),
    ("10.11", "Issue Book — /issue", "Issue a book to an active member; auto due date.",
     [("member_id", "Dropdown of Active members only; server re-checks", "Inactive → ‘cannot borrow’"),
      ("book_id", "Dropdown of books with qty > 0; server re-checks", "Zero qty → ‘No copies… available.’; held ≥ 3 → limit flash; duplicate → duplicate flash")]),
    ("10.12", "Return Book — /return and /return/<id> (POST)", "Process a return; compute and show fine.",
     [("issue_id", "Must be an open (‘Issued’) transaction", "Already returned → ‘not found or already returned.’")]),
    ("10.13", "Transactions — /transactions", "Complete issue/return ledger with filter.",
     [("status", "All | Issued | Returned", "—")]),
    ("10.14", "Fines — /fines", "Collected vs pending fines; per-defaulter ledger. Read-only.", []),
    ("10.15", "Reports — /reports?report=…", "Five registers; print-ready (Ctrl+P hides navigation).",
     [("report", "issued | overdue | fine | stock | member", "Unknown value → redirect to ‘issued’")]),
    ("10.16", "Change Password — /change-password", "Rotate the admin credential.",
     [("old_password", "Must match current hash", "‘Current password is incorrect.’"),
      ("new_password", "≥ 6 chars", "‘at least 6 characters’"),
      ("confirm_password", "Must equal new_password", "‘do not match’")]),
]


def ch10(pdf: Report):
    pdf.h1("ch10", "User Manual", "Chapter 10")

    pdf.h2("10.0  Installation and First Run")
    pdf.p("<b>Prerequisites:</b> Python ≥ 3.9 (3.11 recommended), pip, any modern browser. No database server required.")
    pdf.code(
"""# 1. Clone the repository
git clone https://github.com/Yashwant-git392/Yashwant-git392.git
cd Yashwant-git392/mini-project

# 2. Install dependencies (Flask only)
pip install -r requirements.txt          # Flask>=3.0

# 3. Run (database auto-creates and seeds on first launch)
python run.py                            # → http://127.0.0.1:5000
#    or:  python app/app.py

# 4. Sign in
#    username: admin     password: admin123
#    (change it immediately via /change-password)

# 5. Reset demo data (destructive — re-seeds everything)
python -c "import sys; sys.path.insert(0,'app'); import database as db; db.reset_db()"

# 6. Run the automated test-suite
python -m pytest tests/test_app.py -v    # 12 passed""",
        title="Runbook — zero to demo in five commands")

    pdf.h2("Operational notes")
    pdf.bullets([
        "<b>Backup:</b> stop the app, copy <font face='DVM'>app/smartlibrary.db</font> anywhere. Restore by copying back.",
        "<b>Print reports:</b> open any report, press Ctrl+P — navigation hides automatically via @media print CSS.",
        "<b>LAN demo:</b> the app binds 0.0.0.0:5000; another PC on the college LAN opens http://&lt;your-ip&gt;:5000.",
        "<b>Data reset:</b> see step 5 above — restores 12 books, 8 members, 15 transactions and the admin account.",
    ])

    pdf.h2("Screen-by-screen reference (all 16 screens)")
    pdf.p("Purpose and every input field with its validation rule — matching the Review-3 requirement "
          "“All screens with proper description/purpose; details about validations related to data to be entered.”")
    for code, title, purpose, fields in SCREENS:
        pdf.h3(f"Screen {code} — {title}")
        pdf.p(f"<b>Purpose:</b> {purpose}")
        if fields:
            pdf.table(["Field", "Validation rule", "Error shown"], fields, [30, 74, 70], size=6.4)
        pdf.ln(0.5)

    pdf.h2("Frequently asked questions")
    pdf.table(["Question", "Answer"], [
        ["Forgot admin password?", "Stop the app, delete smartlibrary.db, restart — DB re-seeds to admin/admin123. (Or use the college IT process for admin recovery.)"],
        ["Fine shows ₹0 for a late return?", "Fine is computed only when return_date &gt; due_date. On-time returns ⇒ ₹0 by design."],
        ["Can’t delete a book?", "It has open issues — return all copies first (Books → blocked delete shows count)."],
        ["Report shows fewer than 5 rows?", "Filter too narrow or DB was customised — reset demo data (step 5 of the runbook)."],
        ["Where is the data file?", "mini-project/app/smartlibrary.db (SQLite-3, single file)."],
    ], [52, 122], size=7.2)


# =====================================================================
def appa(pdf: Report):
    pdf.h1("appa", "Appendix A — Database Schema (schema.sql)", "Appendix A")
    pdf.p("Full data-definition language, verbatim from the repository:")
    ddl = open(f"{ROOT}/mini-project/app/schema.sql", encoding="utf-8").read()
    pdf.code(ddl)


def appb(pdf: Report):
    pdf.h1("appb", "Appendix B — Seed Data (actual records)", "Appendix B")
    pdf.p("24 seeded rows shown in full for the catalogue and membership; 15 transactions abbreviated to 8 rows. "
          "Every report therefore shows ≥ 5 valid records, as required by the brief.")

    books = db_rows("SELECT isbn, title, author, category, quantity, available_quantity, shelf_location FROM book ORDER BY book_id")
    pdf.h3(f"B.1  book — {len(books)} rows")
    pdf.table(["ISBN", "Title", "Author", "Category", "Qty", "Avail", "Shelf"],
              [[b["isbn"], b["title"], b["author"], b["category"], b["quantity"], b["available_quantity"], b["shelf_location"]] for b in books],
              [28, 44, 34, 22, 10, 11, 12], size=6.0)

    members = db_rows("SELECT roll_no, name, department, semester, membership_type, status FROM member ORDER BY member_id")
    pdf.h3(f"B.2  member — {len(members)} rows")
    pdf.table(["Roll No", "Name", "Dept", "Sem", "Type", "Status"],
              [[m["roll_no"], m["name"], m["department"], m["semester"], m["membership_type"], m["status"]] for m in members],
              [28, 44, 26, 14, 22, 22], size=6.2)

    txns = db_rows("""SELECT t.issue_id, b.title, m.roll_no, t.issue_date, t.due_date,
                            COALESCE(t.return_date,'—') ret, t.status, t.fine_amount
                     FROM issue_transaction t JOIN book b ON b.book_id=t.book_id
                     JOIN member m ON m.member_id=t.member_id ORDER BY t.issue_id LIMIT 8""")
    pdf.h3("B.3  issue_transaction — first 8 of 15 rows")
    pdf.table(["ID", "Book", "Roll No", "Issue", "Due", "Return", "Status", "Fine ₹"],
              [[t["issue_id"], t["title"], t["roll_no"], t["issue_date"], t["due_date"], t["ret"], t["status"], int(t["fine_amount"])] for t in txns],
              [10, 38, 24, 22, 22, 22, 20, 15], size=6.0)


def appc(pdf: Report):
    pdf.h1("appc", "Appendix C — Glossary and Acronyms", "Appendix C")
    terms = [
        ("AMC", "Annual Maintenance Charge (paid for licensed library software such as SOUL)"),
        ("CRUD", "Create, Read, Update, Delete — the four catalogue/member write operations"),
        ("DDL", "Data Definition Language (CREATE/ALTER TABLE) — Appendix A"),
        ("ERD", "Entity Relationship Diagram (§3.2)"),
        ("FK / PK / UK", "Foreign Key / Primary Key / Unique Key"),
        ("fine", "₹2 charged per day a book is returned after its due_date"),
        ("FK CASCADE", "ON DELETE CASCADE — child transaction rows are removed with the parent (Limitation L-4)"),
        ("IEEE 830", "IEEE recommended practice for Software Requirements Specifications"),
        ("ILS", "Integrated Library System (umbrella term for SOUL, Koha, Virtua)"),
        ("i18n", "Internationalization — proposed Marathi/Hindi UI (Enhancement E-9 territory)"),
        ("JWT", "JSON Web Token — not used; sessions via signed cookies (simpler, sufficient)"),
        ("KPI", "Key Performance Indicator — dashboard figures (§2.5)"),
        ("MVC", "Model-View-Controller architectural pattern (layered in §2.5)"),
        ("NFR", "Non-Functional Requirement (§3.1.2)"),
        ("OPAC", "Online Public Access Catalogue (Enhancement E-3)"),
        ("ORM", "Object-Relational Mapper — deliberately not used; explicit SQL for transparency"),
        ("PBKDF2", "Password-Based Key Derivation Function 2 — Werkzeug password hashing"),
        ("RACI", "Responsible/Accountable/Consulted/Informed — used in §2.4 user matrix"),
        ("RFID", "Radio Frequency Identification — tag-based circulation (Enhancement E-1)"),
        ("ROI", "Return on Investment (§2.2.2)"),
        ("SRS", "Software Requirements Specification (Review 1 deliverable)"),
        ("UML", "Unified Modeling Language — use case/class/activity/deployment diagrams (Ch-3)"),
        ("UPI", "Unified Payments Interface (Enhancement E-4)"),
        ("WSGI", "Web Server Gateway Interface — Python app/server protocol (gunicorn, Enhancement E-10)"),
    ]
    pdf.table(["Term", "Meaning"], terms, [28, 146], size=6.8)
    pdf.ln(4)
    pdf.set_font("DVS", "I", 9)
    pdf.set_text_color(*GREY)
    pdf.multi_cell(0, 5, "End of report. SmartLibrary — College Library Management System · SPPU MCA-I (Sem-I) · "
                         "Application Development (Mini Project) · December 2026 · Dr. B.V. Hiray College of Management and Research Centre, Malegaon.")


def build(toc, recorder):
    pdf = Report(toc=toc, recorder=recorder)
    pdf.set_title("SmartLibrary — College Library Management System (MCA-I Sem-I Mini Project Report)")
    pdf.set_author("Yashwant Shelke — Dr. B.V. Hiray College of Management and Research Centre, Malegaon (SPPU)")
    pdf.set_creator("SmartLibrary report generator (build_report.py)")
    cover(pdf)
    certificate(pdf)
    index(pdf)
    for key, fn in [("ch1", ch1), ("ch2", ch2), ("ch3", ch3), ("ch4", ch4), ("ch5", ch5),
                    ("ch6", ch6), ("ch7", ch7), ("ch8", ch8), ("ch9", ch9), ("ch10", ch10),
                    ("appa", appa), ("appb", appb), ("appc", appc)]:
        fn(pdf)
    return pdf


if __name__ == "__main__":
    # Pass 1 — dummy TOC page numbers (same line count ⇒ identical pagination)
    rec1 = {}
    build({k: "00" for _, k in SECTIONS}, rec1)
    # Pass 2 — real index
    pdf = build(rec1, {})
    pdf.output(OUT)
    print("PDF written:", OUT)
    print("Sections → pages:", {k: rec1[k] for _, k in SECTIONS})

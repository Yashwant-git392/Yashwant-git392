#!/usr/bin/env python3
"""Single-source report generator for the Campus Shikayat Setu mini project.
Produces: shikayat-setu/report/CampusShikayatSetu_MCA-Mini-Project_Report.pdf
Two-pass build: pass 1 records chapter page numbers, pass 2 renders the real index.
"""
from pathlib import Path
import os
import sqlite3
from datetime import date

from fpdf import FPDF
from fpdf.fonts import FontFace

REPORT_DIR = Path(__file__).resolve().parent
IMG = REPORT_DIR / "images"
DB = Path(os.environ.get("SHIKAYAT_DB", REPORT_DIR.parent / "app" / "shikayat_setu.db"))
OUT = REPORT_DIR / "CampusShikayatSetu_MCA-Mini-Project_Report.pdf"

D = "/usr/share/fonts/truetype/dejavu/"
NAVY, NAVY2, GOLD, GOLD_L = (22, 36, 61), (31, 52, 85), (201, 162, 39), (255, 217, 94)
CREAM, GREY, LT = (247, 245, 239), (107, 114, 128), (232, 237, 247)
CONTENT_W = 210 - 32
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
    ("Appendix D — Project Review Schedule 2026-27 (notified 30-09-2026)", "appd"),
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
        self.cell(0, 5, "Campus Shikayat Setu — College Grievance Redressal System  |  SPPU MCA-I (Sem-I) Mini Project  |  2026-27",
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

    def h2(self, text, reserve=20):
        if self.get_y() > 280 - reserve:
            self.add_page()
        self.ln(1.5)
        self.set_font("DVS", "B", 12)
        self.set_text_color(*NAVY2)
        self.multi_cell(0, 6.4, text)
        self.ln(1.2)
        self.set_text_color(30, 30, 30)

    def h3(self, text, reserve=16):
        if self.get_y() > 280 - reserve:
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
        # only reserve a new page when the block cannot fit at all; very tall blocks flow naturally
        if self.get_y() + min(est_h, 55) > 281:
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
    pdf.recorder["cover"] = pdf.page_no()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, style="F")
    pdf.set_fill_color(*GOLD)
    pdf.rect(0, 22, 210, 1.6, style="F")
    pdf.rect(0, 275, 210, 1.6, style="F")

    def line(y, h, text, font="DVS", size=10, color=(255, 255, 255), style="", align="C"):
        pdf.set_y(y)
        pdf.set_font(font, style, size)
        pdf.set_text_color(*color)
        pdf.cell(0, h, text, align=align)

    line(30, 6, "K.B.H.S.S.T's  ·  ESTABLISHED 1988", "DVS", 7.2, GOLD_L, "B")
    # crest: double gold ring with initials
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(2.4)
    pdf.ellipse(80.5, 46, 49, 49)
    pdf.set_line_width(1.0)
    pdf.ellipse(85.5, 51, 39, 39)
    line(60, 6, "K.B.H.S.S.T's", "DVS", 8.5, GOLD_L, "B")
    line(67.5, 11, "MCA", "DVS", 20, (255, 255, 255), "B")
    line(80, 6, "SPPU  ·  2026-27", "DVS", 6.2, GOLD_L, "B")

    line(105, 9, "DR. B.V. HIRAY COLLEGE OF", "DVS", 21.5, (255, 255, 255), "B")
    line(115.5, 9, "MANAGEMENT AND RESEARCH CENTRE", "DVS", 21.5, (255, 255, 255), "B")
    line(129, 5, "Malegaon Camp, Malegaon — Affiliated to Savitribai Phule Pune University, Pune (SPPU)", "DVS", 8.2, (205, 210, 224))
    line(135, 5, "Approved by AICTE, New Delhi  ·  NAAC Accredited", "DVS", 8.2, (205, 210, 224))
    pdf.set_draw_color(*GOLD); pdf.set_line_width(1.6); pdf.line(70, 145, 140, 145)
    line(150, 6, "M I N I   P R O J E C T   R E P O R T", "DVS", 8.5, GOLD_L, "B")
    line(160, 15, "CAMPUS SHIKAYAT SETU", "DVS", 27, (255, 255, 255), "B")
    line(177, 8, "College Grievance Redressal System", "DVS", 14.5, GOLD_L, "B")
    line(188, 5, "Full-stack web application for complaint lodging, automatic department routing,", "DVS", 9.2, (205, 210, 224))
    line(194, 5, "SLA-bound resolution and print-ready administrative registers", "DVS", 9.2, (205, 210, 224))
    pdf.set_draw_color(*GOLD); pdf.set_line_width(1.2); pdf.line(78, 205, 132, 205)

    line(212, 6.2, "Course:  Application Development  (Mini Project — Semester I)", "DVS", 9.2, (255, 255, 255))
    line(218.5, 6.2, "Program:  Master of Computer Applications (MCA)  ·  Sem-I", "DVS", 9.2, (255, 255, 255))
    line(225, 6.2, "Academic Year:  2026–27", "DVS", 9.2, (255, 255, 255))

    line(236, 6.0, "Submitted by", "DVS", 10, GOLD_L, "B")
    line(242.5, 6.0, "Yashwant Santosh Ahire   ·   Roll No.: ____________________", "DVS", 9.6, (255, 255, 255))
    line(253, 6.0, "Under the guidance of", "DVS", 10, GOLD_L, "B")
    line(259.5, 6.0, "Project Guide: ____________________", "DVS", 9.6, (255, 255, 255))

    line(268.5, 5.4, "SPPU MCA-I (SEM-I)  ·  Application Development  ·  AY 2026–27  ·  November 2026", "DVS", 6.8, (160, 164, 178))


def certificate(pdf: Report):
    pdf.add_page()
    pdf.recorder["certificate"] = pdf.page_no()
    pdf.start_section("Certificate", level=0)
    pdf.set_draw_color(*GOLD); pdf.set_line_width(1.2); pdf.rect(12, 12, 186, 273, style="D")
    pdf.set_y(20)
    pdf.set_font("DVS", "B", 15); pdf.set_text_color(*NAVY)
    pdf.cell(0, 8, "CERTIFICATE", align="C")
    pdf.set_draw_color(*GOLD); pdf.set_line_width(0.9); pdf.line(80, pdf.get_y() + 1, 130, pdf.get_y() + 1)
    pdf.ln(8)
    pdf.set_font("DVS", "", 10.5); pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6.2,
        "This is to certify that the Mini Project entitled “CAMPUS SHIKAYAT SETU — College Grievance Redressal "
        "System” is a bona fide work carried out by Mr. Yashwant Santosh Ahire, student of MCA-I (Semester-I), "
        "Dr. B.V. Hiray College of Management and Research Centre, Malegaon, under the SPPU MCA curriculum "
        "(Course: Application Development), during the academic year 2026–27.")
    pdf.ln(2)
    pdf.multi_cell(0, 6.2,
        "Draft certificate for guide review and signature. Completion and acceptance must be confirmed by the institution. The project is submitted in partial fulfilment of the requirements "
        "of the Mini Project Review schedule issued by the Department of MCA on 30-09-2026 — First Review "
        "(10-10-2026), Second Review (24-10-2026), Third Review (21-11-2026), Fourth Review (05-12-2026) and the "
        "Final Internal Demo with project submission (19-12-2026).")
    pdf.ln(2)
    pdf.multi_cell(0, 6.2,
        "Any originality declaration must be checked and approved by the student and guide before signing. This draft does not itself certify authorship or acceptance.")
    pdf.ln(14)
    pdf.set_font("DVS", "", 9.5)
    pdf.cell(0, 6, "Date: ____________________"); pdf.ln(6)
    pdf.cell(0, 6, "Place: Malegaon"); pdf.ln(6)

    def sig_block(y, left, right, role_l, role_r, bold=True, size=9):
        pdf.set_xy(18, y); pdf.set_font("DVS", "", 9); pdf.set_text_color(30, 30, 30)
        pdf.cell(90, 6, "_________________________"); pdf.set_xy(118, y); pdf.cell(74, 6, "_________________________")
        pdf.set_xy(18, y + 6); pdf.set_font("DVS", "B" if bold else "", size); pdf.set_text_color(*NAVY); pdf.cell(90, 6, left)
        pdf.set_xy(118, y + 6); pdf.cell(74, 6, right)
        pdf.set_xy(18, y + 11.5); pdf.set_font("DVS", "", 7.6); pdf.set_text_color(30, 30, 30); pdf.cell(90, 6, role_l)
        pdf.set_xy(118, y + 11.5); pdf.cell(74, 6, role_r)

    sig_block(188, "________________________", "________________________", "Project Guide", "Head of Department (MCA)")
    sig_block(226, "________________________", "________________________", "Principal / Dy. Director", "External Examiner")
    pdf.ln(6)


def index(pdf: Report):
    pdf.add_page()
    pdf.recorder["index"] = pdf.page_no()
    pdf.set_y(18)
    pdf.set_font("DVS", "B", 17); pdf.set_text_color(*NAVY)
    pdf.cell(0, 9, "INDEX", align="L")
    pdf.set_draw_color(*GOLD); pdf.set_line_width(1.2); pdf.line(16, pdf.get_y() + 1, 62, pdf.get_y() + 1)
    pdf.ln(6)
    pdf.set_font("DVS", "", 9.3); pdf.set_text_color(30, 30, 30)
    for title, key in SECTIONS:
        pg = pdf.toc.get(key, "•")
        pdf.set_font("DVS", "", 9.3)
        pdf.cell(160, 6.4, "  " + title)
        pdf.set_font("DVS", "B", 9.3); pdf.cell(0, 6.4, str(pg), align="R")
        pdf.ln(6.4)
    pdf.ln(3)
    pdf.set_font("DVS", "I", 7.6); pdf.set_text_color(*GREY)
    pdf.multi_cell(0, 4.2, "List of Figures and Tables is maintained in-line within each chapter. Screen images are screenshots of the current application using seeded demo data; counts and dates may change when the database is reset.")
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
    pdf.p("Assumed baseline for comparison: complaints are written on paper and forwarded manually. The actual existing "
          "college process has not been surveyed; confirm it with the guide or stakeholders before final submission.")
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
    pdf.figure(f"{IMG}/fig-gantt.png", 172, "Figure 1.1  Project timeline — milestones notified 30-09-2026: Review 1 (10 Oct) → Review 2 (24 Oct) → Review 3 (21 Nov) → Review 4 (05 Dec) → Final Internal Demo (19 Dec).")
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
        ["IDE / Editor", "VS Code + Git + GitHub", "Development & version control"],
    ], [42, 62, 74])

    pdf.h2("1.5  Brief Description of Technology Used")
    pdf.p("<b>Python 3</b> is the implementation language — readable, rapid to build with, and immediately familiar to the "
          "review panel. <b>Flask</b> provides routing, sessions and Jinja2 rendering without imposing an ORM; all SQL is "
          "explicit, bound-parameterised and visible in the source for examination. <b>Jinja2</b> templates keep presentation "
          "out of logic; the front end uses semantic HTML5, a navy, off-white and teal CSS theme and zero build tooling.")
    pdf.p("<b>SQLite 3</b> was selected after matching databases to the use case: single-campus, low-write, read-mostly, "
          "one-machine demo with zero DBA. It enforces integrity with UNIQUE, CHECK and FOREIGN KEY constraints. The schema "
          "works without a separate server. A move to MySQL would require changes to queries, connection handling and deployment (see Chapter 7).")
    pdf.p("<b>Security:</b> passwords are hashed with Werkzeug; protected routes check login and relevant roles "
          "server-side (students cannot open the admin console — covered by test_11); SQL uses bound parameters; "
          "anonymous identity fields and student event actors are hidden from officers, but free text may reveal identity; status changes write event records. POST forms use CSRF tokens.")
    pdf.h3("1.5.1  Operating systems used")
    pdf.p("Development and automated testing were executed on GNU/Linux. The app is intended to work on Windows with Python and dependencies, but native Windows testing remains outstanding.")


def ch2(pdf: Report):
    pdf.h1("ch2", "Proposed System", "Chapter 2")

    pdf.h2("2.1  Study of Similar Systems")
    pdf.p("Similar grievance tooling was studied before design: CPGRAMS (Government of India public-grievance portal), the "
          "academic complaint web apps found on GitHub (e.g. the “Smart Complaint Management System” concept), and an "
          "assumed manual process. The comparisons are illustrative; college workflow and vendor characteristics require "
          "verification. A research paper is optional under the college circular if required.")
    pdf.table(["System", "Type / Cost", "Strengths", "Limitations vs need"], [
        ["Manual paper process (assumed)", "Paper", "Simple to introduce",
         "No routing, no status, no SLA, no reports"],
        ["CPGRAMS (GoI)", "Citizen portal · free", "National scale, escalation matrix",
         "Heavyweight; external identity; no college-department model"],
        ["Smart Complaint Management System (GitHub reference)", "Concept repo · free",
         "Keyword routing + status tracking idea",
         "Empty PHP backend (0 bytes), localStorage-only demo, no DB, no auth, no reports, no tests"],
        ["ERP grievance module (generic)", "Varies", "May integrate with student records",
         "Features and cost depend on the vendor; not evaluated here"],
    ], [38, 26, 52, 60])

    pdf.h2("2.2  Feasibility Study")
    pdf.table(["Dimension", "Assessment"], [
        ["Technical", "Flask + SQLite requires only Python 3.11; no drivers, no services, no network. Dependencies require a network connection or locally available installation packages."],
        ["Operational", "The demo presents department actions as buttons. Actual workflow and training needs require stakeholder confirmation."],
        ["Economic", "The software components used have no purchase cost for this demo; hardware, support and operating costs depend on deployment."],
        ["Schedule", "Design, build, seed, tests and documentation completed inside the Sem-I window. Milestones as notified 30-09-2026 — Review 1 (SRS) 10-10-2026 (10 marks) · Review 2 24-10-2026 (15) · Review 3 21-11-2026 (15) · Review 4 (1st PPT) 05-12-2026 (10) · Final Internal Demo 19-12-2026 (50)."],
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

    pdf.h2("2.5  Proposed System Overview")
    pdf.p("Campus Shikayat Setu keeps the proven workflow of the reference concept — lodge → auto-route → track — and "
          "implements the demo using a relational schema with foreign-key "
          "enforcement, Werkzeug password hashing with three roles, a transparent router whose scoring is printed on the "
          "complaint timeline, an SLA engine, a 7-day student reopen window, full audit events and six print registers.")
    pdf.bullets([
        "<b>Student layer:</b> register → lodge (category, location, anonymous flag) → track (code and roll no.) → confirm or reopen with feedback.",
        "<b>Officer layer:</b> department queue ordered by priority then recency; acknowledge → start work → resolve with mandatory remark.",
        "<b>Admin layer:</b> college-wide console — filter, reassign, escalate (priority→High), force-close resolved complaints, manage officer accounts.",
        "<b>Report layer:</b> six Ctrl+P print-ready registers; routing has two summary modes and a separate complaint-level record table.",
    ])

    pdf.h2("2.6  Modules Identified")
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
    pdf.figure(f"{IMG}/fig-erd.png", 178, "Figure 3.1  ERD — actual SQLite foreign keys and relationship cardinalities.")

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
    pdf.p("Each actor has a separate use-case diagram. The first three are stored user roles; the public visitor is an external actor, not a database role.")
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
    pdf.figure(f"{IMG}/fig-class.png", 178, "Figure 3.3  Conceptual data records and selected associations; the app does not use ORM classes.")

    pdf.h2("3.6  Activity Diagram", reserve=155)
    pdf.figure(f"{IMG}/fig-activity.png", 178, "Figure 3.4  Activity diagram — submission and supported status transitions.")
    pdf.note("Overdue is never stored — it is derived: now > sla_due_at AND status NOT IN (Resolved, Closed). This keeps every register consistent even if the server is restarted after a long break.")

    pdf.h2("3.7  Deployment Diagram", reserve=110)
    pdf.figure(f"{IMG}/fig-deployment.png", 178, "Figure 3.5  Deployment — single node lab PC; browsers on same PC or LAN peers.")

    pdf.h2("3.8  Module Hierarchy Diagram", reserve=125)
    pdf.figure(f"{IMG}/fig-modules.png", 178, "Figure 3.6  Module hierarchy — actual project files and responsibilities.")

    pdf.h2("3.9  Sample Input and Output Screens", reserve=40)
    pdf.p("Screenshots use synthetic seeded data; see Appendix B. The fresh-seed reports contain at least five data rows; routing has two mode summaries and a separate complaint-level table. The full screen catalogue and validation notes are in Chapter 10.")
    pdf.figure(f"{IMG}/screen-login.png", 120, "Figure 3.7  Sample input — Sign-in screen (roll no./username + password).")
    pdf.figure(f"{IMG}/screen-dashboard.png", 132, "Figure 3.8  Sample output — Student dashboard (KPI tiles, status donut, latest complaints).")
    pdf.figure(f"{IMG}/screen-lodge.png", 148, "Figure 3.9  Sample input — Complaint form with estimated routing.")
    pdf.figure(f"{IMG}/screen-console.png", 148, "Figure 3.10  Sample output — Admin console (fresh-seed filterable register).")
    pdf.figure(f"{IMG}/screen-timeline.png", 148, "Figure 3.11  Sample output — Complaint detail: SLA clock, stepper and timeline.")

    pdf.h2("3.10  Constraints and Assumptions")
    pdf.bullets([
        "One campus, one server process, SQLite file in the app directory; contention and capacity depend on workload and have not been load-tested.",
        "Keyword lists are curated per domain; sarcasm/vindication requires admin reassignment (Chapter 6, L-2).",
        "Complaint codes contain the calendar year and a database-generated ID; there is no application delete action for complaints.",
        "Anonymous identity fields are visible to administrators; free text can still identify a complainant.",
    ])

def ch4(pdf: Report):
    pdf.h1("ch4", "Coding", "Chapter 4")
    pdf.p("Full source is in the repository under <b>shikayat-setu/</b>. The following examples show the main routing, workflow and database logic. Ellipses indicate omitted lines.")

    pdf.h2("4.1  Routing engine — scoring and SLA")
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

    pdf.h2("4.2  Selecting a routing category")
    pdf.code('''def select_category(title, description, chosen, categories):
    text = route_text(title, description)
    matched, score = route(text, categories)
    if matched and (matched["id"] == chosen["id"] or
                    score > score_category(text, chosen["keywords"])):
        return matched, "auto", score
    return chosen, "manual", 0''',
        title="routing.py — selection shared by submission, preview and seed")

    pdf.h2("4.3  Resolution workflow — status transitions")
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

    pdf.h2("4.4  SLA compliance report — SQL")
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

    pdf.h2("4.5  Sample of schema constraints in force")
    pdf.code('''status   TEXT NOT NULL DEFAULT 'Submitted'
         CHECK (status IN ('Submitted','Acknowledged','In Progress','Resolved','Closed')),
routing  TEXT NOT NULL DEFAULT 'auto' CHECK (routing IN ('auto','manual')),
priority TEXT NOT NULL CHECK (priority IN ('High','Medium','Low')),
rating   INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5)  -- feedback''', title="schema.sql — CHECK constraints (integrity at the database layer)")
    pdf.h2("4.6  Server-side complaint validation")
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
    pdf.p("Tests run on isolated, freshly seeded temporary SQLite databases. Automated unit and integration tests use Flask's test client; browser checks and print checks are documented separately in TESTING.md. No existing user database is reset. Run python -m pytest tests/ -q from shikayat-setu. Most recent source and extracted-package runs: 114 passed. Results refer to those automated runs, not an unperformed guide acceptance.")
    pdf.h2("5.2  Unit test plan")
    pdf.table(["ID", "Steps / input", "Expected and observed in automated run", "Script"], [
        ["UT-01", "Score 'leaking leak leak.' for keyword leak; score two occurrences of short circuit.", "4 and 8 respectively; PASS.", "test_safety_and_mass_impact_and_word_boundaries"],
        ["UT-02", "Set default Low and enter a fire keyword; check SLA constants.", "High priority; High 24h, Medium 72h, Low 168h; PASS.", "test_safety_and_mass_impact_and_word_boundaries"],
        ["UT-03", "Test tied keyword scores, then unrelated text.", "First category wins tie; no match returns none; PASS.", "test_keyword_scoring_and_tie_break"],
    ], [15, 53, 58, 52], size=7.2)
    pdf.h2("5.3  Acceptance-oriented integration test plan")
    pdf.p("The following are automated test-client scenarios, with their asserted observed results. They are not a substitute for the student's live demonstration or the guide's acceptance.")
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
    pdf.h2("5.4  Test scripts and traceability")
    pdf.p("Functions above are in tests/test_in_depth.py except UT-03 and AT-03, which are in tests/test_app.py. Each test creates or uses a disposable seeded database. To inspect or rerun an individual test: python -m pytest tests/test_in_depth.py -k test_reports_on_controlled_dataset -v. Source code contains the precise setup, requests, assertions and cleanup. HTTP 302 is a redirect; follow it in a browser to see the message.")
    pdf.h2("5.5  Test limitations")
    pdf.p("The suite does not prove absence of defects. Small concurrency tests are not load tests. Linux/Chromium browser and six A4 report print checks were performed; native Windows, other browsers, physical printing, accessibility, penetration, large-scale load and crash recovery were not tested. Test data and dates are synthetic. Re-run the suite and rehearse the live workflow on the actual review computer.")


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
    pdf.note("Known limitation: force-close checks for Resolved status but does not enforce the proposed seven-day waiting period. Administrators should verify the timing manually.")
    pdf.p("<b>Acceptance for the Review 3 build rests on three facts:</b> (i) the complete lifecycle lodge → resolve → "
          "feedback → closed is executable and audit-trailed end to end; (ii) routing, SLA and escalation are deterministic "
          "and explainable on the timeline; (iii) the reports can be checked against seeded data. Final acceptance is the guide’s decision.")


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
    pdf.p("For Review 3, demonstrate the application and discuss test evidence and limitations. Guide approval, complete review submissions "
          "and final hard binding remain separate tasks; the 19 December final date is tentative.")


def ch9(pdf: Report):
    pdf.h1("ch9", "Bibliography", "Chapter 9")
    refs = [
        "Pallets Projects. (2024). <i>Flask — Web development, one drop at a time.</i> https://flask.palletsprojects.com/",
        "Pallets Projects. (2024). <i>Werkzeug — The comprehensive WSGI web application library.</i> https://werkzeug.palletsprojects.com/",
        "The SQLite Consortium. (2024). <i>SQLite documentation — file format, transactions, WAL.</i> https://www.sqlite.org/docs.html",
        "FPDF2 contributors. (2025). <i>fpdf2 — Simple and fast PDF document generation in Python.</i> https://pyfpdf.github.io/fpdf2/",
        "Matplotlib developers. (2024). <i>Matplotlib — Visualisation with Python.</i> https://matplotlib.org/",
        "K.B.H.S.S.T’s Dr. B.V. Hiray College of Management and Research Centre, Department of MCA. (2026, 30 September). <i>Project Review Schedule 2026-27 — MCA-I (SEM-I).</i> Malegaon. [College circular — internal document]",
        "Harney-Jenifar-R-S. (2026). <i>Smart Complaint Management System — reference concept repository.</i> GitHub. https://github.com/Harney-Jenifar-R-S/Smart_Complaint_System",
        "Press Information Bureau. (2024). <i>Centralized Public Grievance Redress and Monitoring System (CPGRAMS).</i> Government of India.",
        "OWASP Foundation. (2023). <i>OWASP Top 10 — A03: Injection, A07: Identification and Authentication Failures.</i> https://owasp.org/www-project-top-ten/",
        "Savitribai Phule Pune University. <i>MCA, 2025 Pattern, Semester I–IV (w.e.f. 2025–26), Mini Project.</i> https://www.iims.ac.in/pdf/Academics/MCA-Syllabus-2025-Pattern-Semester-1-4.pdf. Confirm the applicable pattern with the department.",
    ]
    pdf.set_font("DVS", "", 9.6); pdf.set_text_color(30, 30, 30)
    for i, r in enumerate(refs, 1):
        pdf.write_html(f"<b>[{i}]</b>  {r}<br/><br/>")
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
    pdf.p("Extract the ZIP or clone the repository. Install Python 3.10 or newer (3.11 or 3.12 recommended), then open the shikayat-setu folder in VS Code. Choose Terminal → Run Task → Start Campus Shikayat Setu. First launch creates .venv and installs dependencies (internet usually required); later launches reuse it. Open http://127.0.0.1:5001 and press Ctrl+C in the terminal to stop. On Windows you can also double-click Start_Project.bat; on macOS/Linux run sh start-project.sh. See README.md for troubleshooting. The project database is not reset by the launcher.")

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
        pdf.p(description)
        pdf.figure(f"{IMG}/screen-{filename}.png", 162, f"Figure 10.{i}  {title} — synthetic demo.")

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

    pdf.h2("B.4  complaints — 37 rows (₹-style totals not applicable)")
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


def appd(pdf: Report):
    pdf.h1("appd", "Appendix D — Project Review Schedule 2026-27 (notified 30-09-2026)", "Appendix D")
    pdf.p("Reproduced (in tabular form) from the K.B.H.S.S.T’s Dr. B.V. Hiray College of Management and Research Centre "
          "circular “Project Review Schedule 2026-27 MCA-I (SEM-I)” dated 30th September 2026, countersigned by the Head "
          "of Department (MCA) and the Dy. Director, for cross-check against this report. Roll No. 1–34 → Project Guide "
          "Mrs. Priyanka M. Jagtap; Roll No. 35 &amp; onwards → Mrs. Yogita A. Shirsath.")
    pdf.table(["#", "Review (activity)", "Date", "Marks", "Notified content"], [
        ["1", "Synopsis (SRS) Submission & First Review", "10-10-2026", "10",
         "Ch-1 Introduction — 1.1 Abstract · 1.2 Existing System and Need for System · 1.3 Scope of System · 1.4 Operating Environment — Hardware and Software · 1.5 Brief Description of Technology Used · 1.5.1 Operating systems used (Windows or Unix)"],
        ["2", "Second Review", "24-10-2026", "15",
         "Ch-2 Proposed System — 2.1 Study of Similar Systems (research paper optional) · 2.2 Feasibility Study · 2.3 Objectives of Proposed System · 2.4 Users of System  +  Ch-3 System Analysis and Design — 3.1 System Requirements (Functional and Non-Functional) · 3.2 Entity Relationship Diagram (ERD) · 3.3 Table Structure · 3.4 Use Case Diagrams · 3.5 Class Diagram · 3.6 Activity Diagram · 3.7 Deployment Diagram · 3.8 Module Hierarchy Diagram · 3.9 Sample Input and Output Screens (valid data; ≥ 5 valid records per report)"],
        ["3", "Third Review", "21-11-2026", "15",
         "Ch-4 Coding — 4.1 Code snippets · Ch-5 Testing — 5.1 Test Strategy · 5.2 Unit Test Plan · 5.3 Acceptance Test Plan · 5.4 Test Case / Test Script · Ch-6 Limitations of Proposed System · Ch-7 Proposed Enhancements · Ch-8 Conclusion · Ch-9 Bibliography · Ch-10 User Manual (all screens with description/purpose; details about validations of entered data)"],
        ["4", "Fourth Review", "05-12-2026", "10",
         "1st PPT Presentation"],
        ["5", "Internal Viva and Final Submission", "19-12-2026 (tentative)", "50",
         "2nd Final PPT Presentation and project submission with Hard Binding"],
    ], [7, 33, 22, 12, 104], size=6.9)
    pdf.ln(2)
    pdf.p("<b>Total marks: 100.</b> Guideline 1 — mini project in the first Semester based on the courses learnt; "
          "2 — may be taken individually or in a group based on the scope of the project; 3 — all students shall report "
          "project details to their respective guides on the above schedule dates. Students with Roll No. 1–34 are under "
          "Mrs. Priyanka M. Jagtap; Roll No. 35 & onwards under Mrs. Yogita A. Shirsath.")
    pdf.note("Coverage map — Chapters in this report follow the circular’s item numbers as follows: Ch-2 §2.1–2.4 = items for Review 2; Ch-3 §3.1–3.9 = items for Review 2; Ch-4…Ch-10 = items for Review 3. Chapter 10 (User Manual) lists every screen with purpose and a full validation catalogue (§10.5).")


def build(toc, recorder):
    pdf = Report(toc=toc, recorder=recorder)
    pdf.set_title("Campus Shikayat Setu — College Grievance Redressal System (MCA-I Sem-I Mini Project Report)")
    pdf.set_author("Yashwant Santosh Ahire — Dr. B.V. Hiray College of Management and Research Centre, Malegaon (SPPU)")
    pdf.set_creator("Campus Shikayat Setu report generator (build_report.py)")
    cover(pdf)
    certificate(pdf)
    index(pdf)
    for key, fn in [("ch1", ch1), ("ch2", ch2), ("ch3", ch3), ("ch4", ch4), ("ch5", ch5),
                    ("ch6", ch6), ("ch7", ch7), ("ch8", ch8), ("ch9", ch9), ("ch10", ch10),
                    ("appa", appa), ("appb", appb), ("appc", appc), ("appd", appd)]:
        fn(pdf)
    return pdf


if __name__ == "__main__":
    # Pass 1 — placeholder TOC page numbers (same line count ⇒ identical pagination)
    rec1 = {}
    build({k: "00" for _, k in SECTIONS}, rec1)
    # Pass 2 — real index
    pdf = build(rec1, {})
    pdf.output(OUT)
    print("PDF written:", OUT)
    print("Sections → pages:", {k: rec1[k] for _, k in SECTIONS})

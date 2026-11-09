#!/usr/bin/env python3
"""Build SmartLibrary_MCA-Mini-Project_Review.pptx — 16 slides, 16:9.

Design system matches the project report: NAVY / GOLD / CREAM, Georgia display serif.
All figures are the real generated assets from report/images/.
"""
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

IMG = "/home/user/Yashwant-git392/report/images"
OUT = "/home/user/Yashwant-git392/presentation/SmartLibrary_MCA-Mini-Project_Review.pptx"

NAVY   = RGBColor(0x16, 0x24, 0x3D)
NAVY2  = RGBColor(0x2B, 0x4A, 0x73)
NAVY3  = RGBColor(0x1F, 0x34, 0x55)
GOLD   = RGBColor(0xC9, 0xA2, 0x27)
GOLD_L = RGBColor(0xFF, 0xD9, 0x5E)
CREAM  = RGBColor(0xF7, 0xF5, 0xEF)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GREY   = RGBColor(0x6B, 0x72, 0x80)
GREY_L = RGBColor(0xE8, 0xED, 0xF7)
GREEN  = RGBColor(0x1E, 0x7A, 0x46)
RED    = RGBColor(0xB3, 0x37, 0x2E)
INK    = RGBColor(0x20, 0x20, 0x20)

SERIF = "Georgia"
MONO  = "Courier New"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

TOTAL = 16


# ---------------------------------------------------------------- helpers
def add_slide():
    return prs.slides.add_slide(BLANK)

def set_bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color

def rect(slide, x, y, w, h, fill=None, line=None, line_w=None, round_=False, radius=0.10, shadow=False):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    if round_:
        try:
            shp.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line; shp.line.width = Pt(line_w or 1.0)
    shp.shadow.inherit = False
    return shp

def txt(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, wrap=True):
    """paras: list of dicts {runs:[(text, style)], align, space_after, line_spacing}"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, p in enumerate(paras):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = p.get("align", PP_ALIGN.LEFT)
        if p.get("space_after") is not None: par.space_after = Pt(p["space_after"])
        if p.get("space_before") is not None: par.space_before = Pt(p["space_before"])
        par.line_spacing = p.get("line_spacing", 1.12)
        for text, st in p["runs"]:
            r = par.add_run(); r.text = text
            r.font.name = st.get("font", SERIF)
            r.font.size = Pt(st.get("size", 12))
            r.font.bold = st.get("bold", False)
            r.font.italic = st.get("italic", False)
            r.font.color.rgb = st.get("color", INK)
    return tb

def kicker(slide, text, x=0.55, y=0.32, w=9.5, color=GOLD):
    txt(slide, x, y, w, 0.3, [dict(runs=[(text, dict(font=SERIF, size=10.5, bold=True, color=color))])])

def title(slide, text, x=0.55, y=0.55, w=12.3, size=25, color=NAVY):
    txt(slide, x, y, w, 0.62, [dict(runs=[(text, dict(font=SERIF, size=size, bold=True, color=color))])])

def gold_rule(slide, x=0.55, y=1.22, w=1.6, weight=3.2):
    ln = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Pt(weight))
    ln.fill.solid(); ln.fill.fore_color.rgb = GOLD; ln.line.fill.background(); ln.shadow.inherit = False

def header(slide, kick, ttl, size=25):
    set_bg(slide, CREAM)
    kicker(slide, kick)
    title(slide, ttl, size=size)
    gold_rule(slide)

def footer(slide, n):
    ln = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(7.06), Inches(12.23), Pt(0.9))
    ln.fill.solid(); ln.fill.fore_color.rgb = GOLD; ln.line.fill.background(); ln.shadow.inherit = False
    txt(slide, 0.55, 7.13, 9.6, 0.3,
        [dict(runs=[("SmartLibrary — College Library Management System  ·  SPPU MCA-I (Sem-I) Application Development  ·  2026-27",
                     dict(size=7.5, color=GREY))])])
    txt(slide, 10.6, 7.13, 2.18, 0.3,
        [dict(runs=[(f"{n} / {TOTAL}", dict(size=8.5, bold=True, color=NAVY))], align=PP_ALIGN.RIGHT)])

def chip(slide, x, y, w, text, fill=NAVY, tc=GOLD_L, size=8.5, bold=True):
    c = rect(slide, x, y, w, 0.28, fill=fill, round_=True, radius=0.5)
    tf = c.text_frame; tf.word_wrap = False
    tf.margin_left = tf.margin_right = Inches(0.02); tf.margin_top = tf.margin_bottom = Inches(0.0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.line_spacing = 1.0
    r = p.add_run(); r.text = text
    r.font.name = SERIF; r.font.bold = bold; r.font.size = Pt(size); r.font.color.rgb = tc
    return c

def card(slide, x, y, w, h, fill=WHITE, line=GOLD, line_w=1.15, radius=0.055):
    return rect(slide, x, y, w, h, fill=fill, line=line, line_w=line_w, round_=True, radius=radius)

def pic_fit(slide, path, x, y, max_w, max_h, card_bg=None):
    """Insert picture preserving AR, centered in the (x,y,max_w,max_h) box. Returns placed rect."""
    iw, ih = Image.open(path).size
    ar = iw / ih
    w = max_w; h = w / ar
    if h > max_h:
        h = max_h; w = h * ar
    px = x + (max_w - w) / 2; py = y + (max_h - h) / 2
    slide.shapes.add_picture(path, Inches(px), Inches(py), Inches(w), Inches(h))
    return px, py, w, h

def bullets(slide, x, y, w, h, items, size=12.5, gap=4, color=INK, marker="—  ", mcolor=GOLD, line_spacing=1.12):
    """items: list of (bold_lead, rest) or plain strings."""
    paras = []
    for it in items:
        runs = []
        if isinstance(it, tuple):
            lead, rest = it
            runs.append((marker, dict(size=size, bold=True, color=mcolor)))
            runs.append((lead, dict(size=size, bold=True, color=NAVY)))
            if rest:
                runs.append((rest, dict(size=size, color=color)))
        else:
            runs.append((marker, dict(size=size, bold=True, color=mcolor)))
            runs.append((it, dict(size=size, color=color)))
        paras.append(dict(runs=runs, space_after=gap, line_spacing=line_spacing))
    txt(slide, x, y, w, h, paras)


# ================================================================ SLIDE 1 — Title
s = add_slide(); set_bg(s, NAVY)
# decorative book glyph (drawn, right side)
bx, by = 10.62, 1.55
rect(s, bx, by, 1.66, 2.34, fill=NAVY3, round_=True, radius=0.09)
rect(s, bx + 0.22, by + 0.28, 1.22, 0.16, fill=GOLD)
rect(s, bx + 0.22, by + 0.62, 1.22, 0.075, fill=RGBColor(0x8F, 0xA3, 0xC4))
rect(s, bx + 0.22, by + 0.80, 1.22, 0.075, fill=RGBColor(0x8F, 0xA3, 0xC4))
rect(s, bx + 0.22, by + 0.98, 0.85, 0.075, fill=RGBColor(0x8F, 0xA3, 0xC4))
rect(s, bx + 0.22, by + 1.44, 1.22, 0.34, fill=GOLD)
rect(s, bx + 0.22, by + 1.92, 0.62, 0.10, fill=GOLD_L)
# thin gold frame lines
ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.42), Inches(13.333), Pt(1.6))
ln.fill.solid(); ln.fill.fore_color.rgb = GOLD; ln.line.fill.background(); ln.shadow.inherit = False
ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.08), Inches(13.333), Pt(1.6))
ln.fill.solid(); ln.fill.fore_color.rgb = GOLD; ln.line.fill.background(); ln.shadow.inherit = False

txt(s, 0.75, 0.72, 9.4, 0.35, [dict(runs=[("SAVITRIBAI PHULE PUNE UNIVERSITY  ·  MCA-I (SEM-I)  ·  APPLICATION DEVELOPMENT  ·  2026-27",
                                          dict(size=10, bold=True, color=GOLD))])])
txt(s, 0.75, 1.28, 9.6, 1.55, [dict(runs=[("SmartLibrary", dict(size=79, bold=True, color=WHITE))], line_spacing=0.98)])
txt(s, 0.75, 2.62, 9.4, 0.6, [dict(runs=[("College Library Management System", dict(size=29.5, bold=True, color=GOLD_L))])])
rect(s, 0.78, 3.42, 1.7, 0.037, fill=GOLD)
txt(s, 0.75, 3.62, 9.2, 0.75,
    [dict(runs=[("Turning the college’s handwritten issue register into a boring, reliable, self-hosted web app —",
                 dict(size=14.5, italic=True, color=CREAM))], line_spacing=1.15),
     dict(runs=[("catalogue · circulation · fines · print-ready registers.", dict(size=14.5, italic=True, color=RGBColor(0xC9,0xD2,0xE4)))])])
txt(s, 0.75, 5.05, 8.6, 1.6,
    [dict(runs=[("Yashwant Shelke", dict(size=17.5, bold=True, color=WHITE))], space_after=2),
     dict(runs=[("Guide: Mrs. Priyanka M. Jagtap", dict(size=11.5, color=CREAM))], space_after=2),
     dict(runs=[("Dr. B.V. Hiray College of Management and Research Centre, Malegaon (Nashik)", dict(size=10.5, color=RGBColor(0x9F,0xAD,0xC8)))])])
txt(s, 10.35, 5.28, 2.45, 1.35,
    [dict(runs=[("REVIEW 3", dict(size=9, bold=True, color=GOLD))], space_after=1),
     dict(runs=[("21 November 2026", dict(size=13, bold=True, color=WHITE))], space_after=8),
     dict(runs=[("FINAL REVIEW", dict(size=9, bold=True, color=GOLD))], space_after=1),
     dict(runs=[("19 December 2026", dict(size=13, bold=True, color=WHITE))])])

# ================================================================ SLIDE 2 — Agenda & at a glance
s = add_slide(); header(s, "AGENDA", "What we will walk through — in ten minutes"); footer(s, 2)
agenda = [
    ("01", "The problem", "why the paper register had to go"),
    ("02", "Objectives & scope", "v1.0 goals, in/out of scope"),
    ("03", "Users & use cases", "librarian vs member, one page map"),
    ("04", "Architecture & data", "Flask + SQLite, ERD, constraints"),
    ("05", "Modules & circulation rules", "3 books · 14 days · ₹2/day fine"),
    ("06", "Live demo", "dashboard, issue & return flows"),
    ("07", "Reports", "five registers, ≥ 5 valid records each"),
    ("08", "Testing evidence", "12/12 automated + 8 manual scenarios"),
    ("09", "Timeline & deliverables", "review track, effort, artefacts"),
    ("10", "Future work & Q&A", "enhancements E-1 … E-10"),
]
col_y = 1.52
for i, (n, t, d) in enumerate(agenda):
    col = i // 5; row = i % 5
    x = 0.55 + col * 6.35; y = col_y + row * 0.78
    txt(s, x, y, 0.55, 0.5, [dict(runs=[(n, dict(size=15, bold=True, color=GOLD))])])
    txt(s, x + 0.52, y - 0.015, 5.35, 0.35, [dict(runs=[(t, dict(size=13, bold=True, color=NAVY))])])
    txt(s, x + 0.52, y + 0.185, 5.35, 0.3, [dict(runs=[(d, dict(size=8.5, color=GREY))])])

card(s, 0.55, 5.62, 12.23, 1.15)
txt(s, 0.75, 5.74, 3.0, 0.3, [dict(runs=[("AT A GLANCE", dict(size=9, bold=True, color=GOLD))])])
stats = [("12", "books seeded"), ("8", "members"), ("15", "transactions"), ("16", "screens"), ("5", "print registers"), ("12/12", "tests passing")]
sw = 11.9 / len(stats)
for i, (v, d) in enumerate(stats):
    x = 0.62 + i * sw
    txt(s, x, 6.02, sw - 0.15, 0.5, [dict(runs=[(v, dict(size=21, bold=True, color=NAVY))])])
    txt(s, x, 6.42, sw - 0.15, 0.3, [dict(runs=[(d, dict(size=7.5, color=GREY))])])

# ================================================================ SLIDE 3 — The problem
s = add_slide(); header(s, "01 · CONTEXT", "The register is the database"); footer(s, 3)
txt(s, 0.55, 1.5, 7.1, 0.35, [dict(runs=[("What the college lives with today", dict(size=13, bold=True, color=NAVY))])])
bullets(s, 0.55, 1.95, 7.0, 4.0, [
    ("Handwritten issue register — ", "entries in pencil and ink; torn, smudged, missing pages."),
    ("Fines computed by hand — ", "₹2 × days overdue, argued row-by-row at the desk."),
    ("No live stock figure — ", "“how many copies of Database System Concepts?” = walk the shelves."),
    ("Overdues by eyeball — ", "identification of defaulters is memory-based, not systematic."),
    ("Register lost = data lost — ", "no backup; a misplaced ledger erases years of history."),
], size=12.5, gap=9)
card(s, 8.15, 1.5, 4.62, 4.42, fill=NAVY, line=None)
txt(s, 8.45, 1.78, 4.1, 0.35, [dict(runs=[("WHY NOT THE USUAL ANSWERS?", dict(size=10, bold=True, color=GOLD))])])
bullets(s, 8.45, 2.25, 4.15, 3.5, [
    ("SOUL / Koha / Virtua — ", "enterprise ILS: licence cost, server, dedicated admin."),
    ("Excel sheets — ", "multi-user corruption, broken formulas, no audit trail."),
], size=11, gap=7, color=CREAM, mcolor=GOLD_L)
txt(s, 8.45, 4.65, 4.1, 1.2,
    [dict(runs=[("Right-sized answer: ", dict(size=11, bold=True, color=GOLD_L)),
                ("a focused, self-hosted web app that runs on the library PC — zero licence, zero server.", dict(size=11, color=CREAM))], line_spacing=1.25)])
rect(s, 0.55, 6.12, 12.23, 0.5, fill=GREY_L, round_=True, radius=0.5)
txt(s, 0.85, 6.24, 11.7, 0.3, [dict(runs=[("Requirement elicited on-site with the college librarian, November 2026 — the rules on slide 9 are the college’s, not invented.",
                                           dict(size=9.5, italic=True, color=NAVY3))])])

# ================================================================ SLIDE 4 — Objectives & scope
s = add_slide(); header(s, "02 · OBJECTIVES & SCOPE", "What v1.0 sets out to do"); footer(s, 4)
txt(s, 0.55, 1.5, 4.6, 0.32, [dict(runs=[("OBJECTIVES", dict(size=10, bold=True, color=GOLD))])])
objectives = [
    "Searchable catalogue of 12+ titles, category & availability at a glance",
    "Student & faculty membership — add, edit, (de)activate, delete with guards",
    "Circulation engine enforcing the college’s real rules, atomically",
    "Automatic fine computation and a permanent fine ledger",
    "Five print-ready registers: issued · overdue · fine history · stock · member activity",
    "Seeded demo + reset workflow — reproducible viva, every time",
]
for i, o in enumerate(objectives):
    y = 1.92 + i * 0.62
    chip(s, 0.55, y, 0.42, f"O{i+1}", fill=NAVY, tc=GOLD_L, size=10)
    txt(s, 1.12, y + 0.015, 4.6, 0.6, [dict(runs=[(o, dict(size=9.5, color=INK))], line_spacing=1.08)])

card(s, 6.15, 1.5, 6.6, 2.32)
txt(s, 6.4, 1.66, 3.0, 0.3, [dict(runs=[("IN SCOPE — v1.0", dict(size=9.5, bold=True, color=GREEN))])])
bullets(s, 6.4, 2.05, 6.15, 1.7, [
    "Catalogue CRUD with ISBN regex + uniqueness",
    "Member CRUD with roll-no / e-mail uniqueness, 10-digit phone",
    "Issue / return with atomic stock restore",
    "Fine ledger + ₹-denominated reports, print CSS",
    "Single admin role; password change; session auth",
], size=9.5, gap=3, marker="•  ", mcolor=GREEN)
card(s, 6.15, 4.02, 6.6, 2.35)
txt(s, 6.4, 4.18, 4.5, 0.3, [dict(runs=[("OUT OF SCOPE — v1.0 (each maps to an enhancement)", dict(size=9.5, bold=True, color=RED))])])
bullets(s, 6.4, 4.57, 6.15, 1.75, [
    "Multi-branch / inter-library loan (E-5, E-8)",
    "Member self-service OPAC (E-3, E-8)",
    "SMS / e-mail reminders (E-2)",
    "Online fine payment / receipts (E-4)",
    "Barcode / RFID scanning (E-1)",
    "Marathi / Hindi UI (E-9 territory)",
], size=9.5, gap=3, marker="•  ", mcolor=RED)

# ================================================================ SLIDE 5 — Users & use cases
s = add_slide(); header(s, "03 · USERS & USE CASES", "One librarian, many capabilities"); footer(s, 5)
card(s, 0.55, 1.5, 4.35, 1.62)
txt(s, 0.78, 1.62, 3.9, 0.3, [dict(runs=[("ACTOR 1 — LIBRARIAN / ADMINISTRATOR", dict(size=9, bold=True, color=GOLD))])])
txt(s, 0.78, 1.94, 3.95, 0.3, [dict(runs=[("The single human role (v1.0)", dict(size=11, bold=True, color=NAVY))])])
txt(s, 0.78, 2.28, 3.95, 0.72, [dict(runs=[("Catalogue, members, circulation, fines, registers, credentials — the desk operator for every screen in the demo.",
                                             dict(size=9.5, color=INK))], line_spacing=1.15)])
card(s, 0.55, 3.32, 4.35, 1.62)
txt(s, 0.78, 3.44, 3.9, 0.3, [dict(runs=[("ACTOR 2 — MEMBER (STUDENT / FACULTY)", dict(size=9, bold=True, color=GOLD))])])
txt(s, 0.78, 3.76, 3.9, 0.3, [dict(runs=[("Identified, never logged in (v1.0)", dict(size=11, bold=True, color=NAVY))])])
txt(s, 0.78, 4.10, 3.95, 0.72, [dict(runs=[("The subject of every transaction — identified by roll number at the desk; no self-login until the OPAC phase (E-3).",
                                             dict(size=9.5, color=INK))], line_spacing=1.15)])
rect(s, 0.55, 5.14, 4.35, 1.28, fill=GREY_L, round_=True, radius=0.12)
txt(s, 0.78, 5.28, 3.9, 0.28, [dict(runs=[("RACI SNAPSHOT", dict(size=8.5, bold=True, color=NAVY))])])
txt(s, 0.78, 5.56, 3.95, 0.8, [dict(runs=[("Librarian = Accountable & Responsible · Principal = Consulted · Members = Informed",
                                            dict(size=9, color=NAVY3))], line_spacing=1.2)])
pic_fit(s, f"{IMG}/fig-usecase.png", 5.25, 1.52, 7.55, 4.9)
txt(s, 5.6, 6.42, 7.0, 0.3, [dict(runs=[("Use-case diagram — report §3.5; 40+ use cases in two swimlanes", dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])

# ================================================================ SLIDE 6 — Architecture & stack
s = add_slide(); header(s, "04 · ARCHITECTURE", "Boring technology, deliberately"); footer(s, 6)
pic_fit(s, f"{IMG}/fig-architecture.png", 5.15, 1.5, 7.65, 3.6)
txt(s, 5.5, 5.22, 7.0, 0.3, [dict(runs=[("Three tiers on one machine — scale-out path: gunicorn + nginx + MySQL (E-5 / E-10)",
                                          dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
txt(s, 0.55, 1.5, 4.3, 0.32, [dict(runs=[("WHY THIS STACK", dict(size=10, bold=True, color=GOLD))])])
bullets(s, 0.55, 1.95, 4.35, 3.05, [
    ("Flask 3.1 — ", "server-rendered Jinja; no SPA build step, no hydration, no version drift."),
    ("SQLite — ", "one file = the whole database; 20k+ txns comfortably; backup = copy the file."),
    ("Vanilla JS — ", "progressive enhancement mirroring server validation (ISBN, phone, roll no.)."),
    ("Print CSS — ", "@media print hides chrome; the registers file straight to the principal’s tray."),
], size=10, gap=6)
chip(s, 0.55, 5.32, 1.05, "Python", fill=NAVY, tc=GOLD_L)
chip(s, 1.72, 5.32, 1.15, "Flask 3.1", fill=NAVY, tc=GOLD_L)
chip(s, 2.99, 5.32, 1.0, "Jinja", fill=NAVY, tc=GOLD_L)
chip(s, 4.11, 5.32, 1.15, "SQLite 3", fill=NAVY, tc=GOLD_L)
chip(s, 0.55, 5.72, 1.5, "vanilla JS", fill=NAVY2, tc=WHITE)
chip(s, 2.17, 5.72, 1.05, "pytest", fill=NAVY2, tc=WHITE)
chip(s, 3.34, 5.72, 1.6, "print CSS", fill=NAVY2, tc=WHITE)
chip(s, 5.06, 5.72, 1.15, "PBKDF2", fill=NAVY2, tc=WHITE)

# ================================================================ SLIDE 7 — ERD & constraints
s = add_slide(); header(s, "04 · DATA MODEL", "Four tables, no cleverness"); footer(s, 7)
pic_fit(s, f"{IMG}/fig-erd.png", 0.55, 1.5, 6.6, 4.35)
txt(s, 0.75, 5.9, 6.2, 0.3, [dict(runs=[("ERD — report §3.2; crow’s-foot cardinalities", dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
tables = [
    ("admin", "id · username UNIQUE · PBKDF2 hash · full_name"),
    ("book", "isbn UNIQUE · category · quantity · CHECK (qty ≥ 0, avail ≥ 0)"),
    ("member", "roll_no UNIQUE · email UNIQUE · phone · status CHECK · type CHECK"),
    ("issue_transaction", "FK book / member · dates · status CHECK · fine ≥ 0"),
]
for i, (t, d) in enumerate(tables):
    y = 1.52 + i * 0.92
    card(s, 7.5, y, 5.28, 0.78, radius=0.14)
    txt(s, 7.72, y + 0.075, 4.9, 0.3, [dict(runs=[(t, dict(font=MONO, size=10.5, bold=True, color=NAVY))])])
    txt(s, 7.72, y + 0.345, 4.9, 0.34, [dict(runs=[(d, dict(size=8.3, color=INK))], line_spacing=1.1)])
bullets(s, 7.5, 5.3, 5.3, 1.35, [
    ("Derived availability — ", "available_quantity recomputed from open issues; never hand-set."),
    ("ON DELETE CASCADE — ", "transactions removed with parent (limitation L-4, documented)."),
], size=9.5, gap=4)

# ================================================================ SLIDE 8 — Module hierarchy
s = add_slide(); header(s, "05 · MODULES", "Seven modules, one root package"); footer(s, 8)
pic_fit(s, f"{IMG}/fig-modules.png", 0.55, 1.48, 7.3, 4.35)
txt(s, 0.75, 5.88, 6.9, 0.3, [dict(runs=[("Module hierarchy — report §3.8; each leaf maps to a Flask route group",
                                            dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
routes = [
    ("auth_bp", "login · logout · change-password"),
    ("books", "/books  + /add /edit /delete /search"),
    ("members", "/members + /add /edit /delete /search"),
    ("circulation", "/issue  ·  /return/<id>  ·  /transactions"),
    ("fines", "/fines — collected vs pending, per defaulter"),
    ("reports", "/reports?report=issued|overdue|fine|stock|member"),
]
for i, (m, r) in enumerate(routes):
    y = 1.55 + i * 0.78
    rect(s, 8.15, y, 0.09, 0.62, fill=GOLD)
    txt(s, 8.38, y, 4.4, 0.28, [dict(runs=[(m, dict(font=MONO, size=10, bold=True, color=NAVY))])])
    txt(s, 8.38, y + 0.215, 4.4, 0.5, [dict(runs=[(r, dict(size=8.2, color=GREY))], line_spacing=1.05)])

# ================================================================ SLIDE 9 — Circulation rules
s = add_slide(); header(s, "05 · BUSINESS RULES", "The rules are the product"); footer(s, 9)
kpis = [("3", "books max\nper member"), ("14", "days\nper loan"), ("₹2", "per day\noverdue"), ("0", "borrows while\nmember inactive")]
kw = 2.98
for i, (v, d) in enumerate(kpis):
    x = 0.55 + i * (kw + 0.14)
    card(s, x, 1.5, kw, 1.28)
    txt(s, x, 1.62, kw, 0.75, [dict(runs=[(v, dict(size=44, bold=True, color=NAVY))], align=PP_ALIGN.CENTER)])
    for j, line in enumerate(d.split("\n")):
        txt(s, x, 2.28 + j * 0.19, kw, 0.2, [dict(runs=[(line, dict(size=8.5, bold=True, color=GOLD))], align=PP_ALIGN.CENTER)])
txt(s, 0.55, 3.06, 4.4, 0.3, [dict(runs=[("ISSUE — FAIL FAST, THEN COMMIT", dict(size=9.5, bold=True, color=GOLD))])])
bullets(s, 0.55, 3.4, 4.6, 1.65, [
    "Member exists and is Active",
    "availability > 0 · holds < 3",
    "No duplicate open issue of this title",
    "Insert txn + decrement stock — one commit",
], size=9.5, gap=3, marker="→  ", mcolor=GOLD)
txt(s, 0.55, 5.06, 4.6, 0.3, [dict(runs=[("RETURN — ONE DECISION", dict(size=9.5, bold=True, color=GOLD))])])
bullets(s, 0.55, 5.4, 4.6, 1.5, [
    ("late = ", "max(0, today − due_date)"),
    ("fine = ", "late × ₹2 — stored on the txn"),
    "Restore stock — same commit",
], size=9.5, gap=3, marker="→  ", mcolor=GOLD)
pic_fit(s, f"{IMG}/fig-activity.png", 5.5, 2.88, 7.3, 3.34)
txt(s, 5.75, 6.31, 6.8, 0.28, [dict(runs=[("Swimlane — issue & return paths with fine engine — report §3.6",
                                            dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])

# ================================================================ SLIDE 10 — Demo: dashboard
s = add_slide(); header(s, "06 · LIVE DEMO (1/3)", "Dashboard — the librarian’s morning glance"); footer(s, 10)
pic_fit(s, f"{IMG}/screen-dashboard-mock.png", 5.35, 1.5, 7.45, 4.55)
txt(s, 5.6, 6.12, 7.0, 0.28, [dict(runs=[("Rendering of the running app at http://127.0.0.1:5000 — seeded data, 09-11-2026",
                                           dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
txt(s, 0.55, 1.55, 4.4, 0.3, [dict(runs=[("WHAT TO NOTICE", dict(size=10, bold=True, color=GOLD))])])
bullets(s, 0.55, 2.0, 4.65, 3.9, [
    ("KPIs live from the DB — ", "12 titles · 67 copies · 60 available · 7 active members · ₹26 fines pending."),
    ("Recent transactions — ", "six latest borrows with status pills (Issued / Returned)."),
    ("Low-stock alert — ", "titles at ≤ 2 copies: “Compilers: Principles and Techniques” is flagged amber."),
    ("Session-gated — ", "everything sits behind admin login; anonymous hits bounce to /login (TC-04)."),
], size=10.5, gap=8)
chip(s, 0.55, 6.15, 4.6, "DEMO LOGIN   admin  /  admin123", fill=NAVY, tc=GOLD_L, size=11)

# ================================================================ SLIDE 11 — Demo: add book & return
s = add_slide(); header(s, "06 · LIVE DEMO (2/3)", "Write paths — add book · return book"); footer(s, 11)
pic_fit(s, f"{IMG}/screen-add-book-mock.png", 0.55, 1.5, 6.0, 3.6)
pic_fit(s, f"{IMG}/screen-return-mock.png", 6.8, 1.5, 6.0, 3.6)
txt(s, 0.55, 5.18, 6.0, 0.28, [dict(runs=[("Add book — ISBN regex + uniqueness; qty 0–10 000", dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
txt(s, 6.8, 5.18, 6.0, 0.28, [dict(runs=[("Return — late days & fine rendered per row", dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
card(s, 0.55, 5.62, 12.23, 1.05)
txt(s, 0.78, 5.74, 12, 0.28, [dict(runs=[("DEMO SCRIPT (what the panel watches)", dict(size=8.5, bold=True, color=GOLD))])])
txt(s, 0.78, 6.02, 11.9, 0.55, [dict(runs=[("1  Add a duplicate ISBN → inline error, nothing written   ·   2  Issue to a member already at 3 books → refused   ·   3  Return two days late → fine ₹4 posts to the ledger   ·   4  Open /reports?report=overdue → 5 flagged rows",
                                            dict(size=9, color=INK))], line_spacing=1.35)])

# ================================================================ SLIDE 12 — Reports
s = add_slide(); header(s, "07 · REPORTS", "Five registers, straight to the principal’s tray"); footer(s, 12)
headers = ["Register", "Question it answers", "Live rows", "Totals"]
rows = [
    ("Issued books", "Who holds what right now?", "7", "≥ 5 records ✓"),
    ("Overdue books", "Who is late — and by how much?", "5", "₹60 · ₹38 · ₹28 · ₹22 · ₹12 = ₹160 pending"),
    ("Fine history", "What was collected, when, from whom?", "6", "₹26 collected (0 defaulters waived)"),
    ("Stock register", "Category-wise holdings & availability", "6 groups", "67 copies · 60 available"),
    ("Member activity", "Per-member issues, open loans, fines", "8 members", "incl. members with zero issues (LEFT JOIN)"),
]
# table
tbl_shape = s.shapes.add_table(len(rows) + 1, 4, Inches(0.55), Inches(1.5), Inches(12.23), Inches(3.6)).table
tbl_shape.columns[0].width = Inches(2.15); tbl_shape.columns[1].width = Inches(4.6)
tbl_shape.columns[2].width = Inches(1.15); tbl_shape.columns[3].width = Inches(4.33)
for j, htxt in enumerate(headers):
    cell = tbl_shape.cell(0, j); cell.text = htxt
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    p = cell.text_frame.paragraphs[0]; p.line_spacing = 1.0
    r = p.runs[0]; r.font.name = SERIF; r.font.bold = True; r.font.size = Pt(10); r.font.color.rgb = GOLD_L
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        cell = tbl_shape.cell(i + 1, j); cell.text = val
        cell.fill.solid(); cell.fill.fore_color.rgb = WHITE if i % 2 == 0 else RGBColor(0xFB, 0xFA, 0xF6)
        p = cell.text_frame.paragraphs[0]; p.line_spacing = 1.05
        r = p.runs[0]; r.font.name = SERIF; r.font.size = Pt(9)
        r.font.color.rgb = INK if j != 0 else NAVY
        r.font.bold = (j == 0)
rect(s, 0.55, 5.35, 12.23, 0.62, fill=GREY_L, round_=True, radius=0.5)
txt(s, 0.82, 5.47, 12, 0.3, [dict(runs=[("≥ 5 valid records per report — the Review 3 acceptance bar, met from the seed itself.",
                                          dict(size=9.5, italic=True, color=NAVY3))])])
bullets(s, 0.55, 6.12, 12.2, 0.6, [
    ("Print-ready — ", "Ctrl+P: navigation and filters vanish via @media print; rows break cleanly across A4 pages."),
], size=9.5, gap=2)

# ================================================================ SLIDE 13 — Testing
s = add_slide(); header(s, "08 · TESTING", "Evidence, not adjectives"); footer(s, 13)
card(s, 0.55, 1.5, 6.0, 3.3)
txt(s, 0.8, 1.66, 5.5, 0.3, [dict(runs=[("TRACK A — AUTOMATED (pytest)", dict(size=10, bold=True, color=GOLD))])])
txt(s, 0.8, 2.05, 5.5, 0.6, [dict(runs=[("12 / 12 passing · 0.36 s · isolated temp DB", dict(size=15, bold=True, color=GREEN))])])
bullets(s, 0.8, 2.72, 5.6, 1.6, [
    "Auth: login page, wrong password → 401, anonymous → /login",
    "Catalogue: 12 titles listed · duplicate ISBN rejected · bad ISBN rejected",
    "Circulation: ₹4 fine after 5 days · issue blocks at capacity",
    "Reports & settings: CSV-able output · wrong current password rejected",
], size=8.6, gap=3, marker="•  ", mcolor=GOLD)
rect(s, 0.8, 4.6, 5.5, 0.42, fill=NAVY, round_=True, radius=0.5)
txt(s, 0.95, 4.71, 5.2, 0.24, [dict(runs=[("$ python -m pytest tests/test_app.py -v", dict(font=MONO, size=9.5, color=GOLD_L))])])

card(s, 6.8, 1.5, 6.0, 3.3)
txt(s, 7.05, 1.66, 5.5, 0.3, [dict(runs=[("TRACK B — MANUAL (LIVE, 09-11-2026)", dict(size=10, bold=True, color=GOLD))])])
txt(s, 7.05, 2.05, 5.5, 0.6, [dict(runs=[("8 / 8 scenarios PASS · TC-13 … TC-20", dict(size=15, bold=True, color=GREEN))])])
bullets(s, 7.05, 2.72, 5.6, 1.6, [
    "TC-13/14 login & anonymous bounce (401 / 302)",
    "TC-15 search ‘java’ → Effective Java + The Complete Reference",
    "TC-16/17 overdue & fine ledgers — rows verified vs hand-computed",
    "TC-18/19 duplicate ISBN & phone validation · TC-20 password guard",
], size=8.6, gap=3, marker="•  ", mcolor=GOLD)
rect(s, 7.05, 4.6, 5.5, 0.42, fill=NAVY, round_=True, radius=0.5)
txt(s, 7.2, 4.71, 5.2, 0.24, [dict(runs=[("$ curl -i -X POST …/login  →  HTTP/1.1 401", dict(font=MONO, size=9.5, color=GOLD_L))])])

txt(s, 0.55, 5.06, 12.2, 0.3, [dict(runs=[("DEFECTS FOUND & FIXED DURING TESTING", dict(size=9.5, bold=True, color=GOLD))])])
bullets(s, 0.55, 5.4, 12.3, 0.95, [
    ("Three, all re-verified — ", "(1) Jinja duplicate-block error in base.html · (2) available_quantity drift after seeding — availability now derived by SQL · (3) test_10 assertion mismatch on flash wording."),
    ("Regression — ", "full suite re-run: 12 passed in 0.36 s; manual TC-16 re-check matched the hand-computed ledger (₹60, ₹38, ₹28, ₹22, ₹12)."),
], size=9.5, gap=3)

# ================================================================ SLIDE 14 — Timeline & deliverables
s = add_slide(); header(s, "09 · TIMELINE", "Seven weeks, four review gates"); footer(s, 14)
pic_fit(s, f"{IMG}/fig-gantt.png", 0.55, 1.5, 12.23, 2.6)
milestones = [
    ("REVIEW 1", "SRS & feasibility", "done"),
    ("REVIEW 2", "ERD · UML · module hierarchy", "done"),
    ("REVIEW 3", "21-11-2026 — working build + tests", "today"),
    ("FINAL", "19-12-2026 — viva + hard-bound report", "next"),
]
mw = 2.98
for i, (r, d, st) in enumerate(milestones):
    x = 0.55 + i * (mw + 0.13)
    done = st == "done"
    card(s, x, 4.6, mw, 1.05, fill=(NAVY if st == "today" else WHITE), line=(GOLD if st == "today" else GOLD))
    txt(s, x + 0.16, 4.72, mw - 0.3, 0.26, [dict(runs=[(r, dict(size=9.5, bold=True, color=(GOLD_L if st == "today" else GOLD)))])])
    txt(s, x + 0.16, 4.98, mw - 0.3, 0.55, [dict(runs=[(d, dict(size=8.5, color=(CREAM if st == "today" else INK)))], line_spacing=1.12)])
rect(s, 0.55, 5.95, 12.23, 0.48, fill=GREY_L, round_=True, radius=0.5)
txt(s, 0.82, 6.07, 12, 0.28, [dict(runs=[("Effort ≈ 70 person-hours  ·  Artefacts: report (33 pp) · PPT · app + tests · this demo — all in the repository on branch arena/aafd53cc-yashwant-git392",
                                           dict(size=9, color=NAVY3))])])

# ================================================================ SLIDE 15 — Future work
s = add_slide(); header(s, "10 · FUTURE WORK", "From a tool to a managed service"); footer(s, 15)
phases = [
    ("v1.x — EXTEND THE DESK", "ships on the current monolith", [
        ("E-1", "Barcode / RFID scanning — keyboard-wedge, zero form redesign", "2 wks"),
        ("E-2", "Overdue reminders — nightly cron, 1/3/7-day buckets", "2 wks"),
        ("E-3", "Member self-service OPAC — search, own history, renew", "3 wks"),
        ("E-4", "Auto-numbered fine receipts + UPI QR", "1 wk"),
    ]),
    ("v1.3–1.5 — OPERATE IT", "infrastructure & visibility", [
        ("E-5", "MySQL 8 migration — DDL ports 1:1, portable SQL throughout", "3 days"),
        ("E-6", "Soft-delete + audit tables — reconstruct history anytime", "1 wk"),
        ("E-7", "Management dashboards — circulation/month, defaulter rank", "2 wks"),
        ("E-8", "Public OPAC kiosk — entrance touchscreen, kiosk mode", "1 wk"),
    ]),
    ("v2.0 — RESEARCH", "beyond the brief, deliberately", [
        ("E-9", "Recommendation engine — borrow co-occurrence CF", "research"),
        ("E-10", "docker-compose — gunicorn + nginx + mysql, one command", "3 days"),
    ]),
]
pw = 3.94
for i, (ph, sub, items) in enumerate(phases):
    x = 0.55 + i * (pw + 0.205)
    card(s, x, 1.5, pw, 4.6)
    txt(s, x + 0.2, 1.66, pw - 0.4, 0.3, [dict(runs=[(ph, dict(size=11, bold=True, color=NAVY))])])
    txt(s, x + 0.2, 1.95, pw - 0.4, 0.25, [dict(runs=[(sub, dict(size=8, italic=True, color=GREY))])])
    yy = 2.35
    for eid, d, t in items:
        chip(s, x + 0.2, yy, 0.52, eid, fill=NAVY, tc=GOLD_L, size=9)
        txt(s, x + 0.82, yy + 0.01, pw - 1.75, 0.75, [dict(runs=[(d, dict(size=8.2, color=INK))], line_spacing=1.1)])
        txt(s, x + pw - 0.85, yy + 0.01, 0.68, 0.3, [dict(runs=[(t, dict(size=7.5, bold=True, color=GOLD))], align=PP_ALIGN.RIGHT)])
        yy += 0.88 if len(items) > 2 else 0.78
rect(s, 0.55, 6.3, 12.23, 0.42, fill=GREY_L, round_=True, radius=0.5)
txt(s, 0.82, 6.41, 12, 0.24, [dict(runs=[("Every limitation in the report (L-1…L-10) maps to one of these — the upgrade path is written down, not improvised.",
                                           dict(size=9, italic=True, color=NAVY3))])])

# ================================================================ SLIDE 16 — Thanks / Q&A
s = add_slide(); set_bg(s, NAVY)
ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.42), Inches(13.333), Pt(1.6))
ln.fill.solid(); ln.fill.fore_color.rgb = GOLD; ln.line.fill.background(); ln.shadow.inherit = False
ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.08), Inches(13.333), Pt(1.6))
ln.fill.solid(); ln.fill.fore_color.rgb = GOLD; ln.line.fill.background(); ln.shadow.inherit = False
txt(s, 0.85, 0.78, 6.0, 0.35, [dict(runs=[("QUESTIONS & ANSWERS", dict(size=12, bold=True, color=GOLD))])])
txt(s, 0.85, 1.18, 8.2, 1.5, [dict(runs=[("Thank you.", dict(size=72, bold=True, color=WHITE))], line_spacing=0.98)])
rect(s, 0.88, 2.78, 1.7, 0.034, fill=GOLD)
txt(s, 0.85, 3.02, 6.4, 0.35, [dict(runs=[("If you remember three things", dict(size=13, bold=True, color=GOLD_L))])])
bullets(s, 0.85, 3.45, 6.1, 2.2, [
    ("Boring works — ", "Flask + SQLite + seeded data beats a grand stack the library cannot maintain."),
    ("Tests are the demo — ", "12/12 automated and 8/8 manual, run live in front of you."),
    ("The college can run this tomorrow — ", "clone, pip install, python run.py, sign in."),
], size=11, gap=8, color=CREAM, mcolor=GOLD_L)
card(s, 8.35, 1.18, 4.15, 4.6, fill=NAVY3, line=GOLD, line_w=1.3, radius=0.07)
txt(s, 8.62, 1.38, 3.6, 0.3, [dict(runs=[("TRY IT YOURSELF", dict(size=9.5, bold=True, color=GOLD))])])
txt(s, 8.62, 1.78, 3.7, 0.32, [dict(runs=[("git clone https://github.com/", dict(font=MONO, size=9, color=GOLD_L))])])
txt(s, 8.62, 2.06, 3.7, 0.32, [dict(runs=[("Yashwant-git392/Yashwant-git392.git", dict(font=MONO, size=9, color=GOLD_L))])])
txt(s, 8.62, 2.4, 3.7, 0.32, [dict(runs=[("cd Yashwant-git392/mini-project", dict(font=MONO, size=9, color=CREAM))])])
txt(s, 8.62, 2.68, 3.7, 0.32, [dict(runs=[("pip install -r requirements.txt", dict(font=MONO, size=9, color=CREAM))])])
txt(s, 8.62, 2.96, 3.7, 0.32, [dict(runs=[("python run.py", dict(font=MONO, size=9, color=CREAM))])])
rect(s, 8.62, 3.4, 3.6, 0.015, fill=GOLD)
txt(s, 8.62, 3.55, 3.7, 0.3, [dict(runs=[("http://127.0.0.1:5000", dict(font=MONO, size=10.5, bold=True, color=WHITE))])])
txt(s, 8.62, 3.9, 3.7, 0.3, [dict(runs=[("admin  /  admin123", dict(font=MONO, size=10.5, bold=True, color=GOLD_L))])])
txt(s, 8.62, 4.35, 3.7, 1.3,
    [dict(runs=[("Report — 33 pages, Ch. 1–10 + Appendices A–C", dict(size=9, color=CREAM))], space_after=3),
     dict(runs=[("Branch — arena/aafd53cc-yashwant-git392", dict(size=9, color=CREAM))], space_after=3),
     dict(runs=[("Yashwant Shelke · MCA-I (Sem-I) · 2026-27", dict(size=9, color=RGBColor(0x9F,0xAD,0xC8)))])])
txt(s, 0.85, 6.35, 12.0, 0.35,
    [dict(runs=[("SmartLibrary — because the register deserved a better afterlife.", dict(size=11, italic=True, color=RGBColor(0xC9,0xD2,0xE4)))])])

prs.save(OUT)
print("Saved:", OUT, "| slides:", len(prs.slides._sldIdLst))

#!/usr/bin/env python3
"""Build CampusShikayatSetu_MCA-Mini-Project_Review.pptx — 16 slides, 16:9.

Design system matches the project report: NAVY / GOLD / CREAM, Georgia display serif.
All figures are the real generated assets from ../report/images/.
"""
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

IMG = "/home/user/Yashwant-git392/shikayat-setu/report/images"
OUT = "/home/user/Yashwant-git392/shikayat-setu/presentation/CampusShikayatSetu_MCA-Mini-Project_Review.pptx"

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
        [dict(runs=[("Campus Shikayat Setu — College Grievance Redressal System  ·  SPPU MCA-I (Sem-I) Application Development  ·  2026-27",
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
# notice-board glyph (drawn, right side)
bx, by = 10.62, 1.55
rect(s, bx, by, 1.66, 2.34, fill=NAVY3, round_=True, radius=0.09)
rect(s, bx + 0.22, by + 0.24, 1.22, 0.16, fill=GOLD)
rect(s, bx + 0.22, by + 0.56, 1.22, 0.075, fill=RGBColor(0x8F, 0xA3, 0xC4))
rect(s, bx + 0.22, by + 0.74, 1.22, 0.075, fill=RGBColor(0x8F, 0xA3, 0xC4))
rect(s, bx + 0.22, by + 0.92, 0.85, 0.075, fill=RGBColor(0x8F, 0xA3, 0xC4))
rect(s, bx + 0.22, by + 1.38, 0.9, 0.34, fill=GOLD)
ln = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(bx + 0.32), Inches(by + 1.455), Inches(0.10), Inches(0.15))
ln.fill.solid(); ln.fill.fore_color.rgb = RGBColor(0x3D, 0x2E, 0x00); ln.line.fill.background(); ln.shadow.inherit = False
rect(s, bx + 0.22, by + 1.86, 1.22, 0.10, fill=GOLD_L)
ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.42), Inches(13.333), Pt(1.6))
ln.fill.solid(); ln.fill.fore_color.rgb = GOLD; ln.line.fill.background(); ln.shadow.inherit = False
ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.08), Inches(13.333), Pt(1.6))
ln.fill.solid(); ln.fill.fore_color.rgb = GOLD; ln.line.fill.background(); ln.shadow.inherit = False

txt(s, 0.75, 0.72, 9.4, 0.35, [dict(runs=[("SAVITRIBAI PHULE PUNE UNIVERSITY  ·  MCA-I (SEM-I)  ·  APPLICATION DEVELOPMENT  ·  2026-27",
                                          dict(size=10, bold=True, color=GOLD))])])
txt(s, 0.75, 1.28, 9.6, 1.55, [dict(runs=[("Campus Shikayat Setu", dict(size=58, bold=True, color=WHITE))], line_spacing=0.98)])
txt(s, 0.75, 2.55, 9.4, 0.6, [dict(runs=[("College Grievance Redressal System", dict(size=26, bold=True, color=GOLD_L))])])
rect(s, 0.78, 3.35, 1.7, 0.037, fill=GOLD)
txt(s, 0.75, 3.55, 9.2, 0.75,
    [dict(runs=[("Turning the college’s complaint box into an auditable, SLA-bound grievance pipeline —",
                 dict(size=14, italic=True, color=CREAM))], line_spacing=1.15),
     dict(runs=[("lodge · auto-route · track · resolve — with a paper trail for every step.", dict(size=14, italic=True, color=RGBColor(0xC9,0xD2,0xE4)))])])
txt(s, 0.75, 5.0, 8.6, 1.6,
    [dict(runs=[("Yashwant Santosh Ahire", dict(size=17.5, bold=True, color=WHITE))], space_after=2),
     dict(runs=[("Guide: Mrs. Priyanka M. Jagtap", dict(size=11.5, color=CREAM))], space_after=2),
     dict(runs=[("Dr. B.V. Hiray College of Management and Research Centre, Malegaon (Nashik)", dict(size=10.5, color=RGBColor(0x9F,0xAD,0xC8)))])])
txt(s, 10.35, 5.28, 2.45, 1.35,
    [dict(runs=[("REVIEW 3", dict(size=9, bold=True, color=GOLD))], space_after=1),
     dict(runs=[("21 November 2026", dict(size=13, bold=True, color=WHITE))], space_after=8),
     dict(runs=[("FINAL VIVA", dict(size=9, bold=True, color=GOLD))], space_after=1),
     dict(runs=[("19 December 2026", dict(size=13, bold=True, color=WHITE))])])

# ================================================================ SLIDE 2 — Agenda & at a glance
s = add_slide(); header(s, "AGENDA", "What we will walk through — in ten minutes"); footer(s, 2)
agenda = [
    ("01", "The problem", "why the complaint box had to go"),
    ("02", "Objectives & scope", "v1.0 goals, in/out of scope"),
    ("03", "Users & use cases", "student · officer · admin · public"),
    ("04", "Architecture & data", "Flask + SQLite, ERD, constraints"),
    ("05", "Modules & routing rules", "keyword engine · SLA · audit timeline"),
    ("06", "Live demo", "dashboard, console, timeline"),
    ("07", "Reports", "six registers, ≥ 5 valid records each"),
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
stats = [("6", "departments"), ("15", "categories"), ("15", "users seeded"), ("32", "complaints"), ("100", "audit events"), ("12/12", "tests passing")]
sw = 11.9 / len(stats)
for i, (v, d) in enumerate(stats):
    x = 0.62 + i * sw
    txt(s, x, 6.02, sw - 0.15, 0.5, [dict(runs=[(v, dict(size=21, bold=True, color=NAVY))])])
    txt(s, x, 6.42, sw - 0.15, 0.3, [dict(runs=[(d, dict(size=7.5, color=GREY))])])

# ================================================================ SLIDE 3 — The problem
s = add_slide(); header(s, "01 · CONTEXT", "The complaint box is a black hole"); footer(s, 3)
txt(s, 0.55, 1.5, 7.1, 0.35, [dict(runs=[("What the college lives with today", dict(size=13, bold=True, color=NAVY))])])
bullets(s, 0.55, 1.95, 7.0, 4.0, [
    ("A locked wooden box — ", "complaints dropped in weekly; read when the cell gets around to it."),
    ("No routing, no owner — ", "a broken fan complaint may sit in the admin room for weeks."),
    ("No status, ever — ", "students walk back to ask “what happened to my complaint?”"),
    ("Sensitive topics go unsaid — ", "ragging & harassment: never named, because nothing is anonymous."),
    ("Zero data — ", "pendency, SLA breaches, repeat offenders: nobody knows."),
], size=12, gap=8)
card(s, 8.15, 1.5, 4.62, 4.42, fill=NAVY, line=None)
txt(s, 8.45, 1.78, 4.1, 0.35, [dict(runs=[("WHY NOT THE USUAL ANSWERS?", dict(size=10, bold=True, color=GOLD))])])
bullets(s, 8.45, 2.25, 4.15, 3.5, [
    ("CPGRAMS — ", "central government portal; no department mapping, no campus context."),
    ("Excel registers — ", "linear scan, version corruption, zero privacy for complainants."),
    ("ERP add-ons — ", "vendor lock-in, licence cost; a grievance module nobody opens."),
], size=10, gap=7, color=CREAM, mcolor=GOLD_L)
txt(s, 8.45, 4.72, 4.1, 1.1,
    [dict(runs=[("Right-sized answer: ", dict(size=10.5, bold=True, color=GOLD_L)),
                ("a focused, self-hosted web app that runs on the college PC — SLA-bound, audit-trailed, anonymous-safe.", dict(size=10.5, color=CREAM))], line_spacing=1.22)])
rect(s, 0.55, 6.12, 12.23, 0.5, fill=GREY_L, round_=True, radius=0.5)
txt(s, 0.85, 6.24, 11.7, 0.3, [dict(runs=[("Scope fixed for Sem-I: student · officer · admin roles, feedback & reopen loop — nothing more, nothing hidden.",
                                           dict(size=9.5, italic=True, color=NAVY3))])])

# ================================================================ SLIDE 4 — Objectives & scope
s = add_slide(); header(s, "02 · OBJECTIVES & SCOPE", "What v1.0 sets out to do"); footer(s, 4)
txt(s, 0.55, 1.5, 4.6, 0.32, [dict(runs=[("OBJECTIVES", dict(size=10, bold=True, color=GOLD))])])
objectives = [
    "One-page complaint lodging with title/description guard rails",
    "Keyword-scored auto-routing to the right department on submit",
    "SLA engine: High 24 h · Medium 72 h · Low 7 days, stamped at lodge time",
    "Full audit timeline per complaint — every action, every actor, forever",
    "Anonymous lodgement for sensitive grievances (admin-only identity)",
    "Six print-ready registers + public tracker (code + roll no.)",
]
for i, o in enumerate(objectives):
    y = 1.92 + i * 0.62
    chip(s, 0.55, y, 0.42, f"O{i+1}", fill=NAVY, tc=GOLD_L, size=10)
    txt(s, 1.12, y + 0.015, 4.6, 0.6, [dict(runs=[(o, dict(size=9.2, color=INK))], line_spacing=1.08)])

card(s, 6.15, 1.5, 6.6, 2.32)
txt(s, 6.4, 1.66, 3.0, 0.3, [dict(runs=[("IN SCOPE — v1.0", dict(size=9.5, bold=True, color=GREEN))])])
bullets(s, 6.4, 2.05, 6.15, 1.7, [
    "Register & login; PBKDF2 hashing; signed sessions",
    "Keyword routing with explainable scores (title weighted ×2)",
    "Acknowledge → in-progress → resolve; feedback ★1–5 closes; reopen ≤ 7 days",
    "Officer department queue; admin console (reassign/escalate/force-close)",
    "Print CSS registers; public tracker without login",
], size=9.2, gap=3, marker="•  ", mcolor=GREEN)
card(s, 6.15, 4.02, 6.6, 2.35)
txt(s, 6.4, 4.18, 4.5, 0.3, [dict(runs=[("OUT OF SCOPE — v1.0 (each maps to an enhancement)", dict(size=9.5, bold=True, color=RED))])])
bullets(s, 6.4, 4.57, 6.15, 1.75, [
    "E-mail / SMS / WhatsApp notifications (E-1, E-2)",
    "Photo evidence upload (E-3)",
    "Category admin UI & MySQL migration (E-4, E-5)",
    "Nightly SLA-breach cron + auto-escalation (E-6)",
    "Marathi / Hindi UI (E-9) · ERP roll-no bridge (E-10)",
], size=9.2, gap=3, marker="•  ", mcolor=RED)

# ================================================================ SLIDE 5 — Users & use cases
s = add_slide(); header(s, "03 · USERS & USE CASES", "Three logged-in roles, one public door"); footer(s, 5)
card(s, 0.55, 1.5, 4.35, 1.5)
txt(s, 0.78, 1.62, 3.9, 0.3, [dict(runs=[("ACTOR 1 — STUDENT (COMPLAINANT)", dict(size=9, bold=True, color=GOLD))])])
txt(s, 0.78, 1.94, 3.9, 0.26, [dict(runs=[("The aggrieved", dict(size=11, bold=True, color=NAVY))])])
txt(s, 0.78, 2.26, 3.95, 0.72, [dict(runs=[("Lodges complaints (optionally anonymous), tracks by code, rates resolutions, reopens within 7 days.",
                                             dict(size=9.5, color=INK))], line_spacing=1.15)])
card(s, 0.55, 3.14, 4.35, 1.5)
txt(s, 0.78, 3.26, 3.9, 0.3, [dict(runs=[("ACTOR 2 — OFFICER (DEPARTMENT)", dict(size=9, bold=True, color=GOLD))])])
txt(s, 0.78, 3.58, 3.9, 0.26, [dict(runs=[("The resolver", dict(size=11, bold=True, color=NAVY))])])
txt(s, 0.78, 3.90, 3.95, 0.72, [dict(runs=[("Sees only own-department queue; acknowledges, works, resolves with a mandatory remark.",
                                             dict(size=9.5, color=INK))], line_spacing=1.15)])
card(s, 0.55, 4.78, 4.35, 1.5)
txt(s, 0.78, 4.90, 3.9, 0.3, [dict(runs=[("ACTOR 3 — ADMINISTRATOR", dict(size=9, bold=True, color=GOLD))])])
txt(s, 0.78, 5.22, 3.9, 0.26, [dict(runs=[("The backstop", dict(size=11, bold=True, color=NAVY))])])
txt(s, 0.78, 5.54, 3.95, 0.72, [dict(runs=[("Console over everything; reassign, escalate to High, force-close after 7 quiet days; identity of anonymous complainants.",
                                             dict(size=9.5, color=INK))], line_spacing=1.12)])
pic_fit(s, f"{IMG}/fig-usecase.png", 5.25, 1.52, 7.55, 4.9)
txt(s, 5.6, 6.5, 7.0, 0.3, [dict(runs=[("Use-case diagram — report §3.3; roles swimlane-separated, public tracker outside login",
                                          dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])

# ================================================================ SLIDE 6 — Architecture & stack
s = add_slide(); header(s, "04 · ARCHITECTURE", "Boring technology, deliberately"); footer(s, 6)
pic_fit(s, f"{IMG}/fig-architecture.png", 5.15, 1.5, 7.65, 3.6)
txt(s, 5.5, 5.22, 7.0, 0.3, [dict(runs=[("Three tiers on one machine — scale-out path: gunicorn + nginx + MySQL (E-5 / E-10)",
                                          dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
txt(s, 0.55, 1.5, 4.3, 0.32, [dict(runs=[("WHY THIS STACK", dict(size=10, bold=True, color=GOLD))])])
bullets(s, 0.55, 1.95, 4.35, 3.05, [
    ("Flask 3.x — ", "server-rendered Jinja; zero build step; the demo never depends on the network."),
    ("SQLite — ", "one file = whole DB; FK/CHECK/UNIQUE enforced; backup = copy file."),
    ("Vanilla JS — ", "length/roll sanity mirrors server validation; no framework."),
    ("Print CSS — ", "registers file straight to the principal’s tray, A4, no truncation."),
], size=10, gap=6)
chip(s, 0.55, 5.32, 1.05, "Python", fill=NAVY, tc=GOLD_L)
chip(s, 1.72, 5.32, 1.15, "Flask 3.x", fill=NAVY, tc=GOLD_L)
chip(s, 2.99, 5.32, 1.0, "Jinja", fill=NAVY, tc=GOLD_L)
chip(s, 4.11, 5.32, 1.15, "SQLite 3", fill=NAVY, tc=GOLD_L)
chip(s, 0.55, 5.72, 1.5, "vanilla JS", fill=NAVY2, tc=WHITE)
chip(s, 2.17, 5.72, 1.05, "pytest", fill=NAVY2, tc=WHITE)
chip(s, 3.34, 5.72, 1.6, "print CSS", fill=NAVY2, tc=WHITE)
chip(s, 5.06, 5.72, 1.15, "PBKDF2", fill=NAVY2, tc=WHITE)

# ================================================================ SLIDE 7 — ERD & constraints
s = add_slide(); header(s, "04 · DATA MODEL", "Six tables, no cleverness"); footer(s, 7)
pic_fit(s, f"{IMG}/fig-erd.png", 0.55, 1.5, 6.6, 4.35)
txt(s, 0.75, 5.9, 6.2, 0.3, [dict(runs=[("ERD — report §3.2; PK/FK crow’s-foot cardinalities", dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
tables = [
    ("departments", "name UNIQUE · head_name · email · location"),
    ("categories", "FK→departments · default_priority CHECK · keywords TEXT"),
    ("users", "role CHECK(student|officer|admin) · username UNIQUE · roll_no UNIQUE"),
    ("complaints", "code UNIQUE (CMP-YYYY-NNNN) · priority/routing/status CHECKs · sla_due_at"),
    ("complaint_events", "append-only audit log · FK ON DELETE CASCADE · actor NULL for system"),
    ("feedback", "complaint_id UNIQUE · rating CHECK(1..5)"),
]
for i, (t, d) in enumerate(tables):
    y = 1.5 + i * 0.72
    card(s, 7.5, y, 5.28, 0.6, radius=0.14)
    txt(s, 7.72, y + 0.05, 4.9, 0.26, [dict(runs=[(t, dict(font=MONO, size=9.5, bold=True, color=NAVY))])])
    txt(s, 7.72, y + 0.28, 4.9, 0.3, [dict(runs=[(d, dict(size=7.4, color=INK))], line_spacing=1.05)])
bullets(s, 7.5, 5.95, 5.3, 1.1, [
    ("Overdue never stored — ", "derived: now > sla_due_at AND status ∉ (Resolved, Closed)."),
], size=9, gap=3)

# ================================================================ SLIDE 8 — Module hierarchy
s = add_slide(); header(s, "05 · MODULES", "One app, three role layers"); footer(s, 8)
pic_fit(s, f"{IMG}/fig-modules.png", 0.55, 1.48, 7.3, 4.35)
txt(s, 0.75, 5.88, 6.9, 0.3, [dict(runs=[("Module hierarchy — report §3.7; each leaf maps to a Flask route group",
                                            dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
routes = [
    ("auth_bp", "/login · /logout · /register · /change-password"),
    ("student", "/lodge · /my-complaints · /complaint/<code>/feedback|reopen"),
    ("officer", "/queue · /complaint/<code>/acknowledge|start|resolve|remark"),
    ("admin", "/console · /reassign · /escalate · /force-close · /users · /officers"),
    ("public", "/track — complaint code + roll no., no login"),
    ("reports", "/reports?report=pendency|sla|restime|trend|feedback|routing"),
]
for i, (m, r) in enumerate(routes):
    y = 1.55 + i * 0.78
    rect(s, 8.15, y, 0.09, 0.62, fill=GOLD)
    txt(s, 8.38, y, 4.4, 0.28, [dict(runs=[(m, dict(font=MONO, size=10, bold=True, color=NAVY))])])
    txt(s, 8.38, y + 0.215, 4.4, 0.5, [dict(runs=[(r, dict(size=7.9, color=GREY))], line_spacing=1.05)])

# ================================================================ SLIDE 9 — Business rules
s = add_slide(); header(s, "05 · BUSINESS RULES", "The rules are the product"); footer(s, 9)
kpis = [("24h", "High\npriority SLA"), ("72h", "Medium\npriority SLA"), ("7d", "Low priority SLA\n& reopen window"), ("×2", "title keyword\nweighting")]
kw = 2.98
for i, (v, d) in enumerate(kpis):
    x = 0.55 + i * (kw + 0.14)
    card(s, x, 1.5, kw, 1.28)
    txt(s, x, 1.62, kw, 0.75, [dict(runs=[(v, dict(size=40, bold=True, color=NAVY))], align=PP_ALIGN.CENTER)])
    for j, line in enumerate(d.split("\n")):
        txt(s, x, 2.26 + j * 0.19, kw, 0.2, [dict(runs=[(line, dict(size=8, bold=True, color=GOLD))], align=PP_ALIGN.CENTER)])
txt(s, 0.55, 3.06, 5.0, 0.3, [dict(runs=[("ROUTING — EXPLAINABLE, ALWAYS", dict(size=9.5, bold=True, color=GOLD))])])
bullets(s, 0.55, 3.4, 4.9, 1.85, [
    "Weight = 2 per word of keyword; title scores ×2",
    "SAFETY_WORDS (ragging, shock, fire…) force High",
    "MASS_IMPACT (“entire”, “all students”) bumps one level",
    "No match → General & Administration (logged manual fallback)",
], size=9.2, gap=3, marker="→  ", mcolor=GOLD)
txt(s, 0.55, 5.3, 4.6, 0.3, [dict(runs=[("RESOLUTION LOOP", dict(size=9.5, bold=True, color=GOLD))])])
bullets(s, 0.55, 5.64, 4.6, 1.3, [
    ("resolve — ", "remark ≥ 10 chars, status → Resolved"),
    ("close — ", "student rates ★1–5 → Closed"),
    ("reopen — ", "≤ 7 days → back to In Progress"),
], size=9.2, gap=3, marker="→  ", mcolor=GOLD)
pic_fit(s, f"{IMG}/fig-activity.png", 5.55, 2.9, 7.25, 3.35)
txt(s, 5.75, 6.33, 6.8, 0.28, [dict(runs=[("Swimlane — lodge → route → resolve → close, admin escalation path — report §3.4",
                                            dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
# ================================================================ SLIDE 10 — Demo: student view
s = add_slide(); header(s, "06 · LIVE DEMO (1/2)", "Student view — lodge, track, confirm"); footer(s, 10)
pic_fit(s, f"{IMG}/screen-dashboard-mock.png", 5.3, 1.5, 7.5, 4.55)
txt(s, 5.55, 6.12, 7.0, 0.28, [dict(runs=[("Rendering of the running app at http://127.0.0.1:5001 — seeded data, 09-11-2026",
                                           dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
txt(s, 0.55, 1.55, 4.4, 0.3, [dict(runs=[("WHAT TO NOTICE", dict(size=10, bold=True, color=GOLD))])])
bullets(s, 0.55, 2.0, 4.6, 3.9, [
    ("Signed in as MCA2026001 — ", "dashboard shows only your own complaints, KPIs counted live."),
    ("Lodge in one page — ", "title ≥ 8 · description ≥ 20; router confirms or overrides the picked category, score printed on the timeline."),
    ("Feedback closes, reopen ≤ 7 days — ", "if the fix failed, one click sends it back to In Progress."),
    ("Public tracker — ", "CMP code + roll number, no login: great for the demo queue."),
], size=10.5, gap=8)

# ================================================================ SLIDE 11 — Demo: admin/console + audit timeline
s = add_slide(); header(s, "06 · LIVE DEMO (2/2)", "Admin view — console & audit trail"); footer(s, 11)
pic_fit(s, f"{IMG}/screen-console-mock.png", 0.55, 1.5, 6.05, 3.6)
txt(s, 0.75, 5.18, 5.8, 0.28, [dict(runs=[("Admin console — filters, reassign, escalate → High, force-close — report §3.3 UC-11",
                                            dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
pic_fit(s, f"{IMG}/screen-timeline-mock.png", 6.9, 1.5, 5.9, 3.6)
txt(s, 7.1, 5.18, 5.5, 0.28, [dict(runs=[("Complaint detail — the timeline IS the audit trail (append-only events)",
                                            dict(size=8, italic=True, color=GREY))], align=PP_ALIGN.CENTER)])
card(s, 0.55, 5.55, 12.23, 0.85, fill=NAVY, line=None)
txt(s, 0.8, 5.68, 11.8, 0.3, [dict(runs=[("EVERY DEMO IS DETERMINISTIC", dict(size=9, bold=True, color=GOLD))])])
txt(s, 0.8, 5.95, 11.8, 0.3, [dict(runs=[("Fresh clone → seed → 32 complaints, 100 events, 6 feedback rows — the viva demo reproduces exactly; no live typing needed.",
                                            dict(size=9.5, color=CREAM))])])

# ================================================================ SLIDE 12 — Reports
s = add_slide(); header(s, "07 · REPORTS", "Six print registers, straight from SQL"); footer(s, 12)
tbl_shape = s.shapes.add_table(7, 3, Inches(0.55), Inches(1.5), Inches(12.23), Inches(3.6)).table
tbl_shape.columns[0].width = Inches(0.55); tbl_shape.columns[1].width = Inches(5.4); tbl_shape.columns[2].width = Inches(6.28)
rows = [
    ("#", "Register", "What it proves"),
    ("1", "Department pendency", "Open workload per department + overdue count (derives from SLA)"),
    ("2", "SLA compliance", "% resolved within deadline per department — ROUND over COUNT"),
    ("3", "Avg resolution time", "Hours per category, julianday arithmetic on timestamps"),
    ("4", "Monthly trend", "Lodged vs resolved, last 6 months — capacity planning"),
    ("5", "Feedback / ratings", "Average ★ per department + latest 10 comments"),
    ("6", "Routing quality", "auto vs manual split + avg routing score — proves the router"),
]
tbl_shape.rows[0].height = Inches(0.42)
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        cell = tbl_shape.cell(i, j); cell.text = val
        if i == 0:
            cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
            p = cell.text_frame.paragraphs[0]; p.line_spacing = 1.0
            r = p.runs[0]; r.font.name = SERIF; r.font.bold = True; r.font.size = Pt(10); r.font.color.rgb = GOLD_L
        else:
            cell.fill.solid(); cell.fill.fore_color.rgb = WHITE if i % 2 else RGBColor(0xFB, 0xFA, 0xF6)
            p = cell.text_frame.paragraphs[0]; p.line_spacing = 1.05
            r = p.runs[0]; r.font.name = SERIF; r.font.size = Pt(9)
            r.font.color.rgb = INK if j != 0 else NAVY
            r.font.bold = (j == 0)
rect(s, 0.55, 5.35, 12.23, 0.62, fill=GREY_L, round_=True, radius=0.5)
txt(s, 0.82, 5.47, 12, 0.3, [dict(runs=[("≥ 5 valid records per report — the Review 3 acceptance bar, met from the seed itself (32 complaints, 6 departments).",
                                          dict(size=9.5, italic=True, color=NAVY3))])])
bullets(s, 0.55, 6.12, 12.2, 0.6, [
    ("Print-ready — ", "Ctrl+P: chrome vanishes via @media print; A4 portrait; headers repeat per page."),
], size=9.5, gap=2)

# ================================================================ SLIDE 13 — Testing
s = add_slide(); header(s, "08 · TESTING", "Evidence, not adjectives"); footer(s, 13)
card(s, 0.55, 1.5, 6.0, 3.3)
txt(s, 0.8, 1.66, 5.5, 0.3, [dict(runs=[("TRACK A — AUTOMATED (pytest)", dict(size=10, bold=True, color=GOLD))])])
txt(s, 0.8, 2.05, 5.5, 0.6, [dict(runs=[("12 / 12 passing · isolated temp DB", dict(size=15, bold=True, color=GREEN))])])
bullets(s, 0.8, 2.72, 5.6, 1.6, [
    "Auth: login page · wrong password → 401 · anonymous → /login",
    "Register: happy path · duplicate roll no. → 400",
    "Routing: washroom-tap text → Sanitation · “shock” → High",
    "Flow: lodge → acknowledge → resolve → ★5 → Closed",
], size=8.6, gap=3, marker="•  ", mcolor=GOLD)
rect(s, 0.8, 4.6, 5.5, 0.42, fill=NAVY, round_=True, radius=0.5)
txt(s, 0.95, 4.71, 5.2, 0.24, [dict(runs=[("$ python -m pytest tests/ -q", dict(font=MONO, size=9.5, color=GOLD_L))])])

card(s, 6.8, 1.5, 6.0, 3.3)
txt(s, 7.05, 1.66, 5.5, 0.3, [dict(runs=[("TRACK B — MANUAL (LIVE, 09-11-2026)", dict(size=10, bold=True, color=GOLD))])])
txt(s, 7.05, 2.05, 5.5, 0.6, [dict(runs=[("8 / 8 scenarios PASS · TC-13 … TC-20", dict(size=15, bold=True, color=GREEN))])])
bullets(s, 7.05, 2.72, 5.6, 1.6, [
    "TC-13/14 login & admin KPI counts match seed",
    "TC-15 officer queue hides other departments",
    "TC-16 anonymous complaint: identity hidden from officer",
    "TC-17/18 routed Medium/72h · reopen within 7 days",
], size=8.6, gap=3, marker="•  ", mcolor=GOLD)
rect(s, 7.05, 4.6, 5.5, 0.42, fill=NAVY, round_=True, radius=0.5)
txt(s, 7.2, 4.71, 5.2, 0.24, [dict(runs=[("$ curl -i -X POST …/login  →  HTTP/1.1 401", dict(font=MONO, size=9.5, color=GOLD_L))])])

txt(s, 0.55, 5.06, 12.2, 0.3, [dict(runs=[("DEFECTS FOUND & FIXED DURING TESTING", dict(size=9.5, bold=True, color=GOLD))])])
bullets(s, 0.55, 5.4, 12.3, 0.95, [
    ("Three, all re-verified — ", "(1) seed NOT NULL crash on complaints.code — placeholder + UPDATE · (2) minute-overflow in seed times · (3) officer dashboard Row vs dict is_overdue KeyError."),
    ("Regression — ", "suite re-run green; manual TC-17 lodge → routed to Sanitation & Maintenance, Medium, SLA 72 h."),
], size=9.5, gap=3)

# ================================================================ SLIDE 14 — Timeline & deliverables
s = add_slide(); header(s, "09 · TIMELINE", "Five notified milestones — Review 3 is nine days away"); footer(s, 14)
pic_fit(s, f"{IMG}/fig-gantt.png", 0.55, 1.42, 12.23, 2.5)
milestones = [
    ("BUILD\n21 Sep → 08 Nov", "schema · engine · console · reports · tests (12/12)", "done"),
    ("REVIEW 1 ✓\n10-10-2026", "SRS + Ch-1 · 10 marks", "done"),
    ("REVIEW 2 ✓\n24-10-2026", "Ch-2 Proposed System + Ch-3 design · 15 marks", "done"),
    ("REVIEW 3 — NEXT UP\n21-11-2026", "working build + this demo + report · 15 marks", "today"),
    ("REVIEW 4\n05-12-2026", "1st PPT presentation · 10 marks", "next"),
    ("FINAL VIVA\n19-12-2026", "2nd PPT + hard-bound report · 50 marks", "next"),
]
mw = 1.93
gap = (12.23 - 6 * mw) / 5
for i, (r, d, st) in enumerate(milestones):
    x = 0.55 + i * (mw + gap)
    card(s, x, 4.08, mw, 1.78, fill=(NAVY if st == "today" else WHITE), line=GOLD)
    txt(s, x + 0.12, 4.2, mw - 0.24, 0.52, [dict(runs=[(r, dict(size=7.3, bold=True, color=(GOLD_L if st == "today" else GOLD)))], line_spacing=1.12)])
    txt(s, x + 0.12, 4.8, mw - 0.24, 1.0, [dict(runs=[(d, dict(size=6.4, color=(CREAM if st == "today" else INK)))], line_spacing=1.15)])
rect(s, 0.55, 6.05, 12.23, 0.42, fill=GREY_L, round_=True, radius=0.5)
txt(s, 0.82, 6.15, 12, 0.26, [dict(runs=[("Artefacts: report (30 pp, 4 appendices) · this deck · app + tests · README — schedule as notified 30-09-2026",
                                           dict(size=9, color=NAVY3))])])

# ================================================================ SLIDE 15 — Future work
s = add_slide(); header(s, "10 · FUTURE WORK", "From a tool to a managed service"); footer(s, 15)
phases = [
    ("v1.x — EXTEND THE DESK", "ships on the current monolith", [
        ("E-1", "E-mail + SMS on status change (SMTP/SMS gateway)", "2 wks"),
        ("E-2", "WhatsApp deep-link tracker — wa.me with prefilled code", "3 days"),
        ("E-3", "Photo evidence upload — MIME + size ≤ 2 MB guard", "1 wk"),
        ("E-4", "Admin category management UI — add/retire keywords", "1 wk"),
    ]),
    ("v1.3–1.5 — OPERATE IT", "infrastructure & visibility", [
        ("E-5", "MySQL 8 migration — schema ports 1:1", "3 days"),
        ("E-6", "Nightly SLA-breach cron — 50%/100% auto-escalate", "2 days"),
        ("E-7", "Charts dashboard — pendency, trend, SLA %", "2 wks"),
        ("E-8", "Public board in the admin corridor — live counts", "1 wk"),
    ]),
    ("v2.0 — RESEARCH", "beyond the brief, deliberately", [
        ("E-9", "Marathi / Hindi UI toggle — ~120 gettext keys", "2 wks"),
        ("E-10", "ERP bridge — roll-no ↔ ERP student master sync", "3 wks"),
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
        txt(s, x + 0.82, yy + 0.01, pw - 1.75, 0.75, [dict(runs=[(d, dict(size=8.0, color=INK))], line_spacing=1.08)])
        txt(s, x + pw - 0.85, yy + 0.01, 0.68, 0.3, [dict(runs=[(t, dict(size=7.5, bold=True, color=GOLD))], align=PP_ALIGN.RIGHT)])
        yy += 0.88 if len(items) > 2 else 0.78
rect(s, 0.55, 6.3, 12.23, 0.42, fill=GREY_L, round_=True, radius=0.5)
txt(s, 0.82, 6.41, 12, 0.24, [dict(runs=[("Every limitation in the report (L-1…L-9) maps to one of these — the upgrade path is written down, not improvised.",
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
    ("Boring works — ", "Flask + SQLite + seeded data: the college can maintain it."),
    ("Tests are the demo — ", "12/12 automated and 8/8 manual, run live in front of you."),
    ("Every complaint gets a trail — ", "lodge to close, one timeline, zero lost grievances."),
], size=11, gap=8, color=CREAM, mcolor=GOLD_L)
card(s, 8.35, 1.18, 4.15, 4.6, fill=NAVY3, line=GOLD, line_w=1.3, radius=0.07)
txt(s, 8.62, 1.38, 3.6, 0.3, [dict(runs=[("TRY IT YOURSELF", dict(size=9.5, bold=True, color=GOLD))])])
txt(s, 8.62, 1.78, 3.7, 0.32, [dict(runs=[("git clone https://github.com/", dict(font=MONO, size=9, color=GOLD_L))])])
txt(s, 8.62, 2.06, 3.7, 0.32, [dict(runs=[("Yashwant-git392/Yashwant-git392.git", dict(font=MONO, size=9, color=GOLD_L))])])
txt(s, 8.62, 2.4, 3.7, 0.32, [dict(runs=[("cd Yashwant-git392/shikayat-setu", dict(font=MONO, size=9, color=CREAM))])])
txt(s, 8.62, 2.68, 3.7, 0.32, [dict(runs=[("pip install -r requirements.txt", dict(font=MONO, size=9, color=CREAM))])])
txt(s, 8.62, 2.96, 3.7, 0.32, [dict(runs=[("python run.py", dict(font=MONO, size=9, color=CREAM))])])
rect(s, 8.62, 3.4, 3.6, 0.015, fill=GOLD)
txt(s, 8.62, 3.55, 3.7, 0.3, [dict(runs=[("http://127.0.0.1:5001", dict(font=MONO, size=10.5, bold=True, color=WHITE))])])
txt(s, 8.62, 3.9, 3.7, 0.3, [dict(runs=[("admin / admin123 · MCA2026001 / student123", dict(font=MONO, size=8.2, bold=True, color=GOLD_L))])])
txt(s, 8.62, 4.35, 3.7, 1.3,
    [dict(runs=[("Report — 27 pages, Ch. 1–10 + Appendices A–C", dict(size=9, color=CREAM))], space_after=3),
     dict(runs=[("Branch — arena/aafd53cc-yashwant-git392", dict(size=9, color=CREAM))], space_after=3),
     dict(runs=[("Yashwant Santosh Ahire · MCA-I (Sem-I) · 2026-27", dict(size=9, color=RGBColor(0x9F,0xAD,0xC8)))])])
txt(s, 0.85, 6.35, 12.0, 0.35,
    [dict(runs=[("Campus Shikayat Setu — because every grievance deserves a paper trail.", dict(size=11, italic=True, color=RGBColor(0xC9,0xD2,0xE4)))])])

prs.save(OUT)
print("Saved:", OUT, "| slides:", len(prs.slides._sldIdLst))

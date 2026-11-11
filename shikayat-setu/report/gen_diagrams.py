"""Generate all report diagrams for Campus Shikayat Setu (SPPU MCA mini project)."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

NAVY, NAVY2, GOLD, GOLD_L = "#16243d", "#2b4a73", "#c9a227", "#ffd95e"
CREAM, CARD, LT = "#f7f5ef", "#ffffff", "#e8edf7"
GREEN, RED, GREY = "#1e7a46", "#b3372e", "#6b7280"
OUT = "/home/user/Yashwant-git392/shikayat-setu/report/images"

def canvas(w=100, h=62):
    fig, ax = plt.subplots(figsize=(w / 8.4, h / 8.4), dpi=160)
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax

def box(ax, x, y, w, h, fc=CARD, ec=NAVY, lw=1.6, style="round,pad=0,rounding_size=1.2", z=3, alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec, lw=lw, zorder=z, mutation_scale=1, alpha=alpha))

def arrow(ax, x1, y1, x2, y2, color=NAVY2, lw=2.0, style="-|>", ls="-", z=4, ms=16):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=ms,
                                 color=color, lw=lw, linestyle=ls, zorder=z, shrinkA=0, shrinkB=0))

def entity(ax, x, y, w, h, name, attrs, header_h=4.0):
    box(ax, x, y, w, h, fc=CARD, ec=NAVY, lw=1.8)
    box(ax, x, y + h - header_h, w, header_h, fc=NAVY, ec=NAVY, lw=1.8, style="square,pad=0")
    ax.text(x + w / 2, y + h - header_h / 2, name, ha="center", va="center",
            color=GOLD_L, fontsize=7.8, fontweight="bold", family="DejaVu Sans Mono")
    for i, a in enumerate(attrs):
        ty = y + h - header_h - 2.1 - i * 1.95
        ax.text(x + 1.1, ty, a, fontsize=5.6, va="center", family="DejaVu Sans Mono", color="#202020")

def cls_box(ax, x, y, w, h, name, attrs, methods, header_h=3.2):
    box(ax, x, y, w, h, fc=CARD, ec=NAVY, lw=1.6)
    ax.add_patch(mpatches.Rectangle((x, y + h - header_h), w, header_h, fc=NAVY, ec=NAVY, zorder=4))
    ax.text(x + w / 2, y + h - header_h / 2, name, ha="center", va="center", zorder=6,
            color=GOLD_L, fontsize=7.2, fontweight="bold", family="DejaVu Sans Mono")
    sep1 = y + h - header_h - len(attrs) * 1.85 - 0.8
    ax.plot([x, x + w], [sep1, sep1], color=NAVY, lw=1.0, zorder=5)
    for i, a in enumerate(attrs):
        ax.text(x + 1.1, y + h - header_h - 1.4 - i * 1.85, a, fontsize=5.3, va="center",
                family="DejaVu Sans Mono", color="#202020")
    for i, m in enumerate(methods):
        ax.text(x + 1.1, sep1 - 1.3 - i * 1.85, m, fontsize=5.3, va="center",
                family="DejaVu Sans Mono", color=NAVY2)

def fig_architecture():
    fig, ax = canvas(100, 60)
    ax.text(50, 57, "Campus Shikayat Setu — Three-Tier Architecture", ha="center", fontsize=12.5, fontweight="bold", color=NAVY)
    tiers = [
        ("PRESENTATION TIER (Client)", "Web Browser — HTML5 · CSS3 · JavaScript\nResponsive screens · print-ready Ctrl+P registers\nclient-side sanity (length/roll formats)", 40, GOLD),
        ("APPLICATION TIER (Server)", "Python 3.11 + Flask 3.x — Jinja2 templates\nSession auth · Role-based access (student/officer/admin)\nkeyword router · SLA engine · audit event log", 24, NAVY2),
        ("DATA TIER (Storage)", "SQLite 3 — file shikayat_setu.db\nFK · CHECK · UNIQUE constraints · ACID\n(1:1 mappable to MySQL 8 for production)", 8, "#3d5a80"),
    ]
    for title, body, y, color in tiers:
        box(ax, 4, y, 92, 12.5, fc=LT if color != GOLD else "#fbf3d9", ec=color, lw=2.2)
        ax.text(8, y + 9.6, title, fontsize=8.6, fontweight="bold", color=color)
        ax.text(8, y + 2.0, body, fontsize=7.5, va="bottom", color="#222", linespacing=1.55)
    for yy in (40, 24):
        for x in (18, 50, 82):
            arrow(ax, x, yy, x, yy - 3.5, style="<|-|>", lw=2.4)
    ax.text(96.5, 38.3, "HTTP / HTML", fontsize=5.4, rotation=90, va="center", color=GREY)
    ax.text(96.5, 22.3, "SQL via sqlite3 driver", fontsize=5.4, rotation=90, va="center", color=GREY)
    fig.savefig(f"{OUT}/fig-architecture.png", bbox_inches="tight"); plt.close(fig)
    print("fig-architecture.png")

def fig_erd():
    fig, ax = canvas(100, 68)
    ax.text(50, 65, "ERD — Campus Shikayat Setu (six tables)", ha="center", fontsize=11.5, fontweight="bold", color=NAVY)
    entity(ax, 1.5, 38, 29, 21, "DEPARTMENTS", [
        "PK  id : INTEGER", "UK  name : VARCHAR(80)", "    head_name : VARCHAR(80)",
        "    email : VARCHAR(120)", "    location : VARCHAR(120)",
    ])
    entity(ax, 36, 38, 29, 21, "CATEGORIES", [
        "PK  id : INTEGER", "UK  name : VARCHAR(80)", "FK  department_id : INT",
        "    default_priority : VARCHAR(6)", "    keywords : TEXT",
    ])
    entity(ax, 70.5, 38, 28, 21, "USERS", [
        "PK  id : INTEGER", "UK  username : VARCHAR(40)",
        "UK  roll_no : VARCHAR(15) NULL", "FK  department_id : INT NULL",
        "    role : VARCHAR(8)", "    status : VARCHAR(8)",
    ])
    entity(ax, 12, 3, 40, 24, "COMPLAINTS", [
        "PK  id : INTEGER", "UK  code : VARCHAR(14)",
        "FK  student_id : INT", "FK  category_id : INT", "FK  department_id : INT",
        "    priority · status · routing", "    submitted_at · sla_due_at",
    ])
    entity(ax, 62, 15, 27, 19.5, "COMPLAINT_EVENTS", [
        "PK  id : INTEGER", "FK  complaint_id : INT", "    event_type : VARCHAR(12)",
        "FK  actor_id : INT NULL", "    created_at : DATETIME",
    ])
    entity(ax, 62, 1.5, 27, 12.5, "FEEDBACK", [
        "PK  id : INTEGER", "UK&FK complaint_id : INT", "    rating : INT (1–5)", "    comment : TEXT",
    ])
    arrow(ax, 30.5, 48.5, 36, 48.5, style="-", lw=2.0)
    ax.text(33.2, 50.1, "1", fontsize=8, fontweight="bold", color=NAVY); ax.text(35.5, 50.1, "0..*", fontsize=8, fontweight="bold", color=NAVY, ha="right")
    arrow(ax, 65, 48.5, 70.5, 48.5, style="-", lw=2.0)
    ax.text(67.5, 50.1, "1", fontsize=8, fontweight="bold", color=NAVY); ax.text(69.9, 50.1, "0..*", fontsize=8, fontweight="bold", color=NAVY, ha="right")
    arrow(ax, 28, 38, 26, 27, style="-", lw=2.0)
    arrow(ax, 46, 38, 36, 27, style="-", lw=2.0)
    arrow(ax, 82, 38, 46, 27, style="-", lw=2.0)
    arrow(ax, 52, 21, 62, 20.5, style="-", lw=2.0)
    arrow(ax, 52, 9, 62, 7, style="-", lw=2.0)
    fig.savefig(f"{OUT}/fig-erd.png", bbox_inches="tight"); plt.close(fig)
    print("fig-erd.png")

def fig_usecase():
    fig, ax = canvas(112, 64)
    ax.text(56, 61.5, "Use Case Diagram — Campus Shikayat Setu", ha="center", fontsize=12, fontweight="bold", color=NAVY)
    box(ax, 22, 2, 68, 51, fc="#fffdf4", ec=GOLD, lw=2.4, z=1)
    ax.text(56, 49.5, "«system boundary»  SHIKAYAT SETU", ha="center", fontsize=8, fontweight="bold", color="#8a6d1a", zorder=5)

    def actor(x, label, color):
        ax.add_patch(mpatches.Circle((x, 36), 1.7, fill=False, lw=2.2, ec=color, zorder=4))
        ax.plot([x, x], [34.3, 28.5], color=color, lw=2.2, zorder=4)
        ax.plot([x - 3.1, x + 3.1], [31.4, 31.4], color=color, lw=2.2, zorder=4)
        ax.plot([x, x - 2.5], [28.5, 23], color=color, lw=2.2, zorder=4)
        ax.plot([x, x + 2.5], [28.5, 23], color=color, lw=2.2, zorder=4)
        ax.text(x, 18.5, label, ha="center", fontsize=7.2, fontweight="bold", color=color, linespacing=1.3, zorder=5)

    actor(9, "Student\n(complainant)", NAVY)
    actor(103, "Officer\n(department)", NAVY2)
    actor(56, "Administrator", GOLD)   # placed inside boundary visually; move marker text below
    ax.texts[-1].set_position((56, 6))

    uc_left = [("UC-01  Register & Login", 43.5), ("UC-02  Lodge Complaint", 36.5),
               ("UC-03  Track (code / roll no.)", 29.5), ("UC-04  Confirm & Feedback ★", 22.5),
               ("UC-05  Reopen ≤ 7 days", 15.5)]
    uc_right = [("UC-06  Acknowledge", 43.5), ("UC-07  Mark In-Progress", 36.5),
                ("UC-08  Resolve + remark", 29.5), ("UC-09  View department queue", 22.5),
                ("UC-10  Add timeline remark", 15.5)]
    for label, y in uc_left:
        ax.add_patch(mpatches.Ellipse((38, y), 30, 5.0, fc=LT, ec=NAVY2, lw=1.6, zorder=3))
        ax.text(38, y, label, ha="center", va="center", fontsize=6.4, color=NAVY, zorder=5)
    for label, y in uc_right:
        ax.add_patch(mpatches.Ellipse((73, y), 30, 5.0, fc=LT, ec=NAVY2, lw=1.6, zorder=3))
        ax.text(73, y, label, ha="center", va="center", fontsize=6.4, color=NAVY, zorder=5)
    arrow(ax, 13, 23, 23.5, 36.5, lw=1.2, color=NAVY2); arrow(ax, 13, 24, 23.5, 29.5, lw=1.2, color=NAVY2)
    arrow(ax, 13, 30, 23.5, 43.5, lw=1.2, color=NAVY2); arrow(ax, 13, 26, 23.5, 22.5, lw=1.2, color=NAVY2); arrow(ax, 13, 25, 23.5, 15.5, lw=1.2, color=NAVY2)
    arrow(ax, 99, 23, 88.5, 43.5, lw=1.2, color=NAVY2); arrow(ax, 99, 25, 88.5, 36.5, lw=1.2, color=NAVY2)
    arrow(ax, 99, 27, 88.5, 29.5, lw=1.2, color=NAVY2); arrow(ax, 99, 29, 88.5, 22.5, lw=1.2, color=NAVY2); arrow(ax, 99, 31, 88.5, 15.5, lw=1.2, color=NAVY2)
    box(ax, 40, 5.0, 32, 4.4, fc="#fbf3d9", ec=GOLD, lw=1.6, z=3)
    ax.text(56, 7.2, "UC-11  Admin: reassign · escalate · force-close · reports", ha="center", va="center",
            fontsize=5.9, color="#6d5200", zorder=5)
    arrow(ax, 56, 23, 56, 9.6, lw=1.4, color=GOLD, style="-|>")
    fig.savefig(f"{OUT}/fig-usecase.png", bbox_inches="tight"); plt.close(fig)
    print("fig-usecase.png")

def fig_activity():
    fig, ax = canvas(120, 66)
    ax.text(60, 62.5, "Activity Diagram — Lodge → Route → Resolve → Close", ha="center", fontsize=11.5, fontweight="bold", color=NAVY)
    lanes = [("STUDENT", 44, 12.5), ("SYSTEM", 28.5, 12.5), ("OFFICER", 13.5, 12.5), ("ADMIN", 3.5, 7.5)]
    for name, y, h in lanes:
        ax.add_patch(mpatches.Rectangle((2, y), 116, h, fc=("#fbfaf5" if y in (44, 13.5) else "#f4f6fb"), ec=GREY, lw=0.8, zorder=1))
        ax.text(4, y + h - 2.2, f"«{name}»", fontsize=6.8, fontweight="bold", color=NAVY2, zorder=5)
    boxes = [
        # (lane_y, x, w, text)
        (44, 4, 44, "1 · Student lodges complaint\ntitle ≥ 8 chars · description ≥ 20 chars"),
        (28.5, 42, 46, "2 · Validate → keyword-score → route to department\n+ priority resolves + SLA deadline stamped"),
        (13.5, 62, 48, "3 · Officer works the queue\nacknowledge → in-progress → resolve (≥10-char remark)"),
        (44, 64, 48, "4 · Student confirms: ★1–5 → Closed\nor Reopen ≤ 7 days"),
    ]
    for lane_y, x, w, text in boxes:
        box(ax, x, lane_y + 2.0, w, 7.6, fc="white", ec=NAVY, lw=1.6, z=4)
        ax.text(x + w / 2, lane_y + 5.8, text, ha="center", va="center", fontsize=6.3, color=NAVY, zorder=6, linespacing=1.35)
    # arrows: 1 -> 2 -> 3 -> 4 ; 3 can bounce back for In-Progress/Reopen
    arrow(ax, 30, 46.0, 62, 38.6, lw=1.7, color=NAVY2)                      # 1 -> 2
    arrow(ax, 70, 28.5 + 2.0, 84, 13.5 + 9.6, lw=1.7, color=NAVY2)          # 2 -> 3
    arrow(ax, 86, 13.5 + 9.6, 92, 44 + 2.0, lw=1.7, color=NAVY2)            # 3 -> 4
    ax.text(94.5, 28.5, "status: Resolved", fontsize=5.6, color=GREY, zorder=6, rotation=90)
    # admin escalation lane (dashed)
    box(ax, 6, 4.0, 46, 5.2, fc="#fdf0d5", ec=GOLD, lw=1.6, z=4)
    ax.text(29, 6.6, "Admin may escalate to High priority at any point", ha="center", va="center", fontsize=6.0, color="#6d5200", zorder=6)
    arrow(ax, 100, 13.5 + 8.0, 48, 9.2, lw=1.3, ls="--", color=GOLD, style="-|>")
    fig.savefig(f"{OUT}/fig-activity.png", bbox_inches="tight"); plt.close(fig)
    print("fig-activity.png")

def fig_class():
    fig, ax = canvas(112, 62)
    ax.text(56, 60, "Class Diagram — design level", ha="center", fontsize=11.5, fontweight="bold", color=NAVY)
    cls_box(ax, 1, 30, 33, 22, "RouteEngine", [
        "+ SLA_HOURS : dict", "+ SAFETY_WORDS : tuple", "+ MASS_IMPACT : tuple",
    ], [
        "+ score_category(t, kw) : int", "+ route(t, cats) : (cat, score)",
        "+ assign_priority(d, t, d2) : str",
    ])
    cls_box(ax, 42, 30, 33, 22, "Complaint", [
        "- id : int", "- code : str", "- student_id : int  «FK»", "- department_id : int  «FK»",
        "- priority : str", "- status : str", "- routing_score : int", "- sla_due_at : str",
    ], [
        "+ lodged() : code", "+ acknowledge() : void", "+ resolve(remark) : void", "+ reopen(reason) : void",
    ])
    cls_box(ax, 78, 36, 32, 15, "ComplaintEvent", [
        "- id : int  «PK»", "- complaint_id : int  «FK»", "- event_type : str", "- actor_id : int", "- created_at : str",
    ], ["+ append() : void"])
    cls_box(ax, 78, 7, 32, 15, "Feedback", [
        "- id : int  «PK»", "- complaint_id : int  «FK,UK»", "- rating : int  (1–5)", "- comment : str",
    ], ["+ submit(rating) : void"])
    cls_box(ax, 42, 4, 33, 12, "User  «roles: student | officer | admin»", [
        "- id : int  «PK»", "- username : str  «UK»", "- roll_no : str  «UK»", "- department_id : int  «FK»",
    ], ["+ login(u, p) : bool", "+ role_allows(action) : bool"])
    arrow(ax, 34, 45, 42, 45, lw=1.6, color=NAVY2); ax.text(38, 46.5, "uses", fontsize=6, color=GREY)
    arrow(ax, 75, 44, 78, 44, lw=1.6, color=NAVY2); ax.text(76.5, 45.2, "1..*", fontsize=6, color=GREY)
    arrow(ax, 58.5, 30, 82, 22, lw=1.6, color=NAVY2); arrow(ax, 58.5, 30, 60, 16, lw=1.6, color=NAVY2)
    fig.savefig(f"{OUT}/fig-class.png", bbox_inches="tight"); plt.close(fig)
    print("fig-class.png")

def fig_deployment():
    fig, ax = canvas(100, 46)
    ax.text(50, 43.5, "Deployment View — single-node lab PC", ha="center", fontsize=12, fontweight="bold", color=NAVY)
    box(ax, 2, 6, 44, 26, fc=LT, ec=NAVY, lw=2.0)
    ax.text(24, 29.2, "LAB PC (library / demo)", ha="center", fontsize=8.5, fontweight="bold", color=NAVY)
    box(ax, 5.5, 17, 16, 8, fc="white", ec=NAVY2, lw=1.5)
    ax.text(13.5, 22.5, "Flask app", ha="center", fontsize=7, fontweight="bold", color=NAVY)
    ax.text(13.5, 18.8, "run.py :5001", ha="center", fontsize=6.2, color=GREY, family="DejaVu Sans Mono")
    box(ax, 26.5, 17, 16, 8, fc="white", ec=NAVY2, lw=1.5)
    ax.text(34.5, 22.5, "SQLite file", ha="center", fontsize=7, fontweight="bold", color=NAVY)
    ax.text(34.5, 18.8, "shikayat_setu.db", ha="center", fontsize=6.0, color=GREY, family="DejaVu Sans Mono")
    arrow(ax, 21.5, 21, 26.5, 21, lw=1.6, color=NAVY2)
    box(ax, 62, 14, 34, 14, fc="#fbf3d9", ec=GOLD, lw=2.0)
    ax.text(79, 24.6, "CLIENTS (same PC / LAN)", ha="center", fontsize=8, fontweight="bold", color="#6d5200")
    ax.text(79, 19.2, "Chrome · Firefox · Edge", ha="center", fontsize=7, color="#6d5200")
    ax.text(79, 15.6, "http://<lab-pc>:5001", ha="center", fontsize=7, color="#6d5200", family="DejaVu Sans Mono")
    arrow(ax, 62, 21, 46, 21, lw=1.6, color=NAVY2)
    ax.text(54, 22.5, "HTTP", fontsize=6, color=GREY)
    fig.savefig(f"{OUT}/fig-deployment.png", bbox_inches="tight"); plt.close(fig)
    print("fig-deployment.png")

def fig_modules():
    fig, ax = canvas(100, 58)
    ax.text(50, 55.5, "Module Hierarchy — role layers over the core", ha="center", fontsize=11.5, fontweight="bold", color=NAVY)
    box(ax, 30, 44, 40, 8, fc=NAVY, ec=NAVY, lw=2.0)
    ax.text(50, 50.2, "Campus Shikayat Setu", ha="center", fontsize=9, fontweight="bold", color=GOLD_L, zorder=6)
    ax.text(50, 46.3, "app.py · routing.py · database.py", ha="center", fontsize=6.2, color="#cdd6e8", zorder=6, family="DejaVu Sans Mono")
    cols = [
        ("STUDENT LAYER", [("Register & Login", 33), ("Lodge Complaint", 25.5), ("Track (code / roll)", 18), ("Feedback & Reopen", 10.5)], NAVY2),
        ("OFFICER LAYER", [("Department queue", 33), ("Acknowledge", 25.5), ("In-Progress / Resolve", 18), ("Timeline remarks", 10.5)], "#3d5a80"),
        ("ADMIN LAYER", [("Console + filters", 33), ("Reassign · Escalate", 25.5), ("Users & officers", 18), ("6 print registers", 10.5)], GOLD),
    ]
    for i, (title, mods, color) in enumerate(cols):
        x = 2 + i * 33.5
        ax.text(x + 15, 39.5, title, ha="center", fontsize=7.6, fontweight="bold", color=color)
        for label, y in mods:
            box(ax, x, y, 30, 5.6, fc=LT, ec=color, lw=1.6)
            ax.text(x + 15, y + 2.8, label, ha="center", va="center", fontsize=6.4, color=NAVY, zorder=6)
    for i in range(3):
        arrow(ax, 50, 44, 17 + i * 33.5, 38.7, lw=1.5, color=GOLD)
    ax.text(50, 2.2, "Routing / SLA / Audit are shared services used by all three layers", ha="center",
            fontsize=6.2, color=GREY, style="italic")
    fig.savefig(f"{OUT}/fig-modules.png", bbox_inches="tight"); plt.close(fig)
    print("fig-modules.png")

def fig_gantt():
    import matplotlib.patches as mpatches
    weeks = ["Wk 1\n21–27 Sep", "Wk 2\n28 Sep–04 Oct", "Wk 3\n05–11 Oct", "Wk 4\n12–18 Oct",
             "Wk 5\n19–25 Oct", "Wk 6\n26 Oct–01 Nov", "Wk 7\n02–08 Nov", "Dec\n19 Dec"]
    tasks = [
        ("Requirement study & reference audit", 0, 1, GOLD),
        ("Schema + seed + design docs", 1, 1, NAVY2),
        ("Routing / SLA engine", 2, 1, NAVY2),
        ("Core flows (lodge→resolve→close)", 2, 2, NAVY),
        ("Admin console + reports", 3, 2, NAVY),
        ("Testing (12 pytest + 8 manual)", 4, 2, GREEN),
        ("Report & deck (this document)", 5, 2, "#8a6d1a"),
        ("Review 3 — 21 Nov 2026", 6.6, 0.18, RED),
        ("Final Viva — 19 Dec 2026", 7.0, 0.18, RED),
    ]
    fig, ax = plt.subplots(figsize=(13.5, 5.4), dpi=160)
    for i, (name, start, dur, color) in enumerate(tasks):
        ax.barh(len(tasks) - 1 - i, dur, left=start, height=0.62, color=color, zorder=3)
        ax.text(start + dur + 0.07, len(tasks) - 1 - i, name, va="center", fontsize=7.2, color="#222")
    ax.set_yticks([]); ax.set_xticks(range(8)); ax.set_xticklabels(weeks, fontsize=7)
    ax.set_xlim(-0.2, 8.6); ax.grid(axis="x", ls=":", lw=0.6, color="#c9c7bd", zorder=0)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.set_title("Project Timeline — 21 Sep 2026 → 19 Dec 2026", fontsize=11, fontweight="bold", color=NAVY, pad=10)
    fig.savefig(f"{OUT}/fig-gantt.png", bbox_inches="tight"); plt.close(fig)
    print("fig-gantt.png")

if __name__ == "__main__":
    fig_architecture(); fig_erd(); fig_usecase(); fig_activity(); fig_class()
    fig_deployment(); fig_modules(); fig_gantt()

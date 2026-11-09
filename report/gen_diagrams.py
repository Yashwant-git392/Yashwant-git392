"""Generate all report diagrams for SmartLibrary (SPPU MCA mini project)."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

NAVY   = "#16243d"
NAVY2  = "#2b4a73"
GOLD   = "#c9a227"
GOLD_L = "#ffd95e"
CREAM  = "#f7f5ef"
CARD   = "#ffffff"
LT     = "#e8edf7"
GREEN  = "#1e7a46"
RED    = "#b3372e"
GREY   = "#6b7280"

OUT = "/home/user/Yashwant-git392/report/images"

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

def entity(ax, x, y, w, h, name, attrs, header_h=4.2):
    box(ax, x, y, w, h, fc=CARD, ec=NAVY, lw=1.8)
    box(ax, x, y + h - header_h, w, header_h, fc=NAVY, ec=NAVY, lw=1.8, style="square,pad=0")
    ax.text(x + w / 2, y + h - header_h / 2, name, ha="center", va="center",
            color=GOLD_L, fontsize=8.2, fontweight="bold", family="DejaVu Sans Mono")
    for i, a in enumerate(attrs):
        ty = y + h - header_h - 2.2 - i * 2.05
        ax.text(x + 1.2, ty, a, fontsize=5.9, va="center", family="DejaVu Sans Mono", color="#202020")

def cls_box(ax, x, y, w, h, name, attrs, methods, header_h=3.4):
    box(ax, x, y, w, h, fc=CARD, ec=NAVY, lw=1.6)
    ax.add_patch(mpatches.Rectangle((x, y + h - header_h), w, header_h, fc=NAVY, ec=NAVY, zorder=4))
    ax.text(x + w / 2, y + h - header_h / 2, name, ha="center", va="center", zorder=6,
            color=GOLD_L, fontsize=7.6, fontweight="bold", family="DejaVu Sans Mono")
    sep1 = y + h - header_h - len(attrs) * 1.95 - 0.9
    ax.plot([x, x + w], [sep1, sep1], color=NAVY, lw=1.0, zorder=5)
    for i, a in enumerate(attrs):
        ax.text(x + 1.1, y + h - header_h - 1.5 - i * 1.95, a, fontsize=5.6, va="center",
                family="DejaVu Sans Mono", color="#202020")
    for i, m in enumerate(methods):
        ax.text(x + 1.1, sep1 - 1.4 - i * 1.95, m, fontsize=5.6, va="center",
                family="DejaVu Sans Mono", color=NAVY2)

# ---------------------------------------------------------------- 1. ARCHITECTURE
def fig_architecture():
    fig, ax = canvas(100, 60)
    ax.text(50, 57, "SmartLibrary — Three-Tier Architecture", ha="center", fontsize=13, fontweight="bold", color=NAVY)
    tiers = [
        ("PRESENTATION TIER (Client)", "Web Browser — HTML5 · CSS3 · JavaScript\nResponsive screens, client-side validation,\nflash messages, print-friendly reports", 40, GOLD),
        ("APPLICATION TIER (Server)", "Python 3.11 + Flask 3.x — Jinja2 templates\nSession auth · RBAC (Admin) · business rules\nissue/return logic, fine calculation @ ₹2/day", 24, NAVY2),
        ("DATA TIER (Storage)", "SQLite 3 — file smartlibrary.db\nFK constraints · CHECK constraints · UNIQUE keys\n(mappable 1:1 to MySQL 8 in production)", 8, "#3d5a80"),
    ]
    for title, body, y, color in tiers:
        box(ax, 4, y, 92, 12.5, fc=LT if color != GOLD else "#fbf3d9", ec=color, lw=2.2)
        ax.text(8, y + 9.6, title, fontsize=8.6, fontweight="bold", color=color)
        ax.text(8, y + 2.0, body, fontsize=7.6, va="bottom", color="#222", linespacing=1.55)
    arrow(ax, 18, 40, 18, 36.5, style="<|-|>", lw=2.4)
    arrow(ax, 50, 40, 50, 36.5, style="<|-|>", lw=2.4)
    arrow(ax, 82, 40, 82, 36.5, style="<|-|>", lw=2.4)
    arrow(ax, 18, 24, 18, 20.5, style="<|-|>", lw=2.4)
    arrow(ax, 50, 24, 50, 20.5, style="<|-|>", lw=2.4)
    arrow(ax, 82, 24, 82, 20.5, style="<|-|>", lw=2.4)
    ax.text(96.5, 38.3, "HTTP / HTML", fontsize=5.4, rotation=90, va="center", color=GREY)
    ax.text(96.5, 22.3, "SQL via sqlite3 driver", fontsize=5.4, rotation=90, va="center", color=GREY)
    fig.savefig(f"{OUT}/fig-architecture.png", bbox_inches="tight"); plt.close(fig)
    print("fig-architecture.png")

# ---------------------------------------------------------------- 2. ERD
def fig_erd():
    fig, ax = canvas(100, 70)
    ax.text(50, 67, "Entity Relationship Diagram (ERD) — 1 to many relationships", ha="center",
            fontsize=11.5, fontweight="bold", color=NAVY)
    entity(ax, 2, 32, 27, 29, "BOOK", [
        "PK  book_id : INTEGER", "UK  isbn : VARCHAR(20)", "    title : VARCHAR(200)",
        "    author : VARCHAR(120)", "    publisher : VARCHAR(120)", "    category : VARCHAR(60)",
        "    edition : VARCHAR(40)", "    quantity : INTEGER", "    available_qty : INTEGER",
        "    shelf_location : VARCHAR(10)", "    added_on : DATE",
    ])
    entity(ax, 37, 32, 27, 29, "ISSUE_TRANSACTION", [
        "PK  issue_id : INTEGER", "FK  book_id : INTEGER", "FK  member_id : INTEGER",
        "    issue_date : DATE", "    due_date : DATE", "    return_date : DATE(NULL)",
        "    status : VARCHAR(10)", "        (Issued / Returned)", "    fine_amount : REAL",
    ])
    entity(ax, 72, 32, 27, 29, "MEMBER", [
        "PK  member_id : INTEGER", "UK  roll_no : VARCHAR(15)", "    name : VARCHAR(120)",
        "UK  email : VARCHAR(120)", "    phone : CHAR(10)", "    department : VARCHAR(30)",
        "    semester : VARCHAR(10)", "    membership_type : VARCHAR(10)", "        (Student / Faculty)",
        "    status : VARCHAR(10)", "    joined_on : DATE",
    ])
    entity(ax, 2, 2, 27, 15, "ADMIN", [
        "PK  admin_id : INTEGER", "UK  username : VARCHAR(40)",
        "    password_hash : VARCHAR(64)", "    full_name : VARCHAR(120)",
    ])
    # relationships (crow's foot style: 1 to many)
    arrow(ax, 29, 46.5, 37, 46.5, style="-", lw=2.2)
    ax.text(29.6, 48, "1", fontsize=8.5, fontweight="bold", color=NAVY)
    ax.text(36.4, 48, "0..*", fontsize=8.5, fontweight="bold", color=NAVY, ha="right")
    arrow(ax, 64, 46.5, 72, 46.5, style="-", lw=2.2)
    ax.text(64.6, 48, "0..*", fontsize=8.5, fontweight="bold", color=NAVY)
    ax.text(71.4, 48, "1", fontsize=8.5, fontweight="bold", color=NAVY, ha="right")
    ax.text(29.2, 42.3, "is issued in", fontsize=6.2, color=GREY)
    ax.text(65.2, 42.3, "borrows", fontsize=6.2, color=GREY)
    # admin manages (dashed) — to BOOK and ISSUE_TRANSACTION only
    arrow(ax, 15.5, 17, 15.5, 32, ls="--", lw=1.4, color=GREY)
    arrow(ax, 29, 11, 47, 32, ls="--", lw=1.4, color=GREY)
    ax.text(17.3, 24, "manages", fontsize=6.0, color=GREY)
    ax.text(43.5, 16.6, "manages", fontsize=6.0, color=GREY, rotation=32)
    ax.text(50, 0.5, "Member (1) —— ISSUE_TRANSACTION (0..*) —— BOOK (1)  |  ON DELETE CASCADE  |  fine_amount is derived from due_date",
            ha="center", fontsize=6.4, color=GREY, style="italic")
    fig.savefig(f"{OUT}/fig-erd.png", bbox_inches="tight"); plt.close(fig)
    print("fig-erd.png")

# ---------------------------------------------------------------- 3. USE CASE
def fig_usecase():
    fig, ax = canvas(110, 66)
    ax.text(55, 63, "Use Case Diagram — SmartLibrary", ha="center", fontsize=12, fontweight="bold", color=NAVY)
    box(ax, 17, 2, 76, 54, fc="#fffdf4", ec=GOLD, lw=2.4, z=1)
    ax.text(55, 52.0, "«system boundary»  SMARTLIBRARY", ha="center", fontsize=8.5,
            fontweight="bold", color="#8a6d1a", zorder=5)

    def actor(x, label, color):
        ax.add_patch(mpatches.Circle((x, 34.5), 1.7, fill=False, lw=2.2, ec=color, zorder=4))
        ax.plot([x, x], [32.8, 27], color=color, lw=2.2, zorder=4)
        ax.plot([x - 3.2, x + 3.2], [30.3, 30.3], color=color, lw=2.2, zorder=4)
        ax.plot([x, x - 2.6], [27, 21.5], color=color, lw=2.2, zorder=4)
        ax.plot([x, x + 2.6], [27, 21.5], color=color, lw=2.2, zorder=4)
        ax.text(x, 17.0, label, ha="center", fontsize=7.6, fontweight="bold",
                color=color, linespacing=1.35, zorder=5)

    actor(9, "Librarian\n(Admin)", NAVY)
    actor(100.5, "Member\n(Student /\nFaculty)", NAVY2)

    uc = [
        ("UC-01  Login / Logout", 46.0),
        ("UC-02  Manage Book Catalog\n(Add · Edit · Delete · Search)", 39.2),
        ("UC-03  Manage Membership\n(Register · Update · Deactivate)", 32.4),
        ("UC-04  Issue Book", 25.6),
        ("UC-05  Return Book", 18.8),
        ("UC-06  View Transactions & Fine Ledger", 12.2),
        ("UC-07  Generate Reports (5 Registers)", 6.2),
    ]
    for label, y in uc:
        multi = "\n" in label
        ax.add_patch(mpatches.Ellipse((45, y), 45, 5.8 if multi else 4.6,
                                      fc=LT, ec=NAVY2, lw=1.7, zorder=3))
        ax.text(45, y, label, ha="center", va="center", fontsize=6.8, color=NAVY,
                linespacing=1.4, zorder=5)
    ax.add_patch(mpatches.Ellipse((82.0, 15.2), 19, 5.4, fc="#fdf0d5", ec=GOLD, lw=1.9, zorder=3))
    ax.text(82.0, 15.2, "UC-08  Auto Fine\nCalculation (₹2/day)", ha="center", va="center",
            fontsize=6.2, color="#6d5200", linespacing=1.4, zorder=5)

    for _, y in uc:
        arrow(ax, 13.6, 27, 22.8, y, lw=1.25, color=NAVY2, z=4)
    arrow(ax, 96, 23.5, 61.5, 25.6, lw=1.25, color=NAVY2, z=4)   # member -> issue
    arrow(ax, 96, 22.5, 61.5, 18.8, lw=1.25, color=NAVY2, z=4)   # member -> return
    arrow(ax, 63, 18.8, 73.5, 15.6, ls="--", lw=1.5, color=GOLD, style="-|>", z=4)
    ax.text(64.6, 19.9, "«include»", fontsize=6.0, color="#6d5200", zorder=5)
    fig.savefig(f"{OUT}/fig-usecase.png", bbox_inches="tight"); plt.close(fig)
    print("fig-usecase.png")

# ---------------------------------------------------------------- 4. CLASS DIAGRAM
def fig_class():
    fig, ax = canvas(112, 76)
    ax.text(56, 73, "Class Diagram — SmartLibrary (design level)", ha="center",
            fontsize=12, fontweight="bold", color=NAVY)
    cls_box(ax, 1, 47, 33, 20, "Admin", [
        "- admin_id : int", "- username : str", "- password_hash : str", "- full_name : str",
    ], [
        "+ login(u, p) : bool", "+ logout() : void", "+ changePassword(o, n) : bool",
    ])
    cls_box(ax, 1, 6, 33, 27, "Book", [
        "- book_id : int", "- isbn : str", "- title : str", "- author : str",
        "- category : str", "- quantity : int", "- available_qty : int",
    ], [
        "+ add() : bool", "+ update() : bool", "+ delete() : bool", "+ isAvailable() : bool",
    ])
    cls_box(ax, 43, 45, 33, 26, "Member", [
        "- member_id : int", "- roll_no : str", "- name : str", "- email : str",
        "- phone : str", "- membership_type : str", "- status : str",
    ], [
        "+ register() : bool", "+ update() : bool", "+ canBorrow() : bool",
    ])
    cls_box(ax, 43, 4, 33, 30, "IssueTransaction", [
        "- issue_id : int", "- book_id : int  «FK»", "- member_id : int  «FK»",
        "- issue_date : date", "- due_date : date", "- return_date : date",
        "- status : str", "- fine_amount : real",
    ], [
        "+ issue(b, m) : IssueTransaction", "+ processReturn() : void",
        "+ calculateFine() : real",
    ])
    cls_box(ax, 84, 26, 27, 22, "LibraryService", [
        "«facade / controller»",
    ], [
        "+ issueBook(m, b)", "+ returnBook(id)", "+ dashboardStats()",
        "+ generateReport(name)", "+ searchCatalog(q)",
    ])
    # relationships
    arrow(ax, 34, 24, 43, 22, lw=1.7, style="-", z=2)     # Book -> IssueTransaction
    arrow(ax, 59.5, 45, 59.5, 34, lw=1.7, style="-", z=2) # Member -> IssueTransaction
    ax.text(36.0, 26.0, "1 \u2190 0..*", fontsize=6.6, color=NAVY, zorder=5)
    ax.text(60.8, 39.0, "1 \u2190 0..*", fontsize=6.6, color=NAVY, zorder=5)
    arrow(ax, 84, 42, 76, 55, ls="--", lw=1.3, color=GREY, z=2)  # uses Member
    arrow(ax, 84, 35, 76, 22, ls="--", lw=1.3, color=GREY, z=2)  # uses IssueTransaction
    arrow(ax, 84, 29, 34, 30, ls="--", lw=1.3, color=GREY, z=2)  # uses Book
    ax.text(76.5, 50.5, "«uses»", fontsize=5.8, color=GREY, zorder=5)
    fig.savefig(f"{OUT}/fig-class.png", bbox_inches="tight"); plt.close(fig)
    print("fig-class.png")



# ---------------------------------------------------------------- 5. ACTIVITY DIAGRAM
def fig_activity():
    fig, ax = canvas(112, 88)
    ax.text(56, 84.5, "Activity Diagram — Book Issue & Return Process", ha="center",
            fontsize=11.5, fontweight="bold", color=NAVY)
    box(ax, 2, 3, 34, 76, fc="#fbfaf5", ec=GOLD, lw=2.0, z=1)
    box(ax, 38, 3, 72, 76, fc="#f4f7fc", ec=NAVY2, lw=2.0, z=1)
    ax.text(19, 76.5, "LANE 1 — Librarian", ha="center", fontsize=8.5, fontweight="bold", color="#8a6d1a")
    ax.text(74, 76.5, "LANE 2 — System (SmartLibrary)", ha="center", fontsize=8.5, fontweight="bold", color=NAVY2)

    def activity(x, y, w, h, text, fill=CARD, ec=NAVY2, fs=6.8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=2.2",
                                    fc=fill, ec=ec, lw=1.5, zorder=3))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=NAVY, zorder=4, linespacing=1.3)

    def decision(cx, cy, w, h, text):
        ax.add_patch(plt.Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                                 closed=True, fc="#fff3cd", ec="#b58900", lw=1.6, zorder=3))
        ax.text(cx, cy, text, ha="center", va="center", fontsize=6.3, color="#5c4400", zorder=4, linespacing=1.25)

    ax.add_patch(mpatches.Circle((19, 69), 1.9, fc=NAVY, zorder=4))
    activity(5, 56, 28, 7.5, "Scan / enter Book ID &\nMember Roll No", fs=6.8)
    activity(5, 44.5, 28, 7.0, "Click «Issue Book» or\n«Accept Return»", fs=6.8)
    decision(19, 31.5, 26, 9, "Which\naction?")
    activity(5, 12, 28, 9.5, "Collect fine (if any) &\nstamp the due-date slip;\nhand book to member", fs=6.5)
    ax.add_patch(mpatches.Circle((19, 5.5), 1.7, fc="white", ec=NAVY, lw=2.0, zorder=4))
    ax.add_patch(mpatches.Circle((19, 5.5), 0.85, fc=NAVY, zorder=5))

    activity(43, 56, 30, 7.0, "Validate: member Active,\n<= 3 books, no duplicate", fs=6.6)
    decision(58, 46.5, 26, 9, "Valid?")
    activity(43, 33, 30, 7.0, "Check available_qty > 0", fs=6.8)
    activity(43, 22.5, 30, 6.0, "Create ISSUE_TRANSACTION\n& decrement stock", fs=6.4)
    activity(43, 13.5, 30, 5.0, "Flash: «Issued. Due DATE»", fill="#e9f8ee", ec=GREEN, fs=6.6)
    activity(76.5, 44.5, 30, 8.0, "Show error flash &\nabort transaction", fill="#fdeceb", ec=RED, fs=6.6)
    activity(76.5, 30, 30, 9.5, "Compute late_days =\ntoday - due_date;\nfine = late_days x Rs2", fs=6.5)
    activity(76.5, 17, 30, 7.5, "Update ISSUE_TRANSACTION\n& increment stock", fs=6.6)
    activity(76.5, 7, 30, 6.0, "Flash: «Returned. Fine RsX»", fill="#e9f8ee", ec=GREEN, fs=6.6)

    arrow(ax, 19, 67.1, 19, 63.5)
    arrow(ax, 19, 56, 19, 51.5)
    arrow(ax, 19, 44.5, 19, 36)
    arrow(ax, 25.5, 35.3, 43, 59.5, lw=1.6)
    ax.text(33.0, 50.5, "issue", fontsize=6.0, color=GREY, rotation=40)
    arrow(ax, 32, 31.0, 76.3, 31.0, lw=1.6)
    ax.text(47, 28.7, "return", fontsize=6.0, color=GREY)
    arrow(ax, 58, 56, 58, 51.0)
    arrow(ax, 58, 42, 58, 40.0)
    ax.text(52.5, 43.6, "yes", fontsize=6.0, color=GREEN)
    arrow(ax, 71, 46.5, 76.5, 48.5, lw=1.6, color=RED)
    ax.text(73.2, 49.5, "no", fontsize=6.0, color=RED)
    arrow(ax, 58, 33, 58, 28.5)
    arrow(ax, 58, 22.5, 58, 18.5)
    arrow(ax, 73.5, 26.5, 76.5, 26.5, lw=1.6)
    arrow(ax, 91.5, 44.5, 91.5, 39.5)
    arrow(ax, 91.5, 30, 91.5, 24.5)
    arrow(ax, 91.5, 17, 91.5, 13.0)
    arrow(ax, 43, 15.5, 33.4, 19.5, lw=1.6, color=GREEN)
    arrow(ax, 76.5, 10.0, 33.6, 13.5, lw=1.6, color=GREEN)
    arrow(ax, 19, 12, 19, 7.2)
    fig.savefig(f"{OUT}/fig-activity.png", bbox_inches="tight"); plt.close(fig)
    print("fig-activity.png")


# ---------------------------------------------------------------- 6. DEPLOYMENT DIAGRAM
def fig_deployment():
    fig, ax = canvas(112, 58)
    ax.text(56, 54, "Deployment Diagram — SmartLibrary", ha="center", fontsize=11.5, fontweight="bold", color=NAVY)
    box(ax, 2, 12, 30, 34, fc="#fffdf4", ec=GOLD, lw=2.2)
    ax.text(17, 42, "«device»  Client", ha="center", fontsize=8.2, fontweight="bold", color="#8a6d1a")
    box(ax, 6, 26, 22, 12, fc=CARD, ec="#8a6d1a", lw=1.4)
    ax.text(17, 36.0, "artifact", ha="center", fontsize=5.6, color=GREY)
    ax.text(17, 31.8, "Web Browser\n(Chrome / Firefox / Edge)", ha="center", va="center", fontsize=6.6, color=NAVY, linespacing=1.35)
    box(ax, 6, 14.5, 22, 8, fc=CARD, ec="#8a6d1a", lw=1.4)
    ax.text(17, 20.6, "HTML, CSS, JavaScript\nclient-side validation", ha="center", va="center", fontsize=6.2, color=NAVY, linespacing=1.4)

    box(ax, 41, 8, 30, 40, fc="#eef2fb", ec=NAVY2, lw=2.2)
    ax.text(56, 44.5, "«device»  Application Server", ha="center", fontsize=8.2, fontweight="bold", color=NAVY2)
    box(ax, 45, 30, 22, 11, fc=CARD, ec=NAVY2, lw=1.4)
    ax.text(56, 39.0, "artifact", ha="center", fontsize=5.6, color=GREY)
    ax.text(56, 34.3, "Python 3.11 + Flask 3.x\nJinja2 templates, sessions", ha="center", va="center", fontsize=6.4, color=NAVY, linespacing=1.35)
    box(ax, 45, 16, 22, 11, fc=CARD, ec=NAVY2, lw=1.4)
    ax.text(56, 25.0, "artifact", ha="center", fontsize=5.6, color=GREY)
    ax.text(56, 20.3, "app.py, database.py\nschema.sql, static/, templates/", ha="center", va="center", fontsize=6.2, color=NAVY, linespacing=1.4)

    box(ax, 80, 12, 30, 34, fc="#f0faf3", ec=GREEN, lw=2.2)
    ax.text(95, 42, "«device»  Data Tier", ha="center", fontsize=8.2, fontweight="bold", color=GREEN)
    box(ax, 84, 26, 22, 12, fc=CARD, ec=GREEN, lw=1.4)
    ax.text(95, 36.0, "artifact", ha="center", fontsize=5.6, color=GREY)
    ax.text(95, 31.3, "SQLite 3\nsmartlibrary.db", ha="center", va="center", fontsize=6.6, color=NAVY, linespacing=1.4)
    box(ax, 84, 14.5, 22, 8, fc=CARD, ec=GREEN, lw=1.4)
    ax.text(95, 20.3, "tables: admin, book,\nmember, issue_transaction", ha="center", va="center", fontsize=6.1, color=NAVY, linespacing=1.4)

    arrow(ax, 32, 33, 41, 33, lw=2.0)
    arrow(ax, 41, 28, 32, 28, lw=2.0)
    ax.text(36.5, 35.2, "HTTP request", ha="center", fontsize=6.0, color=NAVY)
    ax.text(36.5, 24.2, "HTML response", ha="center", fontsize=6.0, color=NAVY)
    arrow(ax, 71, 26.5, 80, 26.5, lw=2.0)
    arrow(ax, 80, 21.5, 71, 21.5, lw=2.0)
    ax.text(75.5, 28.7, "SQL (file I/O)", ha="center", fontsize=6.0, color=NAVY)
    ax.text(75.5, 16.7, "rows / OK", ha="center", fontsize=6.0, color=NAVY)
    ax.text(56, 3, "Single-machine lab deployment (localhost:5000)  |  scale-out path: WSGI (gunicorn) + Nginx + MySQL 8",
            ha="center", fontsize=6.2, color=GREY, style="italic")
    fig.savefig(f"{OUT}/fig-deployment.png", bbox_inches="tight"); plt.close(fig)
    print("fig-deployment.png")


# ---------------------------------------------------------------- 7. MODULE HIERARCHY
def fig_modules():
    fig, ax = canvas(118, 72)
    ax.text(59, 68.5, "Module Hierarchy Diagram — SmartLibrary", ha="center", fontsize=11.5, fontweight="bold", color=NAVY)
    box(ax, 44, 56, 30, 7.5, fc=NAVY, ec=NAVY, lw=1.8)
    ax.text(59, 59.75, "SmartLibrary\n(root package)", ha="center", va="center", fontsize=8.0, fontweight="bold", color=GOLD_L, linespacing=1.3)
    mods = [
        ("Authentication\n& Security", ["Login", "Logout", "Change password"]),
        ("Dashboard\n& Analytics", ["Live stats", "Low-stock alert", "Recent activity"]),
        ("Book Catalog\nManagement", ["Add / edit book", "Delete book", "Search & filter"]),
        ("Member\nManagement", ["Register member", "Update / delete", "Status control"]),
        ("Circulation\n(Issue / Return)", ["Issue book", "Accept return", "Borrow-limit rule"]),
        ("Fine\nManagement", ["Rs2/day engine", "Fine ledger", "Pending fines"]),
        ("Reports\n& Registers", ["Issued / overdue", "Fine collection", "Stock & member"]),
    ]
    n = len(mods); w = 15.2; gap = (118 - n * w) / (n + 1)
    for i, (title, leaves) in enumerate(mods):
        x = gap + i * (w + gap)
        arrow(ax, 59, 56, x + w / 2, 45.5, lw=1.5, color=NAVY2, z=2)
        box(ax, x, 36, w, 9.5, fc=NAVY2, ec=NAVY2)
        ax.text(x + w / 2, 40.75, title, ha="center", va="center", fontsize=6.6, fontweight="bold", color="white", linespacing=1.3)
        for j, leaf in enumerate(leaves):
            ly = 27 - j * 7.5
            arrow(ax, x + w / 2, 36, x + w / 2, ly + 5.2, lw=1.1, color=GREY, z=2)
            box(ax, x, ly, w, 5.0, fc=LT, ec=NAVY2, lw=1.1)
            ax.text(x + w / 2, ly + 2.5, leaf, ha="center", va="center", fontsize=5.7, color=NAVY, linespacing=1.25)
    fig.savefig(f"{OUT}/fig-modules.png", bbox_inches="tight"); plt.close(fig)
    print("fig-modules.png")


# ---------------------------------------------------------------- 8. GANTT
def fig_gantt():
    import matplotlib.dates as mdates
    from datetime import date
    fig, ax = plt.subplots(figsize=(12.5, 5.4), dpi=160)
    tasks = [
        ("Review 1 — Synopsis / SRS (Ch-1)", date(2026, 9, 20), date(2026, 10, 10), GOLD),
        ("Review 2 — Proposed System + Design (Ch-2, 3)", date(2026, 10, 1), date(2026, 10, 24), GOLD),
        ("Implementation — Coding + DB seeding (Ch-4)", date(2026, 10, 25), date(2026, 11, 15), NAVY2),
        ("Review 3 — Testing + User Manual (Ch-5 to 10)", date(2026, 11, 1), date(2026, 11, 21), RED),
        ("Review 4 — 1st PPT Presentation", date(2026, 11, 22), date(2026, 12, 5), NAVY2),
        ("Final — Viva + Hard-bound Submission (50 marks)", date(2026, 12, 6), date(2026, 12, 19), GREEN),
    ]
    for i, (label, start, end, color) in enumerate(tasks):
        ax.barh(len(tasks) - 1 - i, (end - start).days, left=mdates.date2num(start),
                height=0.62, color=color, edgecolor="white")
        ax.text(mdates.date2num(start) + 1, len(tasks) - 1 - i,
                f"  {start.strftime('%d %b')} > {end.strftime('%d %b')}", va="center", fontsize=7.6, color="#202020")
    for i, (label, *_ ) in enumerate(tasks):
        ax.text(mdates.date2num(date(2026, 9, 14)), len(tasks) - 1 - i, label, va="center", ha="right", fontsize=8.2, color=NAVY)
    reviews = [date(2026, 10, 10), date(2026, 10, 24), date(2026, 11, 21), date(2026, 12, 5), date(2026, 12, 19)]
    names = ["R1", "R2", "R3", "R4", "Final"]
    for r, n in zip(reviews, names):
        ax.axvline(mdates.date2num(r), color=RED, lw=1.2, ls="--", alpha=0.75)
        ax.text(mdates.date2num(r), len(tasks) - 0.28, n, ha="center", fontsize=7.5, fontweight="bold", color=RED)
    ax.set_ylim(-0.6, len(tasks) + 0.4)
    ax.axis("off")
    ax.set_title("Project Schedule 2026-27 — MCA-I (Sem-I) Mini Project", fontsize=11, fontweight="bold", color=NAVY, pad=14)
    fig.savefig(f"{OUT}/fig-gantt.png", bbox_inches="tight", facecolor="white"); plt.close(fig)
    print("fig-gantt.png")


if __name__ == "__main__":
    fig_architecture(); fig_erd(); fig_usecase(); fig_class(); fig_activity(); fig_deployment(); fig_modules(); fig_gantt()

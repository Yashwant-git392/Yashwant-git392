"""Stylized renderings of the SmartLibrary UI (representative of the running app)."""
import sqlite3
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle

NAVY   = "#16243d"; NAVY2 = "#1f3455"; NAVY3 = "#2b4a73"
GOLD   = "#c9a227"; GOLD_L = "#ffd95e"
CREAM  = "#f7f5ef"; CARD = "#ffffff"; LT = "#e8edf7"
GREEN  = "#1e7a46"; RED = "#b3372e"; AMBER = "#a05a00"; GREY = "#6b7280"

OUT = "/home/user/Yashwant-git392/report/images"
DB = "/home/user/Yashwant-git392/mini-project/app/smartlibrary.db"

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def window(fig_w=16, fig_h=10):
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
    ax.set_xlim(0, 160); ax.set_ylim(0, 100); ax.axis("off")
    fig.patch.set_facecolor("#d8d5cb")
    ax.add_patch(FancyBboxPatch((1, 1), 158, 98, boxstyle="round,pad=0,rounding_size=2.6",
                                fc="#efece3", ec="#b9b4a4", lw=2.2))
    ax.add_patch(FancyBboxPatch((1, 90.2), 158, 8.8, boxstyle="round,pad=0,rounding_size=2.6",
                                fc=NAVY, ec="none"))
    ax.add_patch(Rectangle((1, 90.2), 158, 4.4, fc=NAVY, ec="none"))
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        ax.add_patch(mpatches.Circle((6.5 + i * 4.6, 94.6), 1.35, fc=c, ec="#00000022"))
    ax.text(80, 94.6, "SmartLibrary — http://127.0.0.1:5000", ha="center", va="center",
            fontsize=8.5, color="#cdd6e8", family="DejaVu Sans Mono")
    return fig, ax

def sidebar(ax, active):
    ax.add_patch(Rectangle((1, 1), 27, 89.2, fc=NAVY2, ec="none"))
    ax.add_patch(Rectangle((3.2, 82.2), 3.0, 4.2, fc=GOLD, ec="none"))
    ax.add_patch(Rectangle((3.7, 82.2), 0.45, 4.2, fc=NAVY, ec="none"))
    ax.text(8.0, 84.3, "SmartLibrary", ha="left", va="center", fontsize=11, fontweight="bold", color="white")
    ax.text(14.5, 79.6, "Dr. B.V. Hiray College of\nManagement & Research Centre",
            ha="center", va="center", fontsize=5.4, color="#c9c7bd", linespacing=1.4)
    items = [("Dashboard", "dash"), ("Books", "books"), ("Members", "members"),
             ("Issue Book", "issue"), ("Return Book", "return"), ("Transactions", "txns"),
             ("Fines", "fines"), ("Reports", "reports")]
    y = 71
    for label, key in items:
        if key == active:
            ax.add_patch(FancyBboxPatch((2.6, y - 2.3), 24.3, 5.4, boxstyle="round,pad=0,rounding_size=1.6",
                                        fc="#c9a22733", ec=GOLD, lw=1.6))
            ax.text(6.2, y + 0.4, label, ha="left", va="center", fontsize=7.6, color=GOLD_L, fontweight="bold")
        else:
            ax.text(6.2, y + 0.4, label, ha="left", va="center", fontsize=7.6, color="#dcd9ce")
        y -= 9.3

def stat_card(ax, x, y, w, h, label, value, hint):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.8", fc=CARD, ec="#e3e0d2", lw=1.2))
    ax.add_patch(Rectangle((x, y + h - 1.15), w, 1.15, fc=GOLD, ec="none"))
    ax.text(x + w / 2, y + h - 3.6, label.upper(), ha="center", fontsize=4.6, color=GREY, fontweight="bold")
    ax.text(x + w / 2, y + h / 2 - 0.4, str(value), ha="center", va="center", fontsize=15.5, fontweight="bold", color=NAVY)
    ax.text(x + w / 2, y + 1.9, hint, ha="center", fontsize=4.4, color=GREY)

def table(ax, x, y_top, w, cols, rows, row_h=4.6, fs=6.3, max_rows=None):
    """cols: list[(header, col_fraction)]; rows: list[list[str]]"""
    total = sum(c[1] for c in cols)
    cx = x
    # header
    ax.add_patch(Rectangle((x, y_top - 4.4), w, 4.4, fc=NAVY, ec="none"))
    for header, frac in cols:
        cw = w * frac / total
        ax.text(cx + cw / 2, y_top - 2.2, header.upper(), ha="center", va="center",
                fontsize=fs - 0.8, color=GOLD_L, fontweight="bold")
        cx += cw
    yy = y_top - 4.4
    for ridx, row in enumerate(rows if max_rows is None else rows[:max_rows]):
        yy -= row_h
        bg = "#ffffff" if ridx % 2 == 0 else "#fbfaf5"
        ax.add_patch(Rectangle((x, yy), w, row_h, fc=bg, ec="#efede4", lw=0.6))
        cx = x
        for (val, (_, frac)) in zip(row, cols):
            cw = w * frac / total
            color = RED if isinstance(val, str) and val.startswith("!") else "#202020"
            txt = val[1:] if isinstance(val, str) and val.startswith("!") else str(val)
            ax.text(cx + cw / 2, yy + row_h / 2, txt, ha="center", va="center", fontsize=fs, color=color)
            cx += cw
    return yy

def q(sql, args=()):
    c = conn(); rows = c.execute(sql, args).fetchall(); c.close(); return rows

def one(sql, args=()):
    c = conn(); row = c.execute(sql, args).fetchone(); c.close(); return row

# ================================================================ 1. LOGIN
def screen_login():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=150)
    ax.set_xlim(0, 160); ax.set_ylim(0, 100); ax.axis("off")
    fig.patch.set_facecolor("#0d1526")
    for i in range(40):
        ax.add_patch(mpatches.Circle((20 + (i * 37) % 140, 10 + (i * 53) % 85), 0.8, color="#22395e", alpha=0.35))
    ax.add_patch(FancyBboxPatch((49, 6), 62, 88, boxstyle="round,pad=0,rounding_size=3", fc="#fffdf6", ec="none"))
    ax.add_patch(FancyBboxPatch((49, 62), 62, 32, boxstyle="round,pad=0,rounding_size=3", fc=NAVY, ec="none"))
    ax.add_patch(Rectangle((49, 62), 62, 14, fc=NAVY, ec="none"))
    ax.add_patch(Rectangle((72.6, 76.5), 6.4, 8.6, fc=GOLD, ec="none"))
    ax.add_patch(Rectangle((79.3, 76.5), 1.15, 8.6, fc=NAVY, ec="none"))
    ax.add_patch(Rectangle((72.6, 76.5), 6.4, 1.1, fc="#b08d1e", ec="none"))
    ax.text(80, 72.5, "SmartLibrary", ha="center", fontsize=19, fontweight="bold", color="white")
    ax.text(80, 66.5, "Dr. B.V. Hiray College of Management and Research Centre\nMalegaon Camp, Malegaon — SPPU · MCA-I (Sem-I)",
            ha="center", va="center", fontsize=6.6, color="#c9c7bd", linespacing=1.5)
    ax.text(80, 56.5, "Librarian / Admin Sign In", ha="center", fontsize=10, fontweight="bold", color=NAVY)
    ax.text(57.5, 48.6, "USERNAME", fontsize=5.6, color=GREY, fontweight="bold")
    ax.add_patch(FancyBboxPatch((56.5, 38.5), 47, 7, boxstyle="round,pad=0,rounding_size=1.4", fc="white", ec="#dcd9ce"))
    ax.text(59, 42, "admin", va="center", fontsize=8.5, color="#202020")
    ax.text(57.5, 33.6, "PASSWORD", fontsize=5.6, color=GREY, fontweight="bold")
    ax.add_patch(FancyBboxPatch((56.5, 23.5), 47, 7, boxstyle="round,pad=0,rounding_size=1.4", fc="white", ec=GOLD, lw=1.6))
    ax.text(59, 27, "••••••••", va="center", fontsize=8.5, color="#202020")
    ax.add_patch(FancyBboxPatch((56.5, 12.5), 47, 7.4, boxstyle="round,pad=0,rounding_size=1.4", fc=GOLD, ec="none"))
    ax.text(80, 16.2, "Sign In  ›", ha="center", va="center", fontsize=10, fontweight="bold", color="#3d2e00")
    fig.savefig(f"{OUT}/screen-login-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-login-mock.png")

# ================================================================ 2. DASHBOARD
def screen_dashboard():
    total_titles = one("SELECT COUNT(*) c FROM book")["c"]
    copies = one("SELECT COALESCE(SUM(quantity),0) c FROM book")["c"]
    avail = one("SELECT COALESCE(SUM(available_quantity),0) c FROM book")["c"]
    members = one("SELECT COUNT(*) c FROM member WHERE status='Active'")["c"]
    issued = one("SELECT COUNT(*) c FROM issue_transaction WHERE status='Issued'")["c"]
    overdue = one("SELECT COUNT(*) c FROM issue_transaction WHERE status='Issued' AND due_date < date('now')")["c"]
    fines = one("SELECT COALESCE(SUM(fine_amount),0) c FROM issue_transaction")["c"]
    recent = q("""SELECT t.issue_id, b.title, m.name, t.issue_date, t.due_date, t.status,
                          (SELECT COUNT(*) FROM issue_transaction x WHERE x.status='Issued' AND x.due_date < date('now') AND x.issue_id=t.issue_id) overdue_flag
                   FROM issue_transaction t JOIN book b ON b.book_id=t.book_id JOIN member m ON m.member_id=t.member_id
                   ORDER BY t.issue_date DESC, t.issue_id DESC LIMIT 6""")
    low = q("SELECT title, available_quantity FROM book WHERE available_quantity <= 2 ORDER BY available_quantity LIMIT 3")

    fig, ax = window(16, 10)
    sidebar(ax, "dash")
    ax.text(32, 84.5, "Dashboard", fontsize=13, fontweight="bold", color=NAVY)
    ax.text(32, 80.8, date.today().strftime("%d %B %Y"), fontsize=6.6, color=GREY)
    stats = [("Titles", total_titles, "in catalogue"), ("Copies", copies, "total stock"), ("Available", avail, "ready to issue"),
             ("Members", members, "active"), ("Issued", issued, "open issues"), ("Overdue", overdue, "past due date"),
             ("Fines", f"₹{fines:.0f}", "collected")]
    x = 32
    for label, value, hint in stats:
        stat_card(ax, x, 62.5, 16.3, 14.5, label, value, hint)
        x += 17.95
    ax.text(32, 56.5, "Recent Transactions", fontsize=8.6, fontweight="bold", color=NAVY)
    rows = []
    for t in recent:
        status = "Returned" if t["status"] == "Returned" else ("!Overdue" if t["overdue_flag"] else "Issued")
        rows.append([t["title"][:26], t["name"].split()[0] + " " + t["name"].split()[-1][0] + ".", t["issue_date"], t["due_date"], status])
    table(ax, 32, 54.5, 88, [("Book", 2.6), ("Member", 1.5), ("Issued", 1.0), ("Due", 1.0), ("Status", 1.05)], rows, row_h=4.35, fs=5.9)
    ax.text(126, 56.5, "Low Stock Alert", fontsize=8.6, fontweight="bold", color=NAVY)
    ax.add_patch(FancyBboxPatch((123, 28), 34, 25.5, boxstyle="round,pad=0,rounding_size=1.8", fc=CARD, ec="#e3e0d2"))
    if low:
        yy = 47.5
        for b in low:
            ax.text(125.5, yy, f"• {b['title'][:22]}", fontsize=6.2, color=NAVY)
            ax.text(125.5, yy - 2.6, f"   {b['available_quantity']} left", fontsize=5.6, color=AMBER, fontweight="bold")
            yy -= 7.5
    else:
        ax.add_patch(mpatches.Circle((140, 42.5), 4.6, fc="#e3f4ea", ec=GREEN, lw=1.6))
        ax.plot([137.6, 139.6, 143.6], [42.3, 40.3, 45.4], color=GREEN, lw=2.2)
        ax.text(140, 33.0, "All titles\nwell stocked", ha="center", va="center", fontsize=7.2, color=GREEN, linespacing=1.5)
    fig.savefig(f"{OUT}/screen-dashboard-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-dashboard-mock.png")

# ================================================================ 3. ADD BOOK FORM
def screen_add_book():
    fig, ax = window(16, 10)
    sidebar(ax, "books")
    ax.add_patch(FancyBboxPatch((32, 14.5), 125, 66.0, boxstyle="round,pad=0,rounding_size=2", fc=CARD, ec="#e3e0d2"))
    ax.text(32, 84.5, "Add New Book", fontsize=13, fontweight="bold", color=NAVY)
    ax.text(32, 80.8, "All fields marked * are mandatory — ISBN must be unique", fontsize=6.6, color=GREY)
    fields = [("ISBN *", "978-0-13-468599-1"), ("TITLE *", "Effective Java"),
              ("AUTHOR(S) *", "Joshua Bloch"), ("PUBLISHER", "Addison-Wesley"),
              ("CATEGORY *", "Programming"), ("EDITION", "3rd Edition"),
              ("QUANTITY (COPIES) *", "6"), ("SHELF LOCATION", "A-01")]
    fw = 56.5
    rows_y = [63.0, 53.3, 43.6, 33.9]
    for i, (label, value) in enumerate(fields):
        col, row = i % 2, i // 2
        x = 36 + col * (fw + 5)
        y = rows_y[row]
        ax.text(x + 1, y + 8.6, label, fontsize=5.4, color=NAVY, fontweight="bold")
        ax.add_patch(FancyBboxPatch((x, y), fw, 6.9, boxstyle="round,pad=0,rounding_size=1.3",
                                    fc="#fffdf8", ec="#dcd9ce"))
        ax.text(x + 2.2, y + 3.45, value, va="center", fontsize=8, color="#202020")
    ax.add_patch(FancyBboxPatch((36, 18.2), 26, 7.2, boxstyle="round,pad=0,rounding_size=1.4", fc=NAVY, ec="none"))
    ax.text(49, 21.8, "Add Book", ha="center", va="center", fontsize=9, fontweight="bold", color="white")
    ax.add_patch(FancyBboxPatch((66.5, 18.2), 22, 7.2, boxstyle="round,pad=0,rounding_size=1.4", fc="white", ec=NAVY, lw=1.4))
    ax.text(77.5, 21.8, "Cancel", ha="center", va="center", fontsize=9, fontweight="bold", color=NAVY)
    fig.savefig(f"{OUT}/screen-add-book-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-add-book-mock.png")

# ================================================================ 4. RETURN BOOK
def screen_return():
    open_txns = q("""SELECT t.issue_id, b.title, m.name, m.roll_no, t.issue_date, t.due_date,
                          MAX(0, CAST(julianday('now') - julianday(t.due_date) AS INTEGER)) late
                   FROM issue_transaction t JOIN book b ON b.book_id=t.book_id JOIN member m ON m.member_id=t.member_id
                   WHERE t.status='Issued' ORDER BY t.due_date""")
    fig, ax = window(16, 10)
    sidebar(ax, "return")
    ax.text(32, 84.5, "Return a Book", fontsize=13, fontweight="bold", color=NAVY)
    ax.text(32, 80.8, "Fine of ₹2/day is auto-computed from the due date", fontsize=6.6, color=GREY)
    rows = []
    for t in open_txns:
        late = int(t["late"])
        rows.append([f"#{t['issue_id']}", t["title"][:24], t["name"][:17], t["issue_date"], t["due_date"],
                     f"!{late}d" if late else "ok", f"₹{late * 2}" if late else "₹0"])
    table(ax, 32, 77.5, 126, [("ID", 0.6), ("Book", 2.6), ("Member", 1.7), ("Issued", 1.0), ("Due", 1.0), ("Late", 0.8), ("Fine", 0.75)],
          rows, row_h=4.75, fs=6.2)
    yy = 77.5 - 4.4 - len(rows) * 4.75
    ax.add_patch(FancyBboxPatch((32, yy - 9.5), 126, 6.5, boxstyle="round,pad=0,rounding_size=1.4", fc="#fff6dd", ec="#d9a400"))
    ax.text(33.5, yy - 6.2, "Fine policy: ₹2 for every day past due_date. Overdue books are highlighted red.", fontsize=6.4, va="center", color="#6d5200")
    fig.savefig(f"{OUT}/screen-return-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-return-mock.png")

screen_login(); screen_dashboard(); screen_add_book(); screen_return()

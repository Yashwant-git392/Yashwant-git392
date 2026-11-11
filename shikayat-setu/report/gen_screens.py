"""Stylized renderings of the Campus Shikayat Setu UI (representative of the running app)."""
import sqlite3
from datetime import date, datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle

NAVY   = "#16243d"; NAVY2 = "#1f3455"; NAVY3 = "#2b4a73"
GOLD   = "#c9a227"; GOLD_L = "#ffd95e"
CREAM  = "#f7f5ef"; CARD = "#ffffff"; LT = "#e8edf7"
GREEN  = "#1e7a46"; RED = "#b3372e"; AMBER = "#a05a00"; GREY = "#6b7280"

OUT = "/home/user/Yashwant-git392/shikayat-setu/report/images"
DB = "/home/user/Yashwant-git392/shikayat-setu/app/shikayat_setu.db"

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def q(sql, args=()):
    c = conn(); rows = c.execute(sql, args).fetchall(); c.close(); return rows

def one(sql, args=()):
    c = conn(); row = c.execute(sql, args).fetchone(); c.close(); return row

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
    ax.text(80, 94.6, "Campus Shikayat Setu — http://127.0.0.1:5001", ha="center", va="center",
            fontsize=8.5, color="#cdd6e8", family="DejaVu Sans Mono")
    return fig, ax

def sidebar(ax, active, admin=False):
    ax.add_patch(Rectangle((1, 1), 27, 89.2, fc=NAVY2, ec="none"))
    ax.add_patch(Rectangle((3.2, 82.2), 3.0, 4.2, fc=GOLD, ec="none"))
    ax.add_patch(Rectangle((3.7, 82.2), 0.45, 4.2, fc=NAVY, ec="none"))
    ax.text(8.0, 84.3, "Shikayat Setu", ha="left", va="center", fontsize=9.5, fontweight="bold", color="white")
    ax.text(14.5, 78.6, "Dr. B.V. Hiray College of\nManagement & Research Centre",
            ha="center", va="center", fontsize=5.2, color="#c9c7bd", linespacing=1.4)
    if admin:
        items = [("Console", "console"), ("Complaints", "mine"), ("Departments", "depts"),
                 ("Users", "users"), ("Reports", "reports")]
    else:
        items = [("Dashboard", "dash"), ("Lodge Complaint", "lodge"), ("My Complaints", "mine"),
                 ("Track", "track"), ("Profile", "profile")]
    y = 70
    for label, key in items:
        if key == active:
            ax.add_patch(FancyBboxPatch((2.6, y - 2.3), 24.3, 5.4, boxstyle="round,pad=0,rounding_size=1.6",
                                        fc="#c9a22733", ec=GOLD, lw=1.6))
            ax.text(6.2, y + 0.4, label, ha="left", va="center", fontsize=7.4, color=GOLD_L, fontweight="bold")
        else:
            ax.text(6.2, y + 0.4, label, ha="left", va="center", fontsize=7.4, color="#dcd9ce")
        y -= 10

def stat_card(ax, x, y, w, h, label, value, hint):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.8", fc=CARD, ec="#e3e0d2", lw=1.2))
    ax.add_patch(Rectangle((x, y + h - 1.15), w, 1.15, fc=GOLD, ec="none"))
    ax.text(x + w / 2, y + h - 3.6, label.upper(), ha="center", fontsize=4.4, color=GREY, fontweight="bold")
    ax.text(x + w / 2, y + h / 2 - 0.3, str(value), ha="center", va="center", fontsize=14.5, fontweight="bold", color=NAVY)
    ax.text(x + w / 2, y + 1.9, hint, ha="center", fontsize=4.2, color=GREY)

def table(ax, x, y_top, w, cols, rows, row_h=4.6, fs=6.3, max_rows=None):
    total = sum(c[1] for c in cols)
    cx = x
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

# ================================================================ 1. LOGIN
def screen_login():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=150)
    ax.set_xlim(0, 160); ax.set_ylim(0, 100); ax.axis("off")
    fig.patch.set_facecolor("#0d1526")
    for i in range(40):
        ax.add_patch(mpatches.Circle((20 + (i * 37) % 140, 10 + (i * 53) % 85), 0.8, color="#22395e", alpha=0.35))
    ax.add_patch(FancyBboxPatch((44, 5), 72, 90, boxstyle="round,pad=0,rounding_size=3", fc="#fffdf6", ec="none"))
    ax.add_patch(FancyBboxPatch((44, 64), 72, 31, boxstyle="round,pad=0,rounding_size=3", fc=NAVY, ec="none"))
    ax.add_patch(Rectangle((44, 64), 72, 13, fc=NAVY, ec="none"))
    ax.add_patch(Rectangle((76.6, 78.5), 6.8, 8.6, fc=GOLD, ec="none"))
    ax.add_patch(Rectangle((83.3, 78.5), 1.15, 8.6, fc=NAVY, ec="none"))
    ax.text(80, 73.5, "Campus Shikayat Setu", ha="center", fontsize=16.5, fontweight="bold", color="white")
    ax.text(80, 67.8, "Dr. B.V. Hiray College of Management and Research Centre\nMalegaon Camp — SPPU · MCA-I (Sem-I)",
            ha="center", va="center", fontsize=6.6, color="#c9c7bd", linespacing=1.5)
    ax.text(80, 58.5, "Sign In", ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax.text(55.5, 50.6, "USERNAME / ROLL NO.", fontsize=5.6, color=GREY, fontweight="bold")
    ax.add_patch(FancyBboxPatch((54.5, 40.5), 51, 7, boxstyle="round,pad=0,rounding_size=1.4", fc="white", ec="#dcd9ce"))
    ax.text(57, 44, "MCA2026001", va="center", fontsize=8.5, color="#202020")
    ax.text(55.5, 35.6, "PASSWORD", fontsize=5.6, color=GREY, fontweight="bold")
    ax.add_patch(FancyBboxPatch((54.5, 25.5), 51, 7, boxstyle="round,pad=0,rounding_size=1.4", fc="white", ec=GOLD, lw=1.6))
    ax.text(57, 29, "••••••••••", va="center", fontsize=8.5, color="#202020")
    ax.add_patch(FancyBboxPatch((54.5, 14.5), 51, 7.4, boxstyle="round,pad=0,rounding_size=1.4", fc=GOLD, ec="none"))
    ax.text(80, 18.2, "Sign In  ›", ha="center", va="center", fontsize=10, fontweight="bold", color="#3d2e00")
    ax.text(80, 9.5, "Demo: admin / admin123  ·  MCA2026001 / student123", ha="center", fontsize=6.0, color="#8a8578")
    fig.savefig(f"{OUT}/screen-login-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-login-mock.png")

# ================================================================ 2. STUDENT DASHBOARD
def screen_dashboard():
    mine = one("SELECT COUNT(*) c FROM complaints WHERE student_id=(SELECT id FROM users WHERE username='MCA2026001')")["c"]
    closed = one("SELECT COUNT(*) c FROM complaints WHERE student_id=(SELECT id FROM users WHERE username='MCA2026001') AND status IN ('Resolved','Closed')")["c"]
    open_ = mine - closed
    recent = q("""SELECT c.code, c.title, c.priority, c.status FROM complaints c
                  WHERE c.student_id=(SELECT id FROM users WHERE username='MCA2026001')
                  ORDER BY c.submitted_at DESC LIMIT 6""")
    fig, ax = window(16, 10)
    sidebar(ax, "dash")
    ax.text(32, 84.5, "Dashboard", fontsize=13, fontweight="bold", color=NAVY)
    ax.text(32, 80.8, date.today().strftime("%d %B %Y") + "  ·  Signed in as Yashwant Ahire (MCA2026001)", fontsize=6.4, color=GREY)
    stats = [("My Complaints", mine, "all time"), ("Open", open_, "awaiting action"),
             ("Closed", closed, "resolved & rated"), ("Avg Close", "—", "hrs, this semester")]
    x = 32
    for label, value, hint in stats:
        stat_card(ax, x, 62.5, 27.5, 14.5, label, value, hint); x += 30.3
    ax.text(32, 56.5, "Latest complaints", fontsize=8.6, fontweight="bold", color=NAVY)
    rows = [[r["code"], r["title"][:34], r["priority"], r["status"]] for r in recent]
    table(ax, 32, 54.5, 124, [("Code", 1.15), ("Title", 2.9), ("Priority", 0.8), ("Status", 1.0)], rows,
          row_h=4.6, fs=6.0)
    ax.text(32, 20.5, "Tip: use the public tracker with the CMP code + roll no. — no login needed.", fontsize=5.8, color=GREY, style="italic")
    fig.savefig(f"{OUT}/screen-dashboard-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-dashboard-mock.png")

# ================================================================ 3. ADMIN CONSOLE
def screen_console():
    rows = q("""SELECT c.code, c.title, d.name AS dept, c.priority, c.status, c.submitted_at
               FROM complaints c JOIN departments d ON d.id=c.department_id
               ORDER BY c.submitted_at DESC LIMIT 9""")
    total = one("SELECT COUNT(*) c FROM complaints")["c"]
    high = one("SELECT COUNT(*) c FROM complaints WHERE priority='High'")["c"]
    fig, ax = window(16, 10)
    sidebar(ax, "console", admin=True)
    ax.text(32, 84.5, "Admin Console", fontsize=13, fontweight="bold", color=NAVY)
    ax.text(32, 80.8, f"{total} complaints on record  ·  {high} High priority  ·  filters: department / status / priority",
            fontsize=6.4, color=GREY)
    rows2 = [[r["code"], r["title"][:30], r["dept"][:20], r["priority"],
              "!" + r["status"] if r["status"] == "Submitted" else r["status"]] for r in rows]
    table(ax, 32, 78.5, 124, [("Code", 1.1), ("Title", 2.35), ("Department", 1.65), ("Priority", 0.75), ("Status", 1.0)],
          rows2, row_h=6.6, fs=5.9)
    ax.add_patch(FancyBboxPatch((32, 6.5), 30, 6.4, boxstyle="round,pad=0,rounding_size=1.4", fc=RED, ec="none"))
    ax.text(47, 9.7, "Escalate → High", ha="center", va="center", fontsize=7.6, fontweight="bold", color="white")
    ax.add_patch(FancyBboxPatch((66, 6.5), 34, 6.4, boxstyle="round,pad=0,rounding_size=1.4", fc="white", ec=NAVY, lw=1.3))
    ax.text(83, 9.7, "Reassign dept…", ha="center", va="center", fontsize=7.6, fontweight="bold", color=NAVY)
    ax.add_patch(FancyBboxPatch((104, 6.5), 26, 6.4, boxstyle="round,pad=0,rounding_size=1.4", fc="#fdf0d5", ec=GOLD, lw=1.3))
    ax.text(117, 9.7, "Force-close", ha="center", va="center", fontsize=7.6, fontweight="bold", color="#6d5200")
    fig.savefig(f"{OUT}/screen-console-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-console-mock.png")

# ================================================================ 4. COMPLAINT TIMELINE (detail)
def screen_timeline():
    c = q("SELECT c.*, cat.name AS cat, d.name AS dept FROM complaints c JOIN categories cat ON cat.id=c.category_id JOIN departments d ON d.id=c.department_id WHERE c.is_anonymous=0 ORDER BY c.id LIMIT 1")[0]
    ev = q("SELECT e.event_type, e.note, e.created_at FROM complaint_events e WHERE e.complaint_id=? ORDER BY e.id", (c["id"],))
    fig, ax = window(16, 10)
    ax.text(8, 84.5, "Complaint " + c["code"], fontsize=13, fontweight="bold", color=NAVY)
    ax.text(8, 80.3, f"{c['title']}", fontsize=8.5, color="#333")
    ax.text(8, 75.6, f"Category: {c['cat']}    Department: {c['dept']}    Priority: {c['priority']}    Status: {c['status']}",
            fontsize=6.6, color=GREY)
    ax.add_patch(FancyBboxPatch((122, 76.5), 30, 8.5, boxstyle="round,pad=0,rounding_size=1.6", fc="#fbf3d9", ec=GOLD, lw=1.5))
    ax.text(137, 81.8, "SLA", ha="center", fontsize=5.4, color="#8a6d1a", fontweight="bold")
    ax.text(137, 77.8, (datetime.strptime(c["sla_due_at"], "%Y-%m-%d %H:%M:%S")).strftime("%d %b %H:%M"),
            ha="center", fontsize=6.6, fontweight="bold", color="#6d5200")
    ax.plot([10, 10], [10, 66], color=GOLD, lw=2.4, zorder=2)
    yy = 62
    for i, e in enumerate(ev[:7]):
        ax.add_patch(mpatches.Circle((10, yy), 1.35, fc=(NAVY if i else GOLD), ec="white", lw=1.6, zorder=4))
        ax.add_patch(FancyBboxPatch((14, yy - 4.4), 138, 7.6, boxstyle="round,pad=0,rounding_size=1.3",
                                    fc=CARD, ec="#e3e0d2", lw=1.1, zorder=3))
        ax.text(16.5, yy + 0.6, e["event_type"].upper() + "  ·  " + e["created_at"][5:16], fontsize=5.2, color=GREY, fontweight="bold", zorder=6)
        ax.text(16.5, yy - 2.6, e["note"][:96], fontsize=6.0, color="#202020", zorder=6)
        yy -= 8.35
    fig.savefig(f"{OUT}/screen-timeline-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-timeline-mock.png")

screen_login(); screen_dashboard(); screen_console(); screen_timeline()

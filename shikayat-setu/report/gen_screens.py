"""Create illustrative mock-ups of the Campus Shikayat Setu interface."""
from pathlib import Path
import sqlite3
from datetime import date, datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Arc
import numpy as np

NAVY = "#141f36"; NAVY2 = "#1b2b47"; NAVY3 = "#22355a"; PANEL = "#141c2e"
GOLD = "#c9a227"; GOLD_L = "#ffd95e"; GOLD_D = "#241a02"
CREAM = "#f6f5ef"; CARD = "#ffffff"; CARD2 = "#fbfaf6"; LT = "#e8edf7"
GREEN = "#177a46"; RED = "#b3372e"; AMBER = "#96690a"; GREY = "#66707f"
BLUE_BG = "#e9effc"; GREEN_BG = "#e6f6ec"; RED_BG = "#fdeaec"; AMBER_BG = "#fdf3d8"; GOLD_SOFT = "#f5e9c4"
OUT = Path(__file__).resolve().parent / "images"
DB = Path(__file__).resolve().parent.parent / "app" / "shikayat_setu.db"

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def q(sql, args=()):
    c = conn(); rows = c.execute(sql, args).fetchall(); c.close(); return rows

def one(sql, args=()):
    c = conn(); row = c.execute(sql, args).fetchone(); c.close(); return row

def canvas(w=160, h=100, bg="#0b1020"):
    fig, ax = plt.subplots(figsize=(w / 8.6, h / 8.6), dpi=150)
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    fig.patch.set_facecolor(bg)
    return fig, ax

def rrect(ax, x, y, w, h, r, fc, ec="none", lw=0, z=2, alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha,
                                mutation_scale=1))

def sidebar(ax, active, admin=False):
    # gradient-ish panel (two overlapping rects)
    ax.add_patch(Rectangle((0, 0), 34, 100, fc=NAVY, ec="none", zorder=2))
    ax.add_patch(Rectangle((0, 0), 34, 46, fc=NAVY2, ec="none", alpha=.55, zorder=2))
    # gold house badge
    rrect(ax, 4.5, 86.5, 9.5, 9.5, 2.1, ("#ffd95e"), z=3)
    ax.add_patch(Rectangle((6.2, 89.5), 6, 4.4, fc=GOLD, ec="none", zorder=4))
    ax.add_patch(Polygon([[6.2, 93.4], [9.2, 97.2], [12.2, 93.4]], closed=True, fc=GOLD, ec="none", zorder=4))
    ax.text(16.3, 93.2, "Campus\nShikayat Setu", fontsize=6.6, fontweight="bold", color="#ffffff", va="center", zorder=4, linespacing=1.15)
    ax.text(4.5, 79.5, "COLLEGE GRIEVANCE REDRESSAL", fontsize=3.4, color="#7f93b6", zorder=4)
    if admin:
        items = [("Dashboard", "dash"), ("Complaint Queue", "queue"), ("Admin Console", "console"),
                 ("Users & Officers", "users"), ("Print Registers", "reports")]
    else:
        items = [("Dashboard", "dash"), ("Lodge Complaint", "lodge"), ("My Complaints", "mine")]
    y = 71
    for label, key in items:
        if key == active:
            rrect(ax, 3, y - 2.6, 28, 6.2, 1.5, "#c9a2272e", ec="#c9a22766", lw=1.0, z=3)
            ax.add_patch(Circle((6.6, y + 0.5), 1.05, fc=GOLD_L, ec="none", zorder=4))
            ax.text(9.6, y + 0.5, label, fontsize=5.6, fontweight="bold", color=GOLD_L, va="center", zorder=4)
        else:
            ax.add_patch(Circle((6.6, y + 0.5), 1.05, fc="#33415e", ec="none", zorder=4))
            ax.text(9.6, y + 0.5, label, fontsize=5.6, color="#cdd5e4", va="center", zorder=4)
        y -= 8.6
    # account foot
    ax.add_patch(Circle((6.8, 13.5), 2.4, fc=GOLD, ec="none", zorder=4))
    ax.text(6.8, 13.5, "YA" if not admin else "AD", fontsize=4.2, fontweight="bold", color=GOLD_D, ha="center", va="center", zorder=5)
    ax.text(11.2, 15.4, "Yashwant Ahire" if not admin else "System Admin", fontsize=4.6, fontweight="bold", color="#fff", va="center", zorder=4)
    ax.text(11.2, 11.8, ("MCA2026001 · STUDENT") if not admin else "ADMIN", fontsize=3.6, color="#8fa9d0", va="center", zorder=4)

def topbar(ax, crumb_right, x0=34):
    ax.add_patch(Rectangle((x0, 92.5), 160 - x0, 7.5, fc=CREAM, ec="none", zorder=2))
    ax.plot([x0, 160], [92.5, 92.5], color="#eceade", lw=1.4, zorder=3)
    ax.text(x0 + 3, 96.25, "Shikayat Setu  ›  " + crumb_right, fontsize=5.6, color=GREY, va="center", zorder=4)
    rrect(ax, 128.5, 94.6, 12.5, 3.6, 1.8, CARD, ec="#e5e3d8", lw=0.8, z=4)
    ax.text(134.75, 96.4, "RBAC · role", fontsize=3.8, fontweight="bold", color=NAVY3, ha="center", va="center", zorder=5)
    rrect(ax, 143, 94.4, 5.4, 4.2, 1.1, CARD, ec="#e5e3d8", lw=0.8, z=4)
    ax.add_patch(Arc((145.7, 96.6), 2.6, 2.6, angle=0, theta1=35, theta2=325, color=NAVY, lw=1.4, zorder=5))
    ax.plot([145.7], [96.6], marker="o", ms=1.6, color=NAVY, zorder=5)

def stat_card(ax, x, y, w, h, label, value, hint, tone=GOLD):
    rrect(ax, x, y, w, h, 2.0, CARD, ec="#eceade", lw=1.1, z=3)
    ax.add_patch(Rectangle((x + 1.2, y + 0.8), w - 2.4, 0.9, fc=tone, ec="none", zorder=4, alpha=.9))
    ax.text(x + 2.2, y + h - 3.4, label.upper(), fontsize=3.9, fontweight="bold", color=GREY, zorder=4)
    ax.text(x + 2.2, y + h / 2 - 1.2, str(value), fontsize=12.5, fontweight="bold", color=NAVY, zorder=4, family="serif")
    ax.text(x + 2.2, y + 2.2, hint, fontsize=3.4, color=GREY, zorder=4)

def table(ax, x, y_top, w, cols, rows, row_h=4.4, fs=5.0, header_fs=4.2, z=3):
    total = sum(c[1] for c in cols)
    ax.add_patch(Rectangle((x, y_top - 3.6), w, 3.6, fc=NAVY2, ec="none", zorder=z))
    cx = x
    for header, frac in cols:
        cw = w * frac / total
        ax.text(cx + cw / 2, y_top - 1.8, header.upper(), fontsize=header_fs, fontweight="bold",
                color="#f3ead2", ha="center", va="center", zorder=z + 1)
        cx += cw
    yy = y_top - 3.6
    for ridx, row in enumerate(rows):
        yy -= row_h
        bg = CARD if ridx % 2 == 0 else CARD2
        ax.add_patch(Rectangle((x, yy), w, row_h, fc=bg, ec="#f0eee3", lw=0.5, zorder=z))
        cx = x
        for val, (_, frac) in zip(row, cols):
            cw = w * frac / total
            ax.text(cx + cw / 2, yy + row_h / 2, str(val), fontsize=fs, color="#202020",
                    ha="center", va="center", zorder=z + 1)
            cx += cw
    return yy

def pill(ax, x, y, w, text, fg, bg, fs=3.6, z=6):
    rrect(ax, x, y, w, 2.6, 1.3, bg, ec="none", z=z)
    ax.text(x + w / 2, y + 1.3, text.upper(), fontsize=fs, fontweight="bold", color=fg, ha="center", va="center", zorder=z + 1)

def donut(ax, cx, cy, r, segments, total_label):
    colors = [s[1] for s in segments]
    fracs = [s[0] / max(1, sum(seg[0] for seg in segments)) for s in segments]
    theta = 90.0
    for frac, color in zip(fracs, colors):
        sweep = 360 * frac
        ax.add_patch(Arc((cx, cy), 2 * r, 2 * r, angle=0, theta1=theta - sweep, theta2=theta,
                         lw=7.5, color=color, zorder=4))
        theta -= sweep
    ax.text(cx, cy + 0.8, str(total_label), fontsize=10, fontweight="bold", color=NAVY, ha="center", va="center", family="serif", zorder=5)
    ax.text(cx, cy - 3.3, "TOTAL", fontsize=3.4, color=GREY, ha="center", zorder=5)

# ================================================================ 1. LOGIN
def screen_login():
    fig, ax = canvas(160, 100, bg="#0b1020")
    # hero left
    ax.add_patch(Rectangle((0, 0), 84, 100, fc="#0b1020", ec="none"))
    for rr, aa in zip([26, 22, 18, 14, 10, 6], [0.05, 0.07, 0.09, 0.13, 0.18, 0.24]):
        ax.add_patch(Circle((14, 106), rr, fc="#c9a227", alpha=aa, zorder=1))
    for rr, aa in zip([25, 21, 17, 13, 9, 5], [0.05, 0.07, 0.10, 0.14, 0.19, 0.26]):
        ax.add_patch(Circle((78, -4), rr, fc="#3d5a80", alpha=aa, zorder=1))
    ax.text(7, 82, "DR. B.V. HIRAY COLLEGE  ·  MALEGAON", fontsize=4.6, color="#ffd95e", fontweight="bold")
    ax.text(7, 66, "Every\ngrievance,\nheard &", fontsize=17.5, fontweight="bold", color="#ffffff", va="top", linespacing=1.12, family="serif")
    ax.text(7, 36.5, "tracked.", fontsize=17.5, fontweight="bold", color=GOLD_L, va="top", family="serif", style="italic")
    for i, t in enumerate(["( bolt )  Auto-routing — explainable keyword scoring",
                            "( clock )  SLA on every complaint — 24h / 72h / 7d",
                            "( eye )  Anonymous lodgement for sensitive matters"]):
        ax.text(7, 22.5 - i * 4.6, t, fontsize=4.6, color="#cdd7ec")
    ax.add_patch(Rectangle((7, 4), 34, 0.35, fc=GOLD, ec="none"))
    # panel right
    ax.add_patch(Rectangle((84, 0), 76, 100, fc="#0b1020", ec="none"))
    rrect(ax, 96, 12, 52, 76, 3.2, "#141c2e", ec="#2b3a5f", lw=1.2, z=2)
    ax.text(122, 76.5, "Welcome back", fontsize=9.5, fontweight="bold", color="#fff", ha="center", family="serif", zorder=4)
    ax.text(122, 70.5, "Campus Shikayat Setu — Grievance Redressal", fontsize=3.9, color="#8fa9d0", ha="center", zorder=4)
    for i, (lab, val) in enumerate([("ROLL NUMBER / USERNAME", "MCA2026001"), ("PASSWORD", "••••••••••")]):
        ax.text(101.5, 60 - i * 13.5, lab, fontsize=3.6, fontweight="bold", color="#8fa9d0", zorder=4)
        rrect(ax, 101.5, 48.6 - i * 13.5, 41, 7.6, 1.5, "#141c2e", ec="#2b3a5f", lw=1.3, z=3)
        ax.text(104, 52.4 - i * 13.5, val, fontsize=6.4, color="#eef1f8", va="center", zorder=4)
    rrect(ax, 101.5, 22.5, 41, 8.4, 1.7, GOLD, ec="none", z=3)
    ax.text(122, 26.7, "Sign in  →", fontsize=7.6, fontweight="bold", color=GOLD_D, ha="center", va="center", zorder=4)
    ax.text(122, 16.2, "admin / admin123  ·  MCA2026001 / student123", fontsize=4.2, color="#66707f", ha="center", zorder=4)
    fig.savefig(f"{OUT}/screen-login-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-login-mock.png")

# ================================================================ 2. DASHBOARD (student)
def screen_dashboard():
    mine = one("SELECT COUNT(*) c FROM complaints WHERE student_id=(SELECT id FROM users WHERE username='MCA2026001')")["c"]
    closed = one("SELECT COUNT(*) c FROM complaints WHERE student_id=(SELECT id FROM users WHERE username='MCA2026001') AND status IN ('Resolved','Closed')")["c"]
    recent = q("""SELECT c.code, substr(c.title,1,30) AS t, c.priority, c.status FROM complaints c
                  WHERE c.student_id=(SELECT id FROM users WHERE username='MCA2026001')
                  ORDER BY c.submitted_at DESC LIMIT 4""")
    counts = {r["status"]: r["n"] for r in q("SELECT status, COUNT(*) n FROM complaints WHERE student_id=(SELECT id FROM users WHERE username='MCA2026001') GROUP BY status")}
    fig, ax = canvas(160, 100, bg=CREAM)
    sidebar(ax, "dash"); topbar(ax, "Dashboard")
    ax.text(38, 84.5, "MY DASHBOARD", fontsize=3.9, fontweight="bold", color="#a8861b")
    ax.text(38, 79.5, "My Dashboard", fontsize=10.5, fontweight="bold", color=NAVY, family="serif")
    ax.text(38, 74.6, "Your complaints at a glance — SLA-tracked by the college.", fontsize=4.4, color=GREY)
    rrect(ax, 138, 74, 17, 5.6, 1.4, GOLD, ec="none", z=3)
    ax.text(146.5, 76.8, "+ Lodge new", fontsize=4.6, fontweight="bold", color=GOLD_D, ha="center", va="center", zorder=4)
    stats = [("Total", mine, "lodged all time", GOLD), ("Open", mine - closed, "awaiting resolution", "#d97706"),
             ("Resolved", counts.get("Resolved", 0), "awaiting your ★", GREEN), ("Closed", counts.get("Closed", 0), "confirmed by you", GREEN)]
    x = 38
    for label, value, hint, tone in stats:
        stat_card(ax, x, 55.5, 28.6, 15.5, label, value, hint, tone); x += 30.4
    # recent complaints card
    rrect(ax, 38, 12, 74, 38, 2.4, CARD, ec="#eceade", lw=1.1, z=3)
    ax.text(41.5, 44.5, "Latest complaints", fontsize=6.4, fontweight="bold", color=NAVY, zorder=4)
    rows = [[r["code"], r["t"], r["priority"], r["status"]] for r in recent]
    table(ax, 41.5, 41.5, 67, [("Code", 1.15), ("Title", 2.6), ("Priority", 0.8), ("Status", 1.0)], rows, row_h=5.0, fs=3.7, header_fs=3.3)
    # donut card
    rrect(ax, 117, 12, 38, 38, 2.4, CARD, ec="#eceade", lw=1.1, z=3)
    ax.text(120.5, 44.5, "Status distribution", fontsize=6.4, fontweight="bold", color=NAVY, zorder=4)
    segs = [(counts.get(s, 0), c) for s, c in [("Submitted", GOLD), ("Acknowledged", "#5b7bb4"), ("In Progress", "#d97706"), ("Resolved", GREEN), ("Closed", "#8a8f9d")]]
    segs = [s for s in segs if s[0] > 0]
    if segs:
        donut(ax, 136, 29.5, 7.2, segs, mine)
    fig.savefig(f"{OUT}/screen-dashboard-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-dashboard-mock.png")

# ================================================================ 3. ADMIN CONSOLE
def screen_console():
    rows = q("""SELECT c.code, substr(c.title,1,30) AS t, d.name AS dept, c.priority, c.status, c.sla_due_at
               FROM complaints c JOIN departments d ON d.id=c.department_id
               ORDER BY c.submitted_at DESC LIMIT 7""")
    fig, ax = canvas(160, 100, bg=CREAM)
    sidebar(ax, "console", admin=True); topbar(ax, "Admin Console")
    ax.text(38, 84.5, "ADMINISTRATION", fontsize=3.9, fontweight="bold", color="#a8861b")
    ax.text(38, 79.5, "Admin Console", fontsize=10.5, fontweight="bold", color=NAVY, family="serif")
    ax.text(38, 74.6, "Every complaint in the college — filter and act.", fontsize=4.4, color=GREY)
    # filter toolbar
    for i, (t, w) in enumerate([("All departments ▾", 24), ("All statuses ▾", 20), ("All priorities ▾", 20)]):
        rrect(ax, 38 + i * 25.4, 63.5, w, 6.4, 1.6, CARD2, ec="#dcd9ce", lw=1.0, z=3)
        ax.text(38 + i * 25.4 + w / 2, 66.7, t, fontsize=4.4, color=NAVY, ha="center", va="center", zorder=4)
    rrect(ax, 113, 63.5, 15, 6.4, 1.6, NAVY2, ec="none", z=3)
    ax.text(120.5, 66.7, "Apply", fontsize=4.8, fontweight="bold", color="#f6f5ef", ha="center", va="center", zorder=4)
    rrect(ax, 130.5, 63.5, 24.5, 6.4, 1.6, CARD, ec="#dcd9ce", lw=1.0, z=3)
    ax.text(132.6, 66.7, "Instant filter…", fontsize=4.4, color=GREY, va="center", zorder=4)
    table_rows = []
    for r in rows:
        table_rows.append([r["code"], r["t"], r["dept"][:17], r["priority"], r["status"]])
    table(ax, 38, 59.5, 117, [("Code", 1.05), ("Title", 2.35), ("Dept", 1.55), ("Priority", 0.75), ("Status", 0.95)],
          table_rows, row_h=5.6, fs=3.6, header_fs=3.3)
    fig.savefig(f"{OUT}/screen-console-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-console-mock.png")

# ================================================================ 4. COMPLAINT DETAIL + AUDIT TIMELINE
def screen_timeline():
    c = q("SELECT c.*, cat.name AS cat, d.name AS dept FROM complaints c JOIN categories cat ON cat.id=c.category_id JOIN departments d ON d.id=c.department_id WHERE c.is_anonymous=0 AND c.status='Closed' ORDER BY c.id LIMIT 1")[0]
    ev = q("SELECT event_type, note, created_at FROM complaint_events WHERE complaint_id=? ORDER BY id", (c["id"],))
    fig, ax = canvas(160, 100, bg=CREAM)
    sidebar(ax, "mine"); topbar(ax, c["code"])
    ax.text(38, 84.5, "COMPLAINT", fontsize=3.9, fontweight="bold", color="#a8861b")
    ax.text(38, 79.5, c["code"], fontsize=11, fontweight="bold", color=NAVY, family="monospace")
    ax.text(38, 74.6, c["title"], fontsize=5.4, color="#333")
    # stepper
    steps = ["Submitted", "Acknowledged", "In Progress", "Resolved", "Closed"]
    idx = steps.index(c["status"])
    for i, s in enumerate(steps):
        x = 38 + i * 24.6
        ax.plot([x - 11 if i else x, x + 12.3], [66.5, 66.5], color=(GREEN if i <= idx else "#e5e3d8"), lw=2.4, zorder=2)
        done = i <= idx
        ax.add_patch(Circle((x, 66.5), 1.9, fc=(GREEN if done else CARD), ec=(GREEN if done else "#dcd9ce"), lw=1.6, zorder=4))
        if done:
            ax.text(x, 66.5, "✓", fontsize=4.6, color="#fff", ha="center", va="center", zorder=5, fontweight="bold")
        ax.text(x, 61.6, s.upper(), fontsize=3.1, ha="center", color=(GREEN if done else GREY), fontweight="bold", zorder=4)
    # timeline card
    rrect(ax, 38, 6, 76, 48, 2.4, CARD, ec="#eceade", lw=1.1, z=3)
    ax.text(41.5, 49.5, "Timeline — full audit trail", fontsize=6.4, fontweight="bold", color=NAVY, zorder=4)
    icon = {"created": "+", "routed": "R", "acknowledged": "✓", "status": "W", "closed": "x", "feedback": "*"}
    yy = 44
    for e in ev[:5]:
        ax.add_patch(Circle((43.5, yy + 1.5), 1.55, fc=GOLD_SOFT, ec=GOLD, lw=1.1, zorder=4))
        ax.text(43.5, yy + 1.5, icon.get(e["event_type"], "•"), fontsize=3.9, ha="center", va="center", zorder=5)
        rrect(ax, 47.2, yy - 1.5, 63.5, 6.2, 1.4, CARD2, ec="#eceade", lw=0.9, z=3)
        ax.text(49, yy + 2.6, f"{e['event_type'].upper()}  ·  {e['created_at'][5:16]}", fontsize=3.2, fontweight="bold", color="#a8861b", zorder=5)
        ax.text(49, yy - 0.3, e["note"][:88], fontsize=3.5, color="#202020", va="center", zorder=5)
        yy -= 7.9
    # SLA card right
    rrect(ax, 118, 30, 37, 24, 2.4, CARD, ec="#eceade", lw=1.1, z=3)
    ax.text(121.5, 49, "SLA clock", fontsize=6.0, fontweight="bold", color=NAVY, zorder=4)
    ax.text(121.5, 42.5, "Resolved", fontsize=4.6, color=GREY, zorder=4)
    ax.text(121.5, 37.5, "within deadline", fontsize=6.4, fontweight="bold", color=GREEN, family="serif", zorder=4)
    ax.text(121.5, 32.5, "Routing: auto · score 14", fontsize=3.9, color=GREY, zorder=4)
    rrect(ax, 118, 6, 37, 20, 2.4, CARD, ec="#eceade", lw=1.1, z=3)
    ax.text(121.5, 21.3, "Student feedback", fontsize=6.0, fontweight="bold", color=NAVY, zorder=4)
    ax.text(121.5, 13.5, "*****", fontsize=10.5, color=GOLD, zorder=4)
    ax.text(121.5, 8.5, "\"Tap replaced the same day.\"", fontsize=3.8, color=GREY, style="italic", zorder=4)
    fig.savefig(f"{OUT}/screen-timeline-mock.png", bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
    print("screen-timeline-mock.png")

from matplotlib.patches import Polygon
screen_login(); screen_dashboard(); screen_console(); screen_timeline()

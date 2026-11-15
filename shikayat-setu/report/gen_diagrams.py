"""Generate code- and schema-aligned project diagrams.

The ER diagram reads SQLite metadata from schema.sql; class boxes are explicitly
conceptual records, not Python ORM classes. The review schedule chart is separate.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch, Ellipse, Circle
from diagram_data import schema_facts

OUT = Path(__file__).resolve().parent / "images"
NAVY = "#172b3a"
TEAL = "#087e78"
PALE = "#e8f4f2"
BG = "#f7f9f8"
INK = "#21333d"
MUTED = "#50646b"
ORANGE = "#955d11"


def canvas(title, subtitle="", w=16, h=10):
    fig, ax = plt.subplots(figsize=(w * .85, h * .85), dpi=180)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.text(50, 97.5, title, ha="center", va="center", fontsize=17, color=NAVY, weight="bold")
    if subtitle:
        ax.text(50, 93.8, subtitle, ha="center", va="center", fontsize=9.5, color=MUTED)
    return fig, ax


def rect(ax, x, y, w, h, label, sub="", fill="white", edge=TEAL, size=10):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.2,rounding_size=1.5",
                                facecolor=fill,edgecolor=edge,linewidth=1.4,zorder=3))
    ax.text(x+w/2, y+h*(.73 if sub else .5), label, ha="center", va="center",
            fontsize=size, color=NAVY, weight="bold", zorder=4, linespacing=1.18)
    if sub:
        ax.text(x+w/2, y+h*.33, sub, ha="center", va="center", fontsize=8,
                color=MUTED,zorder=4,linespacing=1.15)


def line(ax, points, label=None, label_xy=None, arrow=False, color=MUTED, ls="-"):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color=color, lw=1.4, linestyle=ls, zorder=2)
    if arrow:
        p, q = points[-2:]
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=13,
                                     lw=1.4, color=color, zorder=2))
    if label:
        ax.text(*(label_xy or points[len(points)//2]), label, fontsize=8.2, color=INK,
                ha="center", va="center", zorder=5,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5))


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, facecolor="white", bbox_inches="tight", pad_inches=.12)
    plt.close(fig)
    print(name)


def entity(ax,x,y,w,h,name,rows):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.15,rounding_size=1",
                                fc="white",ec=NAVY,lw=1.4,zorder=3))
    ax.add_patch(Rectangle((x,y+h-4.5),w,4.5,fc=NAVY,ec=NAVY,zorder=4))
    ax.text(x+w/2,y+h-2.25,name,ha="center",va="center",fontsize=10,
            weight="bold",color="white",zorder=5)
    for i,row in enumerate(rows):
        ax.text(x+1.6,y+h-6.6-i*2.6,row,fontsize=8.5,color=INK,va="top",
                family="DejaVu Sans Mono",zorder=5)


def fig_erd():
    facts = schema_facts()
    expected = {
        ("categories", "department_id", "departments"), ("users", "department_id", "departments"),
        ("complaints", "student_id", "users"), ("complaints", "category_id", "categories"),
        ("complaints", "department_id", "departments"), ("complaint_events", "complaint_id", "complaints"),
        ("complaint_events", "actor_id", "users"), ("feedback", "complaint_id", "complaints"),
    }
    actual = {(t, col, spec["table"]) for t, f in facts.items() for col, spec in f["foreign_keys"].items()}
    if actual != expected or "complaint_id" not in facts["feedback"]["unique"]:
        raise ValueError(f"Schema relationships changed: {actual ^ expected}")
    fig,ax=canvas("Entity–relationship diagram", "Actual SQLite foreign keys · selected columns · cardinalities at each end", h=11)
    entity(ax,2,70,27,19,"departments",["PK id  INTEGER", "UQ name  TEXT", "head_name, email, location"])
    entity(ax,37,70,27,19,"categories",["PK id  INTEGER", "UQ name  TEXT", "FK department_id  NOT NULL", "default_priority, keywords"])
    entity(ax,72,70,26,19,"users",["PK id  INTEGER", "UQ username, roll_no", "FK department_id  NULL", "role, full_name, status"])
    entity(ax,36,36,29,24,"complaints",["PK id  INTEGER", "UQ code  TEXT", "FK student_id  NOT NULL", "FK category_id  NOT NULL", "FK department_id  NOT NULL", "priority, status, dates"])
    entity(ax,2,7,28,19,"feedback",["PK id  INTEGER", "FK/UQ complaint_id", "rating, comment, created_at"])
    entity(ax,72,7,26,19,"complaint_events",["PK id  INTEGER", "FK complaint_id  NOT NULL", "FK actor_id  NULL", "event_type, note, created_at"])
    line(ax,[(29,79.5),(37,79.5)],"1     0..*",(33,81.4))
    line(ax,[(17,89),(17,91),(85,91),(85,89)],"department: 0..1  |  users: 0..*",(50,91))
    line(ax,[(17,70),(17,48),(36,48)],"1 → 0..*",(25,49.5))
    line(ax,[(50,70),(50,60)],"1 → 0..*",(50,65))
    line(ax,[(85,70),(85,66),(68,66),(68,52),(65,52)],"1 → 0..*",(76.5,66))
    line(ax,[(98,80),(99.3,80),(99.3,18),(98,18)],"actor: 0..1\nevents: 0..*",(95,53))
    line(ax,[(36,42),(32.5,42),(32.5,17),(30,17)],"1 → 0..1",(32,29))
    line(ax,[(65,43),(69,43),(69,17),(72,17)],"1 → 0..*",(69,29))
    ax.text(50,2.4,"FK = foreign key; UQ = unique. Nullable FK: a user may have no department; an event may have no actor.\nA complaint stores category and assigned department separately; reassignment changes only its department.",
            ha="center",va="center",fontsize=8.3,color=MUTED)
    save(fig,"fig-erd.png")


def actor(ax,x,label):
    ax.add_patch(Circle((x,88.5),1.4,fc="white",ec=NAVY,lw=1.5))
    ax.plot([x,x],[87,83],color=NAVY,lw=1.5)
    ax.plot([x-2.2,x+2.2],[85.5,85.5],color=NAVY,lw=1.5)
    ax.plot([x,x-1.8],[83,80.5],color=NAVY,lw=1.5)
    ax.plot([x,x+1.8],[83,80.5],color=NAVY,lw=1.5)
    ax.text(x,91,label,ha="center",va="center",fontsize=10,weight="bold",color=NAVY)


def fig_usecase():
    fig,ax=canvas("Use-case diagram", "Actors are outside the system boundary; lines are associations", h=10)
    groups=[
        (13,"Student",["Register / sign in", "Lodge complaint", "View own complaints", "Confirm + feedback", "Reopen resolved"]),
        (38,"Officer",["Sign in", "View department queue", "Acknowledge", "Start work / resolve", "Add remark"]),
        (63,"Administrator",["Sign in / view console", "Reassign / escalate", "Force-close resolved", "Manage officers", "View / print reports"]),
        (87.2,"Public visitor",["Track by code\nAND roll number"]),
    ]
    ax.add_patch(Rectangle((1.5,8),97,66,fc=BG,ec=TEAL,lw=1.4,zorder=0))
    ax.text(50,71.7,"CAMPUS SHIKAYAT SETU",fontsize=10,color=TEAL,weight="bold",ha="center")
    for x,role,uses in groups:
        actor(ax,x,role)
        ys=[64-i*10.5 for i in range(len(uses))]
        side = x + 11.6 if x < 75 else x - 11.6
        end = x + 11 if x < 75 else x - 11
        line(ax,[(x,80.5),(x,75.5),(side,75.5),(side,ys[-1])],color="#a1b7b4")
        for y,label in zip(ys,uses):
            line(ax,[(side,y),(end,y)],color="#a1b7b4")
            ax.add_patch(Ellipse((x,y),22,7.3,fc="white",ec=NAVY,lw=1.1,zorder=3))
            ax.text(x,y,label,ha="center",va="center",fontsize=9,color=INK,zorder=4)
    ax.text(50,2.4,"The admin can also use officer complaint actions; authenticated users can change passwords.\nPublic tracking uses both fields; a signed-in admin may bypass the roll-number check.",ha="center",fontsize=8.4,color=MUTED)
    save(fig,"fig-usecase.png")


def fig_activity():
    fig,ax=canvas("Activity diagram — complaint lifecycle", "Application flow and allowed transitions (app.py)", h=9.5)
    ax.text(2,88,"SUBMISSION",fontsize=10,weight="bold",color=TEAL)
    steps=[(2,"Student enters\ncomplaint", "title, description, category"),
           (26,"Validate input", "invalid → return form"),
           (50,"Select category", "compare keyword scores"),
           (74,"Save complaint", "priority, SLA, code + events")]
    for x,a,b in steps: rect(ax,x,72,21,11,a,b,fill=BG,size=10)
    for x in (23,47,71): line(ax,[(x,77.5),(x+3,77.5)],arrow=True,color=TEAL)
    ax.text(50,67,"No stronger match → keep the selected category. Safety words / mass impact adjust priority.",ha="center",fontsize=9,color=MUTED)
    ax.text(2,59,"STATUS TRANSITIONS",fontsize=10,weight="bold",color=TEAL)
    states=[(2,"Submitted"),(22,"Acknowledged"),(42,"In Progress"),(62,"Resolved"),(82,"Closed")]
    for x,label in states: rect(ax,x,40,16,9,label,fill=PALE,size=10)
    for x in (18,38,58,78): line(ax,[(x,44.5),(x+4,44.5)],arrow=True,color=TEAL)
    ax.text(20,51,"acknowledge",ha="center",fontsize=8,color=MUTED)
    ax.text(40,51,"start work",ha="center",fontsize=8,color=MUTED)
    ax.text(60,51,"resolve",ha="center",fontsize=8,color=MUTED)
    ax.text(80,51,"feedback /\nadmin close",ha="center",fontsize=8,color=MUTED)
    line(ax,[(10,49),(10,56),(50,56),(50,49)],"start work",(31,56),arrow=True)
    line(ax,[(10,40),(10,34),(70,34),(70,40)],"resolve directly",(40,34),arrow=True)
    line(ax,[(30,40),(30,30),(70,30),(70,40)],"resolve directly",(51,30),arrow=True)
    line(ax,[(70,40),(70,22),(50,22),(50,40)],"student reopens",(60,22),arrow=True,color=ORANGE)
    ax.text(50,14,"Reopen: own resolved complaint, reason ≥ 10 chars; parsed resolution age in whole days must be ≤ 7.\nIf the timestamp cannot be parsed, the current code skips that age check.",ha="center",fontsize=8.6,color=MUTED)
    ax.text(50,5,"Officer/admin may resolve directly from Submitted or Acknowledged (remark ≥ 10 chars).\nAdmin force-close requires Resolved but does not enforce a waiting period.",ha="center",fontsize=8.6,color=MUTED)
    save(fig,"fig-activity.png")


def fig_class():
    fig,ax=canvas("Class diagram — conceptual data model", "Conceptual SQLite records and selected associations; see ERD for all foreign keys",h=10)
    entity(ax,2,64,27,22,"«record» User",["id, role, username", "password_hash, full_name", "roll_no, phone, status", "department_id  [FK]"])
    entity(ax,36,64,28,22,"«record» Complaint",["id, code, student_id [FK]", "category_id, department_id [FK]", "title, description, status", "priority, routing, sla_due_at"])
    entity(ax,71,64,27,22,"«record» Department",["id, name", "head_name, email, location"])
    entity(ax,2,31,27,22,"«record» Category",["id, name", "department_id [FK]", "default_priority, keywords"])
    entity(ax,36,31,28,22,"«record» ComplaintEvent",["id, complaint_id [FK]", "event_type, note", "actor_id [FK], created_at"])
    entity(ax,71,31,27,22,"«record» Feedback",["id, complaint_id [FK/UQ]", "rating, comment, created_at"])
    line(ax,[(29,75),(36,75)],"student_id",(32.5,77))
    line(ax,[(64,75),(71,75)],"department_id",(67.5,77))
    line(ax,[(36,68),(32,68),(32,42),(29,42)],"category_id",(32,56))
    line(ax,[(50,64),(50,53)],"complaint_id",(50,58.5))
    line(ax,[(64,69),(68,69),(68,42),(71,42)],"complaint_id",(68,56))
    rect(ax,3,5,44,17,"«module» app.py", "select_category() · lodge() · resolve()\nfeedback() · reopen() · log_event()",fill=BG,size=10)
    rect(ax,53,5,44,17,"«module» routing.py", "score_category() · route() · assign_priority()\nroute_text() · SLA_HOURS",fill=BG,size=10)
    line(ax,[(47,13.5),(53,13.5)],"uses",(50,16),arrow=True)
    save(fig,"fig-class.png")


def fig_architecture():
    fig,ax=canvas("Application architecture", "Local Flask / SQLite application, with server-rendered pages", h=7)
    rect(ax,5,42,24,24,"Browser", "HTML forms + local CSS/JS\noptional routing preview",fill=BG,size=12)
    rect(ax,38,42,25,24,"Flask application", "app.py + Jinja templates\nrouting.py · database.py",fill=PALE,size=12)
    rect(ax,72,42,23,24,"SQLite database", "schema.sql → local DB file\nforeign keys enabled",fill=BG,size=12)
    line(ax,[(29,54),(38,54)],"HTTP",(33.5,58),arrow=True,color=TEAL)
    line(ax,[(63,54),(72,54)],"sqlite3",(67.5,58),arrow=True,color=TEAL)
    ax.text(50,23,"run.py initialises / seeds the database, then starts Flask on port 5001.\nJavaScript enhances the interface; server routes validate and enforce access.",ha="center",fontsize=10,color=MUTED)
    save(fig,"fig-architecture.png")


def fig_deployment():
    fig,ax=canvas("Deployment diagram — local demo", "Default configuration; not a production deployment",h=7)
    rect(ax,4,35,26,35,"«device» Browser", "Same computer or LAN client\nhttp://<server>:5001",fill=BG,size=12)
    rect(ax,41,29,54,45,"«device» Demo computer", "run.py / Flask development server\n0.0.0.0:5001 · app templates + static files\nSQLite file: app/shikayat_setu.db",fill=PALE,size=12)
    line(ax,[(30,52.5),(41,52.5)],"HTTP",(35.5,57),arrow=True,color=TEAL)
    ax.text(50,15,"Localhost address: http://127.0.0.1:5001. LAN access depends on network/firewall settings.\nNo external DB server or background worker is part of this demo.",ha="center",fontsize=10,color=MUTED)
    save(fig,"fig-deployment.png")


def fig_modules():
    fig,ax=canvas("Module hierarchy — actual project files", "Logical route groups live in app.py; no Flask blueprints are declared",h=8.5)
    rect(ax,37,75,26,10,"run.py", "initialise, seed, launch",fill=PALE,size=11)
    blocks=[(3,"app/app.py","Flask routes + helpers\nauth · complaints · queue\nconsole · users · reports"),
            (28,"app/routing.py","keyword scoring\npriority rules + SLA hours"),
            (53,"app/database.py","SQLite connection\nschema setup + demo seed"),
            (78,"app/templates/\napp/static/","Jinja HTML templates\nCSS + vanilla JavaScript")]
    for x,title,sub in blocks:
        rect(ax,x,37,19,23,title,sub,fill=BG,size=9.5)
        line(ax,[(50,75),(50,68),(x+9.5,68),(x+9.5,60)],color="#8da8a4")
    ax.text(50,20,"run.py imports app.py and database.py; database.py reads app/schema.sql. app.py imports routing.py;\nFlask renders templates and serves static assets. tests/ exercises the application.",ha="center",fontsize=9.5,color=MUTED)
    save(fig,"fig-modules.png")


# Existing schedule chart, kept separate from the application diagrams.
GOLD, NAVY2, GREEN, RED, GREY = "#c9a227", "#2b4a73", "#1e7a46", "#b3372e", "#6b7280"
def fig_gantt():
    import matplotlib.dates as mdates
    from datetime import date as _date
    tasks = [
        ("Reference audit & requirements", _date(2026, 9, 21), _date(2026, 10, 2), GOLD),
        ("Schema + seed + design docs",    _date(2026, 10, 1), _date(2026, 10, 9), NAVY2),
        ("Routing / SLA engine",           _date(2026, 10, 6), _date(2026, 10, 12), NAVY2),
        ("Core flows (lodge→close)",       _date(2026, 10, 8), _date(2026, 10, 22), NAVY),
        ("Admin console + reports",        _date(2026, 10, 15), _date(2026, 10, 28), NAVY),
        ("Testing (12 pytest + 8 manual)", _date(2026, 10, 20), _date(2026, 11, 8), GREEN),
        ("Report & deck (this document)",  _date(2026, 10, 26), _date(2026, 11, 14), "#8a6d1a"),
    ]
    milestones = [("R1\n10-Oct", _date(2026, 10, 10)), ("R2\n24-Oct", _date(2026, 10, 24)),
                  ("R3\n21-Nov", _date(2026, 11, 21)), ("R4\n05-Dec", _date(2026, 12, 5)),
                  ("FINAL\n19-Dec", _date(2026, 12, 19))]
    fig, ax = plt.subplots(figsize=(13.2, 5.8), dpi=160)
    ypos = list(range(len(tasks)))[::-1]
    for (name, s, e, color), y in zip(tasks, ypos):
        ax.barh(y, (e - s).days, left=mdates.date2num(s), height=0.6, color=color, zorder=3)
    ax.set_yticks(ypos)
    ax.set_yticklabels([t[0] for t in tasks], fontsize=7.6, color="#222")
    ax.set_ylim(-0.55, len(tasks) - 0.45)
    for lab, d in milestones:
        x = mdates.date2num(d)
        ax.axvline(x, color=RED, lw=1.3, ls="--", alpha=0.8, zorder=2)
        ax.annotate(lab, xy=(x, len(tasks) - 0.45), xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=6.6, fontweight="bold", color=RED, linespacing=1.1)
    ax.set_xlim(mdates.date2num(_date(2026, 9, 20)), mdates.date2num(_date(2026, 12, 23)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
    ax.grid(axis="x", ls=":", lw=0.6, color="#c9c7bd", zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_title("Project timeline & review milestones (notified 30-09-2026)",
                 fontsize=10.5, fontweight="bold", color=NAVY, pad=30)
    fig.savefig(f"{OUT}/fig-gantt.png", bbox_inches="tight"); plt.close(fig)
    print("fig-gantt.png")


if __name__ == "__main__":
    fig_architecture(); fig_erd(); fig_usecase(); fig_activity(); fig_class()
    fig_deployment(); fig_modules()

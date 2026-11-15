"""Legacy schedule-chart generator, separate from editable app diagrams.

Run with --schedule only when deliberately refreshing fig-gantt.png. For app
diagrams, use build_drawio.py and diagrams.net instead.
"""
from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "images"
NAVY = "#172b3a"

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
    if sys.argv[1:] == ["--schedule"]:
        fig_gantt()
    else:
        print("Application diagrams: run report/build_drawio.py; see report/DIAGRAMS.md.")

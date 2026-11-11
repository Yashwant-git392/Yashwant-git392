# Campus Shikayat Setu
**College Grievance Redressal System** — turn the college's complaint box into a trackable, SLA-bound digital pipeline.

**SPPU MCA-I (Sem-I) Application Development — mini project**
Dr. B.V. Hiray College of Management and Research Centre, Malegaon (Nashik) · AY 2026-27

**Creator: Yashwant Santosh Ahire** · Guide: Mrs. Priyanka M. Jagtap

---

## The problem
Students report broken benches, leaking taps, dead projectors and missing marks — and hear nothing back for weeks. The complaint box is a black hole: no routing, no accountability, no memory, no analytics. This system gives every complaint a code, a department, an SLA deadline and an audit trail.

## What it does
- **Complaint lifecycle** — Submitted → Acknowledged → In Progress → Resolved → Closed, with a full event timeline.
- **Automatic routing** — keyword-weighted engine assigns each complaint to the right department (multi-word keywords weigh more; title counts double). Falls back to General & Administration when nothing matches.
- **SLA engine** — High 24 h · Medium 72 h · Low 7 days, deadline stamped at submission; safety words (ragging, shock, fire…) force High; mass-impact phrases ("entire", "all students"…) bump one level.
- **Three roles** — Student (lodge / track / feedback / reopen), Department Officer (queue, acknowledge, progress, resolve), Admin (console, reassign, escalate, reports, user management).
- **Anonymous mode** — identity withheld from departments; visible only to administrators.
- **Reopen & feedback** — a student can reject a resolution within 7 days; ratings feed the department scorecard.
- **6 print-ready registers** — Department Pendency · SLA Compliance · Resolution Time · Monthly Trend · Feedback Summary · Routing Audit.
- **Public tracker** — code + roll number, no login required.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python run.py                                       # http://127.0.0.1:5001
```
First run auto-creates and seeds `app/shikayat_setu.db`.

**Demo accounts**
| Role | Credentials |
|---|---|
| Admin | `admin` / `admin123` |
| Officer (any dept) | `hostel.officer` / `it.officer` / `maint.officer` / `exam.officer` / `welfare.officer` / `admin.officer` — all `officer123` |
| Student | `MCA2026001` … `MCA2026008` — all `student123` |

## Tests
```bash
python -m pytest tests/ -q     # 12 passed
```
Covers auth, role scoping (students can't open the admin console; officers can't see other departments), routing (`leak` → Sanitation), safety-word priority escalation, and the full lodge→acknowledge→resolve→feedback→closed cycle.

## Layout
```
shikayat-setu/
├── run.py                 # launcher → :5001
├── requirements.txt
└── app/
    ├── app.py             # Flask routes (auth, lodge, queue, console, reports)
    ├── database.py        # schema init + deterministic seed (6 depts, 15 categories, 32 complaints)
    ├── routing.py         # keyword router + SLA matrix
    ├── schema.sql
    ├── static/css/style.css
    └── templates/         # Jinja2, navy/gold theme
└── tests/test_app.py
```

## Engineering notes
- Flask 3 + SQLite (WAL off, file-based) — zero-configuration; maps 1:1 to MySQL 8 for production.
- Passwords: Werkzeug PBKDF2 hashing. Availability: `available` stock-style recomputation is not needed; SLA state is computed at render time (deterministic demo, no cron).
- Seed is date-offset relative to today so the demo always shows a live semester.
- `app/shikayat_setu.db` is gitignored — delete it and restart to re-seed.

## Roadmap
SMS/e-mail alerts · photo evidence upload · WhatsApp deep-links · multi-branch rollout · grievance analytics public dashboard.

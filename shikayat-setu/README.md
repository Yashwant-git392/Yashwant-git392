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

## Deliverables (this folder)
| Artefact | Path |
|---|---|
| Mini project report (27 pp, PDF) | `report/CampusShikayatSetu_MCA-Mini-Project_Report.pdf` |
| Report generator (build twice for TOC page map) | `report/build_report.py` |
| Diagram + screen generators | `report/gen_diagrams.py` · `report/gen_screens.py` |
| Review deck (16 slides) | `presentation/CampusShikayatSetu_MCA-Mini-Project_Review.pptx` |

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
├── report/            # report PDF + generators + images/
├── presentation/      # review deck (.pptx) + build_pptx.py
└── tests/test_app.py
```

## Engineering notes
- Flask 3 + SQLite (WAL off, file-based) — zero-configuration; maps 1:1 to MySQL 8 for production.
- Passwords: Werkzeug PBKDF2 hashing. Availability: `available` stock-style recomputation is not needed; SLA state is computed at render time (deterministic demo, no cron).
- Seed is date-offset relative to today so the demo always shows a live semester.
- `app/shikayat_setu.db` is gitignored — delete it and restart to re-seed.

## Roadmap
SMS/e-mail alerts · photo evidence upload · WhatsApp deep-links · multi-branch rollout · grievance analytics public dashboard.

---

## Design: deliberately simple, and the right database

**Why this is intentionally low-complexity** — the SPPU Sem-I bar is *working software a reviewer can understand*, not architecture theatre.
- **No ORM, no frameworks beyond Flask.** Plain `sqlite3` + SQL you can show in the viva. ~1,750 lines total including templates and tests; single `app.py` (~450 lines of routes), one small `routing.py` (~60 lines) for the keyword/SLA logic.
- **No background jobs, no message queues, no cache.** SLA and overdue state are computed at render time — deterministic, always demo-able.
- **No microservices, no API layer, no JS build step.** Server-rendered Jinja; progressive-enhancement-free; works with JS disabled.
- **Seeded demo** covers every screen — no live internet dependency during review.

**Use cases → database fit**
| Requirement (real use case) | Choice | Why |
|---|---|---|
| Single college campus, ≤ ~2,000 students, ~35 complaints/day peak | **SQLite** (file-based) | Zero server, zero config, zero admin; backup = copy one file; handles this load trivially in WAL-free mode |
| Structured relational data (complaints ↔ users ↔ departments ↔ feedback) with real FK constraints & CHECK rules | **Relational** (SQL) | Wrong shape for MongoDB — you need joins, transactions and referential integrity, not documents |
| Read-mostly workload with tiny write bursts (a lodge every few minutes) | **SQLite** | No concurrent-writer contention worth worrying about; pragma `foreign_keys=ON` gives ACID |
| Demo must run on the library PC with no DBA | **SQLite** | `python run.py` is the whole deployment |
| Production (multi-department, 10k+ users, HA) | **MySQL 8** | Schema ports 1:1 (only `AUTOINCREMENT`→`AUTO_INCREMENT`, `datetime('now','localtime')`→`CURRENT_TIMESTAMP`), same routing.py, connection string swap in `database.py` |
| Not chosen: MongoDB / PostgreSQL / Firebase | — | Document DB fits unstructured logs, not FK-rich grievance data; Postgres/Firebase add ops cost with zero benefit at this scale; "modern stack" adds no marks in a Sem-I viva |

**Verdict for this project: SQLite now (correct for the use case), MySQL 8 as the documented 1:1 production path — the schema was written to be portable.**

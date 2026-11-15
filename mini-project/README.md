# SmartLibrary — College Library Management System

**SPPU MCA-I · Semester-I · Application Development — Mini Project (2026-27)**
Dr. B.V. Hiray College of Management and Research Centre, Malegaon (Nashik)

SmartLibrary replaces the paper-based issue register of a college library with a small,
self-hosted web application: a searchable book catalogue, student/faculty membership,
the college's real circulation rules (3-book limit · 14-day loan · **₹2/day** fine ·
inactive-member block), and five print-ready registers (issued / overdue / fine history /
stock / member activity). Built with Python + Flask + SQLite — no build step, no licence fees.

> 🎬 The system is intentionally "boring in the right ways": server-side rendering,
> explicit SQL, FK constraints, seeded demo data, and a documented runbook — boring
> software runs on the library PC every single day.

## Quick start

```bash
git clone https://github.com/Yashwant-git392/Yashwant-git392.git
cd Yashwant-git392/mini-project

pip install -r requirements.txt     # Flask >= 3.0
python run.py                       # → http://127.0.0.1:5000
```

Sign in with **`admin` / `admin123`** (change it immediately via **Change Password**).

The SQLite database (`app/smartlibrary.db`) is created and seeded automatically on first
run: **12 books · 8 members · 15 transactions** — every report therefore shows ≥ 5 valid
records out of the box.

## Tests

```bash
python -m pytest tests/test_app.py -v    # 12/12 pass
```

## Layout

```
mini-project/
├── run.py                  # convenience launcher (http://127.0.0.1:5000)
├── requirements.txt        # Flask >= 3.0
├── app/
│   ├── app.py              # ~700 lines — routes, auth, circulation engine, reports
│   ├── database.py         # schema init + deterministic seed (availability derived, never hand-set)
│   ├── schema.sql          # DDL — see report/SmartLibrary_MCA-Mini-Project_Report.pdf, Appendix A
│   ├── templates/          # 16 Jinja templates (base.html + one per screen)
│   └── static/             # css + vanilla JS (client-side validation mirroring server rules)
└── tests/
    └── test_app.py         # 12 integration tests against an isolated temp database
```

## Screens & business rules

| Rule | Value |
|------|-------|
| Books a member may hold | 3 |
| Loan period | 14 days |
| Fine | ₹2 per day overdue |
| Inactive members | cannot borrow |
| Delete protection | blocked while copies are issued / member holds books |
| Passwords | PBKDF2 (Werkzeug); legacy SHA-256 seed hashes upgraded on first change |

The full user manual (per-screen validation tables, FAQ) is **Chapter 10** of the project
report; the report itself lives at [`../report/SmartLibrary_MCA-Mini-Project_Report.pdf`](../report/SmartLibrary_MCA-Mini-Project_Report.pdf).

## Reviews & deliverables

| Review (2026-27) | Date | Artefact |
|------------------|------|----------|
| Review 1 | — | SRS + feasibility (report, Ch. 2) |
| Review 2 | — | ERD · UML use-case/class/activity/deployment · module hierarchy (report, Ch. 3) |
| Review 3 | 21 Nov 2026 | Working app + automated/manual test evidence (report, Ch. 5) |
| Review 4 / Final | 19 Dec 2026 | Presentation + hard-bound report |

*Yashwant Santosh Ahire · Guide: Mrs. Priyanka M. Jagtap · A.Y. 2026-27*

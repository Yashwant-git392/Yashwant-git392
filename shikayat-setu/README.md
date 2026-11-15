# Campus Shikayat Setu

Campus Shikayat Setu is a college grievance management mini project for SPPU MCA-I (Semester I). Students can submit and track complaints, department officers can work on them, and administrators can manage assignments and reports.

- **Creator:** Yashwant Santosh Ahire
- **College:** Dr. B.V. Hiray College of Management and Research Centre, Malegaon (Nashik)
- **Academic year:** 2026–27

## Features

- Submit complaints, track their status and view their event history.
- Route complaints using keywords; when no keyword matches, the selected category is retained.
- Assign priority and a service deadline; safety words raise priority to High.
- Allow students to give feedback or reopen a resolved complaint.
- Provide department queues, an admin console and six printable reports.
- Track a complaint without signing in using its code and roll number.
- Hide the student's identity fields and event actor from officers for anonymous complaints; administrators can see them. Free text may still identify the student.
- Use a responsive interface with a theme toggle, table filters and routing preview.

## Run locally

Python 3 is required. From this directory:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5001. The application creates and seeds `app/shikayat_setu.db` on first run. This database is ignored by Git; deleting it resets the local demo data on the next run.

### Demo accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Officer | `hostel.officer`, `it.officer`, `maint.officer`, `exam.officer`, `welfare.officer` or `admin.officer` | `officer123` |
| Student | `MCA2026001` to `MCA2026008` | `student123` |

These credentials and the development secret key are for the local demo only. Do not use this configuration for a public deployment. The admin force-close action checks for Resolved status but does not enforce a seven-day waiting period; treat this as a known limitation.

## Tests

```bash
python -m pytest tests/ -q
```

The tests use temporary databases and cover login, registration, routing and its preview, access control, the complaint lifecycle and reports.

## Project files

- `run.py` — application launcher.
- `app/app.py` — Flask routes and request handling.
- `app/database.py` and `app/schema.sql` — database setup and sample data.
- `app/routing.py` — keyword scoring, priority and SLA rules.
- `app/templates/` and `app/static/` — page templates, CSS and JavaScript.
- `tests/` — automated tests.
- `report/` — PDF report, diagrams, application screenshots and generators.
- `presentation/` — review slides and their generator.

The app uses Flask, SQLite, Jinja templates and vanilla JavaScript. The report and presentation contain screenshots from a fresh seeded demo database. Screenshots show the visible browser viewport; data and dates can differ after a reset. The report and slide generators require additional libraries (`fpdf2`, `matplotlib`, `numpy`, `Pillow` and `python-pptx`); the PDF generator also uses DejaVu fonts from `/usr/share/fonts/truetype/dejavu/`. Initialize the demo database before rebuilding the report. To recapture the screenshots, install Playwright and Chromium (`pip install playwright` and `python -m playwright install chromium`), then run `python report/capture_screens.py`. The capture script uses a temporary database and does not alter local demo data.

## Possible extensions

Email or SMS notifications, photo attachments, category management and deployment with a production database are possible future additions. SQLite is suitable for this local demonstration; moving to another database would require changes and testing rather than only a connection-string swap.

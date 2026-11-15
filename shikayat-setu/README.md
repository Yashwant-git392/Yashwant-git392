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

Demo credentials and the fallback secret key are for local use only. POST forms (including sign-out) use Flask-WTF CSRF tokens. The application uses a request-scoped SQLite connection and rolls back uncommitted work on teardown. To configure a stable secret and port, set environment variables before running `python run.py`:

```bash
export SHIKAYAT_SECRET_KEY="replace-with-a-strong-private-random-value"
export SHIKAYAT_PORT=5001
```

On Windows PowerShell use `$env:SHIKAYAT_SECRET_KEY = "..."` and `$env:SHIKAYAT_PORT = "5001"`. Changing the secret invalidates existing signed sessions and CSRF tokens; keep it private and stable across app workers. Never commit a real secret. If it is not set, startup warns and uses an insecure demo fallback. This remains a development server, not a production deployment; HTTPS, stronger credentials, rate limiting, secure session handling and a security review are still needed. The admin force-close action checks for Resolved status but does not enforce a seven-day waiting period; treat this as a known limitation.

## Tests

```bash
python -m pytest tests/ -q
```

The tests use temporary databases and cover login, registration, CSRF rejection, connection rollback, routing and its preview, access control, the complaint lifecycle and reports. Invalid or missing resolution timestamps now prevent reopening; valid timestamps still use the existing whole-day age rule.

## Project files

- `run.py` — application launcher.
- `app/app.py` — Flask routes and request handling.
- `app/database.py` and `app/schema.sql` — database setup and sample data.
- `app/routing.py` — keyword scoring, priority and SLA rules.
- `app/templates/` and `app/static/` — page templates, CSS and JavaScript.
- `tests/` — automated tests.
- `report/` — PDF report, diagrams, application screenshots and generators. See `report/diagrams/` for editable diagrams.net files and `report/DIAGRAMS.md` for provenance, editing and traceability.
- `presentation/` — review slides and their generator.
- `study/` — deep project breakdown and viva Q&A in PDF, editable DOCX and Markdown; includes a five-minute demo plan and known limitations.

The app uses Flask, SQLite, Jinja templates and vanilla JavaScript. The report and presentation contain screenshots from a fresh seeded demo database. Screenshots show the visible browser viewport; data and dates can differ after a reset. The report and slide generators require additional libraries (`fpdf2`, `matplotlib`, `numpy`, `Pillow` and `python-pptx`); the PDF generator also uses DejaVu fonts from `/usr/share/fonts/truetype/dejavu/`. Initialize the demo database before rebuilding the report. To recapture the screenshots, install Playwright and Chromium (`pip install playwright` and `python -m playwright install chromium`), then run `python report/capture_screens.py`. The capture script uses a temporary database and does not alter local demo data.

## Possible extensions

Email or SMS notifications, photo attachments, category management and deployment with a production database are possible future additions. SQLite is suitable for this local demonstration; moving to another database would require changes and testing rather than only a connection-string swap.

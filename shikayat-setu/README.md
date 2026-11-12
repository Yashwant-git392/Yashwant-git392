# Campus Shikayat Setu

Campus Shikayat Setu is a college grievance management mini project for SPPU MCA-I (Semester I). Students can submit and track complaints, department officers can work on them, and administrators can manage assignments and reports.

- **Creator:** Yashwant Santosh Ahire
- **College:** Dr. B.V. Hiray College of Management and Research Centre, Malegaon (Nashik)
- **Academic year:** 2026–27

## Features

- Submit complaints, track their status and view their event history.
- Route complaints to departments using keywords, with a general category as fallback.
- Assign priority and a service deadline; safety words raise priority to High.
- Allow students to give feedback or reopen a resolved complaint.
- Provide department queues, an admin console and six printable reports.
- Track a complaint without signing in using its code and roll number.
- Hide the student's identity from department officers for anonymous complaints; administrators can see it.
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

These credentials and the development secret key are for the local demo only. Do not use this configuration for a public deployment.

## Tests

```bash
python -m pytest tests/ -q
```

The tests use temporary databases and cover login, registration, routing, access control, the complaint lifecycle and reports.

## Project files

- `run.py` — application launcher.
- `app/app.py` — Flask routes and request handling.
- `app/database.py` and `app/schema.sql` — database setup and sample data.
- `app/routing.py` — keyword scoring, priority and SLA rules.
- `app/templates/` and `app/static/` — page templates, CSS and JavaScript.
- `tests/` — automated tests.
- `report/` — PDF report, diagrams, illustrative screen mock-ups and generators.
- `presentation/` — review slides and their generator.

The app uses Flask, SQLite, Jinja templates and vanilla JavaScript. The report's screen images are illustrations, not screenshots of the running application. The report and slide generators require additional libraries (`fpdf2`, `matplotlib`, `numpy`, `Pillow` and `python-pptx`); the PDF generator also uses DejaVu fonts from `/usr/share/fonts/truetype/dejavu/`. Initialize the demo database before rebuilding the report or screen mock-ups.

## Possible extensions

Email or SMS notifications, photo attachments, category management and deployment with a production database are possible future additions. SQLite is suitable for this local demonstration; moving to another database would require changes and testing rather than only a connection-string swap.

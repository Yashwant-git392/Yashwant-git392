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

## Easy start in VS Code

You need **Python 3.10 or newer** (Python 3.11 or 3.12 recommended). Install it from [python.org](https://www.python.org/downloads/). On Windows, select **Add Python to PATH** during installation. The first setup generally needs internet to install the packages; later launches reuse the local environment and normally work offline.

1. Download and **extract** the project ZIP, or clone the repository. Do not run the app from inside the ZIP viewer.
2. In VS Code choose **File → Open Folder** and select the `shikayat-setu` folder itself (the folder containing `run.py` and `Start_Project.bat`).
3. Choose **Terminal → Run Task → Start Campus Shikayat Setu**. On the first run it creates `.venv` and installs the requirements. Wait until the terminal says it is running.
4. Open **http://127.0.0.1:5001** on the same computer. Leave the terminal open while using the app. Press **Ctrl+C** in that terminal to stop it.

Alternatively, on Windows double-click `Start_Project.bat` in the extracted project folder, or run `.\Start_Project.bat` in the VS Code terminal. On macOS/Linux run `./start-project.sh` in the VS Code terminal; if your ZIP extractor does not preserve its executable bit, use `sh start-project.sh`. The cross-platform alternative is `python start_project.py` (or `python3 start_project.py`). No manual activation is required. Existing `.venv` and the database are never automatically deleted or reset by the launcher.

VS Code's optional Python extension will find the project environment via `.vscode/settings.json`. After first setup, if the extension still shows another interpreter, open **Python: Select Interpreter** and choose `.venv` (`.venv\Scripts\python.exe` on Windows; `.venv/bin/python` on macOS/Linux). Open a new terminal if needed. The shared VS Code task requires opening `shikayat-setu` itself as the workspace folder.

### Troubleshooting

- **Python not found:** install Python, restart VS Code, and check `py -3 --version` or `python --version` on Windows; `python3 --version` on macOS/Linux. If `py` is unavailable the Windows launcher tries `python`.
- **Installation failed:** check the internet connection and the terminal's pip error, then retry. On Debian/Ubuntu, install the OS package matching your Python, such as `python3-venv`, if venv creation fails. If a partial or copied `.venv` is broken, close the app, rename the **`.venv` folder only**, then rerun the launcher. Keep the database safe; renaming `.venv` does not reset it.
- **Address already in use:** stop the existing app first. To use another port in PowerShell run `$env:SHIKAYAT_PORT = "5002"` before the launcher; in a Unix shell run `SHIKAYAT_PORT=5002 ./start-project.sh`, then open the indicated address. Do not run two copies against the same database unnecessarily.
- **VS Code task not listed:** use **File → Open Folder** on `shikayat-setu` rather than only opening a file; then run the task again. The launcher scripts can also be run directly as above.

Open http://127.0.0.1:5001 by default. The application creates and seeds `app/shikayat_setu.db` only on first run. This database is ignored by Git. Existing databases are not changed by seed updates; to inspect the refreshed demo safely, set `SHIKAYAT_DB` to a new file instead of deleting your data. A prebuilt `.venv` is deliberately not shipped: environments contain machine- and OS-specific paths and binaries, so copying one often causes precisely the errors this launcher avoids.

### Manual setup (optional)

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1 (may require execution-policy permission)
# Windows Command Prompt: .venv\Scripts\activate.bat
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

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

On Windows PowerShell use `$env:SHIKAYAT_SECRET_KEY = "..."` and `$env:SHIKAYAT_PORT = "5001"`. Changing the secret invalidates existing signed sessions and CSRF tokens; keep it private and stable across app workers. Never commit a real secret. If it is not set, startup warns and uses an insecure demo fallback. This remains a development server, not a production deployment; HTTPS, stronger credentials, rate limiting, secure session handling and a security review are still needed. Inactive or deleted accounts lose access on their next request, but copied session cookies could become usable after reactivation; stronger session revocation is needed for production. The admin force-close action checks for Resolved status but does not enforce a seven-day waiting period; treat this as a known limitation.

## Tests

```bash
python -m pytest tests/ -q
```

The tests use temporary databases and cover the full allowed/blocked transition matrix, role and ownership permissions, seeded report data and calculations, simultaneous submissions, and login, registration, CSRF rejection, connection rollback, routing and its preview, access control, inactive-account sessions, safe login redirects, the complaint lifecycle and report edge cases. The fresh seed contains 37 illustrative complaints, including five clearly labelled synthetic historical cases so the trend, feedback and manual-routing views have representative rows. The routing summary has two modes (automatic and manual); a separate complaint-level routing table contains at least five seeded records, with a further manual detail list. Historical timestamps are relative to the seeding date. See `TESTING.md` for the scope and limits of the in-depth test. Diagram consistency checks ignore Windows/Linux line-ending differences while still checking the generated contents. Invalid or missing resolution timestamps now prevent reopening; valid timestamps still use the existing whole-day age rule.

## Project files

- `START_HERE.txt` — short step-by-step launch instructions.
- `Start_Project.bat`, `start-project.sh`, `start_project.py` and `.vscode/` — easy setup and launch for Windows, macOS/Linux and VS Code.
- `run.py` — application server launcher.
- `app/app.py` — Flask routes and request handling.
- `app/database.py` and `app/schema.sql` — database setup and sample data.
- `app/routing.py` — keyword scoring, priority and SLA rules.
- `app/templates/` and `app/static/` — page templates, CSS and JavaScript.
- `tests/` — automated tests.
- `REVIEW_3_CHECKLIST.md` — evidence and remaining personal/guide checks for the third review.
- `report/` — project report and use-case diagrams in PDF and DOCX, screenshots and generators. See `report/REPORT_FORMAT.md` for format, Word page-field updates, semester/binding questions, font fallback and rebuilding instructions. See `report/diagrams/` for editable diagrams.net files and `report/DIAGRAMS.md` for provenance, editing and traceability. `report/diagrams/fig-usecase.drawio` contains four actor-specific pages.
- `presentation/` — review slides and their generator.
- `study/` — deep project breakdown and viva Q&A in PDF, editable DOCX and Markdown; includes a five-minute demo plan and known limitations.

The app uses Flask, SQLite, Jinja templates and vanilla JavaScript. The report and presentation contain screenshots from a fresh seeded demo database. Screenshots show the visible browser viewport; data and dates can differ after a reset. See `report/REPORT_FORMAT.md` and `report/requirements-report.txt` for report regeneration and font details. The slide generator requires additional libraries (`matplotlib`, `numpy`, `Pillow` and `python-pptx`). Initialize a disposable demo database before rebuilding the report; set `SHIKAYAT_DB` to that file when running the report builder so it reads that database without modifying your existing data. To recapture the screenshots, install Playwright and Chromium (`pip install playwright` and `python -m playwright install chromium`), then run `python report/capture_screens.py`. The capture script uses a temporary database and does not alter local demo data.

## Possible extensions

Email or SMS notifications, photo attachments, category management and deployment with a production database are possible future additions. SQLite is suitable for this local demonstration; moving to another database would require changes and testing rather than only a connection-string swap.

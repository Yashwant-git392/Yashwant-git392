# In-depth testing — Campus Shikayat Setu

## Scope and results

Testing used disposable SQLite databases; the existing local application database was not reset or modified.

| Area | Checks performed |
|---|---|
| Automated suite | `python -m pytest tests/ -q`: **114 passed** in the source checkout. Tests include the previous regression suite, diagram tests and `tests/test_in_depth.py`. |
| Access and security | Student/officer/admin page matrix, ownership and department restrictions, CSRF on mutating routes, invalid credentials, deactivation, local redirects, HTML escaping and representative SQL-injection inputs. |
| Workflow | Allowed and blocked acknowledgement, progress, resolution and force-close transitions for all five statuses; feedback and reopen validation; reassignment and escalation; password changes; full registration-to-closure and reopen cycle. |
| Concurrency | Small simultaneous-request tests for six complaint submissions, four duplicate registrations, four duplicate officer creations, and repeated lifecycle transitions. The tests check unique records and single transition events; this is **not** load or stress testing. |
| Routing and database | Keyword boundary, priority and SLA checks; preview/submission agreement; fresh-seed routing consistency; seed idempotence; SQLite integrity and foreign-key checks; rollback tests. |
| Reports | All six reports, a controlled dataset with expected totals and averages, routing detail rows and empty state, escaped titles, reopened items, empty departments, and fresh-seed row coverage. Monthly trend groups by **submission** month and shows the current status of those complaints. |
| Launcher | Five isolated tests cover first setup, reuse, requirements changes, failed install, broken environments, repair and environment-variable isolation. A separate real Linux first launch and offline restart were checked in a path containing spaces; existing disposable database data was preserved. Native Windows batch and VS Code task execution were not tested. |
| Browser | Chromium on Linux, 169 page visits across 320, 390, 768, 1366 and 1920 pixel widths. Registration, student/officer/admin workflows, public tracking, filtering, theme persistence, password visibility, mobile navigation and six A4 PDF renders were checked. No JavaScript errors, unexpected server errors, horizontal page overflow, or external requests were observed in that run. |
| Print | Six seeded reports rendered to A4 PDFs. The revised routing report spans two A4 pages in the seeded run, with repeating headers and all 37 distinct complaint codes. Extracted text was checked for the final column headings, and the widest report was visually inspected. Actual printers and other browsers were not tested. |
| Diagrams and delivery | Diagram XML regeneration, schema relationships, four separate editable actor pages and Windows-style CRLF comparison were tested. The rebuilt ZIP was checked for integrity and tested after extraction. This is not a native Windows execution. |

A fresh seed contains 37 illustrative complaints and 11 feedback entries. Five labelled `Demo case` records use synthetic historical dates relative to the seed date, providing at least five trend rows and feedback departments. The routing summary has exactly two modes; its separate complaint-level table contains 37 seeded records and its manual-detail list has at least five examples. An empty or small real database may have fewer than five records. Existing databases are **not** updated automatically.

## Run automated tests

```bash
cd shikayat-setu
python -m pip install -r requirements.txt
python -m pytest tests/ -q
```

## Optional browser smoke test

`tests/browser_smoke.js` needs Node.js, `puppeteer-core` and a compatible local Chromium/Chrome executable. These are test-only dependencies, not app runtime dependencies. It **registers a student, creates and resolves a complaint, and changes data**. Run it only against a fresh disposable database. For example, in two Linux/macOS terminals:

```bash
# Terminal 1, from shikayat-setu: choose a NEW disposable path
SHIKAYAT_DB=/tmp/shikayat-browser-demo.db SHIKAYAT_PORT=5014 \
  SHIKAYAT_SECRET_KEY=temporary-test-secret python run.py
```

```bash
# Terminal 2; install puppeteer-core in your chosen test environment first
CHROMIUM_EXECUTABLE_PATH=/path/to/chromium \
  SHIKAYAT_DISPOSABLE_DB_CONFIRMED=1 node tests/browser_smoke.js
```

Set `SHIKAYAT_TEST_URL` for a different address. The default test roll is `MCA2026996`; use a new database on each run or set `SHIKAYAT_TEST_ROLL` to an unused valid demo roll. On serverless Chromium builds, the script also supports `CHROMIUM_SERVERLESS=1` with `@sparticuz/chromium` installed. Stop the test server afterward. On Windows, set environment variables in PowerShell and choose a new temporary database path appropriate for Windows.

## Known limits and follow-up

- This is a mini-project/local demo, not a production security audit. Demo passwords and the fallback secret must be replaced; HTTPS, rate limiting, secure deployment, backup/recovery and stronger session revocation remain necessary.
- Public tracking relies on a complaint code and roll number, which are not strong secrets. Anonymous free text can reveal identity. No email or SMS notification is implemented.
- The reopen rule uses whole-day age rather than an exact 168-hour cutoff; admin force-close does not enforce a waiting period. Escalation does not recalculate the stored SLA deadline.
- Status transitions have conditional checks for the observed status, department and resolution timestamp, but small concurrency tests do not establish correctness under all races or high load. SQLite and the Flask development server are not production capacity choices.
- Testing was on Linux with Chromium; no native Windows/macOS, Safari/Firefox, screen-reader, physical-printer, penetration, large-scale load or prolonged soak test was performed. Passing tests do not prove the absence of defects.

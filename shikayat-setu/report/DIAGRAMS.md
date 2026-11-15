# Diagram notes — Campus Shikayat Setu

These diagrams describe the current application, not a proposed rewrite. The source is `gen_diagrams.py`; `diagram_data.py` reads the database schema directly. The project review schedule chart remains separate and was not reconstructed as an application diagram.

## Traceability

| Diagram | Source checked | What it represents |
|---|---|---|
| Architecture | `run.py`, `app/app.py`, `app/database.py`, `app/routing.py`, templates and static files | Browser, Flask/Jinja and a local SQLite file. |
| ERD | `app/schema.sql` via SQLite PRAGMA metadata | Six tables and all eight foreign keys, including nullable `users.department_id` and `complaint_events.actor_id`. `feedback.complaint_id` is unique, so a complaint has at most one feedback row. |
| Use case | Route decorators and handlers in `app/app.py` | Student, officer, administrator and public visitor. Admins can also use officer complaint actions; public tracking normally needs both the complaint code and roll number. |
| Class model | `app/schema.sql`, functions in `app/app.py` and `app/routing.py` | A **conceptual** model of SQLite rows and selected associations. The application does not implement these records as Python/ORM classes. The ERD is authoritative for all foreign keys. |
| Activity | `lodge`, `select_category`, `acknowledge`, `start_work`, `resolve`, `feedback`, `reopen`, `force_close` in `app/app.py` | Submission, optional acknowledgement and progress, direct resolution, feedback closure, reopening and admin force-close. |
| Deployment | `run.py`, `app/database.py` | Flask's development server binds port 5001 and uses a SQLite file. LAN access depends on local network settings. |
| Module hierarchy | Project files and Python imports | Actual launcher, Flask routes, router, database module, schema, templates and static assets; no blueprints or background workers. |

## Important implementation details

- Each category belongs to a department, but a complaint also stores its assigned department separately; an admin can reassign it without changing its category.
- If the keyword router finds no stronger match than the student's chosen category, the chosen category is retained. Priority is recalculated, and the deadline is stamped on submission.
- An officer or admin may start work directly from Submitted, or resolve directly from Submitted or Acknowledged; these steps are not mandatory in sequence.
- Reopening checks `(now - resolved_at).days > 7`; this uses whole days, not an exact 168-hour cutoff. If the timestamp cannot be parsed, the current code skips the age check. Admin force-close checks for Resolved status but does not enforce a waiting period.
- The database foreign keys do not themselves enforce that `complaints.student_id` points to a user with the student role or that `users.department_id` is populated only for officers. These are application conventions.
- Use-case groups are a simplified view: the admin routes also permit feedback directly, and signed-in admins can use the tracker without a matching roll number.

## Rebuilding

Install the app requirements and `matplotlib`, then run from `shikayat-setu/`:

```bash
python report/gen_diagrams.py
python -m pytest tests/ -q
```

The generator checks the schema's eight foreign keys and feedback's unique key before drawing the ERD. After changing diagrams, rebuild the PDF and slides as described in the project README; check their layout and page numbers before submission.

"""
Campus Shikayat Setu — College Grievance Redressal System
SPPU MCA-I (Sem-I) Mini Project  |  Dr. B.V. Hiray College of Management and Research Centre, Malegaon
Creator: Yashwant Santosh Ahire  |  Guide: Mrs. Priyanka M. Jagtap

Roles: student (lodge/track/feedback/reopen) · officer (acknowledge/progress/resolve) · admin (route/escalate/reports/users)
Run:  python run.py            → http://127.0.0.1:5001
"""
import re
from datetime import date, datetime, timedelta
from functools import wraps

from flask import (
    Flask, flash, redirect, render_template, request, session, url_for, abort, jsonify,
)
from werkzeug.security import check_password_hash, generate_password_hash

import database as db
import routing

app = Flask(__name__)
app.secret_key = "campus-shikayat-setu-dev-key"  # dev value; production would use env var

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^[6-9]\d{9}$")
ROLL_RE  = re.compile(r"^MCA2026\d{3}$", re.I)

STATUS_ORDER = ["Submitted", "Acknowledged", "In Progress", "Resolved", "Closed"]


@app.context_processor
def inject_now():
    return {"now_date": date.today().strftime("%d %B %Y, %A")}


# ------------------------------------------------------------- helpers
def current_user():
    if "user_id" in session:
        conn = db.get_conn()
        u = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        conn.close()
        return u
    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def deco(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            if session.get("role") not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return deco


def get_complaint(conn, code):
    return conn.execute(
        """SELECT c.*, cat.name AS category_name, d.name AS department_name,
                  u.full_name AS student_name, u.roll_no AS student_roll
           FROM complaints c
           JOIN categories cat ON cat.id = c.category_id
           JOIN departments d  ON d.id   = c.department_id
           JOIN users u       ON u.id   = c.student_id
           WHERE c.code = ?""", (code,)).fetchone()


def can_see(user, complaint):
    if user["role"] == "admin":
        return True
    if user["role"] == "student":
        return complaint["student_id"] == user["id"]
    if user["role"] == "officer":
        return user["department_id"] == complaint["department_id"]
    return False


def log_event(conn, complaint_id, event_type, note, actor_id=None):
    conn.execute(
        "INSERT INTO complaint_events (complaint_id, event_type, note, actor_id) VALUES (?,?,?,?)",
        (complaint_id, event_type, note, actor_id),
    )


def is_overdue(complaint):
    if complaint["status"] in ("Resolved", "Closed"):
        return False
    try:
        return datetime.strptime(complaint["sla_due_at"], "%Y-%m-%d %H:%M:%S") < datetime.now()
    except ValueError:
        return False


def select_category(title, description, chosen, categories):
    """Use the keyword match when it scores higher than the chosen category."""
    text = routing.route_text(title, description)
    matched, score = routing.route(text, categories)
    if matched and (matched["id"] == chosen["id"] or
                    score > routing.score_category(text, chosen["keywords"])):
        return matched, "auto", score
    return chosen, "manual", 0


@app.route("/api/route-preview")
@login_required
def route_preview():
    title = (request.args.get("title") or "").strip()
    desc = (request.args.get("description") or "").strip()
    category_id = request.args.get("category_id", "")
    conn = db.get_conn()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    chosen = next((cat for cat in categories if str(cat["id"]) == category_id), None)
    if not chosen:
        conn.close()
        return jsonify(error="Choose a valid category."), 400
    category, _, score = select_category(title, desc, chosen, categories)
    dept = conn.execute("SELECT name FROM departments WHERE id=?", (category["department_id"],)).fetchone()["name"]
    priority = routing.assign_priority(category["default_priority"], title, desc)
    conn.close()
    return jsonify(category=category["name"], department=dept, priority=priority,
                   score=score, sla_hours=routing.SLA_HOURS[priority])


def complaint_timeline(conn, complaint_id):
    rows = conn.execute(
        """SELECT e.*, u.full_name AS actor_name
           FROM complaint_events e LEFT JOIN users u ON u.id = e.actor_id
           WHERE e.complaint_id=? ORDER BY e.created_at ASC, e.id ASC""", (complaint_id,)).fetchall()
    return rows


def render_complaint(conn, c, user):
    d = dict(c)
    d["is_overdue"] = is_overdue(c)
    d["steps"] = complaint_timeline(conn, c["id"])
    d["feedback"] = conn.execute("SELECT * FROM feedback WHERE complaint_id=?", (c["id"],)).fetchone()
    d["identity"] = None if (c["is_anonymous"] and user["role"] != "admin") else c["student_name"]
    d["roll"]     = None if (c["is_anonymous"] and user["role"] != "admin") else c["student_roll"]
    return d


# ------------------------------------------------------------- auth
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        conn = db.get_conn()
        u = conn.execute("SELECT * FROM users WHERE username=? OR roll_no=?", (username, username)).fetchone()
        conn.close()
        if not u or not check_password_hash(u["password_hash"], password):
            flash("Invalid credentials.", "danger")
            return render_template("login.html"), 401
        if u["status"] != "Active":
            flash("Your account is deactivated. Contact the administration.", "warning")
            return render_template("login.html"), 403
        session["user_id"], session["role"], session["full_name"] = u["id"], u["role"], u["full_name"]
        session["department_id"] = u["department_id"]
        flash(f"Welcome, {u['full_name']}.", "success")
        nxt = request.args.get("next") or url_for("dashboard")
        return redirect(nxt)
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name  = (request.form.get("full_name") or "").strip()
        roll  = (request.form.get("roll_no") or "").strip().upper()
        email = (request.form.get("email") or "").strip().lower()
        phone = (request.form.get("phone") or "").strip()
        pw    = request.form.get("password") or ""
        pw2   = request.form.get("confirm_password") or ""
        errors = []
        if len(name) < 3: errors.append("Full name must be at least 3 characters.")
        if not ROLL_RE.match(roll): errors.append("Roll number must look like MCA2026001.")
        if not EMAIL_RE.match(email): errors.append("Enter a valid e-mail address.")
        if not PHONE_RE.match(phone): errors.append("Enter a valid 10-digit Indian mobile number.")
        if len(pw) < 6: errors.append("Password must be at least 6 characters.")
        if pw != pw2: errors.append("Passwords do not match.")
        conn = db.get_conn()
        if conn.execute("SELECT 1 FROM users WHERE roll_no=?", (roll,)).fetchone():
            errors.append("Roll number already registered.")
        if conn.execute("SELECT 1 FROM users WHERE username=?", (roll,)).fetchone():
            errors.append("Account already exists for this roll number.")
        if errors:
            conn.close()
            for e in errors: flash(e, "danger")
            return render_template("register.html", form=request.form), 400
        conn.execute(
            "INSERT INTO users (role, username, password_hash, full_name, roll_no, phone, status) VALUES ('student',?,?,?,?,?, 'Active')",
            (roll, generate_password_hash(pw), name, roll, phone))
        conn.commit(); conn.close()
        flash("Registration successful. Please log in with your roll number.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form={})


# ------------------------------------------------------------- dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    conn = db.get_conn()
    user = current_user()
    if user["role"] == "student":
        mine = conn.execute(
            """SELECT c.*, cat.name AS category_name, d.name AS department_name
               FROM complaints c JOIN categories cat ON cat.id=c.category_id JOIN departments d ON d.id=c.department_id
               WHERE c.student_id=? ORDER BY c.submitted_at DESC""", (user["id"],)).fetchall()
        counts = {s: 0 for s in STATUS_ORDER}
        for m in mine: counts[m["status"]] += 1
        recent = mine[:3]
        open_count = sum(v for k, v in counts.items() if k not in ("Resolved", "Closed"))
        ctx = dict(counts=counts, total=len(mine), recent=recent, role="student",
                   donut=counts, open_count=open_count)
    elif user["role"] == "officer":
        rows = conn.execute(
            """SELECT c.*, cat.name AS category_name, u.full_name AS student_name
               FROM complaints c JOIN categories cat ON cat.id=c.category_id JOIN users u ON u.id=c.student_id
               WHERE c.department_id=? AND c.status!='Closed' ORDER BY c.submitted_at DESC""", (user["department_id"],)).fetchall()
        overdue = sum(1 for r in rows if is_overdue(r))
        high = sum(1 for r in rows if r["priority"] == "High")
        status_counts = {s: 0 for s in STATUS_ORDER}
        for r in conn.execute("SELECT status, COUNT(*) c FROM complaints WHERE department_id=? GROUP BY status",
                              (user["department_id"],)):
            status_counts[r["status"]] = r["c"]
        ctx = dict(assigned=len(rows), overdue=overdue, high=high, queue=[dict(r, is_overdue=is_overdue(r)) for r in rows[:6]], role="officer",
                   donut=status_counts, open_count=len(rows),
                   department=conn.execute("SELECT name FROM departments WHERE id=?", (user["department_id"],)).fetchone()["name"])
    else:  # admin
        by_status = {r["status"]: r["c"] for r in conn.execute("SELECT status, COUNT(*) c FROM complaints GROUP BY status")}
        total = conn.execute("SELECT COUNT(*) c FROM complaints").fetchone()["c"]
        rows = conn.execute(
            """SELECT c.*, cat.name AS category_name, d.name AS department_name
               FROM complaints c JOIN categories cat ON cat.id=c.category_id JOIN departments d ON d.id=c.department_id
               WHERE c.status NOT IN ('Resolved','Closed') ORDER BY c.submitted_at DESC""").fetchall()
        overdue = sum(1 for r in rows if is_overdue(r))
        recent = conn.execute(
            """SELECT c.*, cat.name AS category_name, d.name AS department_name
               FROM complaints c JOIN categories cat ON cat.id=c.category_id JOIN departments d ON d.id=c.department_id
               ORDER BY c.submitted_at DESC LIMIT 6""").fetchall()
        donut = {s: by_status.get(s, 0) for s in STATUS_ORDER}
        dept_open = [dict(r) for r in conn.execute(
            "SELECT d.name, COUNT(c.id) AS n FROM departments d JOIN complaints c ON c.department_id=d.id "
            "WHERE c.status NOT IN ('Resolved','Closed') GROUP BY d.id ORDER BY n DESC")]
        decided = conn.execute("SELECT COUNT(*) c FROM complaints WHERE status IN ('Resolved','Closed')").fetchone()["c"]
        on_time = conn.execute("SELECT COUNT(*) c FROM complaints WHERE resolved_at IS NOT NULL AND resolved_at <= sla_due_at").fetchone()["c"]
        on_time_pct = round(100.0 * on_time / decided, 1) if decided else 0
        csat = conn.execute("SELECT AVG(rating) a FROM feedback").fetchone()["a"]
        ctx = dict(total=total, by_status=by_status, overdue=overdue, recent=recent, role="admin",
                   donut=donut, dept_open=dept_open, on_time_pct=on_time_pct,
                   csat=round(csat, 1) if csat else None,
                   open_count=sum(v for k, v in donut.items() if k not in ("Resolved", "Closed")))
    conn.close()
    return render_template("dashboard.html", **ctx)


# ------------------------------------------------------------- lodge & lists
@app.route("/lodge", methods=["GET", "POST"])
@login_required
@role_required("student")
def lodge():
    conn = db.get_conn()
    cats = conn.execute("SELECT c.id, c.name, d.name AS dept FROM categories c JOIN departments d ON d.id=c.department_id ORDER BY c.name").fetchall()
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        desc  = (request.form.get("description") or "").strip()
        loc   = (request.form.get("location") or "").strip()
        anon  = 1 if request.form.get("is_anonymous") == "on" else 0
        cat_id = request.form.get("category_id") or ""
        errors = []
        if len(title) < 8: errors.append("Title must be at least 8 characters.")
        if len(desc) < 20: errors.append("Description must be at least 20 characters — help the department.")
        if not cat_id.isdigit() or not conn.execute("SELECT 1 FROM categories WHERE id=?", (cat_id,)).fetchone():
            errors.append("Choose a valid category.")
        if errors:
            for e in errors: flash(e, "danger")
            conn.close()
            return render_template("lodge.html", cats=cats, form=request.form), 400
        chosen = conn.execute("SELECT * FROM categories WHERE id=?", (cat_id,)).fetchone()
        final_cat, routing_kind, rscore = select_category(
            title, desc, chosen, conn.execute("SELECT * FROM categories").fetchall())
        priority = routing.assign_priority(final_cat["default_priority"], title, desc)
        now = datetime.now()
        due = now + timedelta(hours=routing.SLA_HOURS[priority])
        cur = conn.execute(
            """INSERT INTO complaints (code, student_id, category_id, department_id, title, description, location,
                                        priority, routing, routing_score, status, is_anonymous, submitted_at, sla_due_at)
               VALUES ('TMP',?,?,?,?,?,?,?,?,?,'Submitted',?,?,?)""",
            (session["user_id"], final_cat["id"], final_cat["department_id"], title, desc, loc,
             priority, routing_kind, rscore, anon,
             now.strftime("%Y-%m-%d %H:%M:%S"), due.strftime("%Y-%m-%d %H:%M:%S")))
        cid = cur.lastrowid
        code = f"CMP-{now.year}-{cid:04d}"
        conn.execute("UPDATE complaints SET code=? WHERE id=?", (code, cid))
        log_event(conn, cid, "created", f"Complaint lodged by {'anonymous' if anon else 'student'}.", session["user_id"])
        dept_name = conn.execute("SELECT name FROM departments WHERE id=?", (final_cat["department_id"],)).fetchone()["name"]
        log_event(conn, cid, "routed",
                  f"Routed to {final_cat['name']} → {dept_name} · score {rscore} · SLA {routing.SLA_HOURS[priority]}h",
                  None)
        conn.commit(); conn.close()
        flash(f"Complaint lodged as {code} — SLA {routing.SLA_HOURS[priority]} hours. You will be able to track it with this code.", "success")
        return redirect(url_for("my_complaints"))
    return render_template("lodge.html", cats=cats, form={})


@app.route("/my-complaints")
@login_required
@role_required("student")
def my_complaints():
    conn = db.get_conn()
    rows = conn.execute(
        """SELECT c.*, cat.name AS category_name, d.name AS department_name
           FROM complaints c JOIN categories cat ON cat.id=c.category_id JOIN departments d ON d.id=c.department_id
           WHERE c.student_id=? ORDER BY c.submitted_at DESC""", (session["user_id"],)).fetchall()
    conn.close()
    return render_template("my_complaints.html", rows=[dict(r, is_overdue=is_overdue(r)) for r in rows])


@app.route("/track", methods=["GET", "POST"])
def public_track():
    result = None
    if request.method == "POST":
        code = (request.form.get("code") or "").strip().upper()
        roll = (request.form.get("roll_no") or "").strip().upper()
        conn = db.get_conn()
        row = get_complaint(conn, code)
        if row:
            is_owner = roll == (row["student_roll"] or "")
            if session.get("role") == "admin" or is_owner:
                result = render_complaint(conn, row, {"role": "guest", "id": None})
            else:
                flash("Roll number does not match this complaint.", "danger")
        else:
            flash("No complaint found with that code.", "danger")
        conn.close()
    return render_template("track.html", result=result)


# ------------------------------------------------------------- detail & actions
@app.route("/complaint/<code>")
@login_required
def complaint_detail(code):
    conn = db.get_conn()
    c = get_complaint(conn, code)
    user = current_user()
    if not c:
        conn.close(); abort(404)
    if not can_see(user, c):
        conn.close(); abort(403)
    data = render_complaint(conn, c, user)
    depts = conn.execute("SELECT id, name FROM departments ORDER BY name").fetchall() if user["role"] == "admin" else []
    conn.close()
    return render_template("complaint_detail.html", c=data, depts=depts)


def get_for_action(code, roles=None):
    conn = db.get_conn()
    c = get_complaint(conn, code)
    if not c:
        conn.close(); abort(404)
    user = current_user()
    if roles and user["role"] not in roles:
        conn.close(); abort(403)
    if not can_see(user, c):
        conn.close(); abort(403)
    return conn, c, user


@app.route("/complaint/<code>/acknowledge", methods=["POST"])
@login_required
@role_required("officer", "admin")
def acknowledge(code):
    conn, c, user = get_for_action(code)
    if c["status"] != "Submitted":
        flash("Only Submitted complaints can be acknowledged.", "warning")
    else:
        conn.execute("UPDATE complaints SET status='Acknowledged' WHERE id=?", (c["id"],))
        log_event(conn, c["id"], "acknowledged", (request.form.get("note") or "Complaint acknowledged by department.").strip(), user["id"])
        conn.commit(); flash("Complaint acknowledged.", "success")
    conn.close()
    return redirect(url_for("complaint_detail", code=code))


@app.route("/complaint/<code>/progress", methods=["POST"])
@login_required
@role_required("officer", "admin")
def start_work(code):
    conn, c, user = get_for_action(code)
    if c["status"] not in ("Acknowledged", "Submitted"):
        flash("Work can only start on Submitted/Acknowledged complaints.", "warning")
    else:
        conn.execute("UPDATE complaints SET status='In Progress' WHERE id=?", (c["id"],))
        log_event(conn, c["id"], "status", (request.form.get("note") or "Work started on the complaint.").strip(), user["id"])
        conn.commit(); flash("Marked In Progress.", "success")
    conn.close()
    return redirect(url_for("complaint_detail", code=code))


@app.route("/complaint/<code>/resolve", methods=["POST"])
@login_required
@role_required("officer", "admin")
def resolve(code):
    remark = (request.form.get("remark") or "").strip()
    conn, c, user = get_for_action(code)
    if len(remark) < 10:
        flash("Resolution remark must be at least 10 characters.", "danger")
    elif c["status"] not in ("In Progress", "Acknowledged", "Submitted"):
        flash("Complaint is already resolved or closed.", "warning")
    else:
        conn.execute("UPDATE complaints SET status='Resolved', resolved_at=? WHERE id=?",
                     (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), c["id"]))
        log_event(conn, c["id"], "status", f"Resolved — {remark}", user["id"])
        conn.commit(); flash("Complaint marked Resolved. The student can now confirm or reopen.", "success")
    conn.close()
    return redirect(url_for("complaint_detail", code=code))


@app.route("/complaint/<code>/remark", methods=["POST"])
@login_required
@role_required("officer", "admin")
def add_remark(code):
    note = (request.form.get("note") or "").strip()
    conn, c, user = get_for_action(code)
    if len(note) < 5:
        flash("Remark must be at least 5 characters.", "danger")
    else:
        log_event(conn, c["id"], "remark", note, user["id"])
        conn.commit(); flash("Remark added to timeline.", "success")
    conn.close()
    return redirect(url_for("complaint_detail", code=code))


@app.route("/complaint/<code>/feedback", methods=["POST"])
@login_required
@role_required("student", "admin")
def feedback(code):
    conn, c, user = get_for_action(code)
    if c["status"] != "Resolved" or (user["role"] == "student" and c["student_id"] != user["id"]):
        flash("Feedback is only for your own resolved complaints.", "warning"); conn.close()
        return redirect(url_for("complaint_detail", code=code))
    rating = request.form.get("rating") or ""
    comment = (request.form.get("comment") or "").strip()
    if rating not in ("1", "2", "3", "4", "5"):
        flash("Choose a rating between 1 and 5.", "danger"); conn.close()
        return redirect(url_for("complaint_detail", code=code))
    conn.execute("INSERT OR REPLACE INTO feedback (complaint_id, rating, comment) VALUES (?,?,?)",
                 (c["id"], int(rating), comment))
    conn.execute("UPDATE complaints SET status='Closed' WHERE id=?", (c["id"],))
    log_event(conn, c["id"], "feedback", f"Student rated {rating}/5.{(' — ' + comment) if comment else ''}", user["id"])
    log_event(conn, c["id"], "closed", "Student confirmed resolution. Complaint closed.", user["id"])
    conn.commit(); conn.close()
    flash("Thank you — complaint closed.", "success")
    return redirect(url_for("my_complaints"))


@app.route("/complaint/<code>/reopen", methods=["POST"])
@login_required
@role_required("student")
def reopen(code):
    reason = (request.form.get("reason") or "").strip()
    conn, c, user = get_for_action(code)
    if c["status"] != "Resolved" or c["student_id"] != user["id"]:
        flash("Only your own resolved complaints can be reopened.", "warning")
    elif len(reason) < 10:
        flash("Tell us briefly why you are reopening (min 10 characters).", "danger")
    else:
        try:
            resolved = datetime.strptime(c["resolved_at"], "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - resolved).days > 7:
                flash("Reopen window (7 days) has passed. Please lodge a fresh complaint.", "warning")
                conn.close(); return redirect(url_for("complaint_detail", code=code))
        except Exception:
            pass
        conn.execute("UPDATE complaints SET status='In Progress' WHERE id=?", (c["id"],))
        log_event(conn, c["id"], "reopened", f"Student reopened: {reason}", user["id"])
        conn.commit(); flash("Complaint reopened. The department has been notified.", "success")
    conn.close()
    return redirect(url_for("complaint_detail", code=code))


@app.route("/complaint/<code>/reassign", methods=["POST"])
@login_required
@role_required("admin")
def reassign(code):
    dept_id = request.form.get("department_id") or ""
    conn, c, user = get_for_action(code)
    new = conn.execute("SELECT * FROM departments WHERE id=?", (dept_id,)).fetchone() if dept_id.isdigit() else None
    if not new:
        flash("Choose a valid department.", "danger")
    else:
        old = conn.execute("SELECT name FROM departments WHERE id=?", (c["department_id"],)).fetchone()["name"]
        conn.execute("UPDATE complaints SET department_id=?, routing='manual' WHERE id=?", (new["id"], c["id"]))
        log_event(conn, c["id"], "reassign", f"Admin reassigned: {old} → {new['name']}", user["id"])
        conn.commit(); flash(f"Reassigned to {new['name']}.", "success")
    conn.close()
    return redirect(url_for("complaint_detail", code=code))


@app.route("/complaint/<code>/escalate", methods=["POST"])
@login_required
@role_required("admin")
def escalate(code):
    note = (request.form.get("note") or "Escalated by admin — priority raised to High.").strip()
    conn, c, user = get_for_action(code)
    conn.execute("UPDATE complaints SET priority='High' WHERE id=?", (c["id"],))
    log_event(conn, c["id"], "escalated", note, user["id"])
    conn.commit(); conn.close()
    flash("Complaint escalated to High priority.", "success")
    return redirect(url_for("complaint_detail", code=code))


@app.route("/complaint/<code>/force-close", methods=["POST"])
@login_required
@role_required("admin")
def force_close(code):
    conn, c, user = get_for_action(code)
    if c["status"] != "Resolved":
        flash("Only Resolved complaints can be force-closed.", "warning")
    else:
        conn.execute("UPDATE complaints SET status='Closed' WHERE id=?", (c["id"],))
        log_event(conn, c["id"], "closed", "Closed by admin after 7-day no-response window.", user["id"])
        conn.commit(); flash("Complaint force-closed.", "success")
    conn.close()
    return redirect(url_for("complaint_detail", code=code))


# ------------------------------------------------------------- officer queue & admin console
@app.route("/queue")
@login_required
@role_required("officer", "admin")
def queue():
    conn = db.get_conn()
    user = current_user()
    dept = request.args.get("department_id")
    q = """SELECT c.*, cat.name AS category_name, u.full_name AS student_name, u.roll_no AS student_roll
           FROM complaints c JOIN categories cat ON cat.id=c.category_id JOIN users u ON u.id=c.student_id
           WHERE c.status!='Closed'"""
    params = []
    if user["role"] == "officer":
        q += " AND c.department_id=?"; params.append(user["department_id"])
    elif dept and dept.isdigit():
        q += " AND c.department_id=?"; params.append(int(dept))
    flt_status = request.args.get("status") or ""
    if flt_status in STATUS_ORDER:
        q += " AND c.status=?"; params.append(flt_status)
    q += " ORDER BY CASE c.priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END, c.submitted_at DESC"
    rows = conn.execute(q, params).fetchall()
    depts = conn.execute("SELECT id, name FROM departments ORDER BY name").fetchall() if user["role"] == "admin" else []
    conn.close()
    return render_template("queue.html", rows=[dict(r, is_overdue=is_overdue(r)) for r in rows],
                           depts=depts, filt_status=flt_status, sel_dept=dept)


@app.route("/console")
@login_required
@role_required("admin")
def console():
    conn = db.get_conn()
    dept = request.args.get("department_id") or ""
    status = request.args.get("status") or ""
    prio = request.args.get("priority") or ""
    q = """SELECT c.*, cat.name AS category_name, d.name AS department_name, u.full_name AS student_name
           FROM complaints c JOIN categories cat ON cat.id=c.category_id
           JOIN departments d ON d.id=c.department_id JOIN users u ON u.id=c.student_id WHERE 1=1"""
    params = []
    if dept.isdigit(): q += " AND c.department_id=?"; params.append(int(dept))
    if status in STATUS_ORDER: q += " AND c.status=?"; params.append(status)
    if prio in ("High", "Medium", "Low"): q += " AND c.priority=?"; params.append(prio)
    q += " ORDER BY CASE c.priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END, c.submitted_at DESC"
    rows = conn.execute(q, params).fetchall()
    depts = conn.execute("SELECT id, name FROM departments ORDER BY name").fetchall()
    conn.close()
    return render_template("console.html", rows=[dict(r, is_overdue=is_overdue(r)) for r in rows],
                           depts=depts, sel_dept=dept, sel_status=status, sel_prio=prio)


@app.route("/users")
@login_required
@role_required("admin")
def users():
    conn = db.get_conn()
    rows = conn.execute(
        """SELECT u.*, d.name AS department_name FROM users u LEFT JOIN departments d ON d.id=u.department_id
           ORDER BY u.role, u.full_name""").fetchall()
    depts = conn.execute("SELECT id, name FROM departments ORDER BY name").fetchall()
    conn.close()
    return render_template("users.html", rows=rows, depts=depts)


@app.route("/users/officer", methods=["POST"])
@login_required
@role_required("admin")
def create_officer():
    name = (request.form.get("full_name") or "").strip()
    dept = request.form.get("department_id") or ""
    uname = (request.form.get("username") or "").strip().lower()
    pw = request.form.get("password") or "officer123"
    conn = db.get_conn()
    if len(name) < 3 or not uname or not dept.isdigit():
        flash("Name, username and department are required.", "danger")
    elif conn.execute("SELECT 1 FROM users WHERE username=?", (uname,)).fetchone():
        flash("Username already exists.", "danger")
    else:
        conn.execute(
            "INSERT INTO users (role, username, password_hash, full_name, department_id, status) VALUES ('officer',?,?,?,?, 'Active')",
            (uname, generate_password_hash(pw), name, int(dept)))
        conn.commit(); flash(f"Officer {uname} created.", "success")
    conn.close()
    return redirect(url_for("users"))


@app.route("/users/<int:uid>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def toggle_user(uid):
    conn = db.get_conn()
    u = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not u:
        conn.close(); abort(404)
    if u["username"] == "admin":
        flash("The built-in admin cannot be deactivated.", "warning")
    else:
        new = "Inactive" if u["status"] == "Active" else "Active"
        conn.execute("UPDATE users SET status=? WHERE id=?", (new, uid))
        conn.commit(); flash(f"Account {u['username']} is now {new}.", "success")
    conn.close()
    return redirect(url_for("users"))


# ------------------------------------------------------------- change password
@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old = request.form.get("current_password") or ""
        new = request.form.get("new_password") or ""
        conf = request.form.get("confirm_password") or ""
        conn = db.get_conn()
        u = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        if not check_password_hash(u["password_hash"], old):
            flash("Current password is incorrect.", "danger")
        elif len(new) < 6:
            flash("New password must be at least 6 characters.", "danger")
        elif new != conf:
            flash("Confirmation does not match.", "danger")
        else:
            conn.execute("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(new), u["id"]))
            conn.commit(); flash("Password updated.", "success")
            conn.close(); return redirect(url_for("dashboard"))
        conn.close()
    return render_template("change_password.html")


# ------------------------------------------------------------- reports
@app.route("/reports")
@login_required
@role_required("admin")
def reports():
    conn = db.get_conn()
    which = request.args.get("report", "pendency")
    ctx = {}
    if which == "pendency":
        rows = conn.execute(
            """SELECT d.name AS dept,
                      SUM(CASE WHEN c.status='Submitted' THEN 1 ELSE 0 END) AS submitted,
                      SUM(CASE WHEN c.status='Acknowledged' THEN 1 ELSE 0 END) AS acknowledged,
                      SUM(CASE WHEN c.status='In Progress' THEN 1 ELSE 0 END) AS in_progress,
                      SUM(CASE WHEN c.status='Resolved' THEN 1 ELSE 0 END) AS resolved,
                      SUM(CASE WHEN c.status='Closed' THEN 1 ELSE 0 END) AS closed,
                      COUNT(*) AS total
               FROM departments d LEFT JOIN complaints c ON c.department_id=d.id GROUP BY d.id ORDER BY total DESC""").fetchall()
        pend = conn.execute("""SELECT department_id, COUNT(*) c FROM complaints
                                WHERE status NOT IN ('Resolved','Closed') AND datetime(sla_due_at) < datetime('now','localtime')
                                GROUP BY department_id""").fetchall()
        od = {r["department_id"]: r["c"] for r in pend}
        dept_ids = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM departments")}
        ctx["rows"] = [dict(r, overdue=od.get(dept_ids.get(r["dept"]), 0)) for r in rows]
    elif which == "sla":
        rows = conn.execute(
            """SELECT d.name AS dept,
                      COUNT(c.id) AS resolved_total,
                      SUM(CASE WHEN c.resolved_at IS NOT NULL AND c.resolved_at <= c.sla_due_at THEN 1 ELSE 0 END) AS within_sla,
                      ROUND(100.0 * SUM(CASE WHEN c.resolved_at IS NOT NULL AND c.resolved_at <= c.sla_due_at THEN 1 ELSE 0 END) / NULLIF(COUNT(c.id),0), 1) AS pct
               FROM departments d LEFT JOIN complaints c ON c.department_id=d.id AND c.status IN ('Resolved','Closed')
               GROUP BY d.id ORDER BY pct DESC NULLS LAST""").fetchall()
        ctx["rows"] = rows
    elif which == "restime":
        rows = conn.execute(
            """SELECT cat.name AS category, COUNT(*) AS n,
                      ROUND(AVG((julianday(c.resolved_at) - julianday(c.submitted_at)) * 24), 1) AS avg_hours
               FROM complaints c JOIN categories cat ON cat.id=c.category_id
               WHERE c.resolved_at IS NOT NULL GROUP BY cat.id ORDER BY avg_hours""").fetchall()
        ctx["rows"] = rows
    elif which == "trend":
        rows = conn.execute(
            """SELECT strftime('%Y-%m', submitted_at) AS month,
                      COUNT(*) AS lodged,
                      SUM(CASE WHEN status IN ('Resolved','Closed') THEN 1 ELSE 0 END) AS resolved
               FROM complaints GROUP BY month ORDER BY month DESC LIMIT 6""").fetchall()
        ctx["rows"] = list(reversed(rows))
    elif which == "feedback":
        rows = conn.execute(
            """SELECT d.name AS dept, ROUND(AVG(f.rating), 2) AS avg_rating, COUNT(f.id) AS n
               FROM feedback f JOIN complaints c ON c.id=f.complaint_id JOIN departments d ON d.id=c.department_id
               GROUP BY d.id ORDER BY avg_rating DESC""").fetchall()
        recent = conn.execute(
            """SELECT f.rating, f.comment, d.name AS dept, c.code FROM feedback f
               JOIN complaints c ON c.id=f.complaint_id JOIN departments d ON d.id=c.department_id
               ORDER BY f.created_at DESC LIMIT 10""").fetchall()
        ctx["rows"] = rows; ctx["recent"] = recent
    elif which == "routing":
        rows = conn.execute(
            """SELECT routing, COUNT(*) AS n, ROUND(AVG(routing_score), 1) AS avg_score FROM complaints GROUP BY routing""").fetchall()
        manual = conn.execute(
            """SELECT c.code, c.title, d.name AS dept FROM complaints c JOIN departments d ON d.id=c.department_id
               WHERE routing='manual' ORDER BY c.submitted_at DESC""").fetchall()
        ctx["rows"] = rows; ctx["manual"] = manual
    conn.close()
    return render_template("reports.html", which=which, **ctx)


@app.errorhandler(403)
def forbidden(e):
    return render_template("404.html", code=403, message="You are not allowed to access this page."), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", code=404, message="Page or complaint not found."), 404


if __name__ == "__main__":
    db.init_db()
    db.seed_if_empty()
    print("Campus Shikayat Setu running at http://127.0.0.1:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)

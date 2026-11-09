"""
SmartLibrary — College Library Management System
SPPU MCA-I (Sem-I) Mini Project  |  Dr. B. V. Hiray College of Management and Research Centre, Malegaon

Run:
    python app.py            # serves on http://0.0.0.0:5000
Default login: admin / admin123
"""
import re
from datetime import date, timedelta

from flask import (
    Flask, flash, redirect, render_template, request, session, url_for, abort,
)
from werkzeug.security import check_password_hash, generate_password_hash

import database as db

FINE_PER_DAY = 2          # Rs. 2 per day of late return
MAX_ISSUE_PER_MEMBER = 3  # a member may hold at most 3 books at a time
LOAN_DAYS = 14            # default loan period

app = Flask(__name__)

@app.context_processor
def inject_now():
    return {"now_date": date.today().strftime("%d %B %Y, %A")}

app.secret_key = "smartlibrary-secret-key-change-in-production"

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^[6-9]\d{9}$")              # Indian mobile numbers
ISBN_RE = re.compile(r"^(?:\d[- ]?){9,13}[\dxX]$")  # ISBN-10 / ISBN-13 with hyphens

# ------------------------------------------------------------- helpers

def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def today_str():
    return date.today().strftime("%Y-%m-%d")


def enrich_txn(row):
    """Attach computed fields (late days / payable fine) to a transaction row."""
    t = dict(row)
    due = date.fromisoformat(t["due_date"])
    if t["status"] == "Issued":
        late = max(0, (date.today() - due).days)
        t["late_days"] = late
        t["payable_fine"] = late * FINE_PER_DAY
        t["is_overdue"] = late > 0
    else:
        ret = date.fromisoformat(t["return_date"])
        late = max(0, (ret - due).days)
        t["late_days"] = late
        t["payable_fine"] = t["fine_amount"]
        t["is_overdue"] = False
    return t


# ------------------------------------------------------------- auth

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "admin_id" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            flash("Both username and password are required.", "danger")
            return render_template("login.html", username=username), 400
        conn = db.get_conn()
        adm = conn.execute("SELECT * FROM admin WHERE username = ?", (username,)).fetchone()
        conn.close()
        # support seeded sha256 hashes and werkzeug hashes
        ok = False
        if adm:
            stored = adm["password_hash"]
            if stored.startswith("pbkdf2:") or stored.startswith("scrypt:"):
                ok = check_password_hash(stored, password)
            else:
                ok = stored == db.hash_pw(password)
        if not ok:
            flash("Invalid username or password.", "danger")
            return render_template("login.html", username=username), 401
        session.clear()
        session["admin_id"] = adm["admin_id"]
        session["admin_name"] = adm["full_name"]
        flash(f"Welcome back, {adm['full_name']}!", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html", username="")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old = request.form.get("old_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        conn = db.get_conn()
        adm = conn.execute("SELECT * FROM admin WHERE admin_id = ?", (session["admin_id"],)).fetchone()
        stored = adm["password_hash"]
        ok = check_password_hash(stored, old) if stored.startswith(("pbkdf2:", "scrypt:")) else stored == db.hash_pw(old)
        if not ok:
            conn.close()
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("change_password"))
        if len(new) < 6:
            conn.close()
            flash("New password must be at least 6 characters.", "danger")
            return redirect(url_for("change_password"))
        if new != confirm:
            conn.close()
            flash("New passwords do not match.", "danger")
            return redirect(url_for("change_password"))
        conn.execute("UPDATE admin SET password_hash = ? WHERE admin_id = ?",
                     (generate_password_hash(new), session["admin_id"]))
        conn.commit()
        conn.close()
        flash("Password changed successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("change_password.html")


# ------------------------------------------------------------- dashboard

@app.route("/dashboard")
@login_required
def dashboard():
    conn = db.get_conn()
    stats = {
        "total_titles": conn.execute("SELECT COUNT(*) c FROM book").fetchone()["c"],
        "total_copies": conn.execute("SELECT COALESCE(SUM(quantity),0) c FROM book").fetchone()["c"],
        "available": conn.execute("SELECT COALESCE(SUM(available_quantity),0) c FROM book").fetchone()["c"],
        "members": conn.execute("SELECT COUNT(*) c FROM member WHERE status='Active'").fetchone()["c"],
        "issued": conn.execute("SELECT COUNT(*) c FROM issue_transaction WHERE status='Issued'").fetchone()["c"],
        "overdue": conn.execute("SELECT COUNT(*) c FROM issue_transaction WHERE status='Issued' AND due_date < date('now')").fetchone()["c"],
        "fines_collected": conn.execute("SELECT COALESCE(SUM(fine_amount),0) c FROM issue_transaction").fetchone()["c"],
    }
    recent = [enrich_txn(r) for r in conn.execute(
        """SELECT t.*, b.title, m.name AS member_name FROM issue_transaction t
           JOIN book b ON b.book_id = t.book_id JOIN member m ON m.member_id = t.member_id
           ORDER BY t.issue_date DESC, t.issue_id DESC LIMIT 6""").fetchall()]
    low_stock = conn.execute(
        "SELECT title, available_quantity FROM book WHERE available_quantity <= 1 ORDER BY available_quantity ASC LIMIT 5"
    ).fetchall()
    conn.close()
    return render_template("dashboard.html", stats=stats, recent=recent, low_stock=low_stock)


# ------------------------------------------------------------- books

def validate_book_form(form, is_edit=False):
    errors = []
    data = {
        "isbn": (form.get("isbn") or "").strip(),
        "title": (form.get("title") or "").strip(),
        "author": (form.get("author") or "").strip(),
        "publisher": (form.get("publisher") or "").strip(),
        "category": (form.get("category") or "").strip(),
        "edition": (form.get("edition") or "").strip(),
        "shelf_location": (form.get("shelf_location") or "").strip(),
    }
    try:
        data["quantity"] = int(form.get("quantity") or 0)
    except ValueError:
        errors.append("Quantity must be a whole number.")
        data["quantity"] = 0
    if not ISBN_RE.match(data["isbn"]):
        errors.append("Enter a valid ISBN-10 or ISBN-13 (digits and hyphens).")
    if len(data["title"]) < 2:
        errors.append("Title is required (min 2 characters).")
    if len(data["author"]) < 2:
        errors.append("Author is required (min 2 characters).")
    if not data["category"]:
        errors.append("Category is required.")
    if data["quantity"] < 0 or data["quantity"] > 10000:
        errors.append("Quantity must be between 0 and 10,000.")
    return errors, data


@app.route("/books")
@login_required
def books():
    q = (request.args.get("q") or "").strip()
    category = (request.args.get("category") or "").strip()
    sql = "SELECT * FROM book WHERE 1=1"
    args = []
    if q:
        sql += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
        args += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if category:
        sql += " AND category = ?"
        args.append(category)
    sql += " ORDER BY title"
    conn = db.get_conn()
    rows = conn.execute(sql, args).fetchall()
    categories = [r["category"] for r in conn.execute("SELECT DISTINCT category FROM book ORDER BY category").fetchall()]
    conn.close()
    return render_template("books.html", books=rows, q=q, category=category, categories=categories)


@app.route("/books/add", methods=["GET", "POST"])
@login_required
def add_book():
    if request.method == "POST":
        errors, data = validate_book_form(request.form)
        if not errors:
            conn = db.get_conn()
            dup = conn.execute("SELECT 1 FROM book WHERE isbn = ?", (data["isbn"],)).fetchone()
            if dup:
                errors.append("A book with this ISBN already exists.")
            else:
                conn.execute(
                    "INSERT INTO book (isbn,title,author,publisher,category,edition,quantity,available_quantity,shelf_location) VALUES (?,?,?,?,?,?,?,?,?)",
                    (data["isbn"], data["title"], data["author"], data["publisher"], data["category"],
                     data["edition"], data["quantity"], data["quantity"], data["shelf_location"]),
                )
                conn.commit()
                conn.close()
                flash("Book added successfully.", "success")
                return redirect(url_for("books"))
            conn.close()
        for e in errors:
            flash(e, "danger")
        return render_template("book_form.html", book=data, mode="add", form=request.form)
    return render_template("book_form.html", book={}, mode="add", form={})


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    conn = db.get_conn()
    book = conn.execute("SELECT * FROM book WHERE book_id = ?", (book_id,)).fetchone()
    if not book:
        conn.close()
        abort(404)
    if request.method == "POST":
        errors, data = validate_book_form(request.form, is_edit=True)
        issued_out = conn.execute(
            "SELECT COUNT(*) c FROM issue_transaction WHERE book_id = ? AND status='Issued'", (book_id,)).fetchone()["c"]
        if data["quantity"] < issued_out:
            errors.append(f"Quantity cannot be less than the {issued_out} cop(y/ies) currently issued.")
        if not errors:
            dup = conn.execute("SELECT 1 FROM book WHERE isbn = ? AND book_id != ?", (data["isbn"], book_id)).fetchone()
            if dup:
                errors.append("Another book already uses this ISBN.")
        if errors:
            for e in errors:
                flash(e, "danger")
            conn.close()
            return render_template("book_form.html", book=request.form, mode="edit", form=request.form, book_id=book_id)
        new_available = data["quantity"] - issued_out
        conn.execute(
            "UPDATE book SET isbn=?,title=?,author=?,publisher=?,category=?,edition=?,quantity=?,available_quantity=?,shelf_location=? WHERE book_id=?",
            (data["isbn"], data["title"], data["author"], data["publisher"], data["category"], data["edition"],
             data["quantity"], new_available, data["shelf_location"], book_id),
        )
        conn.commit()
        conn.close()
        flash("Book updated successfully.", "success")
        return redirect(url_for("books"))
    conn.close()
    return render_template("book_form.html", book=book, mode="edit", form={}, book_id=book_id)


@app.route("/books/<int:book_id>/delete", methods=["POST"])
@login_required
def delete_book(book_id):
    conn = db.get_conn()
    active = conn.execute(
        "SELECT COUNT(*) c FROM issue_transaction WHERE book_id = ? AND status='Issued'", (book_id,)).fetchone()["c"]
    if active:
        conn.close()
        flash(f"Cannot delete: {active} cop(y/ies) of this book are currently issued.", "danger")
        return redirect(url_for("books"))
    conn.execute("DELETE FROM book WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()
    flash("Book deleted.", "success")
    return redirect(url_for("books"))


# ------------------------------------------------------------- members

def validate_member_form(form):
    errors = []
    data = {
        "roll_no": (form.get("roll_no") or "").strip().upper(),
        "name": (form.get("name") or "").strip(),
        "email": (form.get("email") or "").strip().lower(),
        "phone": (form.get("phone") or "").strip(),
        "department": (form.get("department") or "").strip(),
        "semester": (form.get("semester") or "").strip(),
        "membership_type": (form.get("membership_type") or "Student").strip(),
        "status": (form.get("status") or "Active").strip(),
    }
    if not re.match(r"^[A-Za-z0-9/-]{4,15}$", data["roll_no"]):
        errors.append("Roll/Employee number must be 4–15 alphanumeric characters.")
    if len(data["name"]) < 2:
        errors.append("Name is required.")
    if not EMAIL_RE.match(data["email"]):
        errors.append("Enter a valid email address (e.g. name@bvhmc.edu.in).")
    if not PHONE_RE.match(data["phone"]):
        errors.append("Enter a valid 10-digit Indian mobile number.")
    if not data["department"]:
        errors.append("Department is required.")
    if not data["semester"]:
        errors.append("Semester/Designation is required.")
    if data["membership_type"] not in ("Student", "Faculty"):
        errors.append("Membership type must be Student or Faculty.")
    if data["status"] not in ("Active", "Inactive"):
        errors.append("Status must be Active or Inactive.")
    return errors, data


@app.route("/members")
@login_required
def members():
    q = (request.args.get("q") or "").strip()
    sql = "SELECT * FROM member WHERE 1=1"
    args = []
    if q:
        sql += " AND (roll_no LIKE ? OR name LIKE ? OR email LIKE ?)"
        args += [f"%{q}%"] * 3
    sql += " ORDER BY name"
    conn = db.get_conn()
    rows = conn.execute(sql, args).fetchall()
    conn.close()
    return render_template("members.html", members=rows, q=q)


@app.route("/members/add", methods=["GET", "POST"])
@login_required
def add_member():
    if request.method == "POST":
        errors, data = validate_member_form(request.form)
        if not errors:
            conn = db.get_conn()
            dup = conn.execute("SELECT 1 FROM member WHERE roll_no=? OR email=?", (data["roll_no"], data["email"])).fetchone()
            if dup:
                errors.append("A member with this roll number or email already exists.")
            else:
                conn.execute(
                    "INSERT INTO member (roll_no,name,email,phone,department,semester,membership_type,status,joined_on) VALUES (?,?,?,?,?,?,?,?,date('now'))",
                    (data["roll_no"], data["name"], data["email"], data["phone"], data["department"],
                     data["semester"], data["membership_type"], data["status"]),
                )
                conn.commit()
                conn.close()
                flash("Member added successfully.", "success")
                return redirect(url_for("members"))
            conn.close()
        for e in errors:
            flash(e, "danger")
        return render_template("member_form.html", member=data, mode="add", form=request.form)
    return render_template("member_form.html", member={}, mode="add", form={})


@app.route("/members/<int:member_id>/edit", methods=["GET", "POST"])
@login_required
def edit_member(member_id):
    conn = db.get_conn()
    member = conn.execute("SELECT * FROM member WHERE member_id = ?", (member_id,)).fetchone()
    if not member:
        conn.close()
        abort(404)
    if request.method == "POST":
        errors, data = validate_member_form(request.form)
        if not errors:
            dup = conn.execute(
                "SELECT 1 FROM member WHERE (roll_no=? OR email=?) AND member_id != ?",
                (data["roll_no"], data["email"], member_id)).fetchone()
            if dup:
                errors.append("Another member already uses this roll number or email.")
        if errors:
            for e in errors:
                flash(e, "danger")
            conn.close()
            return render_template("member_form.html", member=request.form, mode="edit", form=request.form, member_id=member_id)
        conn.execute(
            "UPDATE member SET roll_no=?,name=?,email=?,phone=?,department=?,semester=?,membership_type=?,status=? WHERE member_id=?",
            (data["roll_no"], data["name"], data["email"], data["phone"], data["department"],
             data["semester"], data["membership_type"], data["status"], member_id),
        )
        conn.commit()
        conn.close()
        flash("Member updated successfully.", "success")
        return redirect(url_for("members"))
    conn.close()
    return render_template("member_form.html", member=member, mode="edit", form={}, member_id=member_id)


@app.route("/members/<int:member_id>/delete", methods=["POST"])
@login_required
def delete_member(member_id):
    conn = db.get_conn()
    active = conn.execute(
        "SELECT COUNT(*) c FROM issue_transaction WHERE member_id = ? AND status='Issued'", (member_id,)).fetchone()["c"]
    if active:
        conn.close()
        flash(f"Cannot delete: member has {active} unreturned book(s).", "danger")
        return redirect(url_for("members"))
    conn.execute("DELETE FROM member WHERE member_id = ?", (member_id,))
    conn.commit()
    conn.close()
    flash("Member deleted.", "success")
    return redirect(url_for("members"))


# ------------------------------------------------------------- circulation

@app.route("/issue", methods=["GET", "POST"])
@login_required
def issue_book():
    conn = db.get_conn()
    if request.method == "POST":
        try:
            book_id = int(request.form.get("book_id") or 0)
            member_id = int(request.form.get("member_id") or 0)
        except ValueError:
            flash("Invalid selection.", "danger")
            return redirect(url_for("issue_book"))

        book = conn.execute("SELECT * FROM book WHERE book_id = ?", (book_id,)).fetchone()
        member = conn.execute("SELECT * FROM member WHERE member_id = ?", (member_id,)).fetchone()
        ok = True
        if not book or not member:
            flash("Select both a valid book and member.", "danger")
            ok = False
        elif book["available_quantity"] <= 0:
            flash("No copies of this book are currently available.", "danger")
            ok = False
        elif member["status"] != "Active":
            flash("This member is inactive and cannot borrow books.", "danger")
            ok = False
        else:
            held = conn.execute(
                "SELECT COUNT(*) c FROM issue_transaction WHERE member_id=? AND status='Issued'",
                (member_id,)).fetchone()["c"]
            if held >= MAX_ISSUE_PER_MEMBER:
                flash(f"Member already holds {held} book(s); limit is {MAX_ISSUE_PER_MEMBER}.", "danger")
                ok = False
            dup = conn.execute(
                "SELECT 1 FROM issue_transaction WHERE member_id=? AND book_id=? AND status='Issued'",
                (member_id, book_id)).fetchone()
            if dup:
                flash("Member already holds an unreturned copy of this book.", "danger")
                ok = False
        if ok:
            issue_date = date.today()
            due_date = issue_date + timedelta(days=LOAN_DAYS)
            conn.execute(
                "INSERT INTO issue_transaction (book_id,member_id,issue_date,due_date,status,fine_amount) VALUES (?,?,?,?,'Issued',0)",
                (book_id, member_id, issue_date.strftime("%Y-%m-%d"), due_date.strftime("%Y-%m-%d")),
            )
            conn.execute("UPDATE book SET available_quantity = available_quantity - 1 WHERE book_id = ?", (book_id,))
            conn.commit()
            conn.close()
            flash(f"Book issued successfully. Due date: {due_date.strftime('%d-%m-%Y')}.", "success")
            return redirect(url_for("transactions"))
    books_avail = conn.execute("SELECT * FROM book WHERE available_quantity > 0 ORDER BY title").fetchall()
    members_active = conn.execute("SELECT * FROM member WHERE status='Active' ORDER BY name").fetchall()
    conn.close()
    return render_template("issue.html", books=books_avail, members=members_active, loan_days=LOAN_DAYS)


@app.route("/return")
@login_required
def return_book():
    conn = db.get_conn()
    open_txns = [enrich_txn(r) for r in conn.execute(
        """SELECT t.*, b.title, m.name AS member_name, m.roll_no FROM issue_transaction t
           JOIN book b ON b.book_id = t.book_id JOIN member m ON m.member_id = t.member_id
           WHERE t.status='Issued' ORDER BY t.due_date""").fetchall()]
    conn.close()
    return render_template("return.html", txns=open_txns, fine_per_day=FINE_PER_DAY)


@app.route("/return/<int:issue_id>", methods=["POST"])
@login_required
def process_return(issue_id):
    conn = db.get_conn()
    txn = conn.execute("SELECT * FROM issue_transaction WHERE issue_id = ? AND status='Issued'", (issue_id,)).fetchone()
    if not txn:
        conn.close()
        flash("Transaction not found or already returned.", "warning")
        return redirect(url_for("return_book"))
    today = date.today()
    due = date.fromisoformat(txn["due_date"])
    late = max(0, (today - due).days)
    fine = late * FINE_PER_DAY
    conn.execute(
        "UPDATE issue_transaction SET return_date=?, status='Returned', fine_amount=? WHERE issue_id=?",
        (today.strftime("%Y-%m-%d"), fine, issue_id),
    )
    conn.execute("UPDATE book SET available_quantity = available_quantity + 1 WHERE book_id = ?", (txn["book_id"],))
    conn.commit()
    conn.close()
    if fine:
        flash(f"Book returned late by {late} day(s). Fine collected: Rs. {fine}.", "warning")
    else:
        flash("Book returned on time. No fine.", "success")
    return redirect(url_for("transactions"))


@app.route("/transactions")
@login_required
def transactions():
    status = (request.args.get("status") or "All").strip()
    sql = """SELECT t.*, b.title, m.name AS member_name, m.roll_no FROM issue_transaction t
             JOIN book b ON b.book_id = t.book_id JOIN member m ON m.member_id = t.member_id"""
    args = []
    if status in ("Issued", "Returned"):
        sql += " WHERE t.status = ?"
        args.append(status)
    sql += " ORDER BY t.issue_date DESC, t.issue_id DESC"
    conn = db.get_conn()
    rows = [enrich_txn(r) for r in conn.execute(sql, args).fetchall()]
    conn.close()
    return render_template("transactions.html", txns=rows, status=status)


# ------------------------------------------------------------- reports & fines

@app.route("/fines")
@login_required
def fines():
    conn = db.get_conn()
    rows = [enrich_txn(r) for r in conn.execute(
        """SELECT t.*, b.title, m.name AS member_name, m.roll_no FROM issue_transaction t
           JOIN book b ON b.book_id = t.book_id JOIN member m ON m.member_id = t.member_id
           WHERE t.fine_amount > 0 ORDER BY t.return_date DESC""").fetchall()]
    collected = conn.execute("SELECT COALESCE(SUM(fine_amount),0) c FROM issue_transaction").fetchone()["c"]
    pending = sum(enrich_txn(r)["payable_fine"] for r in conn.execute(
        "SELECT t.*, b.title, m.name AS member_name, m.roll_no FROM issue_transaction t JOIN book b ON b.book_id=t.book_id JOIN member m ON m.member_id=t.member_id WHERE t.status='Issued'").fetchall())
    conn.close()
    return render_template("fines.html", fines=rows, collected=collected, pending=pending)


@app.route("/reports")
@login_required
def reports():
    report = (request.args.get("report") or "issued").strip()
    conn = db.get_conn()
    ctx = {"report": report}
    if report == "issued":
        ctx["rows"] = [enrich_txn(r) for r in conn.execute(
            """SELECT t.*, b.title, m.name AS member_name, m.roll_no FROM issue_transaction t
               JOIN book b ON b.book_id=t.book_id JOIN member m ON m.member_id=t.member_id
               WHERE t.status='Issued' ORDER BY t.due_date""").fetchall()]
    elif report == "overdue":
        ctx["rows"] = [enrich_txn(r) for r in conn.execute(
            """SELECT t.*, b.title, m.name AS member_name, m.roll_no FROM issue_transaction t
               JOIN book b ON b.book_id=t.book_id JOIN member m ON m.member_id=t.member_id
               WHERE t.status='Issued' AND t.due_date < date('now') ORDER BY t.due_date""").fetchall()]
    elif report == "fine":
        ctx["rows"] = conn.execute(
            """SELECT b.title, m.roll_no, m.name AS member_name, t.fine_amount, t.return_date
               FROM issue_transaction t
               JOIN book b ON b.book_id=t.book_id JOIN member m ON m.member_id=t.member_id
               WHERE t.fine_amount > 0 ORDER BY t.fine_amount DESC""").fetchall()
        ctx["total"] = conn.execute("SELECT COALESCE(SUM(fine_amount),0) c FROM issue_transaction").fetchone()["c"]
    elif report == "stock":
        ctx["rows"] = conn.execute(
            """SELECT category, COUNT(*) titles, SUM(quantity) copies, SUM(available_quantity) available
               FROM book GROUP BY category ORDER BY category""").fetchall()
    elif report == "member":
        ctx["rows"] = conn.execute(
            """SELECT m.roll_no, m.name AS member_name, COUNT(t.issue_id) total_issues,
                      SUM(CASE WHEN t.status='Issued' THEN 1 ELSE 0 END) open_issues,
                      COALESCE(SUM(t.fine_amount),0) fines
               FROM member m LEFT JOIN issue_transaction t ON t.member_id = m.member_id
               GROUP BY m.member_id ORDER BY total_issues DESC, m.name""").fetchall()
    else:
        return redirect(url_for("reports", report="issued"))
    conn.close()
    return render_template("reports.html", **ctx)


# ------------------------------------------------------------- misc

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


def create_app():
    db.init_db()
    db.seed_if_empty()
    return app


if __name__ == "__main__":
    db.init_db()
    db.seed_if_empty()
    app.run(host="0.0.0.0", port=5000, debug=False)

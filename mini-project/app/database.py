"""
Database layer for SmartLibrary (College Library Management System).
Uses SQLite (file-based, zero-configuration) which satisfies the
'Minimum system requirement' constraint of the SPPU MCA mini-project.
The same schema maps 1:1 to MySQL 8 for production deployments.
"""
import hashlib
import os
import sqlite3
from datetime import date, timedelta

DB_PATH = os.environ.get("SMARTLIB_DB", os.path.join(os.path.dirname(__file__), "smartlibrary.db"))
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    conn = get_conn()
    conn.executescript(schema)
    conn.close()


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def seed_if_empty():
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) AS c FROM book").fetchone()
    if row["c"] > 0:
        conn.close()
        return

    today = date.today()
    fmt = "%Y-%m-%d"

    def d(offset):  # date relative to today
        return (today + timedelta(days=offset)).strftime(fmt)

    books = [
        ("978-0-13-468599-1", "Effective Java", "Joshua Bloch", "Addison-Wesley", "Programming", "3rd Edition", 6, 6, "A-01"),
        ("978-0-13-235088-4", "Clean Code", "Robert C. Martin", "Prentice Hall", "Programming", "1st Edition", 5, 5, "A-02"),
        ("978-0-07-063477-6", "Database System Concepts", "Silberschatz, Korth", "McGraw-Hill", "Database", "7th Edition", 8, 6, "B-01"),
        ("978-0-13-110362-7", "The C Programming Language", "Kernighan, Ritchie", "Prentice Hall", "Programming", "2nd Edition", 5, 5, "A-03"),
        ("978-0-13-468937-6", "Introduction to Algorithms", "Cormen, Leiserson", "MIT Press", "Algorithms", "4th Edition", 4, 4, "C-01"),
        ("978-0-262-03384-8", "Compilers: Principles and Techniques", "Aho, Sethi, Ullman", "Pearson", "Theory of Computation", "2nd Edition", 3, 3, "D-01"),
        ("978-81-317-6094-9", "Let Us C", "Yashavant Kanetkar", "BPB Publications", "Programming", "17th Edition", 10, 8, "A-04"),
        ("978-0-201-60478-8", "The Pragmatic Programmer", "Andrew Hunt, David Thomas", "Addison-Wesley", "Programming", "20th Anniversary", 4, 4, "A-05"),
        ("978-93-530-6712-7", "Java: The Complete Reference", "Herbert Schildt", "McGraw-Hill", "Programming", "12th Edition", 7, 7, "A-06"),
        ("978-0-19-517776-8", "Operating System Concepts", "Silberschatz, Galvin", "Wiley", "Operating Systems", "10th Edition", 6, 5, "B-02"),
        ("978-81-265-7463-9", "Fundamentals of Software Engineering", "Rajib Mall", "PHI Learning", "Software Engineering", "4th Edition", 5, 5, "E-01"),
        ("978-0-07-182512-8", "Object-Oriented Analysis and Design", "Grady Booch", "Pearson", "Software Engineering", "3rd Edition", 4, 4, "E-02"),
    ]

    members = [
        ("MCA2026001", "Yashwant Santosh Ahire", "yashwant@bvhmc.edu.in", "9876543201", "MCA-I", "1", "Student", "Active"),
        ("MCA2026002", "Priya Patil", "priya.patil@bvhmc.edu.in", "9823456701", "MCA-I", "1", "Student", "Active"),
        ("MCA2026003", "Rohit Deshmukh", "rohit.d@bvhmc.edu.in", "9912345602", "MCA-I", "1", "Student", "Active"),
        ("MCA2026004", "Snehal Jadhav", "snehal.j@bvhmc.edu.in", "9765432103", "MCA-I", "1", "Student", "Active"),
        ("MCA2026005", "Aishwarya Gaikwad", "aish.g@bvhmc.edu.in", "9654321076", "MCA-I", "1", "Student", "Active"),
        ("MCA2026006", "Suraj Pawar", "suraj.p@bvhmc.edu.in", "9543210987", "MCA-I", "1", "Student", "Inactive"),
        ("MCA2026007", "Vaishnavi Kulkarni", "vai.k@bvhmc.edu.in", "9432109876", "MCA-I", "1", "Student", "Active"),
        ("FAC2026001", "Prof. Priyanka Jagtap", "p.jagtap@bvhmc.edu.in", "9321098765", "MCA-I", "Faculty", "Faculty", "Active"),
    ]

    conn.executemany(
        "INSERT INTO book (isbn,title,author,publisher,category,edition,quantity,available_quantity,shelf_location) VALUES (?,?,?,?,?,?,?,?,?)",
        books,
    )
    conn.executemany(
        "INSERT INTO member (roll_no,name,email,phone,department,semester,membership_type,status,joined_on) VALUES (?,?,?,?,?,?,?,?,?)",
        [(m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], d(-180)) for m in members],
    )

    # Admin login
    conn.execute(
        "INSERT INTO admin (username,password_hash,full_name) VALUES (?,?,?)",
        ("admin", hash_pw("admin123"), "Library Administrator"),
    )

    # Transactions: a mix of returned-with-fine, returned-clean, currently issued, and overdue.
    # (book_index, member_index, issue_offset, due_offset, return_offset or None, fine_per_day=2)
    txn_seed = [
        (2, 0, -40, -26, -30),  # returned 4 days late -> fine 8
        (0, 1, -35, -21, -23),  # returned before due -> fine 0
        (6, 2, -30, -16, -15),  # returned 1 day late -> fine 2
        (5, 3, -25, -11, None), # still open, overdue by 11 days
        (2, 4, -20, -6, None),  # still open, overdue by 6 days
        (7, 0, -15, 1, None),   # issued, due soon (tomorrow-ish)
        (9, 6, -12, 2, -9),     # returned early -> fine 0
        (4, 1, -10, 4, None),   # currently issued, within due window
        (10, 5, -50, -36, -34), # returned 2 days late -> fine 4 (member since inactive)
        (11, 7, -18, -4, -2),   # returned 2 days late -> fine 4
        (1, 6, -28, -14, None), # OPEN - overdue by ~14 days
        (3, 1, -33, -19, None), # OPEN - overdue by ~19 days
        (10, 1, -44, -30, None),# OPEN - overdue by ~30 days
        (8, 2, -45, -31, -27),  # returned 4 days late -> fine 8
        (0, 4, -38, -24, -20),  # returned 4 days late -> fine 8
    ]
    FINE_PER_DAY = 2
    for (bi, mi, i_off, d_off, r_off) in txn_seed:
        book_id = conn.execute("SELECT book_id FROM book WHERE isbn=?", (books[bi][0],)).fetchone()["book_id"]
        member_id = conn.execute("SELECT member_id FROM member WHERE roll_no=?", (members[mi][0],)).fetchone()["member_id"]
        issue_date, due_date = d(i_off), d(d_off)
        if r_off is None:
            conn.execute(
                "INSERT INTO issue_transaction (book_id,member_id,issue_date,due_date,return_date,status,fine_amount) VALUES (?,?,?,?,NULL,'Issued',0)",
                (book_id, member_id, issue_date, due_date),
            )
        else:
            return_date = date.fromisoformat(d(r_off))
            due = date.fromisoformat(due_date)
            late = max(0, (return_date - due).days)
            conn.execute(
                "INSERT INTO issue_transaction (book_id,member_id,issue_date,due_date,return_date,status,fine_amount) VALUES (?,?,?,?,?,'Returned',?)",
                (book_id, member_id, issue_date, due_date, d(r_off), late * FINE_PER_DAY),
            )

    # Recompute available quantities from open transactions
    conn.execute(
        """UPDATE book SET available_quantity = quantity - (
               SELECT COUNT(*) FROM issue_transaction
               WHERE issue_transaction.book_id = book.book_id AND issue_transaction.status = 'Issued'
           )"""
    )
    conn.commit()
    conn.close()


def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    seed_if_empty()

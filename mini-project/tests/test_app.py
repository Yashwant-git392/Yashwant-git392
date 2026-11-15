"""
SmartLibrary — Unit & Acceptance test-suite (executed with the Flask test client).
Run:  python -m pytest tests/test_app.py -v
"""
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

TEST_DB = os.path.join(tempfile.mkdtemp(), "test_smartlibrary.db")
os.environ["SMARTLIB_DB"] = TEST_DB

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import database as db  # noqa: E402
import app as app_module  # noqa: E402


class SmartLibraryTestCase(unittest.TestCase):
    def setUp(self):
        db.reset_db()
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()

    def login(self):
        return self.client.post("/login", data={"username": "admin", "password": "admin123"},
                                follow_redirects=True)

    # ---------- authentication ----------
    def test_01_login_page_loads(self):
        r = self.client.get("/login")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"SmartLibrary", r.data)

    def test_02_login_rejects_wrong_password(self):
        r = self.client.post("/login", data={"username": "admin", "password": "wrong"})
        self.assertEqual(r.status_code, 401)

    def test_03_login_success_redirects_to_dashboard(self):
        r = self.login()
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Dashboard", r.data)

    def test_04_protected_page_redirects_anonymous(self):
        r = self.client.get("/dashboard", follow_redirects=False)
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.headers["Location"])

    # ---------- book catalogue ----------
    def test_05_seed_data_present(self):
        self.login()
        r = self.client.get("/books")
        self.assertIn(b"Effective Java", r.data)
        self.assertIn(b"Database System Concepts", r.data)

    def test_06_add_book_validation_rejects_bad_isbn(self):
        self.login()
        r = self.client.post("/books/add", data={
            "isbn": "NOTANISBN", "title": "Test Book", "author": "Test Author",
            "category": "Programming", "quantity": "2",
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"valid ISBN", r.data)

    def test_07_add_book_success_and_duplicate_rejected(self):
        self.login()
        payload = {"isbn": "978-81-0000-000-0", "title": "Python Crash Course",
                   "author": "Eric Matthes", "category": "Programming", "quantity": "3"}
        r = self.client.post("/books/add", data=payload, follow_redirects=True)
        self.assertIn(b"Book added successfully", r.data)
        r = self.client.post("/books/add", data=payload)
        self.assertIn(b"already exists", r.data)

    # ---------- members ----------
    def test_08_add_member_rejects_bad_phone(self):
        self.login()
        r = self.client.post("/members/add", data={
            "roll_no": "MCA2026099", "name": "Test Person", "email": "test@bvhmc.edu.in",
            "phone": "12345", "department": "MCA-I", "semester": "1",
            "membership_type": "Student", "status": "Active",
        })
        self.assertIn(b"10-digit", r.data)

    # ---------- circulation ----------
    def test_09_issue_and_return_flow_computes_fine(self):
        self.login()
        conn = db.get_conn()
        book = conn.execute("SELECT book_id, available_quantity FROM book WHERE title='Compilers: Principles and Techniques'").fetchone()
        member = conn.execute("SELECT member_id FROM member WHERE status='Active' LIMIT 1").fetchone()
        conn.close()
        # Issue the book
        r = self.client.post("/issue", data={"book_id": book["book_id"], "member_id": member["member_id"]},
                             follow_redirects=True)
        self.assertIn(b"Book issued successfully", r.data)
        # Back-date the due date to simulate a late return
        conn = db.get_conn()
        txn = conn.execute("SELECT issue_id FROM issue_transaction WHERE status='Issued' "
                           "AND book_id=? AND member_id=? ORDER BY issue_id DESC LIMIT 1",
                           (book["book_id"], member["member_id"])).fetchone()
        late_due = (date.today() - timedelta(days=5)).strftime("%Y-%m-%d")
        conn.execute("UPDATE issue_transaction SET due_date=? WHERE issue_id=?", (late_due, txn["issue_id"]))
        conn.commit()
        conn.close()
        # Return it -> expect Rs. 10 fine (5 late days x Rs. 2)
        r = self.client.post(f"/return/{txn['issue_id']}", follow_redirects=True)
        self.assertIn(b"Rs. 10", r.data)

    def test_10_issue_blocked_for_unavailable_book(self):
        self.login()
        conn = db.get_conn()
        # Book with all copies out: force available_quantity = 0
        conn.execute("UPDATE book SET available_quantity = 0 WHERE title='Effective Java'")
        book = conn.execute("SELECT book_id FROM book WHERE title='Effective Java'").fetchone()
        member = conn.execute("SELECT member_id FROM member WHERE status='Active' LIMIT 1").fetchone()
        conn.commit()
        conn.close()
        r = self.client.post("/issue", data={"book_id": book["book_id"], "member_id": member["member_id"]},
                             follow_redirects=True)
        self.assertIn(b"currently available", r.data)  # blocked with a flash message

    def test_11_reports_render_with_seed_data(self):
        self.login()
        for name in ("issued", "overdue", "fine", "stock", "member"):
            r = self.client.get(f"/reports?report={name}")
            self.assertEqual(r.status_code, 200, name)
            self.assertIn(b"Report", r.data)

    def test_12_change_password_wrong_current(self):
        self.login()
        r = self.client.post("/change-password", data={
            "old_password": "nope", "new_password": "newpass123", "confirm_password": "newpass123",
        }, follow_redirects=True)
        self.assertIn(b"Current password is incorrect", r.data)


if __name__ == "__main__":
    unittest.main()

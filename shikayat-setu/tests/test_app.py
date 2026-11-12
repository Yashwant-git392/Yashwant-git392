"""Campus Shikayat Setu — automated test suite (12 tests)."""
import os
import sys
import tempfile
from datetime import datetime

import pytest

APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
sys.path.insert(0, os.path.abspath(APP_DIR))

import database as db  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_shikayat.db")
    monkeypatch.setenv("SHIKAYAT_DB", test_db)
    monkeypatch.setattr(db, "DB_PATH", test_db)
    db.init_db()
    db.seed_if_empty()
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=False)


def test_01_login_page_loads(client):
    r = client.get("/login")
    assert r.status_code == 200 and b"Campus Shikayat Setu" in r.data


def test_02_wrong_password_rejected(client):
    r = login(client, "admin", "wrongpass")
    assert r.status_code == 401


def test_03_anonymous_redirected_to_login(client):
    r = client.get("/dashboard")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_04_admin_dashboard_after_login(client):
    login(client, "admin", "admin123")
    r = client.get("/dashboard")
    assert r.status_code == 200 and b"Administration Overview" in r.data


def test_05_student_self_registration(client):
    r = client.post("/register", data={
        "full_name": "Test Student", "roll_no": "MCA2026999",
        "email": "test@bvhrcet.ac.in", "phone": "9876500001",
        "password": "test123", "confirm_password": "test123"}, follow_redirects=False)
    assert r.status_code == 302
    r = login(client, "MCA2026999", "test123")
    assert r.status_code == 302


def test_06_duplicate_roll_rejected(client):
    r = client.post("/register", data={
        "full_name": "Duplicate", "roll_no": "MCA2026001",
        "email": "dup@bvhrcet.ac.in", "phone": "9876500002",
        "password": "test123", "confirm_password": "test123"})
    assert r.status_code == 400 and b"already registered" in r.data


def test_07_lodge_routes_leak_to_sanitation(client):
    login(client, "MCA2026002", "student123")
    r = client.post("/lodge", data={
        "title": "Tap leaking heavily in hostel washroom",
        "description": "The tap near the hostel washroom is leaking continuously for three days; floor is wet.",
        "location": "Hostel 2F", "category_id": "3"}, follow_redirects=False)
    assert r.status_code == 302
    from database import get_conn
    conn = get_conn()
    row = conn.execute("SELECT department_id, priority FROM complaints ORDER BY id DESC LIMIT 1").fetchone()
    dept = conn.execute("SELECT name FROM departments WHERE id=?", (row["department_id"],)).fetchone()["name"]
    conn.close()
    assert dept == "Sanitation & Maintenance"


def test_08_safety_keyword_forces_high_priority(client):
    login(client, "MCA2026003", "student123")
    r = client.post("/lodge", data={
        "title": "Stray electric shock risk near switchboard",
        "description": "A loose wire near the switchboard is giving mild shock; unsafe for all classmates.",
        "location": "Lab 2", "category_id": "2"}, follow_redirects=False)
    assert r.status_code == 302
    from database import get_conn
    conn = get_conn()
    row = conn.execute("SELECT priority FROM complaints ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    assert row["priority"] == "High"


def test_09_officer_sees_only_own_department(client):
    login(client, "it.officer", "officer123")
    r = client.get("/queue")
    assert r.status_code == 200
    assert b"CMP-" in r.data
    # it.officer must not see the ragging complaint (welfare department)
    assert b"Ragging in hostel staircase" not in r.data


def test_10_full_resolution_cycle(client):
    login(client, "MCA2026002", "student123")
    r = client.post("/lodge", data={
        "title": "Dustbin overflowing near canteen",
        "description": "The dustbin near the canteen has not been emptied for two days; very smelly.",
        "location": "Canteen", "category_id": "6"}, follow_redirects=False)
    assert r.status_code == 302
    from database import get_conn
    conn = get_conn(); code = conn.execute("SELECT code FROM complaints ORDER BY id DESC LIMIT 1").fetchone()["code"]; conn.close()
    client.get("/logout")
    login(client, "maint.officer", "officer123")
    client.post(f"/complaint/{code}/acknowledge")
    client.post(f"/complaint/{code}/progress")
    r = client.post(f"/complaint/{code}/resolve", data={"remark": "Dustbin emptied and replaced with a bigger bin."})
    assert r.status_code == 302
    client.get("/logout")
    login(client, "MCA2026002", "student123")
    r = client.post(f"/complaint/{code}/feedback", data={"rating": "5", "comment": "Thanks!"})
    assert r.status_code == 302
    conn = get_conn(); row = conn.execute("SELECT status FROM complaints WHERE code=?", (code,)).fetchone(); conn.close()
    assert row["status"] == "Closed"


def test_11_student_cannot_open_console(client):
    login(client, "MCA2026002", "student123")
    r = client.get("/console")
    assert r.status_code == 403


def test_12_reports_render_for_admin(client):
    login(client, "admin", "admin123")
    for which in ("pendency", "sla", "restime", "trend", "feedback", "routing"):
        r = client.get(f"/reports?report={which}")
        assert r.status_code == 200, which


def test_keyword_scoring_and_tie_break():
    import routing
    categories = [{"keywords": "water leak"}, {"keywords": "water leak"}]
    text = routing.route_text("Water leak", "A water leak in the building")
    category, score = routing.route(text, categories)
    assert category is categories[0]
    assert score == 12
    assert routing.route("unrelated", categories) == (None, 0)
    assert routing.score_category("leaking", "leak") == 0


def test_priority_rules():
    import routing
    assert routing.assign_priority("Low", "Question", "For all students") == "Medium"
    assert routing.assign_priority("Low", "Question", "There is a fire") == "High"
    assert routing.assign_priority("High", "Question", "For everyone") == "High"


def test_seeded_officers_are_assigned_to_departments(client):
    conn = db.get_conn()
    rows = conn.execute("""SELECT u.username, d.name FROM users u
                           JOIN departments d ON d.id = u.department_id
                           WHERE u.role = 'officer'""").fetchall()
    conn.close()
    officer_names = ["hostel.officer", "it.officer", "maint.officer", "exam.officer", "welfare.officer", "admin.officer"]
    expected = {username: department[0] for username, department in zip(officer_names, db.DEPARTMENTS)}
    assert {row["username"]: row["name"] for row in rows} == expected

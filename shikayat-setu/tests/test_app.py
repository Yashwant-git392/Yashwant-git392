"""Campus Shikayat Setu — automated test suite."""
import os
import re
import sqlite3
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


def csrf_token(client):
    response = client.get("/login")
    match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
    assert match, "login form must include a CSRF token"
    return match.group(1).decode()


def post(client, url, data=None, **kwargs):
    payload = dict(data or {})
    payload["csrf_token"] = csrf_token(client)
    return client.post(url, data=payload, **kwargs)


def login(client, username, password):
    return post(client, "/login", data={"username": username, "password": password}, follow_redirects=False)


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
    r = post(client, "/register", data={
        "full_name": "Test Student", "roll_no": "MCA2026999",
        "email": "test@bvhrcet.ac.in", "phone": "9876500001",
        "password": "test123", "confirm_password": "test123"}, follow_redirects=False)
    assert r.status_code == 302
    r = login(client, "MCA2026999", "test123")
    assert r.status_code == 302


def test_06_duplicate_roll_rejected(client):
    r = post(client, "/register", data={
        "full_name": "Duplicate", "roll_no": "MCA2026001",
        "email": "dup@bvhrcet.ac.in", "phone": "9876500002",
        "password": "test123", "confirm_password": "test123"})
    assert r.status_code == 400 and b"already registered" in r.data


def test_07_lodge_routes_leak_to_sanitation(client):
    login(client, "MCA2026002", "student123")
    r = post(client, "/lodge", data={
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
    r = post(client, "/lodge", data={
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
    r = post(client, "/lodge", data={
        "title": "Dustbin overflowing near canteen",
        "description": "The dustbin near the canteen has not been emptied for two days; very smelly.",
        "location": "Canteen", "category_id": "6"}, follow_redirects=False)
    assert r.status_code == 302
    from database import get_conn
    conn = get_conn(); code = conn.execute("SELECT code FROM complaints ORDER BY id DESC LIMIT 1").fetchone()["code"]; conn.close()
    post(client, "/logout")
    login(client, "maint.officer", "officer123")
    post(client, f"/complaint/{code}/acknowledge")
    post(client, f"/complaint/{code}/progress")
    r = post(client, f"/complaint/{code}/resolve", data={"remark": "Dustbin emptied and replaced with a bigger bin."})
    assert r.status_code == 302
    post(client, "/logout")
    login(client, "MCA2026002", "student123")
    r = post(client, f"/complaint/{code}/feedback", data={"rating": "5", "comment": "Thanks!"})
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


def test_routing_preview_matches_submitted_complaint(client):
    login(client, "MCA2026002", "student123")
    data = {"title": "Tap leaking heavily in hostel washroom",
            "description": "The tap near the hostel washroom is leaking continuously for three days; floor is wet.",
            "category_id": "3", "location": "Hostel 2F"}
    preview = client.get("/api/route-preview", query_string=data)
    assert preview.status_code == 200
    expected = preview.get_json()
    assert post(client, "/lodge", data=data).status_code == 302
    conn = db.get_conn()
    actual = conn.execute("""SELECT cat.name AS category, d.name AS department, c.priority, c.routing_score
                             FROM complaints c JOIN categories cat ON cat.id=c.category_id
                             JOIN departments d ON d.id=c.department_id
                             ORDER BY c.id DESC LIMIT 1""").fetchone()
    conn.close()
    assert all(expected[key] == actual[key] for key in ("category", "department", "priority"))
    assert expected["score"] == actual["routing_score"]


def test_routing_preview_uses_selected_category_when_no_keywords_match(client):
    login(client, "MCA2026002", "student123")
    data = {"title": "A puzzling matter", "description": "Nothing specific can be identified here.", "category_id": "1"}
    preview = client.get("/api/route-preview", query_string=data)
    assert preview.status_code == 200
    expected = preview.get_json()
    assert expected["score"] == 0
    assert post(client, "/lodge", data=data).status_code == 302
    conn = db.get_conn()
    actual = conn.execute("""SELECT cat.name AS category, d.name AS department, c.priority
                             FROM complaints c JOIN categories cat ON cat.id=c.category_id
                             JOIN departments d ON d.id=c.department_id
                             ORDER BY c.id DESC LIMIT 1""").fetchone()
    conn.close()
    assert all(expected[key] == actual[key] for key in ("category", "department", "priority"))
    assert client.get("/api/route-preview", query_string={"category_id": "999999"}).status_code == 400


def test_ui_uses_local_assets_and_marks_current_page(client):
    login(client, "MCA2026002", "student123")
    response = client.get("/lodge")
    assert response.status_code == 200
    assert b'fonts.googleapis.com' not in response.data
    assert b'aria-current="page"' in response.data
    assert b'Your identity is hidden from department officers' in response.data
    assert b'aria-describedby="title-hint title-count"' in response.data


def test_anonymous_student_event_actor_hidden_from_officer(client):
    login(client, "MCA2026002", "student123")
    data = {"title": "Leaking tap near washroom",
            "description": "The hostel washroom tap is leaking and the floor is wet.",
            "category_id": "3", "is_anonymous": "on"}
    assert post(client, "/lodge", data=data).status_code == 302
    conn = db.get_conn()
    row = conn.execute("SELECT code, student_id FROM complaints ORDER BY id DESC LIMIT 1").fetchone()
    student_name = conn.execute("SELECT full_name FROM users WHERE id=?", (row["student_id"],)).fetchone()["full_name"]
    code = row["code"]
    conn.close()
    post(client, "/logout")
    login(client, "maint.officer", "officer123")
    response = client.get(f"/complaint/{code}")
    assert response.status_code == 200
    assert student_name.encode() not in response.data
    assert b"Anonymous" in response.data
    post(client, "/logout")
    login(client, "admin", "admin123")
    assert student_name.encode() in client.get(f"/complaint/{code}").data


def test_csrf_rejects_missing_invalid_and_cross_session_tokens(client):
    from app import app
    assert client.post('/login', data={'username': 'admin', 'password': 'admin123'}).status_code == 400
    assert client.post('/register', data={'csrf_token': 'invalid'}).status_code == 400
    token = csrf_token(client)
    other = app.test_client()
    csrf_token(other)
    assert other.post('/login', data={'username': 'admin', 'password': 'admin123', 'csrf_token': token}).status_code == 400
    assert login(client, 'admin', 'admin123').status_code == 302
    conn = db.get_conn()
    complaint = conn.execute("SELECT code, status FROM complaints WHERE status='Resolved' LIMIT 1").fetchone()
    conn.close()
    url = f"/complaint/{complaint['code']}/force-close"
    assert client.post(url).status_code == 400
    assert client.post(url, data={'csrf_token': 'invalid'}).status_code == 400
    conn = db.get_conn()
    assert conn.execute('SELECT status FROM complaints WHERE code=?', (complaint['code'],)).fetchone()['status'] == 'Resolved'
    conn.close()
    assert post(client, url).status_code == 302
    conn = db.get_conn()
    assert conn.execute('SELECT status FROM complaints WHERE code=?', (complaint['code'],)).fetchone()['status'] == 'Closed'
    conn.close()
    assert client.get('/logout').status_code == 405
    assert client.post('/logout').status_code == 400
    assert post(client, '/logout').status_code == 302


def test_post_forms_have_csrf_tokens(client):
    from html.parser import HTMLParser

    class FormParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.forms = []
            self.current = None
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'form':
                self.current = {'method': attrs.get('method', 'get').lower(), 'token': False}
                self.forms.append(self.current)
            elif tag == 'input' and self.current is not None and attrs.get('name') == 'csrf_token':
                self.current['token'] = bool(attrs.get('value'))
        def handle_endtag(self, tag):
            if tag == 'form':
                self.current = None

    paths = ['/login', '/register', '/track']
    login(client, 'admin', 'admin123')
    conn = db.get_conn()
    code = conn.execute("SELECT code FROM complaints WHERE status='Submitted' LIMIT 1").fetchone()['code']
    conn.close()
    paths += ['/dashboard', '/users', '/console', '/change-password', f'/complaint/{code}']
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200, path
        parser = FormParser()
        parser.feed(response.get_data(as_text=True))
        assert all(f['token'] for f in parser.forms if f['method'] == 'post'), path
    post(client, '/logout')
    login(client, 'MCA2026001', 'student123')
    conn = db.get_conn()
    code = conn.execute("""SELECT c.code FROM complaints c JOIN users u ON c.student_id=u.id
                           WHERE u.username='MCA2026001' AND c.status='Resolved' LIMIT 1""").fetchone()['code']
    conn.close()
    for path in ['/lodge', f'/complaint/{code}']:
        parser = FormParser()
        parser.feed(client.get(path).get_data(as_text=True))
        assert all(f['token'] for f in parser.forms if f['method'] == 'post'), path


@pytest.mark.parametrize('timestamp', [None, 'not-a-date'])
def test_reopen_rejects_invalid_resolution_timestamp(client, timestamp):
    login(client, 'MCA2026001', 'student123')
    conn = db.get_conn()
    code = conn.execute("""SELECT c.code FROM complaints c JOIN users u ON c.student_id=u.id
                           WHERE u.username='MCA2026001' AND c.status='Resolved' LIMIT 1""").fetchone()['code']
    conn.execute('UPDATE complaints SET resolved_at=? WHERE code=?', (timestamp, code))
    conn.commit()
    before = conn.execute("SELECT COUNT(*) FROM complaint_events WHERE event_type='reopened' AND complaint_id=(SELECT id FROM complaints WHERE code=?)", (code,)).fetchone()[0]
    conn.close()
    response = post(client, f'/complaint/{code}/reopen', data={'reason': 'The issue is still present'}, follow_redirects=True)
    assert b'Resolution time is unavailable or invalid' in response.data
    conn = db.get_conn()
    assert conn.execute('SELECT status FROM complaints WHERE code=?', (code,)).fetchone()['status'] == 'Resolved'
    assert conn.execute("SELECT COUNT(*) FROM complaint_events WHERE event_type='reopened' AND complaint_id=(SELECT id FROM complaints WHERE code=?)", (code,)).fetchone()[0] == before
    conn.close()


def test_reopen_age_valid_and_expired(client):
    from datetime import timedelta
    login(client, 'MCA2026001', 'student123')
    conn = db.get_conn()
    code = conn.execute("""SELECT c.code FROM complaints c JOIN users u ON c.student_id=u.id
                           WHERE u.username='MCA2026001' AND c.status='Resolved' LIMIT 1""").fetchone()['code']
    conn.execute('UPDATE complaints SET resolved_at=? WHERE code=?', ((datetime.now()-timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S'), code))
    conn.commit()
    conn.close()
    response = post(client, f'/complaint/{code}/reopen', data={'reason': 'The issue is still present'}, follow_redirects=True)
    assert b'Reopen window' in response.data
    conn = db.get_conn()
    assert conn.execute('SELECT status FROM complaints WHERE code=?', (code,)).fetchone()['status'] == 'Resolved'
    conn.execute('UPDATE complaints SET resolved_at=? WHERE code=?', ((datetime.now()-timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), code))
    conn.commit()
    conn.close()
    post(client, f'/complaint/{code}/reopen', data={'reason': 'The issue is still present'})
    conn = db.get_conn()
    assert conn.execute('SELECT status FROM complaints WHERE code=?', (code,)).fetchone()['status'] == 'In Progress'
    conn.close()


def test_request_db_rolls_back_and_closes_after_exception(client, monkeypatch):
    import app as application
    login(client, 'admin', 'admin123')
    conn = db.get_conn()
    complaint = conn.execute("SELECT code, status FROM complaints WHERE status='Submitted' LIMIT 1").fetchone()
    conn.close()
    token = csrf_token(client)
    opened = []
    original_connect = db.get_conn
    def tracked_connect():
        conn = original_connect()
        opened.append(conn)
        return conn
    def fail_event(*args, **kwargs):
        raise RuntimeError('simulated event failure')
    monkeypatch.setattr(db, 'get_conn', tracked_connect)
    monkeypatch.setattr(application, 'log_event', fail_event)
    with pytest.raises(RuntimeError, match='simulated event failure'):
        client.post(f"/complaint/{complaint['code']}/acknowledge", data={'csrf_token': token})
    assert len(opened) == 1  # helpers share the same request-scoped connection
    with pytest.raises(sqlite3.ProgrammingError, match='closed'):
        opened[0].execute('SELECT 1')
    check = original_connect()
    assert check.execute('SELECT status FROM complaints WHERE code=?', (complaint['code'],)).fetchone()['status'] == 'Submitted'
    check.close()


def test_seed_failure_rolls_back_all_seed_inserts(tmp_path, monkeypatch):
    path = str(tmp_path / 'failed-seed.db')
    monkeypatch.setattr(db, 'DB_PATH', path)
    db.init_db()
    def fail_hash(*args, **kwargs):
        raise RuntimeError('simulated seed failure')
    monkeypatch.setattr(db, 'generate_password_hash', fail_hash)
    with pytest.raises(RuntimeError, match='simulated seed failure'):
        db.seed_if_empty()
    conn = db.get_conn()
    assert conn.execute('SELECT COUNT(*) FROM departments').fetchone()[0] == 0
    assert conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0] == 0
    assert conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0
    conn.close()


def test_secret_and_invalid_port_configuration(tmp_path):
    import subprocess
    env = os.environ.copy()
    env['SHIKAYAT_SECRET_KEY'] = 'test-secret-from-environment'
    env['SHIKAYAT_PORT'] = 'not-a-port'
    env['SHIKAYAT_DB'] = str(tmp_path / 'config.db')
    project = os.path.abspath(os.path.join(APP_DIR, '..'))
    env['PYTHONPATH'] = os.path.abspath(APP_DIR) + os.pathsep + env.get('PYTHONPATH', '')
    result = subprocess.run([sys.executable, '-c',
                             "import os; from app import app; assert app.secret_key == os.environ['SHIKAYAT_SECRET_KEY']"],
                            cwd=project, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    result = subprocess.run([sys.executable, 'run.py'], cwd=project, env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'SHIKAYAT_PORT must be an integer between 1 and 65535' in result.stderr

"""Broader isolated checks for access, lifecycle, data validation and reporting."""
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from flask import template_rendered
from werkzeug.security import check_password_hash

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
import database as db
import routing
from app import app


@pytest.fixture(scope='module')
def baseline(tmp_path_factory):
    path = tmp_path_factory.mktemp('baseline') / 'seed.db'
    old = db.DB_PATH
    try:
        db.DB_PATH = str(path)
        db.init_db()
        db.seed_if_empty()
    finally:
        db.DB_PATH = old
    return path


@pytest.fixture
def env(tmp_path, monkeypatch, baseline):
    path = tmp_path / 'test.db'
    shutil.copyfile(baseline, path)
    monkeypatch.setattr(db, 'DB_PATH', str(path))
    monkeypatch.setenv('SHIKAYAT_DB', str(path))
    monkeypatch.setitem(app.config, 'TESTING', True)
    return app.test_client()


def token(client):
    response = client.get('/login')
    match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
    assert match
    return match.group(1).decode()


def post(client, url, data=None, **options):
    return client.post(url, data={**(data or {}), 'csrf_token': token(client)}, **options)


def login(client, name, password):
    assert post(client, '/login', {'username': name, 'password': password}).status_code == 302


def complaint(client, category='5', title='Hostel room furniture broken', anonymous=False):
    login(client, 'MCA2026001', 'student123')
    result = post(client, '/lodge', {'title': title, 'description': 'Hostel room furniture needs repair urgently.',
                                     'category_id': category, 'is_anonymous': 'on' if anonymous else ''})
    assert result.status_code == 302
    conn = db.get_conn()
    row = conn.execute('SELECT * FROM complaints ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    post(client, '/logout')
    return dict(row)


def state(code):
    conn = db.get_conn()
    c = dict(conn.execute('SELECT * FROM complaints WHERE code=?', (code,)).fetchone())
    events = conn.execute('SELECT event_type, note, actor_id FROM complaint_events WHERE complaint_id=? ORDER BY id', (c['id'],)).fetchall()
    conn.close()
    return c, [tuple(e) for e in events]


def set_state(code, status):
    conn = db.get_conn()
    conn.execute('UPDATE complaints SET status=?, resolved_at=? WHERE code=?',
                 (status, datetime.now().strftime('%Y-%m-%d %H:%M:%S') if status in ('Resolved', 'Closed') else None, code))
    conn.commit(); conn.close()


@pytest.mark.parametrize('status,action,allowed,new_status', [
    (status, action, status in allowed, result if status in allowed else status)
    for action, allowed, result in [
        ('acknowledge', ('Submitted',), 'Acknowledged'),
        ('progress', ('Submitted', 'Acknowledged'), 'In Progress'),
        ('resolve', ('Submitted', 'Acknowledged', 'In Progress'), 'Resolved'),
        ('force-close', ('Resolved',), 'Closed'),
    ]
    for status in ('Submitted', 'Acknowledged', 'In Progress', 'Resolved', 'Closed')
])
def test_state_transition_matrix(env, status, action, allowed, new_status):
    c = complaint(env)
    login(env, 'admin', 'admin123')
    set_state(c['code'], status)
    before, events_before = state(c['code'])
    response = post(env, '/complaint/' + c['code'] + '/' + action,
                    {'remark': 'Repaired and checked by officer.'})
    assert response.status_code == 302
    after, events_after = state(c['code'])
    assert after['status'] == new_status
    assert len(events_after) == len(events_before) + (1 if allowed else 0)
    if not allowed:
        assert after == before


@pytest.mark.parametrize('account,role,access', [
    ('MCA2026001', 'student', [200,200,403,403,403,403]),
    ('hostel.officer', 'officer', [200,403,200,403,403,403]),
    ('admin', 'admin', [200,403,200,200,200,200]),
])
def test_role_page_matrix(env, account, role, access):
    login(env, account, {'student':'student123', 'officer':'officer123', 'admin':'admin123'}[role])
    pages = ['/dashboard', '/lodge', '/queue', '/console', '/users', '/reports']
    assert [env.get(p).status_code for p in pages] == access


def test_cross_user_and_department_access_is_denied(env):
    c = complaint(env)
    path = '/complaint/' + c['code']
    login(env, 'MCA2026002', 'student123')
    assert env.get(path).status_code == 403
    assert post(env, path + '/reopen', {'reason':'The issue remains unresolved'}).status_code == 403
    assert post(env, path + '/feedback', {'rating':'5'}).status_code == 403
    post(env, '/logout')
    login(env, 'it.officer', 'officer123')
    assert env.get(path).status_code == 403
    for action in ('acknowledge', 'progress', 'resolve', 'remark'):
        assert post(env, path + '/' + action, {'remark':'A valid longer resolution remark', 'note':'A valid note'}).status_code == 403
    assert post(env, path + '/reassign', {'department_id':'2'}).status_code == 403
    assert state(c['code'])[0]['status'] == 'Submitted'


def test_csrf_blocks_every_mutating_endpoint(env):
    c = complaint(env)
    login(env, 'admin', 'admin123')
    before, events = state(c['code'])
    paths = ['/logout', '/register', '/lodge', '/track', '/change-password', '/users/officer', '/users/2/toggle']
    paths += ['/complaint/' + c['code'] + '/' + a for a in
              ('acknowledge','progress','resolve','remark','feedback','reopen','reassign','escalate','force-close')]
    for path in paths:
        assert env.post(path, data={}).status_code == 400, path
    assert state(c['code']) == (before, events)


@pytest.mark.parametrize('field,value', [
    ('full_name', 'ab'), ('roll_no', 'MCA20269999'), ('roll_no', 'MCA2026١٢٣'),
    ('email', 'bad-address'), ('phone', '1234567890'), ('phone', '9८७६५४३२१०'),
    ('password', 'short'), ('confirm_password', 'different'),
])
def test_registration_invalid_inputs_do_not_create_user(env, field, value):
    data = {'full_name':'New Student', 'roll_no':'MCA2026999', 'email':'test@example.com',
            'phone':'9876543210', 'password':'abc123', 'confirm_password':'abc123'}
    data[field] = value
    assert post(env, '/register', data).status_code == 400
    conn = db.get_conn()
    assert conn.execute('SELECT 1 FROM users WHERE roll_no=?', (data['roll_no'].upper(),)).fetchone() is None
    conn.close()


def test_registration_duplicate_and_password_change(env):
    data = {'full_name':'New Student', 'roll_no':'mca2026999', 'email':'test@example.com',
            'phone':'9876543210', 'password':'abc123', 'confirm_password':'abc123'}
    assert post(env, '/register', data).status_code == 302
    assert post(env, '/register', data).status_code == 400
    login(env, 'MCA2026999', 'abc123')
    for d in [
        {'current_password':'wrong', 'new_password':'newpass1', 'confirm_password':'newpass1'},
        {'current_password':'abc123', 'new_password':'short', 'confirm_password':'short'},
        {'current_password':'abc123', 'new_password':'newpass1', 'confirm_password':'different'},
    ]:
        assert post(env, '/change-password', d).status_code == 200
    assert post(env, '/change-password', {'current_password':'abc123','new_password':'newpass1','confirm_password':'newpass1'}).status_code == 302
    post(env, '/logout')
    assert post(env, '/login', {'username':'MCA2026999','password':'abc123'}).status_code == 401
    login(env, 'MCA2026999', 'newpass1')
    conn = db.get_conn(); row = conn.execute("SELECT password_hash FROM users WHERE roll_no='MCA2026999'").fetchone(); conn.close()
    assert row[0] != 'newpass1' and check_password_hash(row[0], 'newpass1')


@pytest.mark.parametrize('field,value', [('title','short'), ('description','too short'), ('category_id','999999'), ('category_id','²')])
def test_lodge_validation_no_partial_insert(env, field, value):
    login(env, 'MCA2026001', 'student123')
    conn = db.get_conn(); count = conn.execute('SELECT COUNT(*) FROM complaints').fetchone()[0]; conn.close()
    data = {'title':'Valid subject here', 'description':'A sufficiently long complaint description.', 'category_id':'1'}
    data[field] = value
    assert post(env, '/lodge', data).status_code == 400
    conn = db.get_conn(); assert conn.execute('SELECT COUNT(*) FROM complaints').fetchone()[0] == count; conn.close()


def test_valid_routing_preview_sla_and_escaping(env):
    login(env, 'MCA2026001', 'student123')
    data = {'title':'<script>alert(1)</script> room', 'description':'Hostel room furniture is broken. <img src=x onerror=alert(2)>', 'category_id':'5'}
    preview = env.get('/api/route-preview', query_string=data).get_json()
    assert post(env, '/lodge', data).status_code == 302
    conn = db.get_conn(); c=conn.execute('SELECT * FROM complaints ORDER BY id DESC LIMIT 1').fetchone(); conn.close()
    assert c['priority'] == preview['priority']
    assert (datetime.strptime(c['sla_due_at'],'%Y-%m-%d %H:%M:%S') - datetime.strptime(c['submitted_at'],'%Y-%m-%d %H:%M:%S')).total_seconds() == preview['sla_hours'] * 3600
    body = env.get('/complaint/' + c['code']).data
    assert b'<script>alert(1)</script>' not in body and b'&lt;script&gt;alert(1)&lt;/script&gt;' in body
    assert b'<img src=x onerror=alert(2)>' not in body


def test_tracking_code_and_roll_and_sql_injection(env):
    c = complaint(env, anonymous=True)
    path = '/track'
    r = post(env, path, {'code':c['code'], 'roll_no':'MCA2026002'})
    assert b'Roll number does not match' in r.data and c['title'].encode() not in r.data
    r = post(env, path, {'code':c['code'], 'roll_no':"' OR 1=1 --"})
    assert b'Roll number does not match' in r.data and c['title'].encode() not in r.data
    r = post(env, path, {'code':c['code'].lower(), 'roll_no':'mca2026001'})
    assert c['title'].encode() in r.data and b'Yashwant Santosh Ahire' not in r.data
    assert b'No complaint found' in post(env, path, {'code':"' OR 1=1 --",'roll_no':'MCA2026001'}).data


def test_admin_reassignment_and_escalation_preserve_sla(env):
    c = complaint(env)
    login(env, 'admin', 'admin123')
    path = '/complaint/' + c['code']
    old, events = state(c['code'])
    post(env, path+'/reassign', {'department_id':'999999'})
    assert state(c['code']) == (old, events)
    post(env, path+'/reassign', {'department_id':'2'})
    post(env, path+'/escalate')
    new, events = state(c['code'])
    assert new['department_id'] == 2 and new['category_id'] == old['category_id']
    assert new['routing'] == 'manual' and new['priority'] == 'High' and new['sla_due_at'] == old['sla_due_at']
    assert events[-2][0] == 'reassign' and events[-1][0] == 'escalated'
    post(env, '/logout'); login(env, 'hostel.officer', 'officer123')
    assert env.get(path).status_code == 403
    post(env, '/logout'); login(env, 'it.officer', 'officer123')
    assert env.get(path).status_code == 200


def test_admin_officer_creation_activation_and_protected_admin(env):
    login(env, 'admin', 'admin123')
    d={'full_name':'New Officer','department_id':'1','username':'New.Officer','password':'newpass'}
    post(env, '/users/officer', d)
    conn=db.get_conn(); officer=conn.execute("SELECT * FROM users WHERE username='new.officer'").fetchone(); admin=conn.execute("SELECT * FROM users WHERE username='admin'").fetchone(); conn.close()
    assert officer and officer['department_id'] == 1 and check_password_hash(officer['password_hash'],'newpass')
    assert b'Username already exists' in post(env, '/users/officer', d, follow_redirects=True).data
    post(env, '/users/%d/toggle' % admin['id'])
    post(env, '/users/%d/toggle' % officer['id'])
    post(env, '/logout')
    assert post(env, '/login', {'username':'new.officer','password':'newpass'}).status_code == 403
    login(env, 'admin', 'admin123'); post(env, '/users/%d/toggle' % officer['id']); post(env, '/logout')
    login(env, 'new.officer', 'newpass')
    assert env.get('/queue').status_code == 200


def test_oversized_integer_user_id_does_not_crash(env):
    login(env, 'admin', 'admin123')
    assert post(env, '/users/999999999999999999999999999999/toggle').status_code == 404



def test_officer_short_password_rejected(env):
    login(env, 'admin', 'admin123')
    response = post(env, '/users/officer', {'full_name':'Valid Officer', 'department_id':'1', 'username':'short.officer', 'password':'abc'}, follow_redirects=True)
    assert b'password must be at least 6 characters' in response.data
    conn = db.get_conn()
    assert conn.execute("SELECT 1 FROM users WHERE username='short.officer'").fetchone() is None
    conn.close()
    assert b'type="password" name="password"' in env.get('/users').data


@pytest.mark.parametrize('status', ['Submitted', 'Acknowledged', 'In Progress', 'Closed'])
def test_student_feedback_and_reopen_require_resolved(env, status):
    c = complaint(env)
    set_state(c['code'], status)
    login(env, 'MCA2026001', 'student123')
    original = state(c['code'])
    post(env, '/complaint/' + c['code'] + '/feedback', {'rating':'5'})
    post(env, '/complaint/' + c['code'] + '/reopen', {'reason':'The problem is still present.'})
    assert state(c['code']) == original


def test_resolution_remark_feedback_rating_and_reopen_reason_validated(env):
    c = complaint(env)
    login(env, 'hostel.officer', 'officer123')
    path = '/complaint/' + c['code']
    original = state(c['code'])
    post(env, path + '/resolve', {'remark':'short'})
    assert state(c['code']) == original
    post(env, path + '/resolve', {'remark':'The furniture was repaired.'})
    post(env, '/logout'); login(env, 'MCA2026001', 'student123')
    original = state(c['code'])
    for rating in ('0', '6', 'bad', ''):
        post(env, path + '/feedback', {'rating':rating})
    post(env, path + '/reopen', {'reason':'short'})
    assert state(c['code']) == original
    post(env, path + '/reopen', {'reason':'The furniture is still broken.'})
    assert state(c['code'])[0]['status'] == 'In Progress'


def test_queue_and_console_server_filters(env):
    login(env, 'admin', 'admin123')
    contexts=[]
    def capture(sender, template, context, **extra): contexts.append(context)
    with template_rendered.connected_to(capture,app):
        assert env.get('/queue?department_id=1&status=Submitted').status_code == 200
        assert all(r['department_id']==1 and r['status']=='Submitted' for r in contexts[-1]['rows'])
        assert env.get('/console?department_id=1&status=Submitted&priority=High').status_code == 200
        assert all(r['department_id']==1 and r['status']=='Submitted' and r['priority']=='High' for r in contexts[-1]['rows'])


def test_reports_on_controlled_dataset(env):
    login(env, 'admin', 'admin123')
    conn=db.get_conn()
    conn.execute('DELETE FROM feedback'); conn.execute('DELETE FROM complaint_events'); conn.execute('DELETE FROM complaints')
    student=conn.execute("SELECT id FROM users WHERE username='MCA2026001'").fetchone()[0]
    for i, (status, resolved, priority, routing_mode) in enumerate([
        ('Submitted', None, 'High','auto'), ('In Progress',None,'Low','manual'),
        ('Resolved','2026-01-01 12:00:00','Medium','auto'), ('Closed','2026-01-04 00:00:00','Medium','manual'),
        ('Resolved','2026-01-01 08:00:00','Low','auto')], 1):
        conn.execute('''INSERT INTO complaints (code, student_id, category_id, department_id, title, description, priority, routing, routing_score, status, submitted_at, sla_due_at, resolved_at)
                        VALUES (?,?,5,1,?,?,?,?,?,?, '2026-01-01 00:00:00', '2026-01-02 00:00:00', ?)''',
                     (f'REPORT-{i}', student, f'Title {i}', 'Description', priority, routing_mode, i, status, resolved))
    closed=conn.execute("SELECT id FROM complaints WHERE code='REPORT-4'").fetchone()[0]
    conn.execute('INSERT INTO feedback (complaint_id,rating,comment) VALUES (?,4,?)',(closed,'Helpful'))
    conn.commit();conn.close()
    contexts=[]
    def capture(sender, template, context, **extra): contexts.append(context)
    with template_rendered.connected_to(capture,app):
        def report(which):
            assert env.get('/reports?report='+which).status_code == 200
            return contexts[-1]
        row = next(x for x in report('pendency')['rows'] if x['dept']=='Hostel Office')
        assert (row['submitted'],row['in_progress'],row['resolved'],row['closed'],row['total'])==(1,1,2,1,5)
        row = next(x for x in report('sla')['rows'] if x['dept']=='Hostel Office')
        assert (row['resolved_total'],row['within_sla'],row['pct']) == (3,2,66.7)
        row = next(x for x in report('restime')['rows'] if x['category']=='Hostel Room & Mess')
        assert (row['n'],row['avg_hours']) == (3, 30.7)
        row = report('trend')['rows'][0]; assert (row['month'],row['lodged'],row['resolved']) == ('2026-01',5,3)
        row = report('feedback')['rows'][0]; assert (row['avg_rating'],row['n']) == (4.0,1)
        rows = {r['routing']:r['n'] for r in report('routing')['rows']}; assert rows == {'auto':3,'manual':2}


def test_seed_is_idempotent_and_foreign_keys_enforced(env):
    conn=db.get_conn(); counts={t:conn.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('users','complaints','categories','departments','complaint_events','feedback')};conn.close()
    db.init_db();db.seed_if_empty()
    conn=db.get_conn(); assert counts == {t:conn.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in counts}
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE complaints SET department_id=999999 WHERE id=(SELECT MIN(id) FROM complaints)")
    conn.close()


def test_safety_and_mass_impact_and_word_boundaries():
    assert routing.score_category('leaking leak leak.', 'leak') == 4
    assert routing.score_category('WiFi and wifi', 'wifi') == 4
    assert routing.score_category('short circuit, short circuit.', 'short circuit') == 8
    assert routing.assign_priority('Low','general query','everyone affected') == 'Medium'
    assert routing.assign_priority('Low','general query','fire nearby') == 'High'
    assert routing.SLA_HOURS == {'High':24,'Medium':72,'Low':168}


def test_fresh_seed_populates_report_views(env):
    login(env, 'admin', 'admin123')
    contexts=[]
    def capture(sender, template, context, **extra): contexts.append(context)
    with template_rendered.connected_to(capture, app):
        for report in ('pendency','sla','restime','trend','feedback','routing'):
            assert env.get('/reports?report=' + report).status_code == 200
            result = contexts[-1]
            if report == 'routing':
                assert {r['routing'] for r in result['rows']} == {'auto','manual'}
                assert len(result['manual']) >= 5
            else:
                assert len(result['rows']) >= 5, (report, len(result['rows']))
    conn = db.get_conn()
    assert conn.execute("SELECT COUNT(*) FROM complaints WHERE title LIKE 'Demo case %' AND routing='manual'").fetchone()[0] == 5
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    conn.close()


def test_seed_routing_matches_actual_rules_and_contains_anonymous_example(env):
    conn = db.get_conn()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    rows = conn.execute('SELECT * FROM complaints').fetchall()
    by_id = {r['id']: r for r in categories}
    # Original seed cases declare a chosen category; validate against it, not
    # only against the stored final category, so incorrect overrides are caught.
    for row, example in zip(rows[:len(db.COMPLAINTS)], db.COMPLAINTS):
        chosen = next(cat for cat in categories if cat['name'] == db.CATEGORIES[example[1]][0])
        final, mode, score = routing.select_category(row['title'], row['description'], chosen, categories)
        assert final['id'] == row['category_id']
        assert mode == row['routing'] and score == row['routing_score'], row['code']
        assert row['department_id'] == final['department_id']
    for row in rows[len(db.COMPLAINTS):]:
        final, mode, score = routing.select_category(row['title'], row['description'], by_id[row['category_id']], categories)
        assert (final['id'], mode, score) == (row['category_id'], row['routing'], row['routing_score'])
        assert row['department_id'] == final['department_id']
    assert any(row['is_anonymous'] for row in rows)
    conn.close()


def test_simultaneous_complaint_submissions_create_unique_complete_records(env):
    from concurrent.futures import ThreadPoolExecutor
    clients = [app.test_client() for _ in range(6)]
    for client in clients:
        login(client, 'MCA2026001', 'student123')
    def submit(item):
        i, client = item
        return post(client, '/lodge', {'title':f'Concurrent test case {i}',
                    'description':'A valid complaint submitted during concurrency testing.', 'category_id':'15'}).status_code
    with ThreadPoolExecutor(max_workers=6) as pool:
        assert list(pool.map(submit, enumerate(clients))) == [302] * 6
    conn = db.get_conn()
    rows = conn.execute("SELECT id,code FROM complaints WHERE title LIKE 'Concurrent test case %'").fetchall()
    assert len(rows) == 6 and len({r['code'] for r in rows}) == 6
    for row in rows:
        assert conn.execute('SELECT COUNT(*) FROM complaint_events WHERE complaint_id=?', (row['id'],)).fetchone()[0] == 2
    assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    conn.close()


def test_simultaneous_duplicate_registrations_fail_gracefully(env):
    from concurrent.futures import ThreadPoolExecutor
    clients = [app.test_client() for _ in range(4)]
    payloads = [{'csrf_token': token(c), 'full_name':'Concurrent Student', 'roll_no':'MCA2026999',
                 'email':'test@example.com', 'phone':'9876543210', 'password':'abc123', 'confirm_password':'abc123'} for c in clients]
    def submit(i): return clients[i].post('/register', data=payloads[i]).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        statuses = list(pool.map(submit, range(4)))
    assert sorted(statuses) == [302,400,400,400]
    conn = db.get_conn()
    assert conn.execute("SELECT COUNT(*) FROM users WHERE roll_no='MCA2026999'").fetchone()[0] == 1
    conn.close()


def test_simultaneous_duplicate_officer_creation_fails_gracefully(env):
    from concurrent.futures import ThreadPoolExecutor
    clients = [app.test_client() for _ in range(4)]
    for client in clients:
        login(client, 'admin', 'admin123')
    payloads = [{'csrf_token':token(c), 'full_name':'Concurrent Officer', 'department_id':'1',
                 'username':'concurrent.officer','password':'abc123'} for c in clients]
    def submit(i): return clients[i].post('/users/officer', data=payloads[i], follow_redirects=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(submit, range(4)))
    assert all(r.status_code == 200 for r in responses)
    assert sum(b'Username already exists.' in r.data for r in responses) == 3
    conn = db.get_conn()
    assert conn.execute("SELECT COUNT(*) FROM users WHERE username='concurrent.officer'").fetchone()[0] == 1
    conn.close()


def test_simultaneous_resolve_has_one_transition_event(env):
    from concurrent.futures import ThreadPoolExecutor
    c = complaint(env)
    clients = [app.test_client() for _ in range(6)]
    for client in clients:
        login(client, 'hostel.officer', 'officer123')
    tokens = [token(client) for client in clients]
    def resolve(i):
        return clients[i].post('/complaint/' + c['code'] + '/resolve',
                               data={'csrf_token':tokens[i], 'remark':'Furniture repaired successfully.'}).status_code
    with ThreadPoolExecutor(max_workers=6) as pool:
        assert list(pool.map(resolve, range(6))) == [302] * 6
    row, events = state(c['code'])
    assert row['status'] == 'Resolved'
    assert len([e for e in events if e[0] == 'status' and e[1].startswith('Resolved')]) == 1


@pytest.mark.parametrize('action,initial,account,password,data,final,event', [
    ('acknowledge','Submitted','hostel.officer','officer123',{},'Acknowledged','acknowledged'),
    ('progress','Acknowledged','hostel.officer','officer123',{},'In Progress','status'),
    ('reopen','Resolved','MCA2026001','student123',{'reason':'The issue still remains.'},'In Progress','reopened'),
    ('feedback','Resolved','MCA2026001','student123',{'rating':'5','comment':'Works.'},'Closed','feedback'),
    ('force-close','Resolved','admin','admin123',{},'Closed','closed'),
])
def test_simultaneous_lifecycle_action_logs_once(env, action, initial, account, password, data, final, event):
    from concurrent.futures import ThreadPoolExecutor
    c = complaint(env)
    set_state(c['code'], initial)
    clients = [app.test_client() for _ in range(4)]
    for client in clients:
        login(client, account, password)
    tokens = [token(client) for client in clients]
    def send(i):
        return clients[i].post('/complaint/' + c['code'] + '/' + action,
                               data={**data, 'csrf_token':tokens[i]}).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(send, range(4))) == [302] * 4
    row, events = state(c['code'])
    assert row['status'] == final
    assert sum(e[0] == event for e in events) == 1

"""Capture the user manual screens using a fresh, disposable demo database.

Install Playwright and Chromium (see README). No existing app database is used.
Set CHROMIUM_EXECUTABLE_PATH for an installed browser if necessary.
"""
import os
import sys
import tempfile
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / 'app'))
import database as db
from app import app

OUT = PROJECT / 'report' / 'images'


def main():
    with tempfile.TemporaryDirectory(prefix='shikayat-screens-') as temp:
        db.DB_PATH = str(Path(temp) / 'screens.db')
        db.init_db()
        db.seed_if_empty()
        conn = db.get_conn()
        def code(sql):
            row = conn.execute(sql).fetchone()
            if not row:
                raise RuntimeError('Seed does not contain required screenshot example')
            return row[0]
        student_resolved = code("""SELECT c.code FROM complaints c JOIN users u ON u.id=c.student_id
                                  WHERE u.username='MCA2026001' AND c.status='Resolved' ORDER BY c.id LIMIT 1""")
        officer_open = code("""SELECT c.code FROM complaints c JOIN departments d ON d.id=c.department_id
                               WHERE d.name='Hostel Office' AND c.status IN ('Submitted','Acknowledged','In Progress') ORDER BY c.id LIMIT 1""")
        conn.close()
        server = make_server('127.0.0.1', 0, app)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as pw:
                options = {'headless': True, 'args': ['--no-sandbox']}
                if os.environ.get('CHROMIUM_EXECUTABLE_PATH'):
                    options['executable_path'] = os.environ['CHROMIUM_EXECUTABLE_PATH']
                browser = pw.chromium.launch(**options)
                try:
                    page = browser.new_page(viewport={'width': 1440, 'height': 900}, color_scheme='light', reduced_motion='reduce')
                    def go(path):
                        response = page.goto(base + path)
                        if not response or response.status != 200:
                            raise RuntimeError(f'{path}: HTTP {response.status if response else "no response"}')
                    def snap(name, selector=None):
                        if selector:
                            page.locator(selector).first.scroll_into_view_if_needed()
                        page.wait_for_timeout(350)
                        page.screenshot(path=str(OUT / f'screen-{name}.png'))
                        print('Captured', name)
                    def login(username, password):
                        go('/login')
                        page.fill('#login-user', username)
                        page.fill('#login-pass', password)
                        page.click('button[type="submit"]')
                        page.wait_for_url('**/dashboard')
                        if page.locator('.toast-close').count():
                            page.locator('.toast-close').first.click()
                    def signout():
                        page.context.clear_cookies()
                    go('/login'); snap('login')
                    go('/register'); snap('register')
                    go('/track'); snap('track')
                    page.fill('[name=code]', student_resolved); page.fill('[name=roll_no]', 'MCA2026001')
                    page.click('button[type=submit]'); snap('track-result')
                    login('MCA2026001', 'student123'); snap('dashboard')
                    go('/lodge')
                    page.fill('#lodge-title', 'Leaking tap near the library')
                    page.fill('#lodge-desc', 'The tap near the library entrance has been leaking since yesterday and the floor is wet.')
                    page.select_option('#lodge-cat', '3'); page.wait_for_selector('#route-preview.show'); snap('lodge')
                    go('/my-complaints'); snap('my-complaints')
                    go('/complaint/' + student_resolved); snap('timeline'); snap('student-actions', '#fb-comment')
                    go('/change-password'); snap('change-password')
                    signout(); login('hostel.officer', 'officer123'); snap('officer-dashboard')
                    go('/queue'); snap('queue')
                    go('/complaint/' + officer_open); snap('officer-actions', '#resolve-remark')
                    signout(); login('admin', 'admin123'); snap('admin-dashboard')
                    go('/console'); snap('console')
                    go('/users'); snap('users')
                    go('/complaint/' + officer_open); snap('admin-actions', '#reassign-dept')
                    for report in ('pendency', 'sla', 'restime', 'trend', 'feedback', 'routing'):
                        go('/reports?report=' + report); snap('report-' + report)
                    page.locator('#routing-details').evaluate("el => window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 160)"); snap('report-routing-details')
                    # Error template (the response is intentionally 403).
                    signout(); login('MCA2026001', 'student123')
                    assert page.goto(base + '/console').status == 403
                    snap('forbidden')
                finally:
                    browser.close()
        finally:
            server.shutdown(); thread.join(); server.server_close()


if __name__ == '__main__':
    main()

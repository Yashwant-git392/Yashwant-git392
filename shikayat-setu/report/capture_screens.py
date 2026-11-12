"""Capture the main application screens using an isolated demo database.

Install Playwright and Chromium first (see README). The app is served only on
localhost for the duration of this script; existing application data is untouched.
"""
import os
import sys
import tempfile
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "app"))
import database as db
from app import app

OUT = PROJECT / "report" / "images"


def main():
    with tempfile.TemporaryDirectory(prefix="shikayat-screens-") as temp:
        db.DB_PATH = str(Path(temp) / "screens.db")
        db.init_db()
        db.seed_if_empty()
        server = make_server("127.0.0.1", 0, app)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as playwright:
                executable = os.environ.get("CHROMIUM_EXECUTABLE_PATH")
                browser = playwright.chromium.launch(headless=True, executable_path=executable)
                try:
                    page = browser.new_page(viewport={"width": 1440, "height": 900},
                                            color_scheme="light", reduced_motion="reduce")

                    def screenshot(name):
                        page.wait_for_timeout(800)
                        page.screenshot(path=str(OUT / f"screen-{name}.png"))
                        print(f"screen-{name}.png")

                    page.goto(base + "/login")
                    screenshot("login")
                    page.fill("#login-user", "MCA2026001")
                    page.fill("#login-pass", "student123")
                    page.click('button[type="submit"]')
                    page.wait_for_url("**/dashboard")
                    page.locator(".toast-close").click()
                    screenshot("dashboard")
                    page.goto(base + "/lodge")
                    page.fill("#lodge-title", "Leaking tap near the library")
                    page.fill("#lodge-desc", "The tap near the library entrance has been leaking since yesterday and the floor is wet.")
                    page.select_option("#lodge-cat", "3")
                    page.wait_for_selector("#route-preview.show")
                    screenshot("lodge")
                    page.goto(base + "/my-complaints")
                    page.locator('a[href^="/complaint/"]').first.click()
                    screenshot("timeline")
                    page.goto(base + "/logout")
                    page.goto(base + "/login")
                    page.fill("#login-user", "admin")
                    page.fill("#login-pass", "admin123")
                    page.click('button[type="submit"]')
                    page.wait_for_url("**/dashboard")
                    page.goto(base + "/console")
                    screenshot("console")
                finally:
                    browser.close()
        finally:
            server.shutdown()
            thread.join()
            server.server_close()


if __name__ == "__main__":
    main()

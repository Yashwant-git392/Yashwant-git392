"""Convenience launcher:  python run.py  (http://127.0.0.1:5001)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

import database as db  # noqa: E402
from app import app    # noqa: E402

if __name__ == "__main__":
    db.init_db()
    db.seed_if_empty()
    try:
        port = int(os.environ.get("SHIKAYAT_PORT", "5001"))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise SystemExit("SHIKAYAT_PORT must be an integer between 1 and 65535.")
    if not os.environ.get("SHIKAYAT_SECRET_KEY"):
        print("WARNING: using the demo-only secret key; set SHIKAYAT_SECRET_KEY for deployment.")
    print(f"Campus Shikayat Setu running at http://127.0.0.1:{port}  (login admin / admin123)")
    app.run(host="0.0.0.0", port=port, debug=False)

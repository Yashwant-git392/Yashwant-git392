"""Convenience launcher:  python run.py  (http://127.0.0.1:5001)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

import database as db  # noqa: E402
from app import app    # noqa: E402

if __name__ == "__main__":
    db.init_db()
    db.seed_if_empty()
    print("Campus Shikayat Setu running at http://127.0.0.1:5001  (login admin / admin123)")
    app.run(host="0.0.0.0", port=5001, debug=False)

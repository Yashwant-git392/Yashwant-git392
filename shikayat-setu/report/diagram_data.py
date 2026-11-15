"""Schema facts used by the project diagrams (loaded directly from schema.sql)."""
from pathlib import Path
import sqlite3

SCHEMA = Path(__file__).resolve().parent.parent / "app" / "schema.sql"
TABLES = ("departments", "categories", "users", "complaints", "complaint_events", "feedback")


def schema_facts():
    """Return the actual columns, foreign keys and single-column unique keys."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        facts = {}
        for table in TABLES:
            columns = {row[1]: {"type": row[2], "notnull": bool(row[3]), "pk": bool(row[5])}
                       for row in conn.execute(f'PRAGMA table_info("{table}")')}
            fks = {row[3]: {"table": row[2], "column": row[4], "on_delete": row[6]}
                   for row in conn.execute(f'PRAGMA foreign_key_list("{table}")')}
            unique = set()
            for index in conn.execute(f'PRAGMA index_list("{table}")'):
                if index[2]:
                    cols = list(conn.execute(f'PRAGMA index_info("{index[1]}")'))
                    if len(cols) == 1:
                        unique.add(cols[0][2])
            facts[table] = {"columns": columns, "foreign_keys": fks, "unique": unique}
        return facts
    finally:
        conn.close()

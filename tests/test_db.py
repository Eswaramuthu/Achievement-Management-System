import sqlite3
from app import app, DB_PATH


def test_tables_exist():
    from app import init_db

    init_db()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for table in ("student", "teacher", "achievements", "admin", "departments", "achievement_categories"):
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        assert cur.fetchone() is not None, f"Table '{table}' should exist"

    conn.close()

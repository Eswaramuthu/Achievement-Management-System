import sqlite3
from app import app

def test_tables_exist():
    from app import init_db

    init_db()

    db_path = app.config.get("DB_PATH", getattr(app, "DB_PATH", None)) or __import__("app").DB_PATH
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for table in ("student", "teacher", "achievements"):
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        assert cur.fetchone() is not None

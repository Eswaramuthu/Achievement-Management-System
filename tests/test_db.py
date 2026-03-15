import sqlite3
from app import app

def test_tables_exist():
    from app import init_db

    init_db()

    conn = sqlite3.connect(app.config["DB_PATH"])
    cur = conn.cursor()

    for table in ("student", "teacher", "achievements"):
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        assert cur.fetchone() is not None

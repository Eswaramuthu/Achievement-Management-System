import sqlite3
import pytest
from app import app, DB_PATH


def get_db_path():
    """Get the database path, respecting test configuration.
    
    conftest.py sets app.config['DATABASE'] to a temp path for test isolation,
    but DB_PATH is a module-level constant that ignores app.config. This function
    bridges the gap so tests use the correct isolated database.
    """
    return app.config.get('DATABASE', DB_PATH)


def test_tables_exist():
    from app import init_db

    init_db()

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for table in ("student", "teacher", "achievements", "admin", "departments", "achievement_categories"):
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        assert cur.fetchone() is not None, f"Table '{table}' should exist"

    conn.close()


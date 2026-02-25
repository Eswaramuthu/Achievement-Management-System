# tests/test_db.py

import sqlite3
from app import app, init_db


def test_tables_exist():
    """Ensure required database tables are created."""

    # Initialize database
    init_db()

    # Connect to test database
    conn = sqlite3.connect(app.config["DB_PATH"])
    cursor = conn.cursor()

    required_tables = ("student", "teacher", "achievements")

    for table in required_tables:
        cursor.execute(
            """
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name=?
            """,
            (table,),
        )
        assert cursor.fetchone() is not None, f"Table '{table}' does not exist"

    conn.close()

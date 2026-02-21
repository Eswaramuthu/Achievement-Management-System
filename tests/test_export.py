import pytest
import sqlite3
import csv
import io
from unittest.mock import patch
from app import app

@pytest.fixture(autouse=True)
def patch_db_path(test_app):
    """Patch app.DB_PATH to use the test database."""
    db_path = test_app.config['DATABASE']
    with patch('app.DB_PATH', db_path):
        yield

@pytest.fixture
def db_with_achievements(test_app):
    """Fixture to set up achievements table and data."""
    db_path = test_app.config['DATABASE']
    
    with test_app.app_context():
        # db_path is already patched globally in app context? 
        # No, patch_db_path patches 'app.DB_PATH'.
        # We connect using sqlite3 directly here to setup data.
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create achievements table if not exists
        # Note: initialization in conftest might not have created achievements table if it's not in explicit schema there.
        # But app.init_db() creates it.
        # We'll create it manually to be safe.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            achievement_type TEXT NOT NULL,
            event_name TEXT NOT NULL,
            achievement_date DATE NOT NULL,
            organizer TEXT NOT NULL,
            position TEXT NOT NULL,
            achievement_description TEXT,
            certificate_path TEXT,

            symposium_theme TEXT,
            programming_language TEXT,
            coding_platform TEXT,
            paper_title TEXT,
            journal_name TEXT,
            conference_level TEXT,
            conference_role TEXT,
            team_size INTEGER,
            project_title TEXT,
            database_type TEXT,
            difficulty_level TEXT,
            other_description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student(student_id),
            FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
        )
        """)

        # Insert test achievement
        cursor.execute("""
            INSERT INTO achievements (
                student_id, teacher_id, achievement_type, event_name, 
                achievement_date, organizer, position, achievement_description, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            'S001', 'T001', 'Hackathon', 'Super Hack 2026',
            '2026-02-20', 'Winner', 'Tech Corp', 'Built a cool AI app'
        ))

        conn.commit()
        conn.close()
    return test_app

def test_export_unauthorized(client):
    """Test that unauthorized users cannot export data."""
    response = client.get('/export_achievements')
    assert response.status_code == 302  # Redirects to teacher login

def test_export_success(client, auth_teacher_client, db_with_achievements):
    """Test that authorized teachers can export data as CSV."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['teacher_id'] = 'T001'
    
    response = client.get('/export_achievements')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv'
    assert 'attachment' in response.headers['Content-Disposition']

    # content is bytes, decode to string
    content = response.data.decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    # Check header
    assert rows[0] == ["Student Name", "Student ID", "Type", "Event Name", "Date", "Position", "Organizer", "Description"]
    
    # Check data row
    assert len(rows) > 1, f"No data rows found. Content: {content}"
    row = rows[1]
    assert "Test Student" in row
    assert "S001" in row
    assert "Hackathon" in row
    assert "Super Hack 2026" in row
    assert "Winner" in row

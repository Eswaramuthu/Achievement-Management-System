"""
Database Initialization Script for Achievement Management System
This script creates the SQLite database and all required tables.
Run this before starting the application for the first time.
"""

import sqlite3
import os

# Define database path - adjust this to match your system
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ams.db")

def init_database():
    """
    Initialize the database with all required tables.
    Creates student, teacher, and achievements tables.
    """
    print(f"Initializing database at: {DB_PATH}")
    
    # Create database connection
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    # Create student table
    print("Creating student table...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student (
        student_name TEXT NOT NULL,
        student_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        phone_number TEXT,
        password TEXT NOT NULL,
        student_gender TEXT,
        student_dept TEXT
    )
    ''')
    
    # Create teacher table
    print("Creating teacher table...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teacher (
        teacher_name TEXT NOT NULL,
        teacher_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        phone_number TEXT,
        password TEXT NOT NULL,
        teacher_gender TEXT,
        teacher_dept TEXT
    )
    ''')
    
    # Create achievements table
    print("Creating achievements table...")
    cursor.execute('''
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
        
        /* For Symposium */
        symposium_theme TEXT,
                   
        /* For Coding Competition */
        programming_language TEXT,
        coding_platform TEXT,

        /* For Paper Presentation */
        paper_title TEXT,
        journal_name TEXT,
                   
        /* For Conference */
        conference_level TEXT,
        conference_role TEXT,
                   
        /* For Hackathon */
        team_size INTEGER,
        project_title TEXT,
                   
        /* For SQL Query Event */
        database_type TEXT,
        difficulty_level TEXT,
                   
        /* For other events - achievement type description */
        other_description TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES student(student_id),
        FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
    )
    ''')
    
    # Commit changes
    connection.commit()
    print("✓ All tables created successfully!")
    
    # Display table information
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\nTables in database: {[table[0] for table in tables]}")
    
    connection.close()
    print(f"\n✓ Database initialization complete!")
    print(f"Database location: {DB_PATH}")

def add_sample_data():
    """
    Optional: Add sample data for testing purposes.
    Uncomment the function call in main() to use this.
    """
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    # Sample student
    try:
        cursor.execute("""
            INSERT INTO student (student_name, student_id, email, phone_number, password, student_gender, student_dept)
            VALUES ('John Doe', 'STU001', 'john.doe@example.com', '1234567890', 'password123', 'Male', 'Computer Science')
        """)
        print("✓ Sample student added")
    except sqlite3.IntegrityError:
        print("Sample student already exists")
    
    # Sample teacher
    try:
        cursor.execute("""
            INSERT INTO teacher (teacher_name, teacher_id, email, phone_number, password, teacher_gender, teacher_dept)
            VALUES ('Dr. Jane Smith', 'TCH001', 'jane.smith@example.com', '0987654321', 'teacher123', 'Female', 'Computer Science')
        """)
        print("✓ Sample teacher added")
    except sqlite3.IntegrityError:
        print("Sample teacher already exists")
    
    connection.commit()
    connection.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Achievement Management System - Database Initialization")
    print("=" * 60)
    print()
    
    # Initialize database
    init_database()
    
    print("\n" + "=" * 60)
    print("You can now run the application with: python app.py")
    print("=" * 60)

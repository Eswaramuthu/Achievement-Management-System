from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.String(50), primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    password = db.Column(db.String(200), nullable=False)
    student_gender = db.Column(db.String(20))
    student_dept = db.Column(db.String(50))
    
    # Relationships
    achievements = db.relationship('Achievement', backref='student', lazy=True)

class Teacher(db.Model):
    __tablename__ = 'teacher'
    teacher_id = db.Column(db.String(50), primary_key=True)
    teacher_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    password = db.Column(db.String(200), nullable=False)
    teacher_gender = db.Column(db.String(20))
    teacher_dept = db.Column(db.String(50))
    
    # Relationships
    achievements = db.relationship('Achievement', backref='teacher', lazy=True)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(50), db.ForeignKey('student.student_id'), nullable=False)
    teacher_id = db.Column(db.String(50), db.ForeignKey('teacher.teacher_id'), nullable=False, default='unknown')
    
    achievement_type = db.Column(db.String(50), nullable=False)
    event_name = db.Column(db.String(200), nullable=False)
    achievement_date = db.Column(db.Date, nullable=False) # Changed to Date type if possible, or keep as String if input is string
    organizer = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    achievement_description = db.Column(db.Text)
    certificate_path = db.Column(db.String(200))
    
    # Common additional fields
    symposium_theme = db.Column(db.String(200))
    programming_language = db.Column(db.String(100))
    coding_platform = db.Column(db.String(100))
    paper_title = db.Column(db.String(200))
    journal_name = db.Column(db.String(200))
    conference_level = db.Column(db.String(100))
    conference_role = db.Column(db.String(100))
    team_size = db.Column(db.Integer)
    project_title = db.Column(db.String(200))
    database_type = db.Column(db.String(100))
    difficulty_level = db.Column(db.String(50))
    other_description = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

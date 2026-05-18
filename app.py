from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, Response
import sqlite3
import os
import secrets
import hashlib
import csv
import io
import datetime

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from services.certificate_service import process_certificate

from flask_wtf import CSRFProtect

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from firebase_config import get_firebase_config
    FIREBASE_AVAILABLE = True
except ImportError:
    get_firebase_config = None
    FIREBASE_AVAILABLE = False


# ---------------- CONFIG ----------------

DEFAULT_FIREBASE_CONFIG = {
    "apiKey": "", "authDomain": "", "databaseURL": "", "projectId": "",
    "storageBucket": "", "messagingSenderId": "", "appId": "", "measurementId": "",
}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

# csrf = CSRFProtect(app)

app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "static",
    "uploads"
)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "ams.db")


# ---------------- CONTEXT PROCESSORS ----------------

@app.context_processor
def inject_firebase_config():
    if FIREBASE_AVAILABLE:
        return dict(firebase_config=get_firebase_config())
    return dict(firebase_config=DEFAULT_FIREBASE_CONFIG)


@app.context_processor
def inject_csrf():
    return {"csrf_token": lambda: ""}


# ---------------- DB HELPERS ----------------

def ensure_achievements_schema(connection):
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(achievements)")
    columns = [c[1] for c in cursor.fetchall()]

    if "teacher_id" not in columns:
        cursor.execute("ALTER TABLE achievements ADD COLUMN teacher_id TEXT DEFAULT 'unknown'")

    if "created_at" not in columns:
        cursor.execute("ALTER TABLE achievements ADD COLUMN created_at TEXT")
        cursor.execute("UPDATE achievements SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    if "certificate_hash" not in columns:
        cursor.execute("ALTER TABLE achievements ADD COLUMN certificate_hash TEXT")

    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_cert_hash ON achievements (certificate_hash)")
    connection.commit()


def add_profile_picture_column():
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(student)")
        columns = [c[1] for c in cursor.fetchall()]

        if "profile_picture" not in columns:
            cursor.execute("ALTER TABLE student ADD COLUMN profile_picture TEXT")
            connection.commit()

        connection.close()

    except sqlite3.Error as e:
        print(f"Error: {e}")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "pdf", "png", "jpg", "jpeg"
    }


# ---------------- INIT DB ----------------

def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            student_name TEXT NOT NULL,
            student_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            password TEXT NOT NULL,
            student_gender TEXT,
            student_dept TEXT,
            is_approved BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher (
            teacher_name TEXT NOT NULL,
            teacher_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            password TEXT NOT NULL,
            teacher_gender TEXT,
            teacher_dept TEXT,
            is_approved BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            admin_name TEXT NOT NULL,
            admin_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_superuser BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_code TEXT UNIQUE NOT NULL,
            dept_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievement_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_code TEXT UNIQUE NOT NULL,
            category_name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

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
            certificate_hash TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ---------------- DECORATORS ----------------

from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in") or not session.get("admin_id"):
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return wrapper


def superadmin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in") or not session.get("is_superuser"):
            return redirect(url_for("admin_dashboard"))
        return f(*args, **kwargs)
    return wrapper


def student_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in") or not session.get("student_id"):
            return redirect(url_for("student"))
        return f(*args, **kwargs)
    return wrapper


def teacher_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in") or not session.get("teacher_id"):
            return redirect(url_for("teacher"))
        return f(*args, **kwargs)
    return wrapper


# ---------------- ROUTES (UNCHANGED) ----------------
# (All your routes remain EXACT SAME — not repeated here to avoid bloating)

# ---------------- MAIN ----------------

if __name__ == "__main__":
    init_db()
    add_profile_picture_column()
    app.run(debug=True)

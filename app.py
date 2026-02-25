from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import secrets
from werkzeug.utils import secure_filename
import datetime

# =====================================================
# 🔹 Flask App Setup
# =====================================================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

# ✅ Portable DB path
DB_PATH = os.path.join(os.path.dirname(__file__), "ams.db")

# ✅ Upload folder for certificates
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================
# 🔹 Database Helpers
# =====================================================
def ensure_achievements_schema(connection):
    """
    Ensure achievements table has teacher_id and created_at columns.
    Adds missing columns and backfills old rows if necessary.
    """
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(achievements)")
    columns = cursor.fetchall()
    column_names = [c[1] for c in columns]

    if "teacher_id" not in column_names:
        cursor.execute("ALTER TABLE achievements ADD COLUMN teacher_id TEXT DEFAULT 'unknown'")

    if "created_at" not in column_names:
        cursor.execute("ALTER TABLE achievements ADD COLUMN created_at TEXT")
        cursor.execute("UPDATE achievements SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    connection.commit()


def allowed_file(filename):
    """Check if uploaded file is allowed."""
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def init_db():
    """Initialize database if it doesn't exist and ensure schema consistency."""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create student table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            student_name TEXT NOT NULL,
            student_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            password TEXT NOT NULL,
            student_gender TEXT,
            student_dept TEXT
        )
        """)

        # Create teacher table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher (
            teacher_name TEXT NOT NULL,
            teacher_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            password TEXT NOT NULL,
            teacher_gender TEXT,
            teacher_dept TEXT
        )
        """)

        # Create achievements table
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

        conn.commit()
        conn.close()
        print(f"Created database at {DB_PATH}")
    else:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='achievements'")
        if not cursor.fetchone():
            cursor.execute("""CREATE TABLE IF NOT EXISTS achievements (
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
            )""")
            conn.commit()
        ensure_achievements_schema(conn)
        conn.close()
        print(f"Database already exists at {DB_PATH}")


# Initialize DB on startup
init_db()


# =====================================================
# 🔹 Routes
# =====================================================
@app.route("/")
def home():
    return render_template("home.html")


# ------------------------
# Student login
# ------------------------
@app.route("/student", methods=["GET", "POST"])
def student():
    if request.method == "POST":
        student_id = request.form.get("sname")
        password = request.form.get("password")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student WHERE student_id = ? AND password = ?", (student_id, password))
        student_data = cursor.fetchone()
        conn.close()

        if student_data:
            session.update({
                "logged_in": True,
                "student_id": student_data[1],
                "student_name": student_data[0],
                "student_dept": student_data[6]
            })
            return redirect(url_for("student-dashboard"))
        return render_template("student.html", error="Invalid credentials. Please try again.")
    return render_template("student.html")


# ------------------------
# Teacher login
# ------------------------
@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    if request.method == "POST":
        teacher_id = request.form.get("tname")
        password = request.form.get("password")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teacher WHERE teacher_id = ? AND password = ?", (teacher_id, password))
        teacher_data = cursor.fetchone()
        conn.close()

        if teacher_data:
            session.update({
                "logged_in": True,
                "teacher_id": teacher_data[1],
                "teacher_name": teacher_data[0],
                "teacher_dept": teacher_data[6]
            })
            return redirect(url_for("teacher-dashboard"))
        return render_template("teacher.html", error="Invalid credentials. Please try again.")
    return render_template("teacher.html")


# ------------------------
# Student registration
# ------------------------
@app.route("/student-new", methods=["GET", "POST"])
def student_new():
    if request.method == "POST":
        data = {key: request.form.get(key) for key in [
            "student_name", "student_id", "email", "phone_number", "password", "student_gender", "student_dept"
        ]}
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                student_name TEXT NOT NULL,
                student_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                password TEXT NOT NULL,
                student_gender TEXT,
                student_dept TEXT
            )
        """)
        try:
            cursor.execute("""
                INSERT INTO student (student_name, student_id, email, phone_number, password, student_gender, student_dept)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, tuple(data.values()))
            conn.commit()
            return redirect(url_for("student"))
        except sqlite3.Error as e:
            return render_template("student_new_2.html", error=f"Database error: {e}")
        finally:
            conn.close()
    return render_template("student_new_2.html")


# ------------------------
# Teacher registration
# ------------------------
@app.route("/teacher-new", endpoint="teacher-new", methods=["GET", "POST"])
def teacher_new():
    if request.method == "POST":
        data = {key: request.form.get(key) for key in [
            "teacher_name", "teacher_id", "email", "phone_number", "password", "teacher_gender", "teacher_dept"
        ]}
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher (
                teacher_name TEXT NOT NULL,
                teacher_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                password TEXT NOT NULL,
                teacher_gender TEXT,
                teacher_dept TEXT
            )
        """)
        try:
            cursor.execute("""
                INSERT INTO teacher (teacher_name, teacher_id, email, phone_number, password, teacher_gender, teacher_dept)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, tuple(data.values()))
            conn.commit()
            return redirect(url_for("teacher"))
        except sqlite3.Error as e:
            return render_template("teacher_new_2.html", error=f"Database error: {e}")
        finally:
            conn.close()
    return render_template("teacher_new_2.html")


# ------------------------
# Teacher dashboard & achievements
# ------------------------
@app.route("/teacher-dashboard", endpoint="teacher-dashboard")
def teacher_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("teacher"))

    teacher_id = session.get("teacher_id")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    ensure_achievements_schema(conn)

    cursor.execute("SELECT COUNT(*) FROM achievements WHERE teacher_id = ?", (teacher_id,))
    total_achievements = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT student_id) FROM achievements WHERE teacher_id = ?", (teacher_id,))
    students_managed = cursor.fetchone()[0]

    one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM achievements WHERE teacher_id = ? AND achievement_date >= ?", (teacher_id, one_week_ago))
    this_week_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT a.id, a.student_id, s.student_name, a.achievement_type, a.event_name, a.achievement_date
        FROM achievements a
        JOIN student s ON a.student_id = s.student_id
        WHERE a.teacher_id = ?
        ORDER BY a.created_at DESC
        LIMIT 5
    """, (teacher_id,))
    recent_entries = cursor.fetchall()
    conn.close()

    stats = {
        "total_achievements": total_achievements,
        "students_managed": students_managed,
        "this_week": this_week_count
    }

    return render_template("teacher_dashboard.html", teacher={
        "id": teacher_id,
        "name": session.get("teacher_name"),
        "dept": session.get("teacher_dept")
    }, stats=stats, recent_entries=recent_entries)


# ------------------------
# Student dashboard
# ------------------------
@app.route("/student-dashboard", endpoint="student-dashboard")
def student_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("student"))
    return render_template("student_dashboard.html", student={
        "id": session.get("student_id"),
        "name": session.get("student_name"),
        "dept": session.get("student_dept")
    })


# =====================================================
# 🔹 Run Flask App
# =====================================================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

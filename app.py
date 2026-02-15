from unittest import result
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import secrets
from werkzeug.utils import secure_filename
import datetime
from services.certificate_service import process_certificate
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

csrf = CSRFProtect(app)

from firebase_config import get_firebase_config

@app.context_processor
def inject_firebase_config():
    return dict(firebase_config=get_firebase_config())

# ✅ Portable DB path (works on Windows/Linux/Vercel)
DB_PATH = os.path.join(os.path.dirname(__file__), "ams.db")

# Define upload folder path for certificates
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def ensure_achievements_schema(connection):
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(achievements)")
    columns = cursor.fetchall()
    column_names = [c[1] for c in columns]

    # Add teacher_id if missing
    if "teacher_id" not in column_names:
        cursor.execute("ALTER TABLE achievements ADD COLUMN teacher_id TEXT DEFAULT 'unknown'")

    # Add created_at if missing
    if "created_at" not in column_names:
        cursor.execute("ALTER TABLE achievements ADD COLUMN created_at TEXT")
        cursor.execute("UPDATE achievements SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    # Add certificate_hash if missing
    if "certificate_hash" not in column_names:
        cursor.execute("ALTER TABLE achievements ADD COLUMN certificate_hash TEXT")
    
    # This works even if the column was added via ALTER TABLE earlier
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_cert_hash ON achievements (certificate_hash)")

    connection.commit()



# Define a function to check allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Initialize database on startup
def init_db():
    if not os.path.exists(DB_PATH):
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
            student_dept TEXT
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
            teacher_dept TEXT
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (student_id) REFERENCES student(student_id),
                FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
            )
            """)


        connection.commit()
        connection.close()
        print(f"Created database at {DB_PATH}")
    else:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Ensure achievements table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='achievements'")
        if not cursor.fetchone():
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (student_id) REFERENCES student(student_id),
                    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
                )
                """)

            connection.commit()
            print("Created achievements table")

        # ✅ IMPORTANT: fix old DBs missing columns (created_at issue)
        ensure_achievements_schema(connection)

        connection.close()
        print(f"Database already exists at {DB_PATH}")


# Call initialization function
init_db()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/student", methods=["GET", "POST"])
def student():
    if request.method == "POST":
        student_id = request.form.get("sname")
        password = request.form.get("password")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM student WHERE student_id = ? AND password = ?", (student_id, password))
        student_data = cursor.fetchone()
        connection.close()

        if student_data:
            session["logged_in"] = True
            session["student_id"] = student_data[1]
            session["student_name"] = student_data[0]
            session["student_dept"] = student_data[6]
            return redirect(url_for("student-dashboard"))
        else:
            return render_template("student.html", error="Invalid credentials. Please try again.")

    return render_template("student.html")


@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    if request.method == "POST":
        teacher_id = request.form.get("tname")
        password = request.form.get("password")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM teacher WHERE teacher_id = ? AND password = ?", (teacher_id, password))
        teacher_data = cursor.fetchone()
        connection.close()

        if teacher_data:
            session["logged_in"] = True
            session["teacher_id"] = teacher_data[1]
            session["teacher_name"] = teacher_data[0]
            session["teacher_dept"] = teacher_data[6]
            return redirect(url_for("teacher-dashboard"))
        else:
            return render_template("teacher.html", error="Invalid credentials. Please try again.")

    return render_template("teacher.html")


@app.route("/student-new", methods=["GET", "POST"])
def student_new():
    if request.method == "POST":
        student_name = request.form.get("student_name")
        student_id = request.form.get("student_id")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        student_gender = request.form.get("student_gender")
        student_dept = request.form.get("student_dept")

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
            student_dept TEXT
        )
        """)

        try:
            cursor.execute("""
                INSERT INTO student (student_name, student_id, email, phone_number, password, student_gender, student_dept)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_name, student_id, email, phone_number, password, student_gender, student_dept))
            connection.commit()
            return redirect(url_for("student"))
        except sqlite3.Error as e:
            return render_template("student_new_2.html", error=f"Database error: {e}")
        finally:
            connection.close()

    return render_template("student_new_2.html")


@app.route("/teacher-new", endpoint="teacher-new", methods=["GET", "POST"])
def teacher_new():
    if request.method == "POST":
        teacher_name = request.form.get("teacher_name")
        teacher_id = request.form.get("teacher_id")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        teacher_gender = request.form.get("teacher_gender")
        teacher_dept = request.form.get("teacher_dept")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

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
            """, (teacher_name, teacher_id, email, phone_number, password, teacher_gender, teacher_dept))
            connection.commit()
            return redirect(url_for("teacher"))
        except sqlite3.Error as e:
            return render_template("teacher_new_2.html", error=f"Database error: {e}")
        finally:
            connection.close()

    return render_template("teacher_new_2.html")


@app.route("/teacher-achievements", endpoint="teacher-achievements")
def teacher_achievements():
    return render_template("teacher_achievements_2.html")


@app.route("/submit_achievements", methods=["GET", "POST"])
def submit_achievements():
    if not session.get("logged_in") or not session.get("teacher_id"):
        return redirect(url_for("teacher"))

    teacher_id = session.get("teacher_id")

    if request.method == "POST":
        try:
            import hashlib
            
            # Extract standard form data
            student_id = request.form.get("student_id")
            achievement_type = request.form.get("achievement_type")
            event_name = request.form.get("event_name")
            achievement_date = request.form.get("achievement_date")
            organizer = request.form.get("organizer")
            position = request.form.get("position")
            achievement_description = request.form.get("achievement_description")
            
            # Handle numeric fields
            team_size = request.form.get("team_size")
            team_size = int(team_size) if team_size and team_size.strip() else None

            # Optional detail fields
            details = {
                "symposium_theme": request.form.get("symposium_theme"),
                "programming_language": request.form.get("programming_language"),
                "coding_platform": request.form.get("coding_platform"),
                "paper_title": request.form.get("paper_title"),
                "journal_name": request.form.get("journal_name"),
                "conference_level": request.form.get("conference_level"),
                "conference_role": request.form.get("conference_role"),
                "project_title": request.form.get("project_title"),
                "database_type": request.form.get("database_type"),
                "difficulty_level": request.form.get("difficulty_level"),
                "other_description": request.form.get("other_description")
            }

            certificate_path = None
            certificate_hash = None

            # -----------------------------
            # FILE & HASH HANDLING
            # -----------------------------
            if "certificate" in request.files:
                file = request.files["certificate"]

                if file and file.filename != "":
                    if not allowed_file(file.filename):
                        return render_template("submit_achievements.html", error="Invalid file type.")

                    # 1. Read bytes for hashing
                    file.seek(0) 
                    file_bytes = file.read()
                    certificate_hash = hashlib.sha256(file_bytes).hexdigest()
                    file.seek(0) # 2. Reset pointer so we can save it later

                    # 3. DB Check for existing Hash
                    with sqlite3.connect(DB_PATH) as check_conn:
                        cursor = check_conn.cursor()
                        cursor.execute("SELECT id FROM achievements WHERE certificate_hash = ?", (certificate_hash,))
                        if cursor.fetchone():
                            return render_template("submit_achievements.html", 
                                                 error="Duplicate detected! This certificate is already registered.")

                    # 4. Save File if check passed
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    secure_name = f"{timestamp}_{secure_filename(file.filename)}"
                    file_path = os.path.join(UPLOAD_FOLDER, secure_name)
                    file.save(file_path)
                    certificate_path = f"uploads/{secure_name}"

                    # 5. Optional OCR
                    try:
                        res = process_certificate(file_path)
                        parsed = res.get("parsed_data", {})
                        event_name = event_name or parsed.get("event_name")
                        achievement_date = achievement_date or parsed.get("achievement_date")
                    except Exception as ocr_err:
                        print(f"OCR failed: {ocr_err}")

            # -----------------------------
            # DATABASE INSERT
            # -----------------------------
            with sqlite3.connect(DB_PATH) as connection:
                cursor = connection.cursor()
                ensure_achievements_schema(connection)

                # Validate Student
                cursor.execute("SELECT student_name FROM student WHERE student_id = ?", (student_id,))
                student_row = cursor.fetchone()
                if not student_row:
                    return render_template("submit_achievements.html", error="Student ID not found.")
                
                student_name = student_row[0]

                query = """
                    INSERT INTO achievements (
                        student_id, teacher_id, achievement_type, event_name, achievement_date,
                        organizer, position, achievement_description, certificate_path,
                        symposium_theme, programming_language, coding_platform, paper_title,
                        journal_name, conference_level, conference_role, team_size,
                        project_title, database_type, difficulty_level, other_description,
                        certificate_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    student_id, teacher_id, achievement_type, event_name, achievement_date,
                    organizer, position, achievement_description, certificate_path,
                    details["symposium_theme"], details["programming_language"], 
                    details["coding_platform"], details["paper_title"], details["journal_name"], 
                    details["conference_level"], details["conference_role"], team_size,
                    details["project_title"], details["database_type"], 
                    details["difficulty_level"], details["other_description"], certificate_hash
                )

                cursor.execute(query, params)
                connection.commit()

            return render_template("submit_achievements.html", 
                                 success=f"Success! Achievement for {student_name} recorded.")

        except sqlite3.IntegrityError:
            return render_template("submit_achievements.html", error="Database error: Duplicate certificate hash.")
        except Exception as e:
            return render_template("submit_achievements.html", error=f"Error: {str(e)}")

    return render_template("submit_achievements.html")


@app.route("/student-achievements", endpoint="student-achievements")
def student_achievements():
    if not session.get("logged_in"):
        return redirect(url_for("student"))

    student_data = {
        "id": session.get("student_id"),
        "name": session.get("student_name"),
        "dept": session.get("student_dept"),
    }
    return render_template("student_achievements_1.html", student=student_data)


@app.route("/student-dashboard", endpoint="student-dashboard")
def student_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("student"))

    student_data = {
        "id": session.get("student_id"),
        "name": session.get("student_name"),
        "dept": session.get("student_dept"),
    }
    return render_template("student_dashboard.html", student=student_data)


@app.route("/teacher-dashboard", endpoint="teacher-dashboard")
def teacher_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("teacher"))

    teacher_id = session.get("teacher_id")
    teacher_data = {
        "id": teacher_id,
        "name": session.get("teacher_name"),
        "dept": session.get("teacher_dept"),
    }

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # ✅ Ensure schema exists so query never crashes
    ensure_achievements_schema(connection)

    cursor.execute("SELECT COUNT(*) FROM achievements WHERE teacher_id = ?", (teacher_id,))
    total_achievements = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT student_id) FROM achievements WHERE teacher_id = ?", (teacher_id,))
    students_managed = cursor.fetchone()[0]

    one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM achievements WHERE teacher_id = ? AND achievement_date >= ?",
                   (teacher_id, one_week_ago))
    this_week_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT a.id, a.student_id, s.student_name, a.achievement_type,
               a.event_name, a.achievement_date
        FROM achievements a
        JOIN student s ON a.student_id = s.student_id
        WHERE a.teacher_id = ?
        ORDER BY a.created_at DESC
        LIMIT 5
    """, (teacher_id,))
    recent_entries = cursor.fetchall()

    connection.close()

    stats = {
        "total_achievements": total_achievements,
        "students_managed": students_managed,
        "this_week": this_week_count,
    }

    return render_template(
        "teacher_dashboard.html",
        teacher=teacher_data,
        stats=stats,
        recent_entries=recent_entries,
    )


@app.route("/all-achievements", endpoint="all-achievements")
def all_achievements():
    if not session.get("logged_in"):
        return redirect(url_for("teacher"))

    teacher_id = session.get("teacher_id")

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT a.id, a.student_id, s.student_name, a.achievement_type,
               a.event_name, a.achievement_date, a.position, a.organizer,
               a.certificate_path
        FROM achievements a
        JOIN student s ON a.student_id = s.student_id
        WHERE a.teacher_id = ?
        ORDER BY a.achievement_date DESC
    """, (teacher_id,))

    achievements = cursor.fetchall()
    connection.close()

    return render_template("all_achievements.html", achievements=achievements)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


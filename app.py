import os
import io
import csv
import sqlite3
import datetime
import secrets

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    send_file,
    abort,
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# ------------------------------------------------------------
# Optional imports (don’t break if files not present)
# ------------------------------------------------------------
try:
    from config import DevelopmentConfig, ProductionConfig  # type: ignore
except Exception:
    DevelopmentConfig = None
    ProductionConfig = None

try:
    from firebase_config import get_firebase_config as _get_firebase_config  # type: ignore
except Exception:
    _get_firebase_config = None


def get_firebase_config():
    return _get_firebase_config() if _get_firebase_config else {}


# ------------------------------------------------------------
# App setup
# ------------------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-this")

env = os.getenv("FLASK_ENV", "development").lower()

# Load config if available (safe)
if env == "production" and ProductionConfig is not None:
    app.config.from_object(ProductionConfig)
elif DevelopmentConfig is not None:
    app.config.from_object(DevelopmentConfig)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = app.config.get("DB_PATH", os.path.join(BASE_DIR, "ams.db"))
UPLOAD_FOLDER = app.config.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "static", "uploads"))
ALLOWED_EXTENSIONS = app.config.get("ALLOWED_EXTENSIONS", {"pdf", "png", "jpg", "jpeg"})

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def has_student_session() -> bool:
    return bool(session.get("logged_in") and session.get("student_id"))


def has_teacher_session() -> bool:
    return bool(session.get("logged_in") and session.get("teacher_id"))


def verify_password(stored_pw: str, incoming_pw: str) -> bool:
    """
    Supports both hashed passwords (new) and plain-text (old DB).
    """
    if not stored_pw:
        return False
    try:
        return check_password_hash(stored_pw, incoming_pw)
    except Exception:
        return stored_pw == incoming_pw


# ------------------------------------------------------------
# DB schema safety (non-destructive)
# ------------------------------------------------------------
def ensure_achievements_schema(connection: sqlite3.Connection) -> None:
    """
    Non-destructive migration:
    - ensure teacher_id exists
    - ensure created_at exists (needed for teacher dashboard ordering)
    """
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(achievements)")
    cols = cursor.fetchall()
    col_names = [c[1] for c in cols]

    if "teacher_id" not in col_names:
        cursor.execute("ALTER TABLE achievements ADD COLUMN teacher_id TEXT DEFAULT 'unknown'")

    if "created_at" not in col_names:
        cursor.execute("ALTER TABLE achievements ADD COLUMN created_at TEXT")
        cursor.execute("UPDATE achievements SET created_at = datetime('now') WHERE created_at IS NULL")

    connection.commit()


def init_db() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student (
            student_name TEXT NOT NULL,
            student_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            password TEXT NOT NULL,
            student_gender TEXT,
            student_dept TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS teacher (
            teacher_name TEXT NOT NULL,
            teacher_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            password TEXT NOT NULL,
            teacher_gender TEXT,
            teacher_dept TEXT
        )
        """
    )

    cursor.execute(
        """
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
        """
    )

    connection.commit()

    # Ensure schema for older DBs
    ensure_achievements_schema(connection)

    connection.close()


# Run init on import
init_db()


# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/student", methods=["GET", "POST"])
def student():
    firebase_config = get_firebase_config()

    if request.method == "POST":
        student_id = request.form.get("sname")
        password = request.form.get("password")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM student WHERE student_id = ?", (student_id,))
        student_data = cursor.fetchone()
        connection.close()

        if student_data:
            stored_pw = student_data[4]
            if verify_password(stored_pw, password):
                session.permanent = True
                session["logged_in"] = True
                session["student_id"] = student_data[1]
                session["student_name"] = student_data[0]
                session["student_dept"] = student_data[6]
                return redirect(url_for("student-dashboard"))

        return render_template(
            "student.html",
            error="Invalid credentials. Please try again.",
            firebase_config=firebase_config,
        )

    return render_template("student.html", firebase_config=firebase_config)


@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    if request.method == "POST":
        teacher_id = request.form.get("tname")
        password = request.form.get("password")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM teacher WHERE teacher_id = ?", (teacher_id,))
        teacher_data = cursor.fetchone()
        connection.close()

        if teacher_data:
            stored_pw = teacher_data[4]
            if verify_password(stored_pw, password):
                session.permanent = True
                session["logged_in"] = True
                session["teacher_id"] = teacher_data[1]
                session["teacher_name"] = teacher_data[0]
                session["teacher_dept"] = teacher_data[6]
                return redirect(url_for("teacher-dashboard"))

        return render_template("teacher.html", error="Invalid credentials. Please try again.")

    return render_template("teacher.html")


@app.route("/student_new", methods=["GET", "POST"])
def student_new():
    firebase_config = get_firebase_config()

    if request.method == "POST":
        student_name = request.form.get("student_name")
        student_id = request.form.get("student_id")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = generate_password_hash(request.form.get("password"))
        student_gender = request.form.get("student_gender")
        student_dept = request.form.get("student_dept")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO student (student_name, student_id, email, phone_number, password, student_gender, student_dept)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (student_name, student_id, email, phone_number, password, student_gender, student_dept),
            )
            connection.commit()
            return redirect(url_for("student"))
        except sqlite3.Error as e:
            return render_template("student_new.html", firebase_config=firebase_config, error=str(e))
        finally:
            connection.close()

    return render_template("student_new.html", firebase_config=firebase_config)


@app.route("/teacher-new", methods=["GET", "POST"], endpoint="teacher-new")
def teacher_new():
    if request.method == "POST":
        teacher_name = request.form.get("teacher_name")
        teacher_id = request.form.get("teacher_id")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = generate_password_hash(request.form.get("password"))
        teacher_gender = request.form.get("teacher_gender")
        teacher_dept = request.form.get("teacher_dept")

        # Optional: protect teacher registration with a code
        teacher_code = request.form.get("teacher_code")
        required_code = os.environ.get("TEACHER_REGISTRATION_CODE", "admin123")
        if teacher_code is not None and teacher_code != required_code:
            return render_template("teacher_new_2.html", error="Invalid Teacher Code. Registration denied.")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO teacher (teacher_name, teacher_id, email, phone_number, password, teacher_gender, teacher_dept)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (teacher_name, teacher_id, email, phone_number, password, teacher_gender, teacher_dept),
            )
            connection.commit()
            return redirect(url_for("teacher"))
        except sqlite3.Error as e:
            return render_template("teacher_new_2.html", error=str(e))
        finally:
            connection.close()

    return render_template("teacher_new_2.html")


@app.route("/teacher-achievements", endpoint="teacher-achievements")
def teacher_achievements():
    return render_template("teacher_achievements_2.html")


@app.route("/submit_achievements", methods=["GET", "POST"], endpoint="submit_achievements")
def submit_achievements():
    if not has_teacher_session():
        return redirect(url_for("teacher"))

    teacher_id = session.get("teacher_id")

    if request.method == "POST":
        try:
            student_id = request.form.get("student_id")
            achievement_type = request.form.get("achievement_type")
            event_name = request.form.get("event_name")
            achievement_date = request.form.get("achievement_date")
            organizer = request.form.get("organizer")
            position = request.form.get("position")
            achievement_description = request.form.get("achievement_description")

            symposium_theme = request.form.get("symposium_theme")
            programming_language = request.form.get("programming_language")
            coding_platform = request.form.get("coding_platform")
            paper_title = request.form.get("paper_title")
            journal_name = request.form.get("journal_name")
            conference_level = request.form.get("conference_level")
            conference_role = request.form.get("conference_role")
            project_title = request.form.get("project_title")
            database_type = request.form.get("database_type")
            difficulty_level = request.form.get("difficulty_level")
            other_description = request.form.get("other_description")

            team_size = request.form.get("team_size")
            team_size = int(team_size) if team_size and team_size.strip() else None

            # Handle certificate file upload
            certificate_path = None
            if "certificate" in request.files:
                file = request.files["certificate"]
                if file and file.filename:
                    if not allowed_file(file.filename):
                        return render_template(
                            "submit_achievements.html",
                            error="Invalid file type. Please upload PDF, PNG, JPG, or JPEG files.",
                        )
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    safe_name = f"{timestamp}_{secure_filename(file.filename)}"
                    file.save(os.path.join(UPLOAD_FOLDER, safe_name))
                    certificate_path = f"uploads/{safe_name}"

            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            ensure_achievements_schema(connection)

            # Validate student exists
            cursor.execute("SELECT student_id, student_name FROM student WHERE student_id = ?", (student_id,))
            student_data = cursor.fetchone()
            if not student_data:
                connection.close()
                return render_template("submit_achievements.html", error="Student ID does not exist in the system.")

            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """
                INSERT INTO achievements (
                    student_id, teacher_id, achievement_type, event_name, achievement_date,
                    organizer, position, achievement_description, certificate_path,
                    symposium_theme, programming_language, coding_platform, paper_title,
                    journal_name, conference_level, conference_role, team_size,
                    project_title, database_type, difficulty_level, other_description,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_id,
                    teacher_id,
                    achievement_type,
                    event_name,
                    achievement_date,
                    organizer,
                    position,
                    achievement_description,
                    certificate_path,
                    symposium_theme,
                    programming_language,
                    coding_platform,
                    paper_title,
                    journal_name,
                    conference_level,
                    conference_role,
                    team_size,
                    project_title,
                    database_type,
                    difficulty_level,
                    other_description,
                    created_at,
                ),
            )

            connection.commit()
            connection.close()

            success_message = f"Achievement of {student_data[1]} has been successfully registered!!"
            return render_template("submit_achievements.html", success=success_message)

        except Exception as e:
            return render_template("submit_achievements.html", error=f"An error occurred: {str(e)}")

    return render_template("submit_achievements.html")


# ------------------------------------------------------------
# Student: My Achievements (View / Download / Export)
# ------------------------------------------------------------
@app.route("/student-achievements", endpoint="student-achievements")
def student_achievements():
    if not has_student_session():
        return redirect(url_for("student"))

    student_id = session.get("student_id")
    student_data = {
        "id": student_id,
        "name": session.get("student_name"),
        "dept": session.get("student_dept"),
    }

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, achievement_type, event_name, achievement_date, organizer,
               position, achievement_description, certificate_path
        FROM achievements
        WHERE student_id = ?
        ORDER BY achievement_date DESC, id DESC
        """,
        (student_id,),
    )
    achievements = cursor.fetchall()
    connection.close()

    total_achievements = len(achievements)
    first_positions = sum(1 for a in achievements if "first" in (a["position"] or "").lower())

    return render_template(
        "student_achievements_1.html",
        student=student_data,
        achievements=achievements,
        total_achievements=total_achievements,
        first_positions=first_positions,
    )


@app.route("/student-achievements/<int:achievement_id>")
def student_achievement_details(achievement_id: int):
    if not has_student_session():
        return redirect(url_for("student"))

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM achievements WHERE id = ? AND student_id = ?",
        (achievement_id, session.get("student_id")),
    )
    achievement = cursor.fetchone()
    connection.close()

    if not achievement:
        abort(404)

    return render_template("student_achievement_details.html", achievement=achievement)


@app.route("/student-achievements/<int:achievement_id>/download")
def download_achievement_certificate(achievement_id: int):
    if not has_student_session():
        return redirect(url_for("student"))

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT certificate_path FROM achievements WHERE id = ? AND student_id = ?",
        (achievement_id, session.get("student_id")),
    )
    row = cursor.fetchone()
    connection.close()

    if not row or not row["certificate_path"]:
        abort(404)

    absolute_path = os.path.join(BASE_DIR, "static", row["certificate_path"])
    if not os.path.exists(absolute_path):
        abort(404)

    return send_file(absolute_path, as_attachment=True)


@app.route("/student-achievements/export")
def export_student_achievements():
    if not has_student_session():
        return redirect(url_for("student"))

    student_id = session.get("student_id")

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT achievement_type, event_name, achievement_date, organizer,
               position, achievement_description
        FROM achievements
        WHERE student_id = ?
        ORDER BY achievement_date DESC, id DESC
        """,
        (student_id,),
    )
    rows = cursor.fetchall()
    connection.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Achievement Type", "Event Name", "Date", "Organizer", "Position", "Description"])
    for r in rows:
        writer.writerow(
            [
                r["achievement_type"],
                r["event_name"],
                r["achievement_date"],
                r["organizer"],
                r["position"],
                r["achievement_description"] or "",
            ]
        )

    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{student_id}_achievements.csv",
    )


# ------------------------------------------------------------
# Dashboards
# ------------------------------------------------------------
@app.route("/student-dashboard", endpoint="student-dashboard")
def student_dashboard():
    if not has_student_session():
        return redirect(url_for("student"))

    student_data = {
        "id": session.get("student_id"),
        "name": session.get("student_name"),
        "dept": session.get("student_dept"),
    }
    return render_template("student_dashboard.html", student=student_data)


@app.route("/teacher-dashboard", endpoint="teacher-dashboard")
def teacher_dashboard():
    if not has_teacher_session():
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

    ensure_achievements_schema(connection)

    cursor.execute("SELECT COUNT(*) AS c FROM achievements WHERE teacher_id = ?", (teacher_id,))
    total_achievements = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(DISTINCT student_id) AS c FROM achievements WHERE teacher_id = ?", (teacher_id,))
    students_managed = cursor.fetchone()["c"]

    one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT COUNT(*) AS c FROM achievements WHERE teacher_id = ? AND achievement_date >= ?",
        (teacher_id, one_week_ago),
    )
    this_week_count = cursor.fetchone()["c"]

    cursor.execute(
        """
        SELECT a.id, a.student_id, s.student_name, a.achievement_type,
               a.event_name, a.achievement_date
        FROM achievements a
        JOIN student s ON a.student_id = s.student_id
        WHERE a.teacher_id = ?
        ORDER BY a.created_at DESC
        LIMIT 5
        """,
        (teacher_id,),
    )
    recent_entries = cursor.fetchall()

    connection.close()

    stats = {
        "total_achievements": total_achievements,
        "students_managed": students_managed,
        "this_week": this_week_count,
    }

    return render_template("teacher_dashboard.html", teacher=teacher_data, stats=stats, recent_entries=recent_entries)


@app.route("/all-achievements", endpoint="all-achievements")
def all_achievements():
    if not has_teacher_session():
        return redirect(url_for("teacher"))

    teacher_id = session.get("teacher_id")

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT a.id, a.student_id, s.student_name, a.achievement_type,
               a.event_name, a.achievement_date, a.position, a.organizer,
               a.certificate_path
        FROM achievements a
        JOIN student s ON a.student_id = s.student_id
        WHERE a.teacher_id = ?
        ORDER BY a.achievement_date DESC
        """,
        (teacher_id,),
    )

    achievements = cursor.fetchall()
    connection.close()

    return render_template("all_achievements.html", achievements=achievements)


# ------------------------------------------------------------
# Firebase Auth endpoints (only if firebase_config exists)
# ------------------------------------------------------------
@app.route("/auth/firebase-config", methods=["GET"])
def get_auth_firebase_config():
    return jsonify(get_firebase_config())


@app.route("/auth/google-login", methods=["POST"])
def google_login():
    """
    Works only if your frontend sends {email, uid}. If you don’t use Firebase, ignore this route.
    """
    try:
        data = request.get_json() or {}
        email = data.get("email")
        firebase_uid = data.get("uid")

        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM student WHERE email = ?", (email,))
        student_data = cursor.fetchone()
        connection.close()

        if not student_data:
            return jsonify(
                {"success": False, "message": f"No student account found for {email}. Please register first."}
            ), 404

        session.permanent = True
        session["logged_in"] = True
        session["student_id"] = student_data[1]
        session["student_name"] = student_data[0]
        session["student_dept"] = student_data[6]
        session["google_auth"] = True
        session["firebase_uid"] = firebase_uid

        return jsonify({"success": True, "message": "Student logged in successfully", "redirectUrl": "/student-dashboard"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Login error: {str(e)}"}), 500


@app.route("/logout", methods=["GET"])
def web_logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=(env != "production"))

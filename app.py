from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import os
import secrets
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
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

# Default when Firebase is not configured (student page still renders)
DEFAULT_FIREBASE_CONFIG = {
    "apiKey": "", "authDomain": "", "databaseURL": "", "projectId": "",
    "storageBucket": "", "messagingSenderId": "", "appId": "", "measurementId": "",
}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

# csrf = CSRFProtect(app)

@app.context_processor
def inject_firebase_config():
    if FIREBASE_AVAILABLE:
        return dict(firebase_config=get_firebase_config())
    else:
        return dict(firebase_config=DEFAULT_FIREBASE_CONFIG)


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



def add_profile_picture_column():
    """
    Add profile_picture column to student table if it doesn't exist
    """
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Check if profile_picture column exists in student table
        cursor.execute("PRAGMA table_info(student)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if "profile_picture" not in column_names:
            print("Adding profile_picture column to student table...")
            cursor.execute(
                "ALTER TABLE student ADD COLUMN profile_picture TEXT"
            )
            connection.commit()
            print("profile_picture column added successfully!")
        else:
            print("profile_picture column already exists in student table")

        connection.close()
    except sqlite3.Error as e:
        print(f"Error adding profile_picture column: {e}")



# Define a function to check allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Initialize database on startup
# Initialize database on startup
def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Student table
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

    # Teacher table
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

    # Admin table
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

    # Departments table for admin management
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_code TEXT UNIQUE NOT NULL,
            dept_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Achievement categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievement_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_code TEXT UNIQUE NOT NULL,
            category_name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Achievements table
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

    # Insert default super admin if not exists
    cursor.execute("SELECT COUNT(*) FROM admin WHERE admin_id = 'superadmin'")
    if cursor.fetchone()[0] == 0:
        default_password = generate_password_hash("admin123")
        cursor.execute("""
            INSERT INTO admin (admin_name, admin_id, email, password, is_superuser)
            VALUES (?, ?, ?, ?, ?)
        """, ("Super Administrator", "superadmin", "admin@system.com", default_password, 1))

    # Insert default departments if not exists
    default_departments = [
        ("CSE", "Computer Science and Engineering"),
        ("ECE", "Electronics and Communication Engineering"),
        ("EEE", "Electrical and Electronics Engineering"),
        ("MECH", "Mechanical Engineering"),
        ("CIVIL", "Civil Engineering"),
        ("IT", "Information Technology")
    ]

    for dept_code, dept_name in default_departments:
        cursor.execute("SELECT COUNT(*) FROM departments WHERE dept_code = ?", (dept_code,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO departments (dept_code, dept_name) VALUES (?, ?)", (dept_code, dept_name))

    # Insert default achievement categories if not exists
    default_categories = [
        ("CODING", "Coding Competition", "Programming and coding competitions"),
        ("HACKATHON", "Hackathon", "Hackathon events"),
        ("PAPER", "Paper Presentation", "Research paper presentations"),
        ("PROJECT", "Project Exhibition", "Project exhibitions and demos"),
        ("SPORTS", "Sports Achievement", "Sports and athletic achievements"),
        ("CULTURAL", "Cultural Event", "Cultural and arts events"),
        ("INTERNSHIP", "Internship", "Internship completions"),
        ("CERTIFICATION", "Certification", "Professional certifications")
    ]

    for cat_code, cat_name, description in default_categories:
        cursor.execute("SELECT COUNT(*) FROM achievement_categories WHERE category_code = ?", (cat_code,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO achievement_categories (category_code, category_name, description) VALUES (?, ?, ?)",
                          (cat_code, cat_name, description))

    connection.commit()
    connection.close()
    print("Database initialized successfully")



# Call initialization function
init_db()

# Permission decorators for RBAC
def login_required(f):
    """Decorator to check if user is logged in"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("admin_id"):
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    """Decorator to check if user is super admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("admin_id") or not session.get("is_superuser"):
            return redirect(url_for("admin_dashboard"))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Decorator to check if user is student"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("student_id"):
            return redirect(url_for("student"))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Decorator to check if user is teacher"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("teacher_id"):
            return redirect(url_for("teacher"))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_csrf():
    """Provide csrf_token() for templates that expect it (e.g. tests)."""
    return {"csrf_token": lambda: ""}
# Permission decorators for RBAC
def login_required(f):
    """Decorator to check if user is logged in"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("admin_id"):
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    """Decorator to check if user is super admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("admin_id") or not session.get("is_superuser"):
            return redirect(url_for("admin_dashboard"))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Decorator to check if user is student"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("student_id"):
            return redirect(url_for("student"))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Decorator to check if user is teacher"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("teacher_id"):
            return redirect(url_for("teacher"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def home():
    firebase_config = get_firebase_config()
    return render_template("home.html", firebase_config=firebase_config)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.html")















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


@app.route("/student/profile", endpoint="student-profile")
def student_profile():
    # Check if user is logged in
    if not session.get('logged_in') or not session.get('student_id'):
        return redirect(url_for('student'))

    # Get student ID from session
    student_id = session.get('student_id')
    
    # Connect to database
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    # Get student data from database
    cursor.execute("SELECT * FROM student WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    
    connection.close()
    
    if not student:
        # Student not found in database (should not happen)
        session.clear()
        return redirect(url_for('student'))
    
    # Convert row to dict for easier template access
    student_dict = dict(student)
    
    # Build profile picture URL if exists
    profile_picture_url = None
    if student_dict.get('profile_picture'):
        profile_picture_url = url_for('static', filename=student_dict['profile_picture'])
    
    return render_template("student_profile.html", 
                          student=student_dict, 
                          profile_picture_url=profile_picture_url)


@app.route("/student/profile/edit", endpoint="student_profile_edit", methods=["POST"])
def student_profile_edit():
    # Check if user is logged in
    if not session.get('logged_in') or not session.get('student_id'):
        return redirect(url_for('student'))
    
    student_id = session.get('student_id')
    
    try:
        # Get form data
        student_name = request.form.get('student_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        student_gender = request.form.get('student_gender')
        student_dept = request.form.get('student_dept')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Connect to database
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        
        # Get current student data
        cursor.execute("SELECT * FROM student WHERE student_id = ?", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            connection.close()
            session.clear()
            return redirect(url_for('student'))
        
        # Handle password change if requested
        if current_password and new_password and confirm_password:
            # Verify current password
            if not check_password_hash(student[4], current_password):
                connection.close()
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('student-profile'))
            
            # Verify new passwords match
            if new_password != confirm_password:
                connection.close()
                flash('New passwords do not match', 'danger')
                return redirect(url_for('student-profile'))
            
            # Verify password length
            if len(new_password) < 6:
                connection.close()
                flash('New password must be at least 6 characters long', 'danger')
                return redirect(url_for('student-profile'))
            
            # Hash new password
            hashed_password = generate_password_hash(new_password)
        else:
            # Keep existing password
            hashed_password = student[4]
        
        # Handle profile picture upload
        profile_picture_path = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    # Create a secure filename with timestamp to prevent duplicates
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    secure_name = f"profile_{student_id}_{timestamp}_{secure_filename(file.filename)}"
                    
                    # Create profiles subdirectory if it doesn't exist
                    profiles_dir = os.path.join(UPLOAD_FOLDER, 'profiles')
                    os.makedirs(profiles_dir, exist_ok=True)
                    
                    file_path = os.path.join(profiles_dir, secure_name)
                    file.save(file_path)
                    profile_picture_path = f"uploads/profiles/{secure_name}"
                    
                    # Delete old profile picture if exists
                    if student[7]:  # profile_picture is at index 7
                        old_picture_path = os.path.join('static', student[7])
                        if os.path.exists(old_picture_path):
                            try:
                                os.remove(old_picture_path)
                            except:
                                pass  # Ignore error if file doesn't exist
                else:
                    connection.close()
                    flash('Invalid file type. Please upload JPG, JPEG, or PNG files.', 'danger')
                    return redirect(url_for('student-profile'))
        
        # Update student data in database
        if profile_picture_path:
            cursor.execute("""
                UPDATE student 
                SET student_name = ?, email = ?, phone_number = ?, 
                    student_gender = ?, student_dept = ?, password = ?, 
                    profile_picture = ?
                WHERE student_id = ?
            """, (student_name, email, phone_number, student_gender, 
                  student_dept, hashed_password, profile_picture_path, student_id))
        else:
            cursor.execute("""
                UPDATE student 
                SET student_name = ?, email = ?, phone_number = ?, 
                    student_gender = ?, student_dept = ?, password = ?
                WHERE student_id = ?
            """, (student_name, email, phone_number, student_gender, 
                  student_dept, hashed_password, student_id))
        
        connection.commit()
        connection.close()
        
        # Update session data
        session['student_name'] = student_name
        session['student_dept'] = student_dept
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student-profile'))
        
    except Exception as e:
        print(f"Error updating profile: {e}")
        flash(f'Error updating profile: {str(e)}', 'danger')
        return redirect(url_for('student-profile'))


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


# ==================== ADMIN ROUTES ====================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    """Admin login page"""
    if request.method == "POST":
        admin_id = request.form.get("admin_id")
        password = request.form.get("password")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE admin_id = ?", (admin_id,))
        admin_data = cursor.fetchone()
        connection.close()

        if admin_data and check_password_hash(admin_data[3], password):
            session["logged_in"] = True
            session["admin_id"] = admin_data[1]
            session["admin_name"] = admin_data[0]
            session["is_superuser"] = bool(admin_data[4])
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid credentials. Please try again.")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin dashboard with system statistics"""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # System statistics
    cursor.execute("SELECT COUNT(*) FROM student")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teacher")
    total_teachers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM achievements")
    total_achievements = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM student WHERE is_approved = 0")
    pending_student_approvals = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teacher WHERE is_approved = 0")
    pending_teacher_approvals = cursor.fetchone()[0]

    # Recent activities
    cursor.execute("""
        SELECT type, name, id, is_approved, created_at FROM (
            SELECT 'student' as type, student_name as name, student_id as id, is_approved, created_at 
            FROM student 
            ORDER BY created_at DESC 
            LIMIT 5
        )
        UNION ALL
        SELECT type, name, id, is_approved, created_at FROM (
            SELECT 'teacher' as type, teacher_name as name, teacher_id as id, is_approved, created_at 
            FROM teacher 
            ORDER BY created_at DESC 
            LIMIT 5
        )
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_activities = cursor.fetchall()

    # Department statistics
    cursor.execute("""
        SELECT student_dept, COUNT(*) as count 
        FROM student 
        WHERE student_dept IS NOT NULL AND student_dept != ''
        GROUP BY student_dept 
        ORDER BY count DESC 
        LIMIT 5
    """)
    dept_stats = cursor.fetchall()

    connection.close()

    stats = {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_achievements": total_achievements,
        "pending_student_approvals": pending_student_approvals,
        "pending_teacher_approvals": pending_teacher_approvals,
    }

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        recent_activities=recent_activities,
        dept_stats=dept_stats,
        admin_name=session.get("admin_name"),
        is_superuser=session.get("is_superuser", False)
    )


@app.route("/admin/users")
@admin_required
def admin_users():
    """Manage users (students and teachers)"""
    user_type = request.args.get("type", "students")
    status = request.args.get("status", "all")
    
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if user_type == "students":
        query = "SELECT * FROM student WHERE 1=1"
        params = []
        
        if status == "pending":
            query += " AND is_approved = 0"
        elif status == "approved":
            query += " AND is_approved = 1"
        
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        users = cursor.fetchall()
        user_type_name = "Students"
    else:
        query = "SELECT * FROM teacher WHERE 1=1"
        params = []
        
        if status == "pending":
            query += " AND is_approved = 0"
        elif status == "approved":
            query += " AND is_approved = 1"
        
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        users = cursor.fetchall()
        user_type_name = "Teachers"

    connection.close()

    return render_template(
        "admin_users.html",
        users=users,
        user_type=user_type,
        user_type_name=user_type_name,
        status=status,
        admin_name=session.get("admin_name")
    )


@app.route("/admin/user/approve", methods=["POST"])
@admin_required
def admin_approve_user():
    """Approve or reject a user"""
    user_id = request.form.get("user_id")
    user_type = request.form.get("user_type")
    action = request.form.get("action")  # "approve" or "reject"

    if user_type not in ["student", "teacher"]:
        return jsonify({"success": False, "error": "Invalid user type"}), 400

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    if action == "approve":
        if user_type == "student":
            cursor.execute("UPDATE student SET is_approved = 1 WHERE student_id = ?", (user_id,))
        else:
            cursor.execute("UPDATE teacher SET is_approved = 1 WHERE teacher_id = ?", (user_id,))
        message = f"{user_type.capitalize()} approved successfully"
    else:
        if user_type == "student":
            cursor.execute("DELETE FROM student WHERE student_id = ?", (user_id,))
        else:
            cursor.execute("DELETE FROM teacher WHERE teacher_id = ?", (user_id,))
        message = f"{user_type.capitalize()} rejected and removed"

    connection.commit()
    connection.close()

    return jsonify({"success": True, "message": message})


@app.route("/admin/departments")
@admin_required
def admin_departments():
    """Manage departments"""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM departments ORDER BY dept_name")
    departments = cursor.fetchall()

    # Get department usage statistics
    cursor.execute("""
        SELECT d.dept_code, d.dept_name, 
               COUNT(s.student_id) as student_count,
               COUNT(t.teacher_id) as teacher_count
        FROM departments d
        LEFT JOIN student s ON d.dept_code = s.student_dept
        LEFT JOIN teacher t ON d.dept_code = t.teacher_dept
        GROUP BY d.dept_code, d.dept_name
        ORDER BY d.dept_name
    """)
    dept_stats = cursor.fetchall()

    connection.close()

    return render_template(
        "admin_departments.html",
        departments=departments,
        dept_stats=dept_stats,
        admin_name=session.get("admin_name"),
        is_superuser=session.get("is_superuser", False)
    )


@app.route("/admin/department/add", methods=["POST"])
@admin_required
def admin_add_department():
    """Add a new department"""
    if not session.get("is_superuser"):
        return jsonify({"success": False, "error": "Permission denied"}), 403

    dept_code = request.form.get("dept_code")
    dept_name = request.form.get("dept_name")

    if not dept_code or not dept_name:
        return jsonify({"success": False, "error": "Department code and name are required"}), 400

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO departments (dept_code, dept_name) VALUES (?, ?)", (dept_code, dept_name))
        connection.commit()
        connection.close()
        return jsonify({"success": True, "message": "Department added successfully"})
    except sqlite3.IntegrityError:
        connection.close()
        return jsonify({"success": False, "error": "Department code already exists"}), 400
    except Exception as e:
        connection.close()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/admin/department/delete", methods=["POST"])
@superadmin_required
def admin_delete_department():
    """Delete a department (super admin only)"""
    dept_id = request.form.get("dept_id")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Check if department is in use
    cursor.execute("SELECT COUNT(*) FROM student WHERE student_dept = (SELECT dept_code FROM departments WHERE id = ?)", (dept_id,))
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teacher WHERE teacher_dept = (SELECT dept_code FROM departments WHERE id = ?)", (dept_id,))
    teacher_count = cursor.fetchone()[0]

    if student_count > 0 or teacher_count > 0:
        connection.close()
        return jsonify({"success": False, "error": "Cannot delete department that is in use"}), 400

    try:
        cursor.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
        connection.commit()
        connection.close()
        return jsonify({"success": True, "message": "Department deleted successfully"})
    except Exception as e:
        connection.close()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/admin/categories")
@admin_required
def admin_categories():
    """Manage achievement categories"""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM achievement_categories ORDER BY category_name")
    categories = cursor.fetchall()

    # Get category usage statistics
    cursor.execute("""
        SELECT c.category_code, c.category_name, 
               COUNT(a.id) as achievement_count
        FROM achievement_categories c
        LEFT JOIN achievements a ON c.category_code = a.achievement_type
        GROUP BY c.category_code, c.category_name
        ORDER BY c.category_name
    """)
    category_stats = cursor.fetchall()

    connection.close()

    return render_template(
        "admin_categories.html",
        categories=categories,
        category_stats=category_stats,
        admin_name=session.get("admin_name"),
        is_superuser=session.get("is_superuser", False)
    )


@app.route("/admin/category/add", methods=["POST"])
@admin_required
def admin_add_category():
    """Add a new achievement category"""
    category_code = request.form.get("category_code")
    category_name = request.form.get("category_name")
    description = request.form.get("description", "")

    if not category_code or not category_name:
        return jsonify({"success": False, "error": "Category code and name are required"}), 400

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO achievement_categories (category_code, category_name, description) VALUES (?, ?, ?)", 
                      (category_code, category_name, description))
        connection.commit()
        connection.close()
        return jsonify({"success": True, "message": "Category added successfully"})
    except sqlite3.IntegrityError:
        connection.close()
        return jsonify({"success": False, "error": "Category code already exists"}), 400
    except Exception as e:
        connection.close()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/admin/export")
@admin_required
def admin_export():
    """Export system data"""
    export_type = request.args.get("type", "students")
    
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if export_type == "students":
        cursor.execute("SELECT * FROM student ORDER BY student_name")
        data = cursor.fetchall()
        filename = "students_export.csv"
        headers = ["Student ID", "Name", "Email", "Phone", "Gender", "Department", "Approved", "Created At"]
        
        # Create CSV content
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        
        for row in data:
            writer.writerow([
                row["student_id"],
                row["student_name"],
                row["email"],
                row["phone_number"] or "",
                row["student_gender"] or "",
                row["student_dept"] or "",
                "Yes" if row["is_approved"] else "No",
                row["created_at"]
            ])
        
        content = output.getvalue()
        output.close()
        
    elif export_type == "teachers":
        cursor.execute("SELECT * FROM teacher ORDER BY teacher_name")
        data = cursor.fetchall()
        filename = "teachers_export.csv"
        headers = ["Teacher ID", "Name", "Email", "Phone", "Gender", "Department", "Approved", "Created At"]
        
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        
        for row in data:
            writer.writerow([
                row["teacher_id"],
                row["teacher_name"],
                row["email"],
                row["phone_number"] or "",
                row["teacher_gender"] or "",
                row["teacher_dept"] or "",
                "Yes" if row["is_approved"] else "No",
                row["created_at"]
            ])
        
        content = output.getvalue()
        output.close()
        
    else:  # achievements
        cursor.execute("""
            SELECT a.*, s.student_name, t.teacher_name
            FROM achievements a
            JOIN student s ON a.student_id = s.student_id
            JOIN teacher t ON a.teacher_id = t.teacher_id
            ORDER BY a.achievement_date DESC
        """)
        data = cursor.fetchall()
        filename = "achievements_export.csv"
        headers = ["ID", "Student ID", "Student Name", "Teacher ID", "Teacher Name", 
                  "Achievement Type", "Event Name", "Date", "Organizer", "Position", 
                  "Description", "Certificate Path", "Created At"]
        
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        
        for row in data:
            writer.writerow([
                row["id"],
                row["student_id"],
                row["student_name"],
                row["teacher_id"],
                row["teacher_name"],
                row["achievement_type"],
                row["event_name"],
                row["achievement_date"],
                row["organizer"],
                row["position"],
                row["achievement_description"] or "",
                row["certificate_path"] or "",
                row["created_at"]
            ])
        
        content = output.getvalue()
        output.close()

    connection.close()

    from flask import Response
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@app.route("/admin/logout")
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for("admin_login"))


# ==================== UPDATE EXISTING ROUTES FOR RBAC ====================

# Update student registration to require approval
@app.route("/student-new", methods=["GET", "POST"])
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
            cursor.execute("""
                INSERT INTO student (student_name, student_id, email, phone_number, password, student_gender, student_dept, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_name, student_id, email, phone_number, password, student_gender, student_dept, 0))
            connection.commit()
            return render_template("student_new_2.html", 
                                 success="Registration submitted! Your account will be activated after admin approval.",
                                 firebase_config=firebase_config)
        except sqlite3.Error as e:
            return render_template("student_new_2.html", error=f"Database error: {e}", firebase_config=firebase_config)
        finally:
            connection.close()

    return render_template("student_new_2.html", firebase_config=firebase_config)


# Update teacher registration to require approval
@app.route("/teacher-new", endpoint="teacher-new", methods=["GET", "POST"])
def teacher_new():
    if request.method == "POST":
        teacher_name = request.form.get("teacher_name")
        teacher_id = request.form.get("teacher_id")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = generate_password_hash(request.form.get("password"))
        teacher_gender = request.form.get("teacher_gender")
        teacher_dept = request.form.get("teacher_dept")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO teacher (teacher_name, teacher_id, email, phone_number, password, teacher_gender, teacher_dept, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (teacher_name, teacher_id, email, phone_number, password, teacher_gender, teacher_dept, 0))
            connection.commit()
            return render_template("teacher_new_2.html", 
                                 success="Registration submitted! Your account will be activated after admin approval.")
        except sqlite3.Error as e:
            return render_template("teacher_new_2.html", error=f"Database error: {e}")
        finally:
            connection.close()

    return render_template("teacher_new_2.html")


# Update student login to check approval status
@app.route("/student", methods=["GET", "POST"])
def student():
    if FIREBASE_AVAILABLE:
        firebase_config = get_firebase_config()
    else:
        firebase_config = DEFAULT_FIREBASE_CONFIG
    
    if request.method == "POST":
        student_id = request.form.get("sname")
        password = request.form.get("password")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM student WHERE student_id = ?", (student_id,))
        student_data = cursor.fetchone()
        connection.close()

        if student_data and check_password_hash(student_data[4], password):
            # Check if student is approved
            if not student_data[7]:  # is_approved is at index 7
                return render_template("student.html", error="Your account is pending admin approval. Please wait for activation.", firebase_config=firebase_config)
            
            session["logged_in"] = True
            session["student_id"] = student_data[1]
            session["student_name"] = student_data[0]
            session["student_dept"] = student_data[6]
            return redirect(url_for("student-dashboard"))
        else:
            return render_template("student.html", error="Invalid credentials. Please try again.", firebase_config=firebase_config)

    return render_template("student.html", firebase_config=firebase_config)


# Update teacher login to check approval status
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

        if teacher_data and check_password_hash(teacher_data[4], password):
            # Check if teacher is approved
            if not teacher_data[7]:  # is_approved is at index 7
                return render_template("teacher.html", error="Your account is pending admin approval. Please wait for activation.")
            
            session["logged_in"] = True
            session["teacher_id"] = teacher_data[1]
            session["teacher_name"] = teacher_data[0]
            session["teacher_dept"] = teacher_data[6]
            return redirect(url_for("teacher-dashboard"))
        else:
            return render_template("teacher.html", error="Invalid credentials. Please try again.")

    return render_template("teacher.html")


if __name__ == "__main__":
    init_db()
    add_profile_picture_column()
    app.run(debug=True)


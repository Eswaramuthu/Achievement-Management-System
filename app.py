from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from config import DevelopmentConfig, ProductionConfig
from firebase_config import get_firebase_config, validate_firebase_config

# Load environment variables from .env file
# load_dotenv()

from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------
# App setup
# ------------------------------------------------------------------

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# Choose config based on environment
env = os.environ.get("FLASK_ENV", "development")

if env == "production":
    app.config.from_object(ProductionConfig)
    ProductionConfig.validate()
else:
    app.config.from_object(DevelopmentConfig)
    
# app.config["MAX_CONTENT_LENGTH"] = app.config["MAX_CONTENT_LENGTH"]

DB_PATH = app.config["DB_PATH"]
UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]

os.makedirs(UPLOAD_FOLDER, exist_ok=True)



# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower()
        in app.config["ALLOWED_EXTENSIONS"]
    )


# ------------------------------------------------------------------
# Database migration helpers
# ------------------------------------------------------------------

def add_teacher_id_column():
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(achievements)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if "teacher_id" not in column_names:
            cursor.execute(
                "ALTER TABLE achievements ADD COLUMN teacher_id TEXT DEFAULT 'unknown'"
            )
            connection.commit()

        connection.close()
    except sqlite3.Error as e:
        print(f"Error adding teacher_id column: {e}")


def migrate_achievements_table():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(achievements)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    if "teacher_id" not in column_names:
        cursor.execute("ALTER TABLE achievements RENAME TO achievements_backup")

        cursor.execute("""
        CREATE TABLE achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            teacher_id TEXT NOT NULL DEFAULT 'unknown',
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

        cursor.execute("""
        INSERT INTO achievements (
            id, student_id, achievement_type, event_name,
            achievement_date, organizer, position, achievement_description,
            certificate_path, symposium_theme, programming_language, coding_platform,
            paper_title, journal_name, conference_level, conference_role,
            team_size, project_title, database_type, difficulty_level,
            other_description, created_at
        )
        SELECT
            id, student_id, achievement_type, event_name,
            achievement_date, organizer, position, achievement_description,
            certificate_path, symposium_theme, programming_language, coding_platform,
            paper_title, journal_name, conference_level, conference_role,
            team_size, project_title, database_type, difficulty_level,
            other_description, created_at
        FROM achievements_backup
        """)

        connection.commit()

    connection.close()


# Initialize database on startup
# ------------------------------------------------------------------
# Database init
# ------------------------------------------------------------------

def init_db():
    db_path = app.config["DB_PATH"]

    connection = sqlite3.connect(db_path)
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES student(student_id),
        FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
    )
    """)

    connection.commit()
    connection.close()

# Call initialization function
init_db()

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/student", methods=["GET", "POST"])
def student():
    firebase_config = get_firebase_config()
    
    if request.method == "POST":

        # Get user data
        student_id = request.form.get("sname")
        password = request.form.get("password")

        # Validate credentials against database
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Query the database for the student
        cursor.execute("SELECT * FROM student WHERE student_id = ?", (student_id,))
        student_data = cursor.fetchone()
        connection.close()

        if student_data and check_password_hash(student_data[4], password):
            # Store user information in session
            session.permanent = True
            session['logged_in'] = True
            session['student_id'] = student_data[1]
            session['student_name'] = student_data[0]
            session['student_dept'] = student_data[6]

            # Authentication successful - store student info in session
            return redirect(url_for("student-dashboard"))
        else:
            # Authentication failed
            return render_template("student.html", error="Invalid credentials. Please try again.", firebase_config=firebase_config)
    return render_template("student.html", firebase_config=firebase_config)


@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    if request.method == "POST":

        # Get user data
        teacher_id = request.form.get("tname")
        password = request.form.get("password")

        # Validate credentials against database
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Query for the teacher data
        cursor.execute("SELECT * FROM teacher WHERE teacher_id = ?", (teacher_id,))
        teacher_data = cursor.fetchone()
        connection.close()

        if teacher_data and check_password_hash(teacher_data[4], password):
            # Store user information in session
            session.permanent = True
            session['logged_in'] = True
            session['teacher_id'] = teacher_data[1]
            session['teacher_name'] = teacher_data[0]
            session['teacher_dept'] = teacher_data[6]

            # Authentication successful
            return redirect(url_for("teacher-dashboard"))

        else:
            # Authentication failed
            return render_template("teacher.html", error="Invalid credentials. Please try again.")

    return render_template("teacher.html")


# @app.route("/student-new", methods=["GET", "POST"])
@app.route("/student_new", methods=["GET", "POST"])
def student_new():
    firebase_config = get_firebase_config()

    print(f"Request method: {request.method}")
    
    # Getting the form data
    if request.method == "POST":
        student_name = request.form.get("student_name")
        student_id = request.form.get("student_id")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = generate_password_hash(request.form.get("password"))
        student_gender = request.form.get("student_gender")
        student_dept = request.form.get("student_dept")

        print(f"Form data: {student_name}, {student_id}, {email}, {phone_number}, {student_gender}, {student_dept}")

        # Connecting to the database
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Check if the student table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student'")
        if not cursor.fetchone():
            print("Student table doesn't exist! Creating now...")
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
            connection.commit()
        
        try:
            # Inserting the values into the student table
            cursor.execute("""
                INSERT INTO student (student_name, student_id, email, phone_number, password, student_gender, student_dept)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (student_name, student_id, email, phone_number, password, student_gender, student_dept))
            
            # Committing changes
            connection.commit()
            print("Database update successful!")
            return redirect(url_for("student"))
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            # Add error handling here
        finally:
            # Closing the connection
            connection.close()
    
    return render_template("student_new.html", firebase_config=firebase_config)


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

        print(f"Form data: {teacher_name}, {teacher_id}, {email}, {phone_number}, {teacher_gender}, {teacher_dept}")

        # Check for Teacher Code
        teacher_code = request.form.get("teacher_code")
        # Get the secret code from environment variable or use default
        required_code = os.environ.get("TEACHER_REGISTRATION_CODE", "admin123")
        
        if teacher_code != required_code:
            print("Invalid Teacher Code provided")
            return render_template("teacher_new_2.html", error="Invalid Teacher Code. Registration denied.")

                # Connecting to the database
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Check if the teacher table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teacher'")
        if not cursor.fetchone():
            print("Teacher table doesn't exist! Creating now...")
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
            connection.commit()

        try:
            cursor.execute("""
            INSERT INTO teacher (teacher_name, teacher_id, email, phone_number, password, teacher_gender, teacher_dept)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (teacher_name, teacher_id, email, phone_number, password, teacher_gender, teacher_dept))

            # Committing changes
            connection.commit()
            print("Database update successful!")
            return redirect(url_for("teacher"))
        except sqlite3.Error as e:
            print(f"Database error: {e}")

        finally:
            # Closing the connection
            connection.close()

    return render_template("teacher_new_2.html")


@app.route("/teacher-achievements", endpoint="teacher-achievements")
def teacher_achievements():
    return render_template("teacher_achievements_2.html")


@app.route("/submit_achievements", endpoint="submit_achievements", methods=["GET", "POST"])
def submit_achievements():
    # Check if teacher is logged in
    if not session.get('logged_in') or not session.get('teacher_id'):
        return redirect(url_for('teacher'))
        
    # Get teacher ID from session
    teacher_id = session.get('teacher_id')

    if request.method == "POST":
        try:
            # Debug: Print all form data to see what's being received
            print("Form data received:", request.form)
            print("Files received:", request.files)
            
            student_id = request.form.get("student_id")
            # Get teacher ID from session
            teacher_id = session.get('teacher_id')
            achievement_type = request.form.get("achievement_type")
            event_name = request.form.get("event_name")
            achievement_date = request.form.get("achievement_date")
            organizer = request.form.get("organizer")
            position = request.form.get("position")
            achievement_description = request.form.get("achievement_description")

            # Debug: Print key form values
            print(f"Student ID: {student_id}")
            print(f"Achievement Type: {achievement_type}")
            print(f"Event Name: {event_name}")


            with sqlite3.connect(DB_PATH) as connection:
                # First establish connection and cursor before using them
                # connection = sqlite3.connect(DB_PATH)
                cursor = connection.cursor()

                # Debug: Check if achievements table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='achievements'")
                table_exists = cursor.fetchone()
                print(f"Achievements table exists: {table_exists is not None}")

                # Check if student ID exists - fixed parameter passing
                cursor.execute("SELECT student_id, student_name FROM student WHERE student_id = ?", (student_id,))
                student_data = cursor.fetchone()
                    
                if not student_data:
                    connection.close()
                    return render_template("submit_achievements.html", error="Student ID does not exist in the system.")
                
                student_name = student_data[1]
            
                # Handle certificate file upload
                certificate_path = None
                if 'certificate' in request.files:
                    file = request.files['certificate']
                    if file and file.filename != '':
                        if allowed_file(file.filename):
                            # Create a secure filename with timestamp to prevent duplicates
                            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                            secure_name = f"{timestamp}_{secure_filename(file.filename)}"
                            file_path = os.path.join(UPLOAD_FOLDER, secure_name)
                            file.save(file_path)
                            certificate_path = f"uploads/{secure_name}"
                        else:
                            connection.close()
                            return render_template("submit_achievements.html", error="Invalid file type. Please upload PDF, PNG, JPG, or JPEG files.")
                        
                # Parse team_size
                team_size = request.form.get("team_size")
                if team_size and team_size.strip():
                    team_size = int(team_size)
                else:
                    team_size = None
                    
                # Get other form fields
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
                
                # Debug: Print the values we're about to insert
                print(f"About to insert values: {student_id}, {achievement_type}, {event_name}, {achievement_date}")
                    
                # Insert achievement into database
                try:
                    cursor.execute('''
                    INSERT INTO achievements (
                    student_id, teacher_id, achievement_type, event_name, achievement_date, 
                    organizer, position, achievement_description, certificate_path,
                    symposium_theme, programming_language, coding_platform, paper_title,
                    journal_name, conference_level, conference_role, team_size,
                    project_title, database_type, difficulty_level, other_description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                    student_id, teacher_id, achievement_type, event_name, achievement_date,
                    organizer, position, achievement_description, certificate_path,
                    symposium_theme, programming_language, coding_platform, paper_title,
                    journal_name, conference_level, conference_role, team_size,
                    project_title, database_type, difficulty_level, other_description
                    ))

                    # Check how many rows were affected
                    rows_affected = cursor.rowcount
                    print(f"Rows inserted: {rows_affected}")
                
                    connection.commit()
                    print("Database committed successfully")

                    # Verify the data was inserted by selecting it back
                    cursor.execute("SELECT * FROM achievements WHERE student_id = ? ORDER BY id DESC LIMIT 1", (student_id,))
                    inserted_data = cursor.fetchone()
                    print(f"Data after insertion: {inserted_data}")
            
                    connection.close()

                    success_message = f"Achievement of {student_name} has been successfully registered!!"
                    return render_template("submit_achievements.html", success=success_message)

            
                except sqlite3.Error as sql_error:
                    print(f"SQL Error: {sql_error}")
                    connection.close()
                    return render_template("submit_achievements.html", error=f"Database error: {str(sql_error)}")
    
        except Exception as e:
            print(f"Error submitting achievement: {e}")
            import traceback
            traceback.print_exc()  # Print the full error traceback for debugging
            return render_template("submit_achievements.html", error=f"An error occurred: {str(e)}")
        

    # Redirect to success page or back to dashboard
    return redirect(url_for("teacher-dashboard", success="Achievement submitted successfully!"))


@app.route("/student-achievements", endpoint="student-achievements")
def student_achievements():
    # Check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('student'))

    # Get the current user data from session
    student_data = {
        'id': session.get('student_id'),
        'name': session.get('student_name'),
        'dept': session.get('student_dept')
    }
    return render_template("student_achievements_1.html", student=student_data)


@app.route("/student-dashboard", endpoint="student-dashboard")
def student_dashboard():
    # Check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('student'))

    # Get the current user data from session
    student_data = {
        'id': session.get('student_id'),
        'name': session.get('student_name'),
        'dept': session.get('student_dept')
    }
        
    return render_template("student_dashboard.html", student=student_data)


# Temporary Code. Needs to be updated once the backend is complete
@app.route("/teacher-dashboard", endpoint="teacher-dashboard")
def teacher_dashboard():
    # Check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('teacher'))

    # Get the current user data from session
    teacher_id = session.get('teacher_id')
    teacher_data = {
        'id': teacher_id,
        'name': session.get('teacher_name'),
        'dept': session.get('teacher_dept')
    }

    # Connect to database
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row  # This enables column access by name
    cursor = connection.cursor()

    # Get statistics
    # Total achievements recorded by this teacher
    cursor.execute("SELECT COUNT(*) FROM achievements WHERE teacher_id = ?", (teacher_id,))
    total_achievements = cursor.fetchone()[0]

    # Count unique students managed by this teacher
    cursor.execute("SELECT COUNT(DISTINCT student_id) FROM achievements WHERE teacher_id = ?", 
                  (teacher_id,))
    students_managed = cursor.fetchone()[0]

    # Count achievements recorded this week
    one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM achievements WHERE teacher_id = ? AND achievement_date >= ?", 
                  (teacher_id, one_week_ago))
    this_week_count = cursor.fetchone()[0]

    # Get recent entries
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

    # Prepare statistics data
    stats = {
        'total_achievements': total_achievements,
        'students_managed': students_managed,
        'this_week': this_week_count
    }
    
    return render_template("teacher_dashboard.html", 
                           teacher=teacher_data,
                           stats=stats,
                           recent_entries=recent_entries)



@app.route("/all-achievements", endpoint="all-achievements")
def all_achievements():
    # Check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('teacher'))

    teacher_id = session.get('teacher_id')
    
    # Connect to database
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    # Get all achievements by this teacher
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


# ------------------------------------------------------------------
# Firebase Authentication Routes
# ------------------------------------------------------------------

@app.route("/auth/firebase-config", methods=["GET"])
def get_auth_firebase_config():
    """
    Returns Firebase configuration to frontend
    This endpoint provides the config needed for Firebase initialization
    IMPORTANT: apiKey is public and safe to expose, but never expose private keys
    """
    firebase_config = get_firebase_config()
    return jsonify(firebase_config)


@app.route("/auth/google-login", methods=["POST"])
def google_login():
    """
    Handle Google Sign-In authentication
    
    Expected POST data:
    {
        "email": "user@example.com",
        "displayName": "User Name",
        "photoURL": "https://...",
        "uid": "firebase_uid",
        "idToken": "firebase_id_token"
    }
    
    TODO: Developers should integrate with Firebase Admin SDK to verify idToken
    For now, basic email validation is implemented
    """
    try:
        data = request.get_json()
        email = data.get("email")
        display_name = data.get("displayName")
        photo_url = data.get("photoURL")
        firebase_uid = data.get("uid")
        
        # TODO: Verify idToken with Firebase Admin SDK
        # import firebase_admin
        # from firebase_admin import auth
        # try:
        #     decoded_token = auth.verify_id_token(data.get("idToken"))
        #     uid = decoded_token['uid']
        # except:
        #     return jsonify({"success": False, "message": "Invalid token"}), 401
        
        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400
        
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        
        # Check if student exists (students can login via Google)
        cursor.execute("SELECT * FROM student WHERE email = ?", (email,))
        student_data = cursor.fetchone()
        
        if student_data:
            # Student exists - login via Google
            session.permanent = True
            session['logged_in'] = True
            session['student_id'] = student_data[1]
            session['student_name'] = student_data[0]
            session['student_dept'] = student_data[6]
            session['google_auth'] = True
            session['firebase_uid'] = firebase_uid
            
            connection.close()
            return jsonify({
                "success": True, 
                "message": "Student logged in successfully",
                "redirectUrl": "/student-dashboard"
            }), 200
        else:
            # TODO: Create new student account or ask to register
            # For now, reject unknown users
            connection.close()
            return jsonify({
                "success": False, 
                "message": f"No student account found for {email}. Please register first."
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"Login error: {str(e)}"
        }), 500


@app.route("/auth/logout", methods=["POST"])
def logout():
    """
    Handle logout for both traditional and Google Sign-In users
    Clears session data
    """
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200


    
if __name__ == "__main__":
    init_db()
    # migrate_achievements_table()
    add_teacher_id_column()
    app.run(debug=True)




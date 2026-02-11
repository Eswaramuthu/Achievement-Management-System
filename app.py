import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from config import DevelopmentConfig, ProductionConfig
from firebase_config import get_firebase_config, validate_firebase_config
from utils import allowed_file, init_db, handle_registration

import firebase_admin
from firebase_admin import auth, credentials

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# App setup
# ------------------------------------------------------------------

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# Initialize Firebase Admin SDK
firebase_service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
if firebase_service_account and os.path.exists(firebase_service_account):
    try:
        cred = credentials.Certificate(firebase_service_account)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Firebase Admin SDK: {e}")
else:
    logger.warning("FIREBASE_SERVICE_ACCOUNT_PATH not found or file does not exist. Token verification will be skipped.")

# Choose config based on environment
env = os.environ.get("FLASK_ENV", "development")

if env == "production":
    app.config.from_object(ProductionConfig)
    ProductionConfig.validate()
else:
    app.config.from_object(DevelopmentConfig)

DB_PATH = app.config["DB_PATH"]
UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]

os.makedirs(UPLOAD_FOLDER, exist_ok=True)



# Initialize database on startup
init_db(DB_PATH)

@app.route("/")
def home() -> str:
    """Render the homepage."""
    return render_template("index.html")


@app.route("/student", methods=["GET", "POST"])
def student() -> any:
    """
    Handle student login.
    
    Returns:
        Rendered login template or dashboard redirect
    """
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
def teacher() -> any:
    """
    Handle teacher login.
    
    Returns:
        Rendered login template or dashboard redirect
    """
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


@app.route("/student_new", methods=["GET", "POST"])
def student_new() -> any:
    """
    Handle student registration.
    
    Returns:
        Rendered registration form or login redirect
    """
    return handle_registration(
        user_type="student",
        form_data=request.form,
        template_name="student_new",
        db_path=DB_PATH
    )


@app.route("/teacher-new", endpoint="teacher-new", methods=["GET", "POST"])
def teacher_new() -> any:
    """
    Handle teacher registration.
    
    Requires TEACHER_REGISTRATION_CODE for security.
    
    Returns:
        Rendered registration form or login redirect
    """
    return handle_registration(
        user_type="teacher",
        form_data=request.form,
        template_name="teacher_new",
        db_path=DB_PATH,
        require_auth_code=True,
        auth_code_env_var="TEACHER_REGISTRATION_CODE"
    )


@app.route("/teacher-achievements", endpoint="teacher-achievements")
def teacher_achievements() -> str:
    """Render the teacher achievements page."""
    return render_template("teacher_achievements.html")


@app.route("/submit_achievements", endpoint="submit_achievements", methods=["GET", "POST"])
def submit_achievements() -> any:
    """
    Handle achievement submission by teachers.
    
    Returns:
        Rendered template with success/error message or redirect
    """
    # Check if teacher is logged in
    if not session.get('logged_in') or not session.get('teacher_id'):
        return redirect(url_for('teacher'))
        
    # Get teacher ID from session
    teacher_id = session.get('teacher_id')

    if request.method == "POST":
        try:
            # Debug: Log form data
            logger.info(f"Form data received: {request.form}")
            logger.info(f"Files received: {request.files}")
            
            student_id = request.form.get("student_id")
            # Get teacher ID from session
            teacher_id = session.get('teacher_id')
            achievement_type = request.form.get("achievement_type")
            event_name = request.form.get("event_name")
            achievement_date = request.form.get("achievement_date")
            organizer = request.form.get("organizer")
            position = request.form.get("position")
            achievement_description = request.form.get("achievement_description")

            # Log key form values
            logger.info(f"Student ID: {student_id}, Type: {achievement_type}, Event: {event_name}")


            with sqlite3.connect(DB_PATH) as connection:
                cursor = connection.cursor()

                # Check if achievements table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='achievements'")
                table_exists = cursor.fetchone()
                logger.info(f"Achievements table exists: {table_exists is not None}")

                # Check if student ID exists
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
                        if allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"]):
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
                    logger.info(f"Rows inserted: {rows_affected}")
                
                    connection.commit()
                    logger.info("Database committed successfully")

                    # Verify the data was inserted by selecting it back
                    cursor.execute("SELECT * FROM achievements WHERE student_id = ? ORDER BY id DESC LIMIT 1", (student_id,))
                    inserted_data = cursor.fetchone()
                    logger.info(f"Data after insertion: {inserted_data}")
            
                    connection.close()

                    success_message = f"Achievement of {student_name} has been successfully registered!!"
                    return render_template("submit_achievements.html", success=success_message)

            
                except sqlite3.Error as sql_error:
                    logger.error(f"SQL Error: {sql_error}")
                    connection.close()
                    return render_template("submit_achievements.html", error=f"Database error: {str(sql_error)}")
    
        except Exception as e:
            logger.error(f"Error submitting achievement: {e}")
            return render_template("submit_achievements.html", error=f"An error occurred: {str(e)}")
        

    # Redirect to success page or back to dashboard
    return redirect(url_for("teacher-dashboard", success="Achievement submitted successfully!"))


@app.route("/student-achievements", endpoint="student-achievements")
def student_achievements() -> any:
    """
    Render the student's achievement view.
    
    Returns:
        Rendered template or redirect to login
    """
    # Check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('student'))

    # Get the current user data from session
    student_data = {
        'id': session.get('student_id'),
        'name': session.get('student_name'),
        'dept': session.get('student_dept')
    }
    return render_template("student_achievements.html", student=student_data)


@app.route("/student-dashboard", endpoint="student-dashboard")
def student_dashboard() -> any:
    """
    Render the student dashboard.
    
    Returns:
        Rendered template or redirect to login
    """
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
def teacher_dashboard() -> any:
    """
    Render the teacher dashboard with statistics and recent entries.
    
    Returns:
        Rendered template or redirect to login
    """
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
def all_achievements() -> any:
    """
    Render all achievements recorded by the current teacher.
    
    Returns:
        Rendered template or redirect to login
    """
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
def get_auth_firebase_config() -> any:
    """
    Returns Firebase configuration to frontend.
    
    This endpoint provides the config needed for Firebase initialization.
    IMPORTANT: apiKey is public and safe to expose, but never expose private keys.
    
    Returns:
        JSON response with Firebase config
    """
    firebase_config = get_firebase_config()
    return jsonify(firebase_config)


@app.route("/auth/google-login", methods=["POST"])
def google_login() -> any:
    """
    Handle Google Sign-In authentication.
    
    Expected POST data:
    {
        "email": "user@example.com",
        "displayName": "User Name",
        "photoURL": "https://...",
        "uid": "firebase_uid",
        "idToken": "firebase_id_token"
    }
    
    Verifies the identity token with Firebase Admin SDK if available.
    
    Returns:
        JSON response with success status and redirect URL
    """
    try:
        data = request.get_json()
        id_token = data.get("idToken")
        email = data.get("email")
        firebase_uid = data.get("uid")
        
        # Verify idToken with Firebase Admin SDK if initialized
        verified_email = None
        if firebase_admin._apps:
            try:
                decoded_token = auth.verify_id_token(id_token)
                verified_email = decoded_token.get('email')
                if verified_email != email:
                    logger.warning(f"Email mismatch: {verified_email} vs {email}")
                    return jsonify({"success": False, "message": "Identity verification failed"}), 401
                logger.info(f"Firebase token verified for {email}")
            except Exception as e:
                logger.error(f"Firebase token verification failed: {e}")
                return jsonify({"success": False, "message": f"Invalid token: {str(e)}"}), 401
        else:
            logger.warning("Firebase Admin not initialized. Skipping token verification (Development Mode Only).")
        
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
            connection.close()
            return jsonify({
                "success": False, 
                "message": f"No student account found for {email}. Please register first."
            }), 404
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            "success": False, 
            "message": f"Login error: {str(e)}"
        }), 500


@app.route("/auth/logout", methods=["POST"])
def logout() -> any:
    """
    Handle logout for both traditional and Google Sign-In users.
    
    Clears session data.
    
    Returns:
        JSON response with success status
    """
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200


    
if __name__ == "__main__":
    logger.info("Starting Achievement Management System...")
    init_db(DB_PATH)
    logger.info("Database initialized successfully")
    app.run(debug=True)




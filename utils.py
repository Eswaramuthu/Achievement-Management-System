import os
import sqlite3
import datetime
import logging
from flask import render_template, redirect, url_for, request
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from firebase_config import get_firebase_config

logger = logging.getLogger(__name__)

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if a filename has an allowed extension.
    
    Args:
        filename: The name of the file to check
        allowed_extensions: A set of allowed file extensions
        
    Returns:
        True if the file extension is allowed, False otherwise
    """
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )

def init_db(db_path: str = None) -> None:
    """
    Initialize the SQLite database with required tables.
    
    Args:
        db_path: Optional path to the database file. Defaults to 'ams.db' in the project root.
    """
    if db_path is None:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ams.db")
    
    connection = None
    try:
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

        connection.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        if connection:
            connection.close()


def handle_registration(
    user_type: str, 
    form_data: dict, 
    template_name: str, 
    db_path: str = None, 
    require_auth_code: bool = False, 
    auth_code_env_var: str = None
) -> any:
    """
    Generic registration helper function for both students and teachers.
    
    Args:
        user_type: Type of user ('student' or 'teacher')
        form_data: Dictionary containing form submission data
        template_name: Name of the template to render on failure or GET
        db_path: Optional path to the database file
        require_auth_code: Whether to require an authorization code
        auth_code_env_var: Environment variable name for the registration code
        
    Returns:
        Rendered template or redirect response
    """
    if db_path is None:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ams.db")
    firebase_config = get_firebase_config()
    logger.info(f"{user_type.capitalize()} registration request: {request.method}")
    
    if request.method == "POST":
        # Extract common fields
        name = form_data.get(f"{user_type}_name")
        user_id = form_data.get(f"{user_type}_id")
        email = form_data.get("email")
        phone_number = form_data.get("phone_number")
        password = generate_password_hash(form_data.get("password"))
        gender = form_data.get(f"{user_type}_gender")
        dept = form_data.get(f"{user_type}_dept")
        
        logger.info(f"Registering {user_type}: {user_id}")

        # Authorization code check if required
        if require_auth_code and auth_code_env_var:
            auth_code = form_data.get(f"{user_type}_code")
            required_code = os.environ.get(auth_code_env_var, "default_code")
            if auth_code != required_code:
                logger.warning(f"Invalid {user_type} code provided for: {user_id}")
                return render_template(
                    f"{template_name}.html",
                    error=f"Invalid {user_type.capitalize()} Code. Registration denied.",
                    firebase_config=firebase_config
                )

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            # Insert the user
            cursor.execute(f"""
                INSERT INTO {user_type} (
                    {user_type}_name, {user_type}_id, email, phone_number, 
                    password, {user_type}_gender, {user_type}_dept
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, user_id, email, phone_number, password, gender, dept))
            
            connection.commit()
            logger.info(f"{user_type.capitalize()} {user_id} registered successfully!")
            return redirect(url_for(user_type))
            
        except sqlite3.IntegrityError as e:
            logger.error(f"{user_type.capitalize()} registration failed - Duplicate record: {e}")
            return render_template(
                f"{template_name}.html",
                error="This email or ID already exists",
                firebase_config=firebase_config
            )
        except sqlite3.Error as e:
            logger.error(f"Database error during {user_type} registration: {e}")
            return render_template(
                f"{template_name}.html",
                error="Database error occurred",
                firebase_config=firebase_config
            )
        finally:
            connection.close()
    
    return render_template(f"{template_name}.html", firebase_config=firebase_config)

def migrate_db(db_path: str) -> None:
    """
    Run necessary database migrations for existing tables.
    
    Args:
        db_path: Path to the database file
    """
    # This is a placeholder for the logic previously in migrate_achievements_table and add_teacher_id_column
    # Since init_db now includes all columns, this is mainly for existing databases.
    pass

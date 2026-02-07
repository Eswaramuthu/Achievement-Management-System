from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from models import db, Student, Teacher, Achievement
import os
import datetime
from werkzeug.utils import secure_filename
import logging

teacher_bp = Blueprint('teacher_bp', __name__)
logger = logging.getLogger(__name__)

# Helper function
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@teacher_bp.route("/teacher-achievements", endpoint="teacher-achievements")
def teacher_achievements():
    return render_template("teacher_achievements_2.html")


@teacher_bp.route("/submit_achievements", endpoint="submit_achievements", methods=["GET", "POST"])
def submit_achievements():
    if not session.get('logged_in') or not session.get('teacher_id'):
        return redirect(url_for('auth.teacher'))
        
    teacher_id = session.get('teacher_id')

    if request.method == "POST":
        try:
            student_id = request.form.get("student_id")
            achievement_type = request.form.get("achievement_type")
            event_name = request.form.get("event_name")
            
            # Date handling
            date_str = request.form.get("achievement_date")
            try:
                achievement_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return render_template("submit_achievements.html", error="Invalid date format.")

            organizer = request.form.get("organizer")
            position = request.form.get("position")
            achievement_description = request.form.get("achievement_description")

            # Check if student exists using ORM
            student = db.session.get(Student, student_id)
            if not student:
                 return render_template("submit_achievements.html", error="Student ID does not exist in the system.")
            
            student_name = student.student_name
        
            # Handle certificate file upload
            certificate_path = None
            if 'certificate' in request.files:
                file = request.files['certificate']
                if file and file.filename != '':
                    if allowed_file(file.filename):
                        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        secure_name = f"{timestamp}_{secure_filename(file.filename)}"
                        # UPLOAD_FOLDER should be in current_app.config or relative to root
                        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        upload_folder = os.path.join(base_dir, 'static', 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        file_path = os.path.join(upload_folder, secure_name)
                        file.save(file_path)
                        file.save(file_path)
                        # Store only the filename, not "uploads/" prefix
                        certificate_path = secure_name
                    else:
                        return render_template("submit_achievements.html", error="Invalid file type.")
            
            team_size = request.form.get("team_size")
            if team_size and team_size.strip():
                team_size = int(team_size)
            else:
                team_size = None

            # Create new achievement
            new_achievement = Achievement(
                student_id=student_id,
                teacher_id=teacher_id,
                achievement_type=achievement_type,
                event_name=event_name,
                achievement_date=achievement_date,
                organizer=organizer,
                position=position,
                achievement_description=achievement_description,
                certificate_path=certificate_path,
                symposium_theme=request.form.get("symposium_theme"),
                programming_language=request.form.get("programming_language"),
                coding_platform=request.form.get("coding_platform"),
                paper_title=request.form.get("paper_title"),
                journal_name=request.form.get("journal_name"),
                conference_level=request.form.get("conference_level"),
                conference_role=request.form.get("conference_role"),
                team_size=team_size,
                project_title=request.form.get("project_title"),
                database_type=request.form.get("database_type"),
                difficulty_level=request.form.get("difficulty_level"),
                other_description=request.form.get("other_description")
            )
            
            db.session.add(new_achievement)
            db.session.commit()
            logger.info(f"Achievement submitted for student {student_name}")

            success_message = f"Achievement of {student_name} has been successfully registered!!"
            return render_template("submit_achievements.html", success=success_message)
    
        except Exception as e:
            logger.error(f"Error submitting achievement: {e}")
            return render_template("submit_achievements.html", error=f"An error occurred: {str(e)}")
        

    return redirect(url_for("teacher_bp.teacher-dashboard", success="Achievement submitted successfully!"))

@teacher_bp.route("/teacher-dashboard", endpoint="teacher-dashboard")
def teacher_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('auth.teacher'))

    teacher_id = session.get('teacher_id')
    teacher_data = {
        'id': teacher_id,
        'name': session.get('teacher_name'),
        'dept': session.get('teacher_dept')
    }

    # Statistics using SQLAlchemy
    total_achievements = Achievement.query.filter_by(teacher_id=teacher_id).count()
    students_managed = Achievement.query.with_entities(Achievement.student_id).filter_by(teacher_id=teacher_id).distinct().count()
    
    one_week_ago = datetime.date.today() - datetime.timedelta(days=7)
    this_week_count = Achievement.query.filter(
        Achievement.teacher_id == teacher_id,
        Achievement.achievement_date >= one_week_ago
    ).count()

    # Recent entries
    recent_entries = db.session.query(Achievement, Student.student_name)\
        .join(Student, Achievement.student_id == Student.student_id)\
        .filter(Achievement.teacher_id == teacher_id)\
        .order_by(Achievement.created_at.desc())\
        .limit(5).all()
    
    # Format entries for template
    formatted_entries = []
    for ach, s_name in recent_entries:
        formatted_entries.append({
            'id': ach.id,
            'student_id': ach.student_id,
            'student_name': s_name,
            'achievement_type': ach.achievement_type,
            'event_name': ach.event_name,
            'achievement_date': ach.achievement_date
        })

    stats = {
        'total_achievements': total_achievements,
        'students_managed': students_managed,
        'this_week': this_week_count
    }
    
    return render_template("teacher_dashboard.html", 
                           teacher=teacher_data,
                           stats=stats,
                           recent_entries=formatted_entries)

@teacher_bp.route("/all-achievements", endpoint="all-achievements")
def all_achievements():
    if not session.get('logged_in'):
        return redirect(url_for('auth.teacher'))

    teacher_id = session.get('teacher_id')
    
    # Get all achievements with student names
    achievements_data = db.session.query(Achievement, Student.student_name)\
        .join(Student, Achievement.student_id == Student.student_id)\
        .filter(Achievement.teacher_id == teacher_id)\
        .order_by(Achievement.achievement_date.desc()).all()
    
    # The existing template likely expects a list of objects or dictionaries
    # We'll create a list of objects that combine properties
    achievements = []
    for ach, s_name in achievements_data:
        # Create a hybrid object or dict for the template
        item = ach
        setattr(item, 'student_name', s_name)
        achievements.append(item)
    
    return render_template("all_achievements.html", achievements=achievements)

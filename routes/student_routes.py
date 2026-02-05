from flask import Blueprint, render_template, session, redirect, url_for

student_bp = Blueprint('student_bp', __name__)

@student_bp.route("/student-achievements", endpoint="student-achievements")
def student_achievements():
    if not session.get('logged_in'):
        return redirect(url_for('auth.student'))

    student_data = {
        'id': session.get('student_id'),
        'name': session.get('student_name'),
        'dept': session.get('student_dept')
    }
    return render_template("student_achievements_1.html", student=student_data)


@student_bp.route("/student-dashboard", endpoint="student-dashboard")
def student_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('auth.student'))

    student_data = {
        'id': session.get('student_id'),
        'name': session.get('student_name'),
        'dept': session.get('student_dept')
    }
        
    return render_template("student_dashboard.html", student=student_data)

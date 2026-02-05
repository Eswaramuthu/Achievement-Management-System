from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Student, Teacher
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route("/")
def home():
    return render_template("home.html")

@auth_bp.route("/student", methods=["GET", "POST"])
def student():
    if request.method == "POST":
        student_id = request.form.get("sname")
        password = request.form.get("password")

        student_data = db.session.get(Student, student_id)
        
        is_authenticated = False
        if student_data:
            try:
                if check_password_hash(student_data.password, password):
                    is_authenticated = True
                elif student_data.password == password: # Legacy plaintext
                    is_authenticated = True
            except:
                if student_data.password == password:
                    is_authenticated = True

        if is_authenticated:
            session['logged_in'] = True
            session['student_id'] = student_data.student_id
            session['student_name'] = student_data.student_name
            session['student_dept'] = student_data.student_dept
            return redirect(url_for("student_bp.student_dashboard"))
        else:
            return render_template("student.html", error="Invalid credentials. Please try again.")
    return render_template("student.html")

@auth_bp.route("/teacher", methods=["GET", "POST"])
def teacher():
    if request.method == "POST":
        teacher_id = request.form.get("tname")
        password = request.form.get("password")

        teacher_data = db.session.get(Teacher, teacher_id)

        is_authenticated = False
        if teacher_data:
            try:
                if check_password_hash(teacher_data.password, password):
                    is_authenticated = True
                elif teacher_data.password == password:
                    is_authenticated = True
            except:
                if teacher_data.password == password:
                    is_authenticated = True

        if is_authenticated:
            session['logged_in'] = True
            session['teacher_id'] = teacher_data.teacher_id
            session['teacher_name'] = teacher_data.teacher_name
            session['teacher_dept'] = teacher_data.teacher_dept
            return redirect(url_for("teacher_bp.teacher_dashboard"))
        else:
            return render_template("teacher.html", error="Invalid credentials. Please try again.")

    return render_template("teacher.html")

@auth_bp.route("/student-new", methods=["GET", "POST"])
def student_new():
    if request.method == "POST":
        student_name = request.form.get("student_name")
        student_id = request.form.get("student_id")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        student_gender = request.form.get("student_gender")
        student_dept = request.form.get("student_dept")

        try:
            hashed_password = generate_password_hash(password)
            new_student = Student(
                student_name=student_name,
                student_id=student_id,
                email=email,
                phone_number=phone_number,
                password=hashed_password,
                student_gender=student_gender,
                student_dept=student_dept
            )
            db.session.add(new_student)
            db.session.commit()
            logger.info(f"New student registered: {student_name} ({student_id})")
            return redirect(url_for("auth.student"))
        except Exception as e:
            logger.error(f"Error creating student account: {e}")
            return render_template("student_new_2.html", error="Error creating account. ID or Email might already exist.")
    
    return render_template("student_new_2.html")

@auth_bp.route("/teacher-new", endpoint="teacher-new", methods=["GET", "POST"])
def teacher_new():
    if request.method == "POST":
        teacher_name = request.form.get("teacher_name")
        teacher_id = request.form.get("teacher_id")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        teacher_gender = request.form.get("teacher_gender")
        teacher_dept = request.form.get("teacher_dept")

        try:
            hashed_password = generate_password_hash(password)
            new_teacher = Teacher(
                teacher_name=teacher_name,
                teacher_id=teacher_id,
                email=email,
                phone_number=phone_number,
                password=hashed_password,
                teacher_gender=teacher_gender,
                teacher_dept=teacher_dept
            )
            db.session.add(new_teacher)
            db.session.commit()
            logger.info(f"New teacher registered: {teacher_name} ({teacher_id})")
            return redirect(url_for("auth.teacher"))
        except Exception as e:
            logger.error(f"Error creating teacher account: {e}")
            return render_template("teacher_new_2.html", error="Error creating account. ID or Email might already exist.")

    return render_template("teacher_new_2.html")

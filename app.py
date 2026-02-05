from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import secrets
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

DB_PATH = "C:\\Users\\Dell\\Downloads\\AMS-Achievement-Management-System-main\\AMS-Achievement-Management-System-main\\Achievement-Management-System\\ams.db"

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}


def init_db():
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    connection.commit()
    connection.close()


init_db()


@app.route("/")
def home():
    return render_template("home.html")


# ---------------- STUDENT LOGIN ----------------
@app.route("/student", methods=["GET", "POST"])
def student():
    if request.method == "POST":
        student_id = request.form.get("sname")
        password = request.form.get("password")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM student WHERE student_id = ?", (student_id,))
        student_data = cursor.fetchone()
        connection.close()

        if student_data and check_password_hash(student_data[4], password):
            session.clear()
            session['logged_in'] = True
            session['student_id'] = student_data[1]
            session['student_name'] = student_data[0]
            session['student_dept'] = student_data[6]
            return redirect(url_for("student_dashboard"))

        return render_template("student.html", error="Invalid credentials")

    return render_template("student.html")


# ---------------- TEACHER LOGIN ----------------
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
            session.clear()
            session['logged_in'] = True
            session['teacher_id'] = teacher_data[1]
            session['teacher_name'] = teacher_data[0]
            session['teacher_dept'] = teacher_data[6]
            return redirect(url_for("teacher_dashboard"))

        return render_template("teacher.html", error="Invalid credentials")

    return render_template("teacher.html")


# ---------------- STUDENT REGISTRATION ----------------
@app.route("/student-new", methods=["GET", "POST"])
def student_new():
    if request.method == "POST":
        password = generate_password_hash(request.form.get("password"))

        data = (
            request.form.get("student_name"),
            request.form.get("student_id"),
            request.form.get("email"),
            request.form.get("phone_number"),
            password,
            request.form.get("student_gender"),
            request.form.get("student_dept")
        )

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO student VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)
        connection.commit()
        connection.close()

        return redirect(url_for("student"))

    return render_template("student_new_2.html")


# ---------------- TEACHER REGISTRATION ----------------
@app.route("/teacher-new", methods=["GET", "POST"])
def teacher_new():
    if request.method == "POST":
        password = generate_password_hash(request.form.get("password"))

        data = (
            request.form.get("teacher_name"),
            request.form.get("teacher_id"),
            request.form.get("email"),
            request.form.get("phone_number"),
            password,
            request.form.get("teacher_gender"),
            request.form.get("teacher_dept")
        )

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO teacher VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)
        connection.commit()
        connection.close()

        return redirect(url_for("teacher"))

    return render_template("teacher_new_2.html")


# ---------------- DASHBOARDS ----------------
@app.route("/student-dashboard")
def student_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("student"))
    return render_template("student_dashboard.html")


@app.route("/teacher-dashboard")
def teacher_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("teacher"))
    return render_template("teacher_dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)

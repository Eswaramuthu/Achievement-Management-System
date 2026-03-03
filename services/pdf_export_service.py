from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import A4
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ams.db")

def generate_student_pdf(student_id):
    file_path = f"static/portfolio_{student_id}.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("SELECT student_name FROM student WHERE student_id=?", (student_id,))
    student_name = cursor.fetchone()[0]

    elements.append(Paragraph(f"<b>Achievement Portfolio</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Student Name: {student_name}", styles["Normal"]))
    elements.append(Paragraph(f"Student ID: {student_id}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    cursor.execute("""
        SELECT achievement_type, event_name, achievement_date, position
        FROM achievements
        WHERE student_id = ?
        ORDER BY achievement_date DESC
    """, (student_id,))

    data = [["Type", "Event", "Date", "Position"]]

    for row in cursor.fetchall():
        data.append(list(row))

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(table)

    doc.build(elements)
    connection.close()

    return file_path
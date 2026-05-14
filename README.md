# Achievement Management System

A Flask-based web application for managing student achievements across departments. It provides role-based workflows for students, teachers, and administrators, including certificate upload and achievement analytics.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Eswaramuthu/Achievement-Management-System)
[![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Academic-orange)]()

## Highlights
- Centralized achievement records with category-specific metadata
- Role-based access for `student`, `teacher`, and `admin`
- Certificate upload (`pdf`, `png`, `jpg`, `jpeg`) with duplicate detection via SHA-256 hash
- Built-in analytics and filtering views
- Admin tools for department, user approval, and category management
- Optional Firebase client configuration for front-end integration

## Tech Stack
- Python 3.8+
- Flask
- SQLite (default: `ams.db`)
- Jinja2 templates + vanilla JavaScript
- Pytest for test coverage

## Repository Structure
```text
Achievement-Management-System/
|- app.py                         # Main Flask application and routes
|- config.py                      # App configuration classes
|- requirements.txt               # Python dependencies
|- .env.example                   # Environment variable template
|- services/
|  |- certificate_service.py      # OCR + parsing + duplicate hash orchestration
|- utils/
|  |- certificate_ocr.py
|  |- certificate_parser.py
|- templates/                     # Jinja2 templates
|- static/                        # CSS, JS, images, uploaded files
|- tests/                         # Test suite
`- README.md
```

## Getting Started
### 1. Clone
```bash
git clone https://github.com/Eswaramuthu/Achievement-Management-System.git
cd Achievement-Management-System
```

### 2. Create virtual environment
Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
```
On Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

Set at least:
- `SECRET_KEY` for session security
- Firebase variables only if you need Firebase-enabled front-end behavior

### 5. Run the app
```bash
python app.py
```
The app runs by default at `http://127.0.0.1:5000`.

Note: The database schema is initialized automatically on startup.

## Running Tests
```bash
pytest -v
```
Or:
```bash
python run_tests.py
```

## Architecture Diagram
```text
Browser (Student / Teacher / Admin)
            |
            v
   Flask App (`app.py`)
            |
            +--> Auth + Session Guards
            |    - student_required
            |    - teacher_required
            |    - admin_required
            |
            +--> Route Handlers + Jinja Templates
            |    - templates/*
            |    - static/*
            |
            +--> Certificate Pipeline
            |    - services/certificate_service.py
            |    - utils/certificate_ocr.py
            |    - utils/certificate_parser.py
            |
            +--> SQLite Storage (`ams.db`)
                 - student
                 - teacher
                 - admin
                 - achievements
                 - departments
                 - achievement_categories
```

## Workflow Diagram
```text
Student/Teacher/Admin opens web app
                |
                v
         Login or Register
                |
                v
     Role-based dashboard rendered
                |
      +---------+----------+
      |                    |
      v                    v
Teacher submits        Student views
achievement + file     achievements/profile
      |                    |
      v                    v
Certificate processed   Filter/search analytics
(OCR + parse + hash)         |
      |                    |
      +---------+----------+
                |
                v
         SQLite data updated
                |
                v
    Admin reviews users/departments/categories
```

## Role Workflow (Sequence)
```text
Teacher -> /teacher (login)
Teacher -> /submit_achievements (GET form)
Teacher -> /submit_achievements (POST record + certificate)
App -> certificate_service.py (OCR + parser + SHA-256)
App -> ams.db (insert achievement)
Student -> /student-dashboard (view stats)
Student -> /student-achievements (view records)
Admin -> /admin/users (approve users)
Admin -> /admin/departments and /admin/categories (manage masters)
```

## API-Style Route Table
| Method | Route | Access | Purpose |
|---|---|---|---|
| GET | `/` | Public | Home page |
| GET | `/terms` | Public | Terms page |
| GET | `/privacy-policy` | Public | Privacy policy page |
| GET | `/student-achievements` | Student | Student achievements view |
| GET | `/student-dashboard` | Student | Student dashboard |
| GET | `/student/profile` | Student | Student profile page |
| POST | `/student/profile/edit` | Student | Update student profile |
| GET | `/teacher-achievements` | Teacher | Teacher achievements view |
| GET, POST | `/submit_achievements` | Teacher | Submit new achievement records |
| GET | `/teacher-dashboard` | Teacher | Teacher dashboard |
| GET | `/all-achievements` | Authenticated | Consolidated achievements listing |
| GET, POST | `/student` | Public | Student login/auth flow |
| GET, POST | `/teacher` | Public | Teacher login/auth flow |
| GET, POST | `/student-new` | Public | Student registration |
| GET, POST | `/student_new` | Public | Student registration (alias route) |
| GET, POST | `/teacher-new` | Public | Teacher registration |
| GET, POST | `/admin` | Public | Admin login |
| GET | `/admin/dashboard` | Admin | Admin dashboard |
| GET | `/admin/users` | Admin | Admin user management |
| POST | `/admin/user/approve` | Admin | Approve pending users |
| GET | `/admin/departments` | Admin | Department management page |
| POST | `/admin/department/add` | Admin | Add department |
| POST | `/admin/department/delete` | Admin | Delete department |
| GET | `/admin/categories` | Admin | Achievement category management page |
| POST | `/admin/category/add` | Admin | Add achievement category |
| GET | `/admin/export` | Admin | Export admin data/report |
| GET | `/admin/logout` | Admin | End admin session |

## Configuration Notes
- Default SQLite DB path: `ams.db` in project root
- Upload folder: `static/uploads`
- Max upload size: 5 MB (configured in `config.py`)

## Security Notes
- Do not commit `.env`
- Change default admin credentials in production
- Always set a strong `SECRET_KEY`

## Documentation
- [Contributing Guide](Contributing.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Firebase Setup](FIREBASE_SETUP.md)

## License
This project is maintained as an academic/institutional project at SRM Institute of Science and Technology. Add an explicit OSS license file if public redistribution terms are required.

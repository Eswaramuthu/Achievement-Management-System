# Achievement Management System

A web-based platform for tracking academic achievements. Students can view their accomplishments, teachers can record them, and everyone gains a clear, organized picture of academic progress — all automated and centralized.
> 🔁 This project is a fork of [Eswaramuthu/Achievement-Management-System](https://github.com/Eswaramuthu/Achievement-Management-System) with improvements and documentation enhancements by [divyakrishnaraj0806-maker](https://github.com/divyakrishnaraj0806-maker).


## Problem

- Academic achievements are scattered across folders, emails, and paper records.

- Students struggle to showcase accomplishments during placements or applications.

- Teachers waste time managing spreadsheets and physical documents.

- No unified, organized view of student achievements exists.

## Solution

- Achievement Management System centralizes all achievements in one platform:

- Students see all achievements on a personal dashboard with analytics.

- Teachers input achievements through simple, auto-complete forms.

- Tracks hackathons, coding competitions, paper presentations, conferences, symposiums, including certificates, dates, positions, and detailed descriptions.

- Fast, clean, and fully organized system for academic tracking.

## Quick Start (Windows PowerShell)

```powershell
# Clone repository
git clone https://github.com/divyakrishnaraj0806-maker/Achievement-Management-System.git
cd Achievement-Management-System

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run application
python app.py
```


## Quick Start (macOS/Linux)

```bash
# Clone repository
git clone https://github.com/divyakrishnaraj0806-maker/Achievement-Management-System.git
cd Achievement-Management-System

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run application
python app.py
```

Now open → **http://localhost:5000**

## Tech Stack

- **Flask** (Python web framework)
- **SQLite** (database)
- **JavaScript** (vanilla JS for interactivity)
- **HTML/CSS** (responsive UI with dark/light mode)
- **Jinja2** (templating)

## Core Features

### For Students
- **Personal Dashboard** → View all achievements at a glance
- **Achievement Analytics** → Track progress over time
- **Advanced Filtering** → Search by type, year, position
- **Certificate Access** → Download proof instantly
- **Profile Management** → Update details anytime

### For Teachers
- **Quick Entry Forms** → Record achievements in seconds
- **Student Search** → Auto-complete for easy lookup
- **Certificate Upload** → Attach digital proofs
- **Batch Management** → Handle multiple entries efficiently
- **Dashboard Analytics** → View entry statistics

### Achievement Types Supported
✓ Hackathons  
✓ Coding Competitions  
✓ Paper Presentations  
✓ Conferences  
✓ Symposiums  
✓ Custom Events  

## Core Pages

| Page | Link |
|------|------|
| Home | `/` |
| Student Login | `/student-login` |
| Teacher Login | `/teacher-login` |
| Student Dashboard | `/student-dashboard` |
| Teacher Dashboard | `/teacher-dashboard` |
| View Achievements | `/view-achievements` |
| Add Achievement | `/add-achievement` |


## Project Structure

```
achievement-management-system/
├── app.py              → main flask app + routes
├── init_db.py          → database initialization
├── requirements.txt    → python dependencies
├── static/
│   ├── css/           → styles + themes
│   ├── js/            → client-side logic
│   └── certificates/  → uploaded files
├── templates/         → HTML pages
├── database/          → SQLite database
├── README.md
└── CONTRIBUTING.md
```

## Database Schema

**Students** ↔ **Achievements** ↔ **Teachers**

```
Student (student_id PK, name, email, password, dept, ...)
  ↓ 1:N
Achievement (id PK, student_id FK, type, event, date, position, certificate, ...)
  ↓ N:1
Teacher (teacher_id PK, name, email, password, dept, ...)
```
## Key Features Explained

### Dark/Light Mode
Toggle themes with persistent preference using localStorage

Smooth transitions with optimized color schemes

### Student Search with Auto-Complete
Teachers can quickly find students by typing student ID or name

Results appear instantly as you type

### Achievement Categories
Each achievement type has custom fields:
- **Hackathons**: team size, project title, difficulty level
- **Coding Competitions**: programming language, platform, problem difficulty
- **Paper Presentations**: paper title, journal name, conference level
- **Conferences**: role, conference level, presentation type
- **Symposiums**: theme, event scope, participation type

### Certificate Management
Upload certificates (PDF, JPG, PNG) up to 5MB. 
Access and download anytime from achievement records.

### Analytics Dashboard
Visual representation of achievement metrics by type, year, and position.
Track progress trends over time.

## Contributing

PRs and ideas are welcome! Please check → `CONTRIBUTING.md` before submitting.

## Future Roadmap

- [ ] Mobile app (iOS + Android)
- [ ] LinkedIn integration
- [ ] AI-powered certificate validation
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Advanced analytics with predictive insights
- [ ] Export achievements as PDF portfolio

## License

Academic project developed at SRM Institute of Science and Technology.

## Contact

GitHub Repository:  
https://github.com/divyakrishnaraj0806-maker/Achievement-Management-System  

Issues & Suggestions:  
https://github.com/divyakrishnaraj0806-maker/Achievement-Management-System/issues

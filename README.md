# 🎓 Achievement Management System

A web-based platform designed to help students and teachers **track, manage, and showcase academic achievements in one centralized system**.  
It simplifies record management, improves accessibility, and provides meaningful academic insights through structured analytics.

---

## 📑 Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Tech Stack](#tech-stack)
- [Quick Start Guide](#quick-start-guide)
- [Core Features](#core-features)
- [Achievement Types Supported](#achievement-types-supported)
- [Core Pages](#core-pages)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Key Features Explained](#key-features-explained)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🚩 Problem Statement

Academic achievements are often scattered across emails, paper certificates, spreadsheets, and folders, leading to inefficiencies.

| Problem | Impact |
|--------|--------|
| Certificates stored in multiple places | Difficult to track achievements |
| Manual spreadsheet management | Time-consuming for teachers |
| Lack of centralized record | Students struggle during placements |
| Limited academic visibility | No clear performance insights |

---

## ✅ Solution Overview

The **Achievement Management System** centralizes academic achievement tracking with structured storage, analytics, and certificate management.

| Feature | Description |
|--------|-------------|
| Central Dashboard | View all achievements in one place |
| Teacher Entry Forms | Fast, structured achievement input |
| Certificate Storage | Upload & access proofs anytime |
| Analytics Dashboard | Performance tracking & insights |
| Organized Records | Clean, searchable academic history |

---

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|--------|
| Flask | Python backend framework |
| SQLite | Lightweight database |
| JavaScript | Frontend interactivity |
| HTML/CSS | Responsive UI |
| Jinja2 | Template rendering |

---

## 🚀 Quick Start Guide

### ▶ Windows PowerShell

```bash
git clone https://github.com/Eswaramuthu/Achievement-Management-System.git
cd Achievement-Management-System

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python init_db.py
python app.py
```

---

### ▶ macOS / Linux

```bash
git clone https://github.com/Eswaramuthu/Achievement-Management-System.git
cd Achievement-Management-System

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python init_db.py
python app.py
```

👉 Open browser:

```
http://localhost:5000
```

---

## ⭐ Core Features

### 👨‍🎓 For Students

| Feature | Description |
|--------|-------------|
| Personal Dashboard | View all achievements easily |
| Analytics Tracking | Monitor academic growth |
| Advanced Filtering | Search by year, type, position |
| Certificate Access | Download proofs instantly |
| Profile Management | Update details anytime |

---

### 👩‍🏫 For Teachers

| Feature | Description |
|--------|-------------|
| Quick Entry Forms | Record achievements quickly |
| Student Search | Auto-complete lookup |
| Certificate Upload | Attach digital proofs |
| Batch Management | Handle multiple entries |
| Analytics Dashboard | View statistics |

---

## 🏆 Achievement Types Supported

- Hackathons  
- Coding Competitions  
- Paper Presentations  
- Conferences  
- Symposiums  
- Custom Academic Events  

---

## 🌐 Core Pages

| Page | Link |
|------|-----|
| Home | `/` |
| Student Login | `/student-login` |
| Teacher Login | `/teacher-login` |
| Student Dashboard | `/student-dashboard` |
| Teacher Dashboard | `/teacher-dashboard` |
| View Achievements | `/view-achievements` |
| Add Achievement | `/add-achievement` |

---

## 📂 Project Structure

```
achievement-management-system/
│
├── app.py
├── init_db.py
├── requirements.txt
├── static/
│   ├── css/
│   ├── js/
│   └── certificates/
├── templates/
├── database/
├── README.md
└── CONTRIBUTING.md
```

---

## 🗄 Database Schema

```
Students ↔ Achievements ↔ Teachers

Student
(student_id PK, name, email, password, dept)

Achievement
(id PK, student_id FK, type, event, date,
 position, certificate)

Teacher
(teacher_id PK, name, email, password, dept)
```

---

## 🔍 Key Features Explained

### 🌗 Dark/Light Mode
Persistent theme toggle using `localStorage` with optimized UI colors.

### 🔎 Student Search Auto-Complete
Instant search by student ID or name.

### 📑 Certificate Management
Supports PDF, JPG, PNG uploads (≤5MB).

### 📊 Analytics Dashboard
Visual insights by achievement type, year, and performance trends.

---

## 🛣 Future Roadmap

- Mobile App Integration  
- LinkedIn Achievement Sync  
- AI Certificate Validation  
- Email Notifications  
- Multi-language Support  
- Predictive Academic Analytics  
- PDF Achievement Portfolio Export  

---

## 🤝 Contributing

Contributions are welcome!

Steps:

1. Fork repository  
2. Create feature branch  
3. Commit changes  
4. Submit Pull Request  

Please ensure:

- Clean commit history  
- Proper documentation  
- Tested changes  

---

## 📜 License

Academic project developed at **SRM Institute of Science and Technology**.

---

## 📬 Contact

For questions, suggestions, or collaboration:

👉 GitHub Issues:  
https://github.com/Eswaramuthu/Achievement-Management-System/issues

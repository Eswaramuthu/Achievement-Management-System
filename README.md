# 🏆 Achievement Management System

> A centralized platform for tracking and showcasing academic achievements. Students access their accomplishments instantly. Teachers record them effortlessly. Everyone gets clarity.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Eswaramuthu/Achievement-Management-System)
[![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Academic-orange)](#-license)

---

## 🎯 The Problem

Academic achievements are scattered chaos:
- 📧 Certificates buried in email threads
- 📁 Paper documents lost in folders
- 📊 Teachers drowning in spreadsheets
- 🎓 Students can't showcase accomplishments during placements

**Result:** Wasted time, missed opportunities, zero visibility into actual progress.

---

## ✨ The Solution

**Achievement Management System** brings everything into one organized dashboard:

- 📍 **Centralized tracking** — All achievements in one place
- 📈 **Visual analytics** — Progress trends and insights at a glance
- ⚡ **Fast entry** — Teachers add records in seconds with auto-complete
- 🔍 **Smart filtering** — Find exactly what you need instantly
- 📄 **Certificate storage** — Digital proofs accessible anytime

---

## 🚀 Quick Start

### Windows (PowerShell)

```powershell
# Clone and navigate
git clone https://github.com/Eswaramuthu/Achievement-Management-System.git
cd Achievement-Management-System

# Set up environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Initialize and run
python init_db.py
python app.py
```

### macOS / Linux

```bash
# Clone and navigate
git clone https://github.com/Eswaramuthu/Achievement-Management-System.git
cd Achievement-Management-System

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize and run
python init_db.py
python app.py
```

**🌐 Open your browser** → `http://localhost:5000`

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Flask** | Lightweight Python web framework |
| **SQLite** | Embedded database for local storage |
| **JavaScript** | Dynamic interactivity (vanilla JS) |
| **HTML/CSS** | Responsive UI with theme support |
| **Jinja2** | Server-side templating |

---

## 💡 Core Features

### 👨‍🎓 For Students

| Feature | Description |
|---------|-------------|
| **Dashboard** | View all achievements with stats at a glance |
| **Analytics** | Track your progress over time with visual charts |
| **Filters** | Search by type, year, position, or keyword |
| **Certificates** | Download proof of achievements instantly |
| **📤 Export Cards** | Generate professional PNG/PDF cards with QR codes for LinkedIn |
| **🔗 Share & Verify** | Share achievements with QR code verification links |
| **Profile** | Manage personal details and preferences |

### 👨‍🏫 For Teachers

| Feature | Description |
|---------|-------------|
| **Quick Entry** | Add achievements with intuitive forms |
| **Auto-Complete** | Find students instantly as you type |
| **Upload** | Attach certificates (PDF, JPG, PNG up to 5MB) |
| **Batch Mode** | Manage multiple entries efficiently |
| **Dashboard** | View submission statistics and trends |

### 🎪 Achievement Types

The system supports comprehensive tracking for:

- 💻 **Hackathons** — Team projects, difficulty levels, project titles
- 🏅 **Coding Competitions** — Platforms, languages, problem difficulty
- 📝 **Paper Presentations** — Journal names, conference levels, paper titles
- 🎤 **Conferences** — Roles, presentation types, conference tiers
- 🎭 **Symposiums** — Themes, event scope, participation types
- ✨ **Custom Events** — Flexible fields for unique achievements

---

## 📂 Project Structure

```
achievement-management-system/
│
├── app.py                    # Flask application + routing logic
├── init_db.py                # Database schema initialization
├── requirements.txt          # Python dependencies
│
├── static/
│   ├── css/                  # Stylesheets + dark/light themes
│   ├── js/                   # Client-side JavaScript
│   └── certificates/         # Uploaded certificate files
│
├── templates/                # Jinja2 HTML templates
├── ams.db                    # SQLite database
├── instance/                 # Instance-specific files
│
├── README.md                 # This file
└── Contributing.md           # Contribution guidelines
```

---

## 🗄️ Database Schema

```
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│   Student   │            │ Achievement │            │   Teacher   │
├─────────────┤            ├─────────────┤            ├─────────────┤
│ student_id  │ PK         │ id          │ PK         │ teacher_id  │ PK
│ name        │            │ student_id  │ FK         │ name        │
│ email       │    1:N     │ teacher_id  │ FK   N:1   │ email       │
│ password    │ ─────────> │ type        │ <───────── │ password    │
│ department  │            │ event_name  │            │ department  │
│ ...         │            │ date        │            │ ...         │
└─────────────┘            │ position    │            └─────────────┘
                           │ certificate │
                           │ ...         │
                           └─────────────┘
```

---

## 🎨 Key Features Explained

### 🌓 Dark/Light Mode
Toggle between themes with one click. Preferences persist across sessions using localStorage. Smooth transitions and eye-friendly color schemes.

### 🔎 Smart Student Search
Type student ID or name — results appear instantly. No more scrolling through endless lists. Auto-complete makes teacher workflows lightning-fast.

### 📊 Achievement Analytics
Visual dashboards show:
- Achievements by type (pie charts)
- Progress over time (line graphs)
- Position distribution (bar charts)
- Year-wise breakdown

### 📁 Certificate Management
- Upload formats: PDF, JPG, PNG
- Max file size: 5MB
- Secure storage with unique filenames
- One-click download access

### 🔧 Custom Fields by Type
Each achievement category has specialized fields:

**Hackathons:** Team size, project title, tech stack, difficulty  
**Competitions:** Platform, language, problem set, ranking  
**Papers:** Journal, conference tier, impact factor, citations  
**Conferences:** Role, presentation format, audience size  
**Symposiums:** Theme, scope, participation mode

### 📤 Achievement Card Export & Sharing

Students can now generate professional achievement cards with QR codes:

- **PNG Export**: High-quality 300 DPI PNG images perfect for social media
- **PDF Export**: Printable PDF certificates ready for portfolios
- **QR Codes**: Scannable verification codes linking to public achievement pages
- **Social Sharing**: One-click sharing to LinkedIn, Twitter, and other platforms
- **Public Verification**: Shareable links allow anyone to verify achievements
- **Dark/Light Support**: Exported cards respect user's theme preference

**How to Use:**
1. Go to "My Achievements"
2. Click "Share Achievement" on any achievement card
3. Select "Export Card" to generate PNG/PDF
4. Download and share on LinkedIn or social media
5. Others can scan QR code to verify achievement

For detailed documentation, see [`ACHIEVEMENT_EXPORT_GUIDE.md`](ACHIEVEMENT_EXPORT_GUIDE.md).

---

## 🌐 Navigation Map

| Page | Route | Access |
|------|-------|--------|
| Home | `/` | Public |
| Student Login | `/student-login` | Public |
| Teacher Login | `/teacher-login` | Public |
| Student Dashboard | `/student-dashboard` | Students only |
| Teacher Dashboard | `/teacher-dashboard` | Teachers only |
| View Achievements | `/view-achievements` | Students only |
| Add Achievement | `/add-achievement` | Teachers only |

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
4. **Commit** your changes (`git commit -m 'Add amazing feature'`)
5. **Push** to your branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

📖 Read [`Contributing.md`](Contributing.md) for detailed guidelines.

---

## 🗺️ Roadmap

### Phase 1 (Current)
- [x] Core achievement tracking
- [x] Student & teacher dashboards
- [x] Certificate upload/download
- [x] Dark mode support

### Phase 2 (In Progress)
- [x] 🔗 LinkedIn integration & social sharing
- [x] 📤 Achievement card export (PNG/PDF)
- [x] QR code verification system
- [ ] 📱 Mobile app (iOS + Android)
- [ ] 🤖 AI-powered certificate validation
- [ ] 📧 Email notifications for new achievements
- [ ] 🌍 Multi-language support

### Phase 3 (Future)
- [ ] 📊 Advanced predictive analytics
- [ ] 📄 Export as PDF portfolio
- [ ] 🔐 OAuth authentication
- [ ] ☁️ Cloud deployment options

---

## 📜 License

Academic project developed at **SRM Institute of Science and Technology**.  
For educational and institutional use.

---

## 📬 Contact & Support

**Found a bug?** **Have an idea?** **Need help?**

- 🐛 [Report Issues](https://github.com/Eswaramuthu/Achievement-Management-System/issues)
- 💬 [Discussions](https://github.com/Eswaramuthu/Achievement-Management-System/discussions)
- 📧 Open an issue for direct contact

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ at SRM Institute of Science and Technology

</div>

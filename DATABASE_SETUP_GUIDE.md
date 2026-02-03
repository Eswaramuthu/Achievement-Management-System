# Database Setup Guide

## The Issue

You're encountering errors when trying to run `python init_db.py` because:

1. **The file `init_db.py` doesn't exist** - It's mentioned in the README but is missing from the repository
2. **The database path in `app.py` is hardcoded** - It points to another user's computer and won't work on your system

## Current Problem in app.py

Line 14 in `app.py` contains:
```python
DB_PATH = "C:\\Users\\Dell\\Downloads\\AMS-Achievement-Management-System-main\\AMS-Achievement-Management-System-main\\Achievement-Management-System\\ams.db"
```

This path only exists on the original developer's computer, not yours.

## Solution

### Option 1: Quick Fix (Recommended)

Since `app.py` already calls `init_db()` on startup, you can skip the separate `init_db.py` file entirely:

1. **Fix the database path in app.py**
   
   Change line 14 from:
   ```python
   DB_PATH = "C:\\Users\\Dell\\Downloads\\AMS-Achievement-Management-System-main\\AMS-Achievement-Management-System-main\\Achievement-Management-System\\ams.db"
   ```
   
   To:
   ```python
   DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ams.db")
   ```

2. **Install dependencies**
   ```bash
   source venv/Scripts/activate
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```
   
   The database will be created automatically when the app starts!

### Option 2: Create init_db.py (As per README)

If you want to follow the README exactly:

1. **Fix the database path in app.py** (same as Option 1, step 1)

2. **Create `init_db.py`** with this content:
   ```python
   import os
   import sqlite3
   from app import init_db, add_teacher_id_column

   if __name__ == "__main__":
       print("Initializing database...")
       init_db()
       add_teacher_id_column()
       print("Database initialization complete.")
   ```

3. **Install dependencies**
   ```bash
   source venv/Scripts/activate
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## What Gets Created

After initialization, you'll have:
- `ams.db` - SQLite database file in your project directory
- Tables: `student`, `teacher`, `achievements`

## Verification

To verify the database was created successfully:

```bash
# Check if the file exists
ls -la ams.db

# Or on Windows
dir ams.db
```

You can also use a SQLite browser tool to inspect the database structure.

## Additional Notes

- The virtual environment `venv` only has `pip` installed. You need to run `pip install -r requirements.txt` to install Flask and Flask-SQLAlchemy
- The database will be created in the same directory as `app.py`
- Initial database will be empty - you'll need to register students and teachers through the web interface

## Next Steps

After fixing the database issue:
1. Start the Flask application: `python app.py`
2. Open your browser to: `http://localhost:5000`
3. Register a student account at `/student-new`
4. Register a teacher account at `/teacher-new`
5. Start using the system!

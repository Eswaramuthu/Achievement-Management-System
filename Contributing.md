# Contributing to Achievement Management System

Thanks for your interest in contributing! This document explains how to set up the project locally, the branch and PR workflow, and basic code style expectations.

## Getting started locally

1. Fork the repo and clone your fork locally.

```bash
git clone https://github.com/yourusername/achievement-management-system.git
cd achievement-management-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run application
python app.py
```

2. Open **http://localhost:5000** to verify the app runs.

## Branching & PRs

- Work from feature branches: `feature/short-description` or `fix/short-description`.
- Keep `main` protected and up-to-date. Open a pull request against `main` when ready.
- Provide a clear PR description and link any related issue(s).

Example branch names:
- `feature/add-achievement-analytics`
- `fix/login-validation-error`
- `docs/update-readme`

## Commit messages

Use Conventional Commits style where convenient, for example:

- `feat: add filtering by achievement type`
- `fix: correct student search autocomplete`
- `docs: update installation instructions`
- `chore: update Flask dependencies`
- `refactor: improve database query performance`

## Coding style

### Python (Backend)
- Follow **PEP 8** style guide
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Use type hints where applicable

```python
def get_student_achievements(student_id: str) -> list:
    """
    Retrieve all achievements for a given student.
    
    Args:
        student_id: The unique identifier for the student
        
    Returns:
        List of achievement dictionaries
    """
    pass
```

### JavaScript (Frontend)
- Use `const` and `let` instead of `var`
- Use camelCase for variables and functions
- Add comments for complex logic
- Keep functions small and focused

```javascript
function validateAchievementForm(formData) {
  // Add validation logic here
  return isValid;
}
```

### HTML/CSS
- Use semantic HTML5 elements
- Follow BEM naming convention for CSS classes
- Keep styles modular and reusable

## Database changes

If you're modifying the database schema:

1. Document the changes in the PR description
2. Create a migration script if needed
3. Update the ER diagram documentation
4. Test on a fresh database before submitting

Example:
```python
# migrations/add_achievement_level.py
def upgrade():
    cursor.execute('''
        ALTER TABLE achievements 
        ADD COLUMN achievement_level TEXT
    ''')
```

## Tests

If tests are present, run them locally before requesting review:

```bash
python -m pytest
```

If there are no tests yet, open an issue proposing tests and we can add basic coverage.

## How to propose changes

1. **Small fixes**: Open a PR directly with a clear description
2. **New features**: Open an issue first to discuss the change
3. **Breaking changes**: Always discuss in an issue before starting

## Reporting bugs

Open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Python version, OS, browser (if UI-related)
- Any error messages or logs

Example bug report:
```
**Bug**: Student search returns no results

**Steps to reproduce**:
1. Login as teacher
2. Go to "Add Achievement"
3. Type student ID in search field
4. No results appear

**Environment**:
- Python 3.9.7
- Windows 10
- Chrome 120

**Error logs**:
[Paste any console errors here]
```

## Areas to contribute

Looking for ideas? Check these areas:

### Backend
- Optimize database queries
- Add data validation
- Improve error handling
- Add API endpoints for mobile app

### Frontend
- Enhance UI/UX design
- Improve mobile responsiveness
- Add loading indicators
- Implement better form validation

### Documentation
- Improve setup guides
- Add code comments
- Create video tutorials
- Write API documentation

### Features
- Achievement analytics dashboard
- Email notifications
- Export achievements as PDF
- Multi-language support
- Dark mode improvements

## Code of conduct

Please be respectful and constructive in all interactions. We welcome contributors of all skill levels and backgrounds.

**Expected behavior**:
- Be kind and patient
- Give constructive feedback
- Focus on what's best for the project
- Show empathy to other contributors

**Unacceptable behavior**:
- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Any conduct that creates an uncomfortable environment

## Questions?

- Create an issue with the `question` label
- Check existing issues and discussions
- Reach out to maintainers directly

**Thank you for contributing to Achievement Management System! 🎉**

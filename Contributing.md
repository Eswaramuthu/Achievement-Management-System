# Contributing to Achievement Management System

Thank you for your interest in contributing to the Achievement Management System.  
This document explains how to set up the project locally, contribution workflow, coding standards, and best practices.

---

## 🚀 Getting Started Locally

Follow these steps to run the project on your system:

```bash
# Clone your fork
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
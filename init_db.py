#!/usr/bin/env python
"""
Database initialization script
Initializes the SQLite database with required tables for the Achievement Management System
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import init_db

if __name__ == "__main__":
    try:
        print("Initializing database...")
        init_db()
        print("✓ Database initialized successfully!")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)

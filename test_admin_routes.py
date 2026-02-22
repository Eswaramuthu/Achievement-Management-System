#!/usr/bin/env python3
"""
Test script to verify admin routes work correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import sqlite3
from werkzeug.security import check_password_hash

def test_admin_login():
    """Test admin login functionality"""
    print("Testing admin login...")
    
    # Test database connection
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    
    # Check if admin exists
    cursor.execute("SELECT admin_id, password FROM admin WHERE admin_id = 'superadmin'")
    admin = cursor.fetchone()
    conn.close()
    
    if not admin:
        print("❌ Super admin not found in database")
        return False
    
    admin_id, hashed_password = admin
    
    # Test password
    test_password = "admin123"
    if check_password_hash(hashed_password, test_password):
        print(f"✅ Admin login credentials are correct")
        print(f"   Username: {admin_id}")
        print(f"   Password: {test_password}")
        return True
    else:
        print("❌ Admin password is incorrect")
        return False

def test_admin_routes():
    """Test that admin routes are defined"""
    print("\nTesting admin routes...")
    
    routes = [
        ("/admin", "admin_login", ["GET", "POST"]),
        ("/admin/dashboard", "admin_dashboard", ["GET"]),
        ("/admin/users", "admin_users", ["GET"]),
        ("/admin/departments", "admin_departments", ["GET"]),
        ("/admin/categories", "admin_categories", ["GET"]),
        ("/admin/export", "admin_export", ["GET"]),
        ("/admin/logout", "admin_logout", ["GET"]),
    ]
    
    all_good = True
    for route, endpoint, methods in routes:
        try:
            # Check if route exists in Flask app
            rule = None
            for r in app.url_map.iter_rules():
                if r.rule == route:
                    rule = r
                    break
            
            if rule:
                print(f"✅ Route {route} exists")
                print(f"   Endpoint: {rule.endpoint}")
                print(f"   Methods: {', '.join(rule.methods)}")
            else:
                print(f"❌ Route {route} not found")
                all_good = False
                
        except Exception as e:
            print(f"❌ Error checking route {route}: {e}")
            all_good = False
    
    return all_good

def test_database_tables():
    """Test that all required tables exist"""
    print("\nTesting database tables...")
    
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    
    required_tables = [
        'admin',
        'student', 
        'teacher',
        'achievements',
        'departments',
        'achievement_categories'
    ]
    
    all_good = True
    for table in required_tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            print(f"✅ Table '{table}' exists")
        else:
            print(f"❌ Table '{table}' missing")
            all_good = False
    
    conn.close()
    return all_good

def main():
    """Run all tests"""
    print("=" * 60)
    print("Admin System Route Test")
    print("=" * 60)
    
    tests = [
        test_database_tables,
        test_admin_login,
        test_admin_routes,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ All tests passed! Admin system is ready to use.")
        print("\nTo access the admin panel:")
        print("1. Make sure Flask app is running: python app.py")
        print("2. Open browser to: http://localhost:5000/admin")
        print("3. Login with: superadmin / admin123")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
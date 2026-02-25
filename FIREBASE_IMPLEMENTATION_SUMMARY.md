# firebase_config.py
"""
Firebase Configuration Module
Loads Firebase credentials from environment variables (.env file)
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Firebase Web SDK Configuration
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}

def get_firebase_config():
    """Returns Firebase configuration dictionary"""
    return FIREBASE_CONFIG

def validate_firebase_config():
    """Validates required Firebase config values"""
    required_keys = ["apiKey", "authDomain", "projectId", "appId"]
    missing_keys = [key for key in required_keys if not FIREBASE_CONFIG.get(key)]
    if missing_keys:
        raise ValueError(f"Missing Firebase configuration keys: {missing_keys}. Please check your .env file.")
    return True

# app.py (relevant additions)
from flask import Flask, request, session, jsonify, render_template
from firebase_config import get_firebase_config
import sqlite3

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Replace in production

# Serve Firebase config to frontend
@app.route("/auth/firebase-config", methods=["GET"])
def firebase_config_route():
    config = get_firebase_config()
    return jsonify(config)

# Google Login route
@app.route("/auth/google-login", methods=["POST"])
def google_login():
    """
    Handle Google Sign-In authentication
    TODO: Implement Firebase Admin SDK token verification
    """
    try:
        data = request.get_json()
        email = data.get("email")
        # Basic validation for now
        if not email:
            return jsonify({"success": False, "message": "Email required"}), 400

        # Connect to database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT student_id FROM student WHERE email=?", (email,))
        row = cursor.fetchone()
        if row:
            session['student_id'] = row[0]
            return jsonify({"success": True, "redirect": "/student-dashboard"})
        else:
            return jsonify({"success": False, "message": "Student not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out"})

# templates/home.html snippet
"""
<div id="g_id_onload"
     data-client_id="YOUR_GOOGLE_CLIENT_ID"
     data-callback="handleCredentialResponse">
</div>

<script>
  // Firebase configuration injected from backend
  window.FIREBASE_CONFIG = {
    apiKey: "{{ firebase_config['apiKey'] }}",
    authDomain: "{{ firebase_config['authDomain'] }}",
    databaseURL: "{{ firebase_config['databaseURL'] }}",
    projectId: "{{ firebase_config['projectId'] }}",
    storageBucket: "{{ firebase_config['storageBucket'] }}",
    messagingSenderId: "{{ firebase_config['messagingSenderId'] }}",
    appId: "{{ firebase_config['appId'] }}",
    measurementId: "{{ firebase_config['measurementId'] }}"
  };
</script>
"""

# static/js/firebase-init.js
"""
// Initialize Firebase
const firebaseConfig = window.FIREBASE_CONFIG;
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Google Sign-In
function signInWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider)
        .then(result => {
            const email = result.user.email;
            fetch('/auth/google-login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email: email})
            }).then(res => res.json())
              .then(data => {
                  if(data.success) {
                      window.location.href = data.redirect;
                  } else {
                      alert(data.message);
                  }
              });
        })
        .catch(error => console.error(error));
}

// Sign out
function signOut() {
    auth.signOut().then(() => {
        fetch('/auth/logout', {method:'POST'})
            .then(res => res.json())
            .then(data => alert(data.message));
    });
}
"""

# .env.example
"""
FIREBASE_API_KEY=YOUR_API_KEY_HERE
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=1:your-app-id:web:your-web-id
FIREBASE_MEASUREMENT_ID=your-measurement-id
"""

# FIREBASE_SETUP.md and FIREBASE_DEVELOPER_COMMENTS.md content included above in instructions
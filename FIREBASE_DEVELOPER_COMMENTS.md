"""
Firebase Configuration Module and Integration Guide for Achievement Management System
This single file contains all Firebase setup, backend route, frontend initialization,
and environment instructions in one copy-paste ready block.
"""

import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables
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
    return FIREBASE_CONFIG

def validate_firebase_config():
    required_keys = ["apiKey", "authDomain", "projectId", "appId"]
    missing_keys = [key for key in required_keys if not FIREBASE_CONFIG.get(key)]
    if missing_keys:
        raise ValueError(f"Missing Firebase configuration keys: {missing_keys}")
    return True

app = Flask(__name__)
firebase_config = get_firebase_config()

@app.route("/auth/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    email = data.get("email")
    # TODO: Replace with Firebase Admin SDK token verification
    # idToken = data.get("idToken")
    # decoded_token = auth.verify_id_token(idToken)
    # firebase_uid = decoded_token['uid']
    return jsonify({"success": True, "email": email})

# Frontend Firebase config injection example (in templates/home.html)
# <script>
#   window.FIREBASE_CONFIG = {
#       apiKey: "{{ firebase_config['apiKey'] }}",
#       authDomain: "{{ firebase_config['authDomain'] }}",
#       databaseURL: "{{ firebase_config['databaseURL'] }}",
#       projectId: "{{ firebase_config['projectId'] }}",
#       storageBucket: "{{ firebase_config['storageBucket'] }}",
#       messagingSenderId: "{{ firebase_config['messagingSenderId'] }}",
#       appId: "{{ firebase_config['appId'] }}",
#       measurementId: "{{ firebase_config['measurementId'] }}"
#   };
# </script>

# Frontend Google Sign-In button example (templates/home.html)
# <div id="g_id_onload"
#      data-client_id="YOUR_GOOGLE_CLIENT_ID"
#      data-callback="handleCredentialResponse">
# </div>

# Frontend JS Firebase initialization example (static/js/firebase-init.js)
# const firebaseConfig = window.FIREBASE_CONFIG;

# Optional: Store Firebase UID in database after successful login
# cursor.execute("""
#     UPDATE student SET firebase_uid = ? WHERE student_id = ?
# """, (firebase_uid, student_id))

# Instructions for developers:
# 1. Create Firebase project and Web app
# 2. Enable Google Sign-In
# 3. Copy credentials to .env file in project root:
#    FIREBASE_API_KEY=...
#    FIREBASE_AUTH_DOMAIN=...
#    FIREBASE_DATABASE_URL=...
#    FIREBASE_PROJECT_ID=...
#    FIREBASE_STORAGE_BUCKET=...
#    FIREBASE_MESSAGING_SENDER_ID=...
#    FIREBASE_APP_ID=...
#    FIREBASE_MEASUREMENT_ID=...
# 4. Never commit .env to GitHub
# 5. Replace Google OAuth client ID in home.html
# 6. Optionally implement Firebase Admin SDK token verification
# 7. Use HTTPS in production and secure credentials
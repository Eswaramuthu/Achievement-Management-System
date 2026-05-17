"""
Firebase Configuration Module
Loads Firebase credentials from environment variables (.env file)
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Firebase Web SDK Configuration
# IMPORTANT: These values are loaded from .env file (never committed to GitHub)
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
    """
    Returns Firebase configuration dictionary
    Used to pass to frontend JavaScript
    """
    return FIREBASE_CONFIG

def validate_firebase_config():
    """
    Validates that all required Firebase config values are present
    """
    required_keys = ["apiKey", "authDomain", "projectId", "appId"]
    missing_keys = [key for key in required_keys if not FIREBASE_CONFIG.get(key)]
    
    if missing_keys:
        raise ValueError(f"Missing Firebase configuration keys: {missing_keys}. Please check your .env file.")
    
    return True

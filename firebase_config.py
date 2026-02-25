"""
Firebase Configuration Module
Loads Firebase credentials securely from environment variables (.env file)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Firebase Web SDK Configuration
# ⚠️ Never commit actual credentials to GitHub
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
}


def get_firebase_config() -> dict:
    """
    Returns the Firebase configuration dictionary.
    Can be used to pass credentials to frontend JavaScript safely.

    Returns:
        dict: Firebase config
    """
    return FIREBASE_CONFIG


def validate_firebase_config() -> bool:
    """
    Ensures all required Firebase configuration keys are present.

    Raises:
        ValueError: If any required key is missing.

    Returns:
        bool: True if all required keys are present
    """
    required_keys = ["apiKey", "authDomain", "projectId", "appId"]
    missing_keys = [key for key in required_keys if not FIREBASE_CONFIG.get(key)]

    if missing_keys:
        raise ValueError(
            f"Missing Firebase configuration keys: {missing_keys}. "
            "Please check your .env file."
        )

    return True


# Optional: Automatically validate on import
try:
    validate_firebase_config()
except ValueError as e:
    print(f"[Firebase Config Warning] {e}")
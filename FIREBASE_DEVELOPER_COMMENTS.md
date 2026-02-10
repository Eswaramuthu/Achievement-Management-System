# Firebase Implementation - Developer Comments

This file documents all the places where developers need to add or configure Firebase credentials.

## Configuration File (`.env`)

**Location**: Root directory, `.env` file

```env
# DEVELOPERS: Add your Firebase credentials here
# These values should come from Firebase Console > Project Settings > Your apps

FIREBASE_API_KEY=YOUR_API_KEY_HERE
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=1:your-app-id:web:your-web-id
FIREBASE_MEASUREMENT_ID=your-measurement-id
```

### Instructions for Adding Credentials:
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click **Project Settings** (gear icon)
4. Go to **Your apps** > **Web app**
5. Copy the Firebase config object
6. Paste the values into `.env` file above
7. **IMPORTANT**: Never commit `.env` to GitHub

---

## Frontend Configuration (Google Sign-In Button)

**Location**: `templates/home.html` - Lines 63-66

```html
<div id="g_id_onload"
     data-client_id="YOUR_GOOGLE_CLIENT_ID"  <!-- DEVELOPERS: Replace with your OAuth Client ID -->
     data-callback="handleCredentialResponse">
</div>
```

### Instructions for Adding Client ID:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project
3. Go to **APIs & Services** > **Credentials**
4. Find your **OAuth 2.0 Client ID** (Web application type)
5. Copy the **Client ID** value
6. Replace `YOUR_GOOGLE_CLIENT_ID` with the actual value

**Example**:
```html
<div id="g_id_onload"
     data-client_id="123456789-abc.apps.googleusercontent.com"
     data-callback="handleCredentialResponse">
</div>
```

---

## Backend Authentication Route

**Location**: `app.py` - Lines 728-768

```python
@app.route("/auth/google-login", methods=["POST"])
def google_login():
    """
    Handle Google Sign-In authentication
    
    TODO: DEVELOPER - Implement Firebase Admin SDK Token Verification
    
    Current implementation:
    - Basic email validation only
    - Assumes token is valid
    
    PRODUCTION SETUP:
    1. Install Firebase Admin SDK:
       pip install firebase-admin
    
    2. Download service account key:
       - Go to Firebase Console > Project Settings > Service Accounts
       - Click "Generate New Private Key"
       - Save JSON file to project root (add to .gitignore)
    
    3. Replace the token verification section below with:
       
       from firebase_admin import credentials, auth
       import firebase_admin
       
       # Initialize Firebase Admin (do once at app startup)
       cred = credentials.Certificate('path/to/serviceAccountKey.json')
       firebase_admin.initialize_app(cred)
       
       # In google_login function:
       try:
           decoded_token = auth.verify_id_token(data.get("idToken"))
           firebase_uid = decoded_token['uid']
           email = decoded_token['email']
       except Exception as e:
           return jsonify({"success": False, "message": "Invalid token"}), 401
    """
    
    try:
        data = request.get_json()
        email = data.get("email")
        
        # TODO: DEVELOPER - Replace above basic validation with:
        # idToken = data.get("idToken")
        # decoded_token = auth.verify_id_token(idToken)  # Verify with Firebase Admin SDK
        # firebase_uid = decoded_token['uid']
        
        # ... rest of function
```

---

## Backend Firebase Config Manager

**Location**: `firebase_config.py` - Entire file

```python
"""
DEVELOPERS: This file loads Firebase configuration from environment variables

The get_firebase_config() function retrieves the configuration from the .env file.
You must have a valid .env file with Firebase credentials for this to work.

Example .env file (create this in the project root):
    FIREBASE_API_KEY=your_key
    FIREBASE_AUTH_DOMAIN=your_domain.firebaseapp.com
    ...
"""

from firebase_config import get_firebase_config

# Get config in your route:
firebase_config = get_firebase_config()

# Access specific values:
# firebase_config['apiKey']
# firebase_config['projectId']
# etc.
```

---

## Frontend Firebase Initialization

**Location**: `static/js/firebase-init.js` - Lines 1-20

```javascript
/**
 * DEVELOPERS: Firebase configuration is injected from the server
 * Do NOT hardcode credentials in this file
 * 
 * The server loads from .env:
 * window.FIREBASE_CONFIG = {
 *   apiKey: "{{ firebase_config['apiKey'] }}",
 *   authDomain: "{{ firebase_config['authDomain'] }}",
 *   ...
 * };
 * 
 * If Firebase config is not loading:
 * 1. Check that .env file exists
 * 2. Check browser console for errors
 * 3. Verify all required Firebase fields are in .env
 */

const firebaseConfig = window.FIREBASE_CONFIG;
```

---

## Environment Variables in Templates

**Location**: `templates/home.html` - Lines 104-113

```html
<script>
  /**
   * DEVELOPERS: Firebase configuration is dynamically loaded from the .env file
   * and passed to the template by the Flask backend
   * 
   * DO NOT paste credentials directly here
   * This uses Flask template variables: {{ firebase_config['...'] }}
   * which are populated from .env by firebase_config.py
   */
  
  window.FIREBASE_CONFIG = {
    apiKey: "{{ firebase_config['apiKey'] }}",
    authDomain: "{{ firebase_config['authDomain'] }}",
    // ... other fields from .env
  };
</script>
```

---

## Database Integration (Optional Enhancement)

**Location**: `app.py` - google_login function

```python
# TODO: DEVELOPERS - Consider storing Firebase UID in database for future use

# After successful login:
# 1. Store firebase_uid in student table:
#    cursor.execute("""
#        UPDATE student SET firebase_uid = ? WHERE student_id = ?
#    """, (firebase_uid, student_id))

# 2. This allows future enhancements like:
#    - Linking multiple auth methods
#    - Using Firebase Realtime Database
#    - Implementing Firebase Cloud Functions
```

---

## Checklist for Developers Setting Up Firebase

- [ ] Create Firebase project in Firebase Console
- [ ] Create web app in Firebase project
- [ ] Enable Google Sign-In in Authentication
- [ ] Create OAuth 2.0 credentials in Google Cloud Console
- [ ] Copy `.env.example` to `.env`
- [ ] Fill `.env` with Firebase credentials
- [ ] Update Google Client ID in `templates/home.html`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test Google Sign-In on homepage
- [ ] (Optional) Implement Firebase Admin SDK token verification
- [ ] (Optional) Store Firebase UID in database

---

## Security Best Practices

✅ **DO**:
- Store all credentials in `.env` file
- Keep `.env` in `.gitignore`
- Verify tokens on the backend (see TODO in app.py)
- Use HTTPS in production
- Rotate credentials regularly
- Use service accounts with minimal permissions

❌ **DON'T**:
- Hardcode credentials in any file
- Commit `.env` to version control
- Share credentials via email or chat
- Use the same credentials across environments
- Log sensitive information

---

## References

- [Firebase Console](https://console.firebase.google.com/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Firebase Web Setup Guide](https://firebase.google.com/docs/web/setup)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Google Sign-In Implementation](https://developers.google.com/identity/sign-in/web)

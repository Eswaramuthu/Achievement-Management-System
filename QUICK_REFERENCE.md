# Quick Reference - Firebase Configuration & Endpoints

## 🔐 Credential Locations

### Your Local Credentials (DO NOT COMMIT)
**File**: `.env`
```bash
# Essential Firebase Config
FIREBASE_API_KEY=AIzaSyAxhL77J1VfZJd3rqRyR-AtlPYSnZoXnn4
FIREBASE_PROJECT_ID=task-mate-90eee
# ... other fields
```
⚠️ This file is in `.gitignore` - it will NOT be committed to GitHub

### Template for Other Developers (COMMITTED)
**File**: `.env.example`
```bash
# Instructions for developers to get their own Firebase credentials
FIREBASE_API_KEY=your_api_key_here
FIREBASE_PROJECT_ID=your_project_id
# ...
```
✅ This file IS committed to GitHub - shows the structure

---

## 🌐 API Endpoints

### Authentication Endpoints

| Endpoint | Method | Purpose | Input |
|----------|--------|---------|-------|
| `/auth/google-login` | POST | Handle Google Sign-In | `{email, displayName, photoURL, uid, idToken}` |
| `/auth/logout` | POST | Clear user session | (none) |
| `/auth/firebase-config` | GET | Get Firebase config | (none) |

### Response Examples

**Success Response** (`/auth/google-login`):
```json
{
  "success": true,
  "message": "Student logged in successfully",
  "redirectUrl": "/student-dashboard"
}
```

**Error Response** (`/auth/google-login`):
```json
{
  "success": false,
  "message": "No student account found for user@example.com. Please register first."
}
```

---

## 📝 Configuration Files

### `.env` (Your Credentials - LOCAL ONLY)
```bash
# Firebase Configuration (from Firebase Console > Project Settings)
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_domain.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-db.firebaseio.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abcdef
FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key
```

### `.env.example` (Template - COMMITTED TO GITHUB)
```bash
# Copy this file to .env and fill in your Firebase credentials
# DO NOT commit .env to GitHub
FIREBASE_API_KEY=your_api_key_here
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
# ... etc
```

---

## 🔧 Code Integration Points

### Backend (`app.py`)

**Loading Firebase Config**:
```python
from firebase_config import get_firebase_config

firebase_config = get_firebase_config()
# Use in template: render_template("home.html", firebase_config=firebase_config)
```

**Google Login Route**:
```python
@app.route("/auth/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    email = data.get("email")
    # ... verify with database
    # ... set session
    return jsonify({"success": True, "redirectUrl": "/student-dashboard"})
```

### Frontend (`templates/home.html`)

**Injecting Firebase Config**:
```html
<script>
  window.FIREBASE_CONFIG = {
    apiKey: "{{ firebase_config['apiKey'] }}",
    projectId: "{{ firebase_config['projectId'] }}",
    // ... etc
  };
</script>
```

**Google Sign-In Handler**:
```javascript
function handleCredentialResponse(response) {
  // Send to backend /auth/google-login
  fetch('/auth/google-login', {
    method: 'POST',
    body: JSON.stringify({
      email: userInfo.email,
      idToken: response.credential
    })
  })
  .then(data => {
    if (data.success) {
      window.location.href = data.redirectUrl;
    }
  });
}
```

---

## 🔑 Required OAuth Credentials from Google

### From Google Cloud Console:

1. **OAuth 2.0 Client ID** (Web application):
   ```
   Client ID: 123456789-abc.apps.googleusercontent.com
   Client Secret: GOCSPX-xxxxxxxxxx (keep secret!)
   ```
   
2. **Authorized Redirect URIs**:
   - Development: `http://localhost:5000`
   - Production: `https://yourdomain.com`

### From Firebase Console:

1. **Web App Config**:
   ```javascript
   {
     apiKey: "AIzaSy...",
     authDomain: "project.firebaseapp.com",
     projectId: "project-id",
     // ... etc
   }
   ```

---

## 📱 Frontend Files Structure

```
templates/
  ├── home.html              # Google Sign-In button + Firebase config
  ├── student.html           # Traditional login
  └── teacher.html           # Traditional login

static/
  └── js/
      └── firebase-init.js   # Firebase SDK setup (currently unused, for future)
```

---

## ✅ Setup Checklist

- [ ] Create Firebase project
- [ ] Enable Google Sign-In in authentication
- [ ] Create OAuth 2.0 credentials in Google Cloud
- [ ] Copy `.env.example` → `.env`
- [ ] Add Firebase credentials to `.env`
- [ ] Add Google Client ID to `home.html`
- [ ] Run `pip install python-dotenv`
- [ ] Test: `python app.py` and visit `http://localhost:5000`
- [ ] Verify Google Sign-In button appears and works

---

## 🚀 Deployment

### Before Pushing to GitHub:
- ✅ Check that `.env` is in `.gitignore`
- ✅ Do NOT commit `.env` file
- ✅ Verify `.env.example` is properly documented
- ✅ Update `FIREBASE_DEVELOPER_COMMENTS.md` if needed

### For New Environments:
1. Each developer/environment gets its own `.env` file
2. Based on `.env.example` template
3. With their own Firebase credentials
4. Never shared or hardcoded

---

## 🐛 Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| `No module named 'dotenv'` | Run: `pip install python-dotenv` |
| Firebase config loads but shows undefined | Check `.env` file has all required fields |
| Google Sign-In button doesn't work | Update `data-client_id` in `home.html` |
| Session not created after login | Check student email exists in database |
| "missing .env file" error | Create `.env` based on `.env.example` |

---

## 📚 Related Documentation Files

1. **`FIREBASE_SETUP.md`** - Complete step-by-step setup guide
2. **`FIREBASE_DEVELOPER_COMMENTS.md`** - Detailed code comments
3. **`FIREBASE_IMPLEMENTATION_SUMMARY.md`** - What was implemented
4. **`.env.example`** - Sample configuration file

---

## 🔗 External Resources

- [Firebase Console](https://console.firebase.google.com/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Sign-In Documentation](https://developers.google.com/identity/sign-in/web)
- [Firebase Web Setup](https://firebase.google.com/docs/web/setup)
- [Firebase Authentication](https://firebase.google.com/docs/auth)

---

**Last Updated**: February 8, 2026
**Status**: Ready for Testing ✅

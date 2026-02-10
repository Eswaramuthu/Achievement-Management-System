# Firebase Setup Guide

This document explains how to set up Firebase Google Sign-In authentication for the Achievement Management System.

## Overview

The Achievement Management System uses Firebase for Google Sign-In authentication. This allows users to sign in using their Google accounts instead of traditional username/password login.

## Security Notes

⚠️ **IMPORTANT**: 
- **NEVER commit the `.env` file to GitHub** - it contains sensitive Firebase credentials
- The `.env` file is already in `.gitignore` and will not be committed
- Share `.env.example` instead, which other developers can use as a template
- Each developer and deployment should have their own Firebase project and credentials

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a new project"
3. Enter your project name (e.g., "Achievement Management System")
4. Enable Google Analytics if desired
5. Click "Create project"

## Step 2: Register a Web App

1. In Firebase Console, click the **Web** icon (</> symbol) to register a web app
2. Name your app (e.g., "AMS-Web")
3. Check "Also set up Firebase Hosting for this app" (optional)
4. Click "Register app"
5. Copy the Firebase config object (you'll need this in Step 5)

## Step 3: Enable Google Sign-In

1. In Firebase Console, go to **Authentication** in the left sidebar
2. Click the **Sign-in method** tab
3. Click **Google** from the list
4. Toggle ON the switch
5. Select a project support email
6. Click "Save"

## Step 4: Configure OAuth Consent Screen

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project
3. Go to **APIs & Services** > **OAuth consent screen**
4. Select "External" user type
5. Fill in the app information:
   - **App name**: Achievement Management System
   - **User support email**: Your email
   - **Scopes**: Add `email` and `profile` scopes
6. Add test users (your email account for testing)
7. Click "Save and Continue"

## Step 5: Set Up Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and fill in your Firebase configuration:
   ```bash
   FIREBASE_API_KEY=your_api_key_here
   FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   FIREBASE_DATABASE_URL=https://your_project-default-rtdb.firebaseio.com
   FIREBASE_PROJECT_ID=your_project_id
   FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
   FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   FIREBASE_APP_ID=1:your_app_id:web:your_web_id
   FIREBASE_MEASUREMENT_ID=your_measurement_id
   ```

3. **IMPORTANT**: Never commit this file. It's in `.gitignore` automatically.

## Step 6: Update Google Sign-In Client ID

In `templates/home.html`, update the Google Sign-In element:

```html
<div id="g_id_onload"
     data-client_id="YOUR_ACTUAL_GOOGLE_CLIENT_ID"
     data-callback="handleCredentialResponse">
</div>
```

Replace `YOUR_ACTUAL_GOOGLE_CLIENT_ID` with your actual Google OAuth 2.0 Client ID (found in Google Cloud Console > APIs & Services > Credentials).

## Step 7: Install Dependencies

If you haven't already, install python-dotenv:

```bash
pip install python-dotenv
pip install -r requirements.txt
```

## Step 8: Test the Setup

1. Activate your virtual environment:
   ```bash
   venv1\Scripts\Activate.ps1
   ```

2. Run the Flask app:
   ```bash
   python app.py
   ```

3. Navigate to `http://localhost:5000` in your browser

4. You should see a "Sign in with Google" button on the home page

5. Test the Google Sign-In by clicking the button

## File Structure

```
.env                          # Local config (NOT committed) - ADD YOUR CREDENTIALS HERE
.env.example                  # Template for developers (committed to GitHub)
firebase_config.py            # Server-side Firebase config manager
static/js/firebase-init.js    # Frontend Firebase SDK initialization
templates/home.html           # Updated with Google Sign-In button
app.py                        # Updated with Firebase auth routes
```

## Code Integration Points

### Backend Routes

**Route**: `POST /auth/google-login`
- **Purpose**: Handle Google Sign-In authentication
- **Expected Data**: Email, displayName, photoURL, uid, idToken
- **Response**: JSON with success status and redirect URL
- **TODO**: Add Firebase Admin SDK token verification (see comments in `app.py`)

**Route**: `POST /auth/logout`
- **Purpose**: Clear user session
- **Response**: JSON with success status

**Route**: `GET /auth/firebase-config`
- **Purpose**: Serve Firebase config to frontend
- **Response**: JSON Firebase configuration

### Frontend Files

**File**: `templates/home.html`
- Firebase config is injected from server (lines with `{{ firebase_config['...'] }}`)
- Google Sign-In callback: `handleCredentialResponse()`
- Google client ID needs to be updated (see Step 6)

**File**: `static/js/firebase-init.js`
- Firebase SDK initialization
- Google provider setup
- Sign-in and sign-out functions
- Token verification (currently basic, should be enhanced)

## Testing Accounts

For development, you can test with:
- Any Google account that's a "test user" in the OAuth consent screen
- Make sure you have a matching student record in the database

## Troubleshooting

### "Invalid credentials" error
- Check that the Google client ID in `home.html` matches your project
- Verify the accounts are set as test users in OAuth consent screen

### Firebase config not loading
- Check that `.env` file exists and has all required fields
- Ensure `python-dotenv` is installed
- Check Flask debug logs for errors

### Token verification errors
- TODO: Implement Firebase Admin SDK integration (see `app.py` comments)
- Currently basic validation is in place; add proper verification for production

## Next Steps for Production

1. **Token Verification**: Implement Firebase Admin SDK to verify tokens
   ```python
   from firebase_admin import auth
   decoded_token = auth.verify_id_token(idToken)
   ```

2. **Store Firebase UID**: Save Firebase UID with student records for better tracking

3. **Error Handling**: Implement comprehensive error handling and user feedback

4. **HTTPS**: Use HTTPS in production (Firebase requires it)

5. **CORS**: Configure CORS properly for your domain

## References

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firebase Web SDK Setup](https://firebase.google.com/docs/web/setup)
- [Google Sign-In Web Documentation](https://developers.google.com/identity/sign-in/web)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)

---

**For questions or issues**, refer to the Firebase documentation or contact the development team.

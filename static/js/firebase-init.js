/**
 * Firebase Initialization for Achievement Management System
 * 
 * This module initializes Firebase with proper ES module imports
 * Firebase config is loaded from environment variables (never hardcoded)
 * 
 * Usage: Import this module in your HTML to initialize Firebase
 * <script type="module" src="/static/js/firebase-init.js"></script>
 */

// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-analytics.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, signOut, setPersistence, browserLocalPersistence } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-auth.js";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
// IMPORTANT: Firebase config is injected from the server via window.FIREBASE_CONFIG
// This prevents hardcoding credentials in the frontend

const firebaseConfig = window.FIREBASE_CONFIG || {
  apiKey: "AIzaSyAxhL77J1VfZJd3rqRyR-AtlPYSnZoXnn4",
  authDomain: "task-mate-90eee.firebaseapp.com",
  databaseURL: "https://task-mate-90eee-default-rtdb.firebaseio.com",
  projectId: "task-mate-90eee",
  storageBucket: "task-mate-90eee.firebasestorage.app",
  messagingSenderId: "112228413597",
  appId: "1:112228413597:web:9f77d62ecf0478394f6474",
  measurementId: "G-YVTN10T1Q2"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);

// Set persistence to LOCAL so user stays logged in even after browser closes
setPersistence(auth, browserLocalPersistence);

// Initialize Google Auth Provider
const googleProvider = new GoogleAuthProvider();

/**
 * Sign in with Google
 * Returns a Promise that resolves with the authenticated user
 */
export function signInWithGoogle() {
  return signInWithPopup(auth, googleProvider)
    .then((result) => {
      const user = result.user;
      console.log("✅ User signed in:", user.email);
      
      // Send user info to backend
      sendUserToBackend(user);
      return user;
    })
    .catch((error) => {
      console.error("❌ Error during sign in:", error);
      throw error;
    });
}

/**
 * Sign out from Google
 * Clears Firebase auth and backend session
 */
export function signOutGoogle() {
  return signOut(auth)
    .then(() => {
      console.log("✅ User signed out");
      
      // Clear backend session
      return fetch("/auth/logout", { method: "POST" })
        .then(response => response.json())
        .catch(error => console.error("Logout error:", error));
    })
    .catch((error) => {
      console.error("❌ Error during sign out:", error);
      throw error;
    });
}

/**
 * Get current authenticated user
 * Returns a Promise that resolves with the user or null if not authenticated
 */
export function getCurrentUser() {
  return new Promise((resolve) => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      unsubscribe();
      resolve(user);
    });
  });
}

/**
 * Send authenticated user info to backend
 * Backend will verify the token and create/update user session
 * 
 * @param {Object} user - Firebase user object
 */
function sendUserToBackend(user) {
  user.getIdToken().then((token) => {
    fetch("/auth/google-login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
        uid: user.uid,
        idToken: token
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log("✅ Backend authentication successful");
        window.location.href = data.redirectUrl || "/student-dashboard";
      } else {
        console.error("❌ Backend error:", data.message);
        alert(data.message || "Authentication failed");
      }
    })
    .catch(error => {
      console.error("❌ Error sending user to backend:", error);
      alert("Login failed. Please try again.");
    });
  });
}

// Export Firebase instances for use in other modules if needed
export { auth, googleProvider, app };

console.log("✅ Firebase initialized successfully");

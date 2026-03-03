/**
 * Firebase Initialization for Achievement Management System
 *
 * This module initializes Firebase using ES modules.
 * Firebase config is injected securely from backend via window.FIREBASE_CONFIG.
 *
 * Feature Update (#258):
 * Added refreshUserSession() for token management.
 */

import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-analytics.js";
import {
  getAuth,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  setPersistence,
  browserLocalPersistence,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/11.1.0/firebase-auth.js";

// Firebase configuration (Injected from backend if available)
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

// Keep user logged in
setPersistence(auth, browserLocalPersistence);

// Google Auth Provider
const googleProvider = new GoogleAuthProvider();

/**
 * Sign in with Google
 */
export function signInWithGoogle() {
  return signInWithPopup(auth, googleProvider)
    .then((result) => {
      const user = result.user;
      console.log("User signed in:", user.email);

      sendUserToBackend(user);
      return user;
    })
    .catch((error) => {
      console.error("Error during sign in:", error);
      throw error;
    });
}

/**
 * Sign out user
 */
export function signOutGoogle() {
  return signOut(auth)
    .then(() => {
      console.log("User signed out");

      return fetch("/auth/logout", { method: "POST" })
        .then(response => response.json())
        .catch(error => console.error("Logout error:", error));
    })
    .catch((error) => {
      console.error("Error during sign out:", error);
      throw error;
    });
}

/**
 * Get current authenticated user
 */
export function getCurrentUser() {
  return new Promise((resolve) => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      unsubscribe();
      resolve(user);
    });
  });
}

/**
 *  Feature #258
 * Refresh current user's ID token
 * Useful for protected API calls and token expiration handling
 */
export function refreshUserSession() {
  const user = auth.currentUser;

  if (!user) {
    console.warn("No authenticated user found.");
    return Promise.resolve(null);
  }

  return user.getIdToken(true)
    .then((newToken) => {
      console.log("User session refreshed successfully.");
      return newToken;
    })
    .catch((error) => {
      console.error("Error refreshing user session:", error);
      throw error;
    });
}

/**
 * Send authenticated user info to backend
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
        console.log("Backend authentication successful");
        window.location.href = data.redirectUrl || "/student-dashboard";
      } else {
        console.error("Backend error:", data.message);
        alert(data.message || "Authentication failed");
      }
    })
    .catch(error => {
      console.error("Error sending user to backend:", error);
      alert("Login failed. Please try again.");
    });
  });
}

// Export instances
export { auth, googleProvider, app };

console.log("Firebase initialized successfully");
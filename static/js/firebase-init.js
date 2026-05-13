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
// IMPORTANT: Do NOT hardcode credentials here — they must come from the backend
const firebaseConfig = window.FIREBASE_CONFIG || {
  apiKey: "",
  authDomain: "",
  databaseURL: "",
  projectId: "",
  storageBucket: "",
  messagingSenderId: "",
  appId: "",
  measurementId: ""
};

// Guard: If Firebase config is missing or has empty strings, export safe stubs
// This prevents the module from crashing when backend passes DEFAULT_FIREBASE_CONFIG
// (an object with all empty strings) which is truthy and bypasses the || fallback above.
const isFirebaseConfigured = !!(firebaseConfig.apiKey && firebaseConfig.projectId);

let app = null;
let analytics = null;
let auth = null;
let googleProvider = null;

if (!isFirebaseConfigured) {
  console.warn("⚠️ Firebase config not provided by backend. Authentication features will not work.");
} else {
  // Initialize Firebase only when valid config is available
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);

  // Analytics can fail independently — guard it separately
  try {
    if (firebaseConfig.measurementId) {
      analytics = getAnalytics(app);
    }
  } catch (analyticsError) {
    console.warn("⚠️ Firebase Analytics failed to initialize:", analyticsError.message);
  }

  // Keep user logged in
  setPersistence(auth, browserLocalPersistence);

  // Google Auth Provider
  googleProvider = new GoogleAuthProvider();
}

/**
 * Sign in with Google
 */
export function signInWithGoogle() {
  if (!isFirebaseConfigured || !auth) {
    console.error("Firebase is not configured. Cannot sign in.");
    return Promise.reject(new Error("Authentication is not available. Please contact the administrator."));
  }

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
  if (!isFirebaseConfigured || !auth) {
    console.warn("Firebase is not configured. Redirecting to logout.");
    return fetch("/auth/logout", { method: "POST" })
      .then(response => response.json())
      .catch(error => console.error("Logout error:", error));
  }

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
  if (!isFirebaseConfigured || !auth) {
    return Promise.resolve(null);
  }

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
  if (!isFirebaseConfigured || !auth) {
    return Promise.resolve(null);
  }

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

if (isFirebaseConfigured) {
  console.log("Firebase initialized successfully");
} else {
  console.log("Firebase module loaded with stub exports (not configured)");
}
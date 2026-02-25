/**
 * ===============================================
 * 🔥 Firebase Initialization
 * Achievement Management System
 * ===============================================
 * - Uses ES Module imports
 * - Config injected via window.FIREBASE_CONFIG
 * - Google Authentication enabled
 * - Backend session sync enabled
 * ===============================================
 */

/* =======================
   🔹 Firebase Imports
======================= */

import { 
  initializeApp
 } 
from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";

import {
   getAnalytics 
} 
from "https://www.gstatic.com/firebasejs/11.1.0/firebase-analytics.js";

import { 
  getAuth,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  setPersistence,
  browserLocalPersistence
} 
from "https://www.gstatic.com/firebasejs/11.1.0/firebase-auth.js";


/* =======================
   🔹 Firebase Config
======================= */

if (!window.FIREBASE_CONFIG) {
  throw new Error("❌ Firebase config not found. Check server injection.");
}

const firebaseConfig = window.FIREBASE_CONFIG;


/* =======================
   🔹 Initialize Firebase
======================= */

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);


/* =======================
   🔹 Auth Persistence
======================= */

setPersistence(auth, browserLocalPersistence)
  .then(() => {
    console.log("✅ Auth persistence set to LOCAL");
  })
  .catch((error) => {
    console.error("❌ Persistence error:", error);
  });


/* =======================
   🔹 Google Provider
======================= */

const googleProvider = new GoogleAuthProvider();


/* =====================================================
   🔐 Sign In With Google
===================================================== */

export function signInWithGoogle() {
  return signInWithPopup(auth, googleProvider)
    .then((result) => {
      const user = result.user;

      console.log("✅ User signed in:", user.email);

      // Sync with backend
      sendUserToBackend(user);

      return user;
    })
    .catch((error) => {
      console.error("❌ Sign-in error:", error);
      throw error;
    });
}


/* =====================================================
   🔓 Sign Out
===================================================== */

export function signOutGoogle() {
  return signOut(auth)
    .then(() => {
      console.log("✅ User signed out");

      // Clear backend session
      return fetch("/auth/logout", { method: "POST" })
        .then(res => res.json())
        .catch(err => console.error("Logout error:", err));
    })
    .catch((error) => {
      console.error("❌ Sign-out error:", error);
      throw error;
    });
}


/* =====================================================
   👤 Get Current User
===================================================== */

export function getCurrentUser() {
  return new Promise((resolve) => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      unsubscribe();
      resolve(user);
    });
  });
}


/* =====================================================
   🔄 Backend Sync Function
===================================================== */

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
    .then(res => res.json())
    .then((data) => {
      if (data.success) {
        console.log("✅ Backend authentication successful");
        window.location.href = data.redirectUrl || "/student-dashboard";
      } else {
        console.error("❌ Backend error:", data.message);
        alert(data.message || "Authentication failed");
      }
    })
    .catch((error) => {
      console.error("❌ Backend sync error:", error);
      alert("Login failed. Please try again.");
    });

  });
}


/* =======================
   🔹 Exports
======================= */

export { auth, googleProvider, app };

console.log("🚀 Firebase initialized successfully");

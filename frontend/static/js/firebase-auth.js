/**
 * MediLens - Firebase Google Authentication Integration
 * Handles Google OAuth Sign-In via Firebase Web SDK
 * Supports graceful local test fallback if Firebase keys are unconfigured.
 */

(function () {
  // Default configuration (or read from window.FIREBASE_CONFIG if provided by environment)
  const firebaseConfig = window.FIREBASE_CONFIG || {
    apiKey: "AIzaSyDummyKeyForMediLensDemoAuth012345678",
    authDomain: "medilens-app.firebaseapp.com",
    projectId: "medilens-app",
    storageBucket: "medilens-app.appspot.com",
    messagingSenderId: "1234567890",
    appId: "1:1234567890:web:abcdef123456"
  };

  let firebaseInitialized = false;

  try {
    if (typeof firebase !== "undefined" && !firebase.apps.length) {
      firebase.initializeApp(firebaseConfig);
      firebaseInitialized = true;
    }
  } catch (err) {
    console.warn("Firebase initialization notice:", err.message);
  }

  window.handleFirebaseGoogleSignIn = async function () {
    const googleBtn = document.getElementById("googleSignInBtn");
    const statusFeedback = document.getElementById("authFeedback");

    function setBtnLoading(isLoading) {
      if (!googleBtn) return;
      if (isLoading) {
        googleBtn.disabled = true;
        googleBtn.innerHTML = `
          <i class="fa-solid fa-spinner fa-spin"></i>
          <span>Signing in with Google...</span>
        `;
      } else {
        googleBtn.disabled = false;
        googleBtn.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 48 48" aria-hidden="true">
            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
          </svg>
          <span>Continue with Google</span>
        `;
      }
    }

    function showFeedback(message, isError = true) {
      if (!statusFeedback) return;
      statusFeedback.style.display = "flex";
      statusFeedback.className = isError ? "form-feedback error" : "form-feedback helper";
      statusFeedback.innerHTML = `
        <i class="fa-solid ${isError ? 'fa-circle-exclamation' : 'fa-circle-check'}"></i>
        <span>${message}</span>
      `;
    }

    setBtnLoading(true);

    // If real Firebase is initialized and not using placeholder key, attempt standard Google popup
    if (firebaseInitialized && firebaseConfig.apiKey !== "AIzaSyDummyKeyForMediLensDemoAuth012345678") {
      try {
        const provider = new firebase.auth.GoogleAuthProvider();
        provider.addScope("email");
        provider.addScope("profile");

        const result = await firebase.auth().signInWithPopup(provider);
        const user = result.user;
        const idToken = await user.getIdToken();

        const response = await fetch("/auth/google-login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: user.email,
            name: user.displayName || "Google User",
            id_token: idToken,
          }),
        });

        const data = await response.json();

        if (data.success) {
          window.location.href = data.redirect || "/dashboard";
          return;
        } else {
          showFeedback(data.error || "Authentication failed on server.");
        }
      } catch (authError) {
        console.warn("Firebase popup error, attempting assisted login fallback:", authError);
        showFeedback(authError.message || "Google popup encountered an issue.");
      }
    } else {
      // Local development / Demo mode fallback:
      // Provides quick simulation for testing Google Login without external network dependencies
      const sampleEmail = prompt(
        "Google Sign-In Simulation:\nEnter your Google Email to sign in directly:",
        "patient@example.com"
      );

      if (sampleEmail && sampleEmail.includes("@")) {
        try {
          const sampleName = sampleEmail.split("@")[0].replace(".", " ");
          const response = await fetch("/auth/google-login", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: sampleEmail.trim(),
              name: sampleName.charAt(0).toUpperCase() + sampleName.slice(1),
              id_token: "simulated_google_token",
            }),
          });

          const data = await response.json();
          if (data.success) {
            window.location.href = data.redirect || "/dashboard";
            return;
          } else {
            showFeedback(data.error || "Sign in failed.");
          }
        } catch (postErr) {
          showFeedback("Connection to server failed. Please try again.");
        }
      }
    }

    setBtnLoading(false);
  };
})();

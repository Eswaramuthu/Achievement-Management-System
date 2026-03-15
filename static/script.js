/**
 * Theme Management System
 * Handles light/dark mode persistence and application
 */

// Immediate execution to prevent FOUC (Flash of Unstyled Content)
(function () {
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    
    // Default to dark if no preference, or follow system if preferred
    const initialTheme = savedTheme || (prefersDark ? "dark" : "light");
    
    if (initialTheme === "light") {
        document.documentElement.classList.add("light-mode");
        document.body?.classList.add("light-mode");
    } else {
        document.documentElement.classList.remove("light-mode");
        document.body?.classList.remove("light-mode");
    }
})();

document.addEventListener("DOMContentLoaded", () => {
    const toggleButton = document.getElementById("mode-toggle");
    if (!toggleButton) return;

    const updateToggleButton = (isLight) => {
        // Icon represents what you will GET if you click
        toggleButton.innerHTML = isLight ? "🌙" : "☀️";
        toggleButton.setAttribute("aria-label", isLight ? "Switch to Dark Mode" : "Switch to Light Mode");
    };

    // Initial button state
    const isCurrentlyLight = document.documentElement.classList.contains("light-mode");
    updateToggleButton(isCurrentlyLight);

    toggleButton.addEventListener("click", () => {
        const isLight = document.documentElement.classList.toggle("light-mode");
        document.body.classList.toggle("light-mode", isLight);
        
        const newTheme = isLight ? "light" : "dark";
        localStorage.setItem("theme", newTheme);
        updateToggleButton(isLight);
    });

    // Sync theme across multiple tabs
    window.addEventListener("storage", (e) => {
        if (e.key === "theme") {
            const isLight = e.newValue === "light";
            document.documentElement.classList.toggle("light-mode", isLight);
            document.body.classList.toggle("light-mode", isLight);
            updateToggleButton(isLight);
        }
    });

    // Handle Mobile Menu
    const navToggle = document.querySelector(".nav-toggle");
    const navMenu = document.querySelector(".nav-menu");
    
    if (navToggle && navMenu) {
        navToggle.addEventListener("click", () => {
            navMenu.classList.toggle("active");
            navToggle.classList.toggle("active");
        });

        // Close menu on click outside or on link
        document.addEventListener("click", (e) => {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove("active");
                navToggle.classList.remove("active");
            }
        });

        navMenu.querySelectorAll("a").forEach(link => {
            link.addEventListener("click", () => {
                navMenu.classList.remove("active");
                navToggle.classList.remove("active");
            });
        });
    }

    // Scroll to Top
    const scrollTopBtn = document.getElementById("scrollTopBtn");
    if (scrollTopBtn) {
        window.addEventListener("scroll", () => {
            if (window.pageYOffset > 300) {
                scrollTopBtn.classList.add("visible");
            } else {
                scrollTopBtn.classList.remove("visible");
            }
        });

        scrollTopBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }
});

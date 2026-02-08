document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("mode-toggle");

  // Check for saved theme preference
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.classList.add("light-mode");
    toggleButton.textContent = "Light Mode ☀️";
  }

  // Toggle theme when button is clicked
  toggleButton.addEventListener("click", function () {
    document.body.classList.toggle("light-mode");

    if (document.body.classList.contains("light-mode")) {
      toggleButton.textContent = "Light Mode ☀️";
      localStorage.setItem("theme", "light");
    } else {
      toggleButton.textContent = "Dark Mode 🌙";
      localStorage.setItem("theme", "dark");
    }
  });
});

// ✅ UPGRADED password toggle (BACKWARD SAFE)
function togglePassword(id, icon = null) {
  const field = document.getElementById(id);
  if (!field) return;

  if (field.type === "password") {
    field.type = "text";

    // If Material icon is used
    if (icon && icon.classList.contains("material-symbols-outlined")) {
      icon.textContent = "visibility_off";
    }
  } else {
    field.type = "password";

    if (icon && icon.classList.contains("material-symbols-outlined")) {
      icon.textContent = "visibility";
    }
  }
}

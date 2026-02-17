document.addEventListener("DOMContentLoaded", function () {

  const toggleButton = document.getElementById("mode-toggle");

  if (!toggleButton) return;

  // Load saved theme
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme === "dark") {
    document.body.classList.add("dark-mode");
    toggleButton.textContent = "Light Mode ☀️";
  }

  toggleButton.addEventListener("click", function () {

    document.body.classList.toggle("dark-mode");

    if (document.body.classList.contains("dark-mode")) {
      toggleButton.textContent = "Light Mode ☀️";
      localStorage.setItem("theme", "dark");
    } else {
      toggleButton.textContent = "Dark Mode 🌙";
      localStorage.setItem("theme", "light");
    }

  });

});


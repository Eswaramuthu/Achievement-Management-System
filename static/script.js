document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("mode-toggle");
  const toggleIcon = toggleButton.querySelector(".toggle-icon");

  // Check for saved theme preference
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.body.classList.add("light-mode");
    if (toggleIcon) toggleIcon.textContent = "☀️";
  }

  // Toggle theme when button is clicked
  toggleButton.addEventListener("click", function () {
    document.body.classList.toggle("light-mode");

    // Update button icon based on current mode
    if (document.body.classList.contains("light-mode")) {
      if (toggleIcon) toggleIcon.textContent = "☀️";
      localStorage.setItem('theme', 'light');
    } else {
      if (toggleIcon) toggleIcon.textContent = "🌙";
      localStorage.setItem('theme', 'dark');
    }
  });
});
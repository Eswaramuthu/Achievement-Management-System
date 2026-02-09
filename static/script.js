document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("mode-toggle");
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      document.body.classList.add("light-mode");
      toggleButton.textContent = "Light Mode ☀️";
    }
    
    // Toggle theme when button is clicked
    toggleButton.addEventListener("click", function () {
      document.body.classList.toggle("light-mode");
      
      // Update button text based on current mode
      if (document.body.classList.contains("light-mode")) {
        toggleButton.textContent = "Light Mode ☀️";
        localStorage.setItem('theme', 'light');
      } else {
        toggleButton.textContent = "Dark Mode 🌙";
        localStorage.setItem('theme', 'dark');
      }
    });
  });

function togglePassword(inputId, icon) {
  const input = document.getElementById(inputId);
  if (input.type === "password") {
    input.type = "text";
    icon.textContent = "🙈"; 
  } else {
    input.type = "password";
    icon.textContent = "👁️";
  }
}
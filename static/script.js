document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("mode-toggle");
    
    // Check for saved theme preference (default is light mode)
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      document.body.classList.add("dark-mode");
      toggleButton.textContent = "Dark Mode 🌙";
    } else {
      toggleButton.textContent = "Light Mode ☀️";
    }
    
    // Toggle theme when button is clicked
    toggleButton.addEventListener("click", function () {
      document.body.classList.toggle("dark-mode");
      
      // Update button text based on current mode
      if (document.body.classList.contains("dark-mode")) {
        toggleButton.textContent = "Dark Mode 🌙";
        localStorage.setItem('theme', 'dark');
      } else {
        toggleButton.textContent = "Light Mode ☀️";
        localStorage.setItem('theme', 'light');
      }
    });
  });
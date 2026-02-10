document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("mode-toggle");
  if (!toggleButton) return;

  const savedTheme = localStorage.getItem("theme") || "dark";

  if (savedTheme === "light") {
    document.body.classList.add("light-mode");
    toggleButton.textContent = "☀️";
  } else {
    document.body.classList.remove("light-mode");
    toggleButton.textContent = "🌙";
  }

  toggleButton.addEventListener("click", function () {
    const isLight = document.body.classList.toggle("light-mode");

    if (isLight) {
      toggleButton.textContent = "☀️";
      localStorage.setItem("theme", "light");
    } else {
      toggleButton.textContent = "🌙";
      localStorage.setItem("theme", "dark");
    }
  });
});

// Password visibility toggle
function togglePassword(inputId, icon) {
  const input = document.getElementById(inputId);
  if (!input) return;

  if (input.type === "password") {
    input.type = "text";
    icon.textContent = "🙈";
  } else {
    input.type = "password";
    icon.textContent = "👁️";
  }
}


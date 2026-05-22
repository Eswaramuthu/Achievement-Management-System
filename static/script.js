(function () {
  const stored = localStorage.getItem("theme");
  // Default is dark mode, so only add light-mode if stored theme is "light"
  if (stored === "light") {
    document.body.classList.add("light-mode");
  } else {
    document.body.classList.remove("light-mode");
  }
})();

document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("mode-toggle");
  if (!toggleButton) return;

  const getPreferredTheme = () => {
    const stored = localStorage.getItem("theme");
    return stored || "dark";
  };

  const applyTheme = (theme) => {
    const isLight = theme === "light";
    document.body.classList.toggle("light-mode", isLight);
    toggleButton.textContent = isLight ? "🌙" : "☀️"; // 🌙 icon shows when in light mode (click to toggle to dark), ☀️ shows in dark mode
    toggleButton.setAttribute("aria-pressed", isLight);
  };

  toggleButton.setAttribute("aria-label", "Toggle theme");

  applyTheme(getPreferredTheme());

  toggleButton.addEventListener("click", () => {
    const newTheme = document.body.classList.contains("light-mode")
      ? "dark"
      : "light";

    localStorage.setItem("theme", newTheme);
    applyTheme(newTheme);
  });

  window.addEventListener("storage", (e) => {
    if (e.key === "theme" && e.newValue) {
      applyTheme(e.newValue);
    }
  });
});

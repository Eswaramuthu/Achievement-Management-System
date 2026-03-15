(function () {
  const stored = localStorage.getItem("theme");
  const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
  const theme = stored || (prefersLight ? "light" : "dark");

  if (theme === "light") {
    document.body.classList.add("light-mode");
  }
})();

document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("mode-toggle");
  if (!toggleButton) return;

  const getPreferredTheme = () => {
    const stored = localStorage.getItem("theme");
    if (stored) return stored;
    return window.matchMedia("(prefers-color-scheme: light)").matches
      ? "light"
      : "dark";
  };

  const applyTheme = (theme) => {
    const isLight = theme === "light";
    document.body.classList.toggle("light-mode", isLight);
    toggleButton.textContent = isLight ? "☀️" : "🌙";
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

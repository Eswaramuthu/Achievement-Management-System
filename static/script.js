document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("mode-toggle");
  const systemPrefersLight = window.matchMedia("(prefers-color-scheme: light)");

  function setLightMode(isLight, save = true) {
    document.body.classList.toggle("light-mode", isLight);
    toggleButton.textContent = isLight ? "Light Mode ☀️" : "Dark Mode 🌙";
    if (save) {
      localStorage.setItem("theme", isLight ? "light" : "dark");
    }
  }

  // Check saved theme
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme) {
    setLightMode(savedTheme === "light", false);
  } else {
    // No saved theme → follow system preference
    setLightMode(systemPrefersLight.matches, false);
  }

  // Toggle theme on button click (manual override)
  toggleButton.addEventListener("click", function () {
    const isLight = !document.body.classList.contains("light-mode");
    setLightMode(isLight);
  });

  // Optional: live update if system theme changes (only if no manual override)
  systemPrefersLight.addEventListener("change", (e) => {
    if (!localStorage.getItem("theme")) {
      setLightMode(e.matches, false);
    }
  });
});

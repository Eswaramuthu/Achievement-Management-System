document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("mode-toggle");
  if (!toggleButton) return;

  // ------------------ INITIAL THEME ------------------
  const savedTheme = localStorage.getItem("theme") || "dark";

  const applyTheme = (theme) => {
    if (theme === "light") {
      document.body.classList.add("light-mode");
      toggleButton.textContent = "☀️";
    } else {
      document.body.classList.remove("light-mode");
      toggleButton.textContent = "🌙";
    }
  };

  applyTheme(savedTheme);

  // Smooth transition for body background
  document.body.style.transition = "background-color 0.5s ease, color 0.5s ease";

  // ------------------ BUTTON ANIMATION ------------------
  toggleButton.style.transition = "transform 0.3s ease, background 0.3s ease";
  toggleButton.style.fontSize = "1.5rem";

  toggleButton.addEventListener("mouseover", () => {
    toggleButton.style.transform = "scale(1.2)";
  });

  toggleButton.addEventListener("mouseout", () => {
    toggleButton.style.transform = "scale(1)";
  });

  // ------------------ TOGGLE THEME ------------------
  toggleButton.addEventListener("click", () => {
    const isLight = document.body.classList.toggle("light-mode");

    if (isLight) {
      toggleButton.textContent = "☀️";
      localStorage.setItem("theme", "light");
      // Smooth background flash effect
      document.body.animate(
        [{ backgroundColor: "#f0f0f0" }, { backgroundColor: "#f0f0f0" }],
        { duration: 300 }
      );
    } else {
      toggleButton.textContent = "🌙";
      localStorage.setItem("theme", "dark");
      document.body.animate(
        [{ backgroundColor: "#0d0d0d" }, { backgroundColor: "#0d0d0d" }],
        { duration: 300 }
      );
    }

    // Small bounce effect on click
    toggleButton.animate(
      [
        { transform: "scale(1.2)" },
        { transform: "scale(1)" },
      ],
      { duration: 200 }
    );
  });
});

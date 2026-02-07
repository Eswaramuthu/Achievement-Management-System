document.addEventListener("DOMContentLoaded", function () {
  // 🌙 Dark / Light mode toggle
  const toggleButton = document.getElementById("mode-toggle");

  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.classList.add("light-mode");
    toggleButton.textContent = "Light Mode ☀️";
  }

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

  // ❓ FAQ accordion toggle
  const questions = document.querySelectorAll(".faq-question");

  questions.forEach((question) => {
    question.addEventListener("click", () => {
      question.nextElementSibling.classList.toggle("open");
    });
  });
});

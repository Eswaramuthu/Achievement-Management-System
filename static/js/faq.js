// FAQ Accordion JS
document.addEventListener("DOMContentLoaded", () => {
  const faqItems = document.querySelectorAll(".faq-item");

  faqItems.forEach(item => {
    const question = item.querySelector(".faq-question");

    question.addEventListener("click", () => {
      // Toggle current FAQ
      item.classList.toggle("active");

      // Close others
      faqItems.forEach(other => {
        if (other !== item) {
          other.classList.remove("active");
        }
      });
    });
  });
});

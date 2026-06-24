document.addEventListener("DOMContentLoaded", () => {
  const progressBar = document.getElementById("landing-progress");
  const menuToggle = document.getElementById("landing-menu-toggle");
  const menu = document.getElementById("landing-menu");
  const revealItems = document.querySelectorAll("[data-reveal]");
  const countItems = document.querySelectorAll("[data-count]");
  const faqButtons = document.querySelectorAll(".faq-question");
  const activityCards = document.querySelectorAll(".activity-card");

  if (progressBar) {
    const updateProgress = () => {
      const scrollableHeight =
        document.documentElement.scrollHeight - window.innerHeight;
      const progress = scrollableHeight > 0 ? (window.scrollY / scrollableHeight) * 100 : 0;
      progressBar.style.width = `${progress}%`;
    };

    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
  }

  if (menuToggle && menu) {
    menuToggle.addEventListener("click", () => {
      const isOpen = menu.classList.toggle("is-open");
      menuToggle.setAttribute("aria-expanded", String(isOpen));
    });

    menu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menu.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  if (revealItems.length) {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );

    revealItems.forEach((item) => revealObserver.observe(item));
  }

  if (countItems.length) {
    const numberObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            return;
          }

          const node = entry.target;
          const target = Number(node.getAttribute("data-count")) || 0;
          const duration = 1300;
          const startTime = performance.now();

          const step = (time) => {
            const progress = Math.min((time - startTime) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            node.textContent = Math.round(target * eased).toLocaleString();

            if (progress < 1) {
              requestAnimationFrame(step);
            }
          };

          requestAnimationFrame(step);
          numberObserver.unobserve(node);
        });
      },
      { threshold: 0.55 }
    );

    countItems.forEach((item) => numberObserver.observe(item));
  }

  faqButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const currentItem = button.closest(".faq-item");
      const shouldOpen = currentItem && !currentItem.classList.contains("is-open");

      document.querySelectorAll(".faq-item.is-open").forEach((item) => {
        item.classList.remove("is-open");
        const currentButton = item.querySelector(".faq-question");
        if (currentButton) {
          currentButton.setAttribute("aria-expanded", "false");
        }
      });

      if (currentItem && shouldOpen) {
        currentItem.classList.add("is-open");
        button.setAttribute("aria-expanded", "true");
      }
    });
  });

  if (activityCards.length > 1) {
    let activeIndex = 0;

    window.setInterval(() => {
      activityCards[activeIndex].classList.remove("is-active");
      activeIndex = (activeIndex + 1) % activityCards.length;
      activityCards[activeIndex].classList.add("is-active");
    }, 2600);
  }
});

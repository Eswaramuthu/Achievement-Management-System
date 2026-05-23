(function () {
  const allowedExtensions = new Set(["pdf", "png", "jpg", "jpeg"]);

  function isElementVisible(element) {
    return element && element.offsetParent !== null;
  }

  function getTodayString() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function getContainer(field) {
    return field.closest(".input-box") || field.parentElement;
  }

  function getErrorNode(field) {
    if (!field.name) {
      return null;
    }

    return document.getElementById(`${field.name}-error`);
  }

  function setFieldInvalid(field, message) {
    const container = getContainer(field);
    const errorNode = getErrorNode(field);

    field.setAttribute("aria-invalid", "true");
    if (container) {
      container.classList.add("has-error");
    }
    if (errorNode) {
      errorNode.textContent = message;
    }
  }

  function clearFieldInvalid(field) {
    const container = getContainer(field);
    const errorNode = getErrorNode(field);

    field.removeAttribute("aria-invalid");
    if (container) {
      container.classList.remove("has-error");
    }
    if (errorNode) {
      errorNode.textContent = "";
    }
  }

  function isRelevantField(field) {
    if (field.type === "hidden" || field.type === "submit") {
      return false;
    }

    const achievementSpecific = field.closest(".achievement-specific-field");
    if (achievementSpecific && !isElementVisible(achievementSpecific)) {
      return false;
    }

    return true;
  }

  function validateTextField(field, options) {
    const value = field.value.trim();

    if (options.required && !value) {
      return options.requiredMessage;
    }

    if (value && options.minLength && value.length < options.minLength) {
      return options.minLengthMessage;
    }

    if (value && options.maxLength && value.length > options.maxLength) {
      return options.maxLengthMessage;
    }

    return "";
  }

  function validateDateField(field) {
    const value = field.value;
    if (!value) {
      return "Date of achievement is required.";
    }

    if (value > getTodayString()) {
      return "Achievement date cannot be in the future.";
    }

    return "";
  }

  function validateFileField(field, required) {
    const file = field.files && field.files[0];

    if (!file) {
      return required ? "Please upload a certificate file." : "";
    }

    const fileExtension = file.name.split(".").pop().toLowerCase();
    if (!allowedExtensions.has(fileExtension)) {
      return "Only PDF, PNG, JPG, and JPEG files are allowed.";
    }

    return "";
  }

  function validateTeamSize(field) {
    const value = field.value.trim();
    if (!value) {
      return "";
    }

    const parsed = Number(value);
    if (!Number.isInteger(parsed) || parsed <= 0) {
      return "Team size must be a positive whole number.";
    }

    return "";
  }

  function validateField(field, formType) {
    if (!isRelevantField(field)) {
      clearFieldInvalid(field);
      return true;
    }

    let message = "";

    if (field.name === "student_id") {
      message = validateTextField(field, {
        required: true,
        minLength: 2,
        maxLength: 20,
        requiredMessage: "Student ID is required.",
        minLengthMessage: "Student ID must be at least 2 characters long.",
        maxLengthMessage: "Student ID cannot exceed 20 characters.",
      });
    } else if (field.name === "achievement_type") {
      message = validateTextField(field, {
        required: true,
        requiredMessage: "Please select an achievement type.",
      });
    } else if (field.name === "event_name") {
      message = validateTextField(field, {
        required: true,
        minLength: 3,
        maxLength: 100,
        requiredMessage: "Event name is required.",
        minLengthMessage: "Event name must be at least 3 characters long.",
        maxLengthMessage: "Event name cannot exceed 100 characters.",
      });
    } else if (field.name === "achievement_date") {
      message = validateDateField(field);
    } else if (field.name === "organizer") {
      message = validateTextField(field, {
        required: true,
        minLength: 2,
        maxLength: 100,
        requiredMessage: "Organizer or institution is required.",
        minLengthMessage: "Organizer must be at least 2 characters long.",
        maxLengthMessage: "Organizer cannot exceed 100 characters.",
      });
    } else if (field.name === "position") {
      message = validateTextField(field, {
        required: true,
        maxLength: 50,
        requiredMessage: "Position or award is required.",
        maxLengthMessage: "Position cannot exceed 50 characters.",
      });
    } else if (field.name === "achievement_description") {
      message = validateTextField(field, {
        required: false,
        maxLength: 500,
        maxLengthMessage: "Description cannot exceed 500 characters.",
      });
    } else if (field.name === "team_size") {
      message = validateTeamSize(field);
    } else if (field.name === "certificate") {
      message = validateFileField(field, formType === "achievement-submission-simple");
    }

    if (message) {
      setFieldInvalid(field, message);
      return false;
    }

    clearFieldInvalid(field);
    return true;
  }

  function toggleAchievementFields() {
    const achievementTypeField = document.getElementById("achievement_type");
    if (!achievementTypeField) {
      return;
    }

    const selectedType = achievementTypeField.value;
    const specificFields = document.querySelectorAll(".achievement-specific-field");

    specificFields.forEach((field) => {
      field.style.display = "none";
      field.querySelectorAll("input, select, textarea").forEach((control) => {
        clearFieldInvalid(control);
      });
    });

    if (!selectedType) {
      return;
    }

    document.querySelectorAll(`.${selectedType}-field`).forEach((field) => {
      field.style.display = "block";
    });
  }

  function setupAchievementForm(form) {
    const formType = form.dataset.validationForm;
    form.noValidate = true;

    const dateField = form.querySelector('input[name="achievement_date"]');
    if (dateField) {
      dateField.max = getTodayString();
    }

    const fields = Array.from(form.querySelectorAll("input, select, textarea")).filter((field) => {
      return isRelevantField(field);
    });

    fields.forEach((field) => {
      const eventName = field.type === "file" || field.type === "date" || field.tagName === "SELECT" ? "change" : "input";
      field.addEventListener(eventName, () => validateField(field, formType));
      field.addEventListener("blur", () => validateField(field, formType));
    });

    form.addEventListener("submit", (event) => {
      let firstInvalidField = null;
      let formIsValid = true;

      Array.from(form.querySelectorAll("input, select, textarea")).forEach((field) => {
        const fieldIsValid = validateField(field, formType);
        if (!fieldIsValid && !firstInvalidField && isRelevantField(field)) {
          firstInvalidField = field;
          formIsValid = false;
        } else if (!fieldIsValid) {
          formIsValid = false;
        }
      });

      if (!formIsValid) {
        event.preventDefault();
        if (firstInvalidField) {
          firstInvalidField.focus();
          firstInvalidField.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const achievementTypeField = document.getElementById("achievement_type");
    if (achievementTypeField) {
      achievementTypeField.addEventListener("change", toggleAchievementFields);
      toggleAchievementFields();
    }

    document.querySelectorAll('form[data-validation-form^="achievement-submission"]').forEach(setupAchievementForm);
  });

  window.toggleAchievementFields = toggleAchievementFields;
})();
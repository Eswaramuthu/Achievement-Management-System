/**
 * Form Handler Component
 * Handles form submissions, loading states, and notifications
 */

class FormHandler {
  constructor(options = {}) {
    this.formSelector = options.formSelector || 'form';
    this.submitButtonSelector = options.submitButtonSelector || 'button[type="submit"]';
    this.forms = document.querySelectorAll(this.formSelector);
    this.notificationContainer = this.createNotificationContainer();
    
    this.init();
  }

  init() {
    // Add styles if not already added
    this.addStyles();
    
    // Initialize all forms
    this.forms.forEach(form => {
      this.setupForm(form);
    });
  }

  setupForm(form) {
    const submitButton = form.querySelector(this.submitButtonSelector);
    
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      if (!this.validateForm(form)) {
        return;
      }
      
      this.setFormLoading(form, true);
      
      try {
        const formData = new FormData(form);
        const response = await fetch(form.action || window.location.href, {
          method: form.method || 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        
        const result = await response.json().catch(() => ({}));
        
        if (response.ok) {
          this.showNotification('Success!', 'Operation completed successfully.', 'success');
          if (result.redirect) {
            window.location.href = result.redirect;
          } else if (form.dataset.resetOnSuccess === 'true') {
            form.reset();
          }
        } else {
          throw new Error(result.message || 'An error occurred');
        }
      } catch (error) {
        console.error('Form submission error:', error);
        this.showNotification('Error', error.message || 'An error occurred. Please try again.', 'error');
      } finally {
        this.setFormLoading(form, false);
      }
    });
    
    // Add client-side validation
    this.setupValidation(form);
  }

  validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
      if (!field.value.trim()) {
        this.markFieldAsInvalid(field, 'This field is required');
        isValid = false;
      } else if (field.type === 'email' && !this.isValidEmail(field.value)) {
        this.markFieldAsInvalid(field, 'Please enter a valid email address');
        isValid = false;
      } else if (field.type === 'password' && field.dataset.minLength) {
        const minLength = parseInt(field.dataset.minLength, 10);
        if (field.value.length < minLength) {
          this.markFieldAsInvalid(field, `Password must be at least ${minLength} characters`);
          isValid = false;
        }
      }
    });
    
    // Check password confirmation if exists
    const password = form.querySelector('input[type="password"]');
    const confirmPassword = form.querySelector('input[type="password"][data-confirm]');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      this.markFieldAsInvalid(confirmPassword, 'Passwords do not match');
      isValid = false;
    }
    
    return isValid;
  }

  setupValidation(form) {
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
      // Clear validation on input
      input.addEventListener('input', () => {
        this.clearFieldValidation(input);
      });
      
      // Add validation on blur
      input.addEventListener('blur', () => {
        if (input.required && !input.value.trim()) {
          this.markFieldAsInvalid(input, 'This field is required');
        } else if (input.type === 'email' && input.value && !this.isValidEmail(input.value)) {
          this.markFieldAsInvalid(input, 'Please enter a valid email address');
        }
      });
    });
  }

  markFieldAsInvalid(field, message) {
    const formGroup = field.closest('.form-group') || field.parentElement;
    
    // Remove any existing error messages
    this.clearFieldValidation(field);
    
    // Add error class
    field.classList.add('is-invalid');
    
    // Add error message
    const errorEl = document.createElement('div');
    errorEl.className = 'invalid-feedback';
    errorEl.textContent = message;
    formGroup.appendChild(errorEl);
  }

  clearFieldValidation(field) {
    const formGroup = field.closest('.form-group') || field.parentElement;
    
    field.classList.remove('is-invalid');
    
    const existingError = formGroup.querySelector('.invalid-feedback');
    if (existingError) {
      formGroup.removeChild(existingError);
    }
  }

  setFormLoading(form, isLoading) {
    const submitButton = form.querySelector(this.submitButtonSelector);
    
    if (isLoading) {
      submitButton.disabled = true;
      submitButton.classList.add('btn-loading');
      submitButton.innerHTML = `
        <span class="spinner"></span>
        ${submitButton.textContent}
      `;
      form.classList.add('form-loading');
    } else {
      submitButton.disabled = false;
      submitButton.classList.remove('btn-loading');
      const originalText = submitButton.dataset.originalText || submitButton.textContent.trim();
      submitButton.textContent = originalText;
      form.classList.remove('form-loading');
    }
  }

  createNotificationContainer() {
    let container = document.getElementById('notification-container');
    
    if (!container) {
      container = document.createElement('div');
      container.id = 'notification-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    
    return container;
  }

  showNotification(title, message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    toast.innerHTML = `
      <div class="toast-content">
        <h4 class="toast-title">${title}</h4>
        <p class="toast-message">${message}</p>
      </div>
      <button class="toast-close" aria-label="Close">&times;</button>
    `;
    
    const closeButton = toast.querySelector('.toast-close');
    closeButton.addEventListener('click', () => {
      this.removeNotification(toast);
    });
    
    this.notificationContainer.appendChild(toast);
    
    // Auto-remove notification after duration
    if (duration > 0) {
      setTimeout(() => {
        this.removeNotification(toast);
      }, duration);
    }
    
    return toast;
  }

  removeNotification(toast) {
    if (toast && toast.parentNode === this.notificationContainer) {
      toast.style.animation = 'slideIn 0.3s ease-out reverse';
      
      toast.addEventListener('animationend', () => {
        if (toast.parentNode === this.notificationContainer) {
          this.notificationContainer.removeChild(toast);
        }
      }, { once: true });
    }
  }

  isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  }

  addStyles() {
    // Check if styles are already added
    if (document.getElementById('form-handler-styles')) {
      return;
    }
    
    const style = document.createElement('style');
    style.id = 'form-handler-styles';
    style.textContent = `
      /* Form validation styles */
      .is-invalid {
        border-color: #dc3545 !important;
      }
      
      .invalid-feedback {
        width: 100%;
        margin-top: 0.25rem;
        font-size: 0.875em;
        color: #dc3545;
      }
      
      /* Loading spinner */
      .spinner {
        display: inline-block;
        width: 1rem;
        height: 1rem;
        border: 0.2rem solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
        margin-right: 0.5rem;
        vertical-align: middle;
      }
      
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
      
      /* Button loading state */
      .btn-loading {
        position: relative;
        pointer-events: none;
        opacity: 0.8;
      }
      
      /* Form loading overlay */
      .form-loading {
        position: relative;
      }
      
      .form-loading::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        border-radius: 0.25rem;
      }
    `;
    
    document.head.appendChild(style);
  }
}

// Initialize form handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.formHandler = new FormHandler({
    formSelector: 'form[data-validate="true"]',
    submitButtonSelector: 'button[type="submit"]'
  });
});

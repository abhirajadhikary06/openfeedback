/**
 * Authentication Pages JavaScript
 * Handles password visibility toggle, form validation, and loading states
 */

// ========================================
// Password Visibility Toggle
// ========================================

function togglePasswordVisibility(inputId) {
  const input = document.getElementById(inputId);
  const button = input.parentElement.querySelector('.password-toggle-btn');
  const icon = button.querySelector('i');
  
  if (input.type === 'password') {
    input.type = 'text';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
  } else {
    input.type = 'password';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
  }
}

// Make password toggle keyboard accessible
document.addEventListener('DOMContentLoaded', function() {
  const toggleButtons = document.querySelectorAll('.password-toggle-btn');
  
  toggleButtons.forEach(button => {
    button.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const input = this.parentElement.querySelector('input');
        togglePasswordVisibility(input.id);
      }
    });
  });
});

// ========================================
// Loading State Management
// ========================================

function showLoadingState(buttonElement) {
  if (!buttonElement) return;
  
  // Store original text
  buttonElement.dataset.originalText = buttonElement.textContent;
  
  // Add loading class and disable button
  buttonElement.classList.add('loading');
  buttonElement.disabled = true;
  
  // Change button content to spinner and text
  buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
}

function hideLoadingState(buttonElement) {
  if (!buttonElement) return;
  
  // Remove loading class and enable button
  buttonElement.classList.remove('loading');
  buttonElement.disabled = false;
  
  // Restore original text
  const originalText = buttonElement.dataset.originalText || 'Submit';
  buttonElement.textContent = originalText;
}

// ========================================
// Form Validation Functions
// ========================================

function validateEmail(email) {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!email || email.trim() === '') {
    return { valid: false, message: 'Email is required' };
  }
  
  if (!emailPattern.test(email)) {
    return { valid: false, message: 'Please enter a valid email address' };
  }
  
  return { valid: true, message: '' };
}

function validateUsername(username) {
  if (!username || username.trim() === '') {
    return { valid: false, message: 'Username is required' };
  }
  
  if (username.length < 3) {
    return { valid: false, message: 'Username must be at least 3 characters' };
  }
  
  return { valid: true, message: '' };
}

function validatePassword(password) {
  if (!password || password.trim() === '') {
    return { valid: false, message: 'Password is required' };
  }
  
  if (password.length < 8) {
    return { valid: false, message: 'Password must be at least 8 characters' };
  }
  
  if (!/[A-Z]/.test(password)) {
    return { valid: false, message: 'Password must contain an uppercase letter' };
  }
  
  if (!/[a-z]/.test(password)) {
    return { valid: false, message: 'Password must contain a lowercase letter' };
  }
  
  if (!/[0-9]/.test(password)) {
    return { valid: false, message: 'Password must contain a number' };
  }
  
  return { valid: true, message: '' };
}

function validatePasswordMatch(password, confirmPassword) {
  if (!confirmPassword || confirmPassword.trim() === '') {
    return { valid: false, message: 'Please confirm your password' };
  }
  
  if (password !== confirmPassword) {
    return { valid: false, message: 'Passwords do not match' };
  }
  
  return { valid: true, message: '' };
}

// ========================================
// Validation UI Functions
// ========================================

function showValidationError(inputId, message) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  const inputGroup = input.closest('.input-group');
  const formGroup = input.closest('.form-group');
  
  // Add error class to input group
  if (inputGroup) {
    inputGroup.classList.add('has-error');
  }
  
  // Remove existing error message if any
  clearValidationError(inputId);
  
  // Create and insert error message
  const errorDiv = document.createElement('div');
  errorDiv.className = 'validation-error';
  errorDiv.id = `${inputId}-error`;
  errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
  
  if (formGroup) {
    formGroup.appendChild(errorDiv);
  }
}

function clearValidationError(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  const inputGroup = input.closest('.input-group');
  const formGroup = input.closest('.form-group');
  
  // Remove error class
  if (inputGroup) {
    inputGroup.classList.remove('has-error');
  }
  
  // Remove error message
  const existingError = document.getElementById(`${inputId}-error`);
  if (existingError) {
    existingError.remove();
  }
}

// ========================================
// Form Submission Handlers
// ========================================

document.addEventListener('DOMContentLoaded', function() {
  // Login form handler
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
      const submitButton = this.querySelector('button[type="submit"]');
      showLoadingState(submitButton);
      
      // Note: Form will submit normally, loading state will be cleared on page reload
      // If using AJAX, you would prevent default and handle response
    });
  }
  
  // Register form handler
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
      const submitButton = this.querySelector('button[type="submit"]');
      
      // Validate all fields before submission
      let isValid = true;
      
      const username = document.getElementById('username').value;
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirm_password').value;
      
      // Validate username
      const usernameValidation = validateUsername(username);
      if (!usernameValidation.valid) {
        showValidationError('username', usernameValidation.message);
        isValid = false;
      }
      
      // Validate email
      const emailValidation = validateEmail(email);
      if (!emailValidation.valid) {
        showValidationError('email', emailValidation.message);
        isValid = false;
      }
      
      // Validate password
      const passwordValidation = validatePassword(password);
      if (!passwordValidation.valid) {
        showValidationError('password', passwordValidation.message);
        isValid = false;
      }
      
      // Validate password match
      const passwordMatchValidation = validatePasswordMatch(password, confirmPassword);
      if (!passwordMatchValidation.valid) {
        showValidationError('confirm_password', passwordMatchValidation.message);
        isValid = false;
      }
      
      if (!isValid) {
        e.preventDefault();
        return false;
      }
      
      showLoadingState(submitButton);
    });
    
    // Real-time validation on blur
    const usernameInput = document.getElementById('username');
    if (usernameInput) {
      usernameInput.addEventListener('blur', function() {
        const validation = validateUsername(this.value);
        if (!validation.valid) {
          showValidationError('username', validation.message);
        } else {
          clearValidationError('username');
        }
      });
      
      usernameInput.addEventListener('input', function() {
        if (this.value.length >= 3) {
          clearValidationError('username');
        }
      });
    }
    
    const emailInput = document.getElementById('email');
    if (emailInput) {
      emailInput.addEventListener('blur', function() {
        const validation = validateEmail(this.value);
        if (!validation.valid) {
          showValidationError('email', validation.message);
        } else {
          clearValidationError('email');
        }
      });
      
      emailInput.addEventListener('input', function() {
        const validation = validateEmail(this.value);
        if (validation.valid) {
          clearValidationError('email');
        }
      });
    }
    
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
      passwordInput.addEventListener('blur', function() {
        const validation = validatePassword(this.value);
        if (!validation.valid) {
          showValidationError('password', validation.message);
        } else {
          clearValidationError('password');
        }
      });
      
      passwordInput.addEventListener('input', function() {
        const validation = validatePassword(this.value);
        if (validation.valid) {
          clearValidationError('password');
        }
      });
    }
    
    const confirmPasswordInput = document.getElementById('confirm_password');
    if (confirmPasswordInput) {
      confirmPasswordInput.addEventListener('blur', function() {
        const password = document.getElementById('password').value;
        const validation = validatePasswordMatch(password, this.value);
        if (!validation.valid) {
          showValidationError('confirm_password', validation.message);
        } else {
          clearValidationError('confirm_password');
        }
      });
      
      confirmPasswordInput.addEventListener('input', function() {
        const password = document.getElementById('password').value;
        const validation = validatePasswordMatch(password, this.value);
        if (validation.valid) {
          clearValidationError('confirm_password');
        }
      });
    }
  }
});

// ========================================
// Keyboard Navigation
// ========================================

document.addEventListener('DOMContentLoaded', function() {
  // Enable Enter key to submit forms
  const inputs = document.querySelectorAll('.auth-input, input[type="text"], input[type="email"], input[type="password"]');
  
  inputs.forEach(input => {
    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        const form = this.closest('form');
        if (form) {
          form.requestSubmit();
        }
      }
    });
  });
});

// ========================================
// Flash Message Dismiss
// ========================================

document.addEventListener('DOMContentLoaded', function() {
  const closeButtons = document.querySelectorAll('.flash-close');
  
  closeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const flashMessage = this.closest('.flash-message');
      if (flashMessage) {
        flashMessage.style.opacity = '0';
        setTimeout(() => {
          flashMessage.remove();
        }, 300);
      }
    });
  });
});

// static/js/login.js
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const passwordInput = document.getElementById('password');
    const togglePassword = document.querySelector('.toggle-password');
    const loginButton = document.querySelector('.login-button');
    const buttonText = document.querySelector('.button-text');
    const buttonLoader = document.querySelector('.button-loader');

    // Toggle password visibility
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Toggle icon
            const icon = this.querySelector('i');
            icon.classList.toggle('icon-eye');
            icon.classList.toggle('icon-eye-off');
        });
    }

    // Form submission
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            // Show loading state
            loginButton.disabled = true;
            buttonText.style.opacity = '0';
            buttonLoader.style.display = 'block';

            // Store form data
            const formData = new FormData(this);
            
            // Remember me functionality
            const rememberMe = document.getElementById('remember');
            if (rememberMe && rememberMe.checked) {
                localStorage.setItem('username', formData.get('username'));
            } else {
                localStorage.removeItem('username');
            }
        });
    }

    // Restore remembered username
    const savedUsername = localStorage.getItem('username');
    if (savedUsername) {
        const usernameInput = document.getElementById('username');
        const rememberCheckbox = document.getElementById('remember');
        if (usernameInput) usernameInput.value = savedUsername;
        if (rememberCheckbox) rememberCheckbox.checked = true;
    }

    // Add form validation
    const inputs = loginForm.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('invalid', function(e) {
            e.preventDefault();
            this.classList.add('input-error');
        });

        input.addEventListener('input', function() {
            this.classList.remove('input-error');
        });
    });

    // Add subtle animation on input focus
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const input = group.querySelector('input');
        if (input) {
            input.addEventListener('focus', () => {
                group.classList.add('input-focused');
            });
            input.addEventListener('blur', () => {
                if (!input.value) {
                    group.classList.remove('input-focused');
                }
            });
        }
    });

    // Add error handling for failed login attempts
    const alertError = document.querySelector('.alert-error');
    if (alertError) {
        setTimeout(() => {
            alertError.style.opacity = '0';
            setTimeout(() => {
                alertError.remove();
            }, 300);
        }, 5000);
    }

    // Add keyboard navigation support
    loginForm.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const focusedElement = document.activeElement;
            const inputs = Array.from(this.querySelectorAll('input:not([type="hidden"])'));
            const currentIndex = inputs.indexOf(focusedElement);
            
            if (currentIndex < inputs.length - 1) {
                e.preventDefault();
                inputs[currentIndex + 1].focus();
            }
        }
    });

    // Add touch device detection
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
    }

    // Add input validation feedback
    const usernameInput = document.getElementById('username');
    if (usernameInput) {
        usernameInput.addEventListener('input', function() {
            this.value = this.value.trim();
            if (this.value.length < 3) {
                this.setCustomValidity('El usuario debe tener al menos 3 caracteres');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Add password strength indicator
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            if (this.value.length < 8) {
                this.setCustomValidity('La contraseña debe tener al menos 8 caracteres');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Handle form submission errors gracefully
    window.addEventListener('unhandledrejection', function(event) {
        loginButton.disabled = false;
        buttonText.style.opacity = '1';
        buttonLoader.style.display = 'none';
        
        // Show error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.textContent = 'Error de conexión. Por favor, intente nuevamente.';
        loginForm.insertBefore(errorDiv, loginForm.firstChild);
    });
});
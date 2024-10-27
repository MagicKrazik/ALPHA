// static/js/register.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const passwordInput = document.getElementById('id_password1');
    const confirmPasswordInput = document.getElementById('id_password2');
    const usuarioInput = document.getElementById('id_usuario');
    const submitButton = document.querySelector('.form-submit');
    
    // Password strength indicator
    function checkPasswordStrength(password) {
        let strength = 0;
        
        // Length check
        if (password.length >= 8) strength += 1;
        
        // Contains numbers
        if (/\d/.test(password)) strength += 1;
        
        // Contains lowercase
        if (/[a-z]/.test(password)) strength += 1;
        
        // Contains uppercase
        if (/[A-Z]/.test(password)) strength += 1;
        
        // Contains special characters
        if (/[^A-Za-z0-9]/.test(password)) strength += 1;
        
        return strength;
    }
    
    function updatePasswordStrength() {
        const password = passwordInput.value;
        const strength = checkPasswordStrength(password);
        const strengthIndicator = document.getElementById('passwordStrength');
        
        if (!strengthIndicator) return;
        
        if (strength < 2) {
            strengthIndicator.textContent = 'Débil';
            strengthIndicator.className = 'password-strength strength-weak';
        } else if (strength < 4) {
            strengthIndicator.textContent = 'Media';
            strengthIndicator.className = 'password-strength strength-medium';
        } else {
            strengthIndicator.textContent = 'Fuerte';
            strengthIndicator.className = 'password-strength strength-strong';
        }
    }
    
    // Real-time username validation
    function validateUsername() {
        const username = usuarioInput.value;
        const regex = /^[a-zA-Z0-9._]+$/;
        
        if (!regex.test(username)) {
            usuarioInput.setCustomValidity('El usuario solo puede contener letras, números, puntos y guiones bajos');
        } else {
            usuarioInput.setCustomValidity('');
        }
    }
    
    // Password match validation
    function validatePasswordMatch() {
        if (passwordInput.value !== confirmPasswordInput.value) {
            confirmPasswordInput.setCustomValidity('Las contraseñas no coinciden');
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    }
    
    // Form validation
    function validateForm() {
        const isValid = form.checkValidity();
        submitButton.disabled = !isValid;
        return isValid;
    }
    
    // Event listeners
    if (passwordInput) {
        passwordInput.addEventListener('input', () => {
            updatePasswordStrength();
            validatePasswordMatch();
            validateForm();
        });
    }
    
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', () => {
            validatePasswordMatch();
            validateForm();
        });
    }
    
    if (usuarioInput) {
        usuarioInput.addEventListener('input', () => {
            validateUsername();
            validateForm();
        });
    }
    
    // Toggle password visibility
    const togglePassword = document.querySelectorAll('.toggle-password');
    togglePassword.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            // Update icon
            const icon = this.querySelector('i');
            if (type === 'password') {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            // Show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registrando...';
            
            // Submit the form
            this.submit();
        }
    });
    
    // Initialize form validation
    validateForm();
});
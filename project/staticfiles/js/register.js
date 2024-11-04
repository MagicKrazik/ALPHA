document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const passwordInput = document.getElementById('id_password1');
    const confirmPasswordInput = document.getElementById('id_password2');
    const usuarioInput = document.getElementById('id_usuario');
    const submitButton = document.querySelector('.register-btn');

    if (!form || !submitButton) {
        console.error('Required elements not found');
        return;
    }

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
        if (!passwordInput) return;
        
        const password = passwordInput.value;
        const strength = checkPasswordStrength(password);
        const strengthIndicator = document.getElementById('passwordStrength');
        
        if (!strengthIndicator) return;
        
        const strengthBar = document.createElement('div');
        strengthBar.className = 'password-strength-bar';
        strengthIndicator.innerHTML = '';
        strengthIndicator.appendChild(strengthBar);
        
        if (strength < 2) {
            strengthBar.className = 'password-strength-bar strength-weak';
        } else if (strength < 4) {
            strengthBar.className = 'password-strength-bar strength-medium';
        } else {
            strengthBar.className = 'password-strength-bar strength-strong';
        }
    }
    
    // Username validation
    function validateUsername() {
        if (!usuarioInput) return;
        
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
        if (!passwordInput || !confirmPasswordInput) return;
        
        if (passwordInput.value !== confirmPasswordInput.value) {
            confirmPasswordInput.setCustomValidity('Las contraseñas no coinciden');
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    }
    
    // Add event listeners
    if (passwordInput) {
        passwordInput.addEventListener('input', () => {
            updatePasswordStrength();
            validatePasswordMatch();
        });
    }
    
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    }
    
    if (usuarioInput) {
        usuarioInput.addEventListener('input', validateUsername);
    }
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (this.checkValidity()) {
            submitButton.disabled = true;
            submitButton.innerHTML = 'Registrando...';
            this.submit();
        }
    });
});
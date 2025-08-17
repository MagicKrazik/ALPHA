// static/js/patient_form.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.patient-form');
    if (!form) return;

    // Form validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
                showFieldError(field, 'Este campo es requerido');
            } else {
                field.classList.remove('is-invalid');
                clearFieldError(field);
            }
        });

        if (!isValid) {
            e.preventDefault();
            showAlert('Por favor complete todos los campos requeridos', 'error');
        }
    });

    // Real-time validation
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });

    function validateField(field) {
        const value = field.value.trim();
        
        if (field.hasAttribute('required') && !value) {
            field.classList.add('is-invalid');
            showFieldError(field, 'Este campo es requerido');
            return false;
        }

        // Validate folio format
        if (field.name === 'folio_hospitalizacion') {
            if (value && !/^[A-Z0-9\-]+$/.test(value)) {
                field.classList.add('is-invalid');
                showFieldError(field, 'Formato de folio inválido');
                return false;
            }
        }

        field.classList.remove('is-invalid');
        clearFieldError(field);
        return true;
    }

    function showFieldError(field, message) {
        clearFieldError(field);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    function clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type}`;
        alertDiv.textContent = message;
        
        const container = document.querySelector('.form-container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
});
// Add this to your static/js/forms.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.surgery-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                messages.error('Por favor complete todos los campos requeridos.');
            }
        });
    }
});
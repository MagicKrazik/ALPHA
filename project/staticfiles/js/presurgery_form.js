// PreSurgery Form Scripts
document.addEventListener('DOMContentLoaded', function() {
    // Get the form element
    const form = document.getElementById('presurgeryForm');
    if (!form) {
        console.error('Form not found');
        return;
    }

    const formSections = document.querySelectorAll('.form-section');
    
    // BMI Calculator
    const weightInput = document.querySelector('[name="peso"]');
    const heightInput = document.querySelector('[name="talla"]');
    const bmiInput = document.querySelector('[name="imc"]');

    function calculateBMI() {
        if (weightInput && heightInput && bmiInput) {
            const weight = parseFloat(weightInput.value);
            const height = parseFloat(heightInput.value) / 100;
            
            if (!isNaN(weight) && !isNaN(height) && height > 0) {
                const bmi = (weight / (height * height)).toFixed(2);
                bmiInput.value = bmi;
            }
        }
    }

    // Attach BMI calculation events
    if (weightInput && heightInput) {
        weightInput.addEventListener('input', calculateBMI);
        heightInput.addEventListener('input', calculateBMI);
        calculateBMI(); // Initial calculation
    }

    // Form submission handling
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Recalculate BMI before submission
        calculateBMI();

        // Submit the form
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span>Guardando...';
        
        // Submit the form
        this.submit();
    });

    // Initialize mobile view
    function setupMobileView() {
        if (window.innerWidth < 768) {
            formSections.forEach((section, index) => {
                if (index > 0) {
                    section.classList.add('collapsed');
                }
            });
        }
    }

    // Initialize mobile view
    setupMobileView();

    // Handle window resize
    window.addEventListener('resize', () => {
        setupMobileView();
    });
});
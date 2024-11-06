// PostSurgery Form Scripts
document.addEventListener('DOMContentLoaded', function() {
    // Get the form element
    const form = document.getElementById('postsurgeryForm');
    if (!form) {
        console.error('Form not found');
        return;
    }

    const formSections = document.querySelectorAll('.form-section');

    // Form submission handling
    form.addEventListener('submit', function(e) {
        e.preventDefault();

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

    // Add collapsible functionality for mobile
    formSections.forEach(section => {
        const header = section.querySelector('h3');
        if (header) {
            header.addEventListener('click', () => {
                if (window.innerWidth < 768) {
                    section.classList.toggle('collapsed');
                }
            });
        }
    });
});
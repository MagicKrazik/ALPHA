document.addEventListener('DOMContentLoaded', function() {
    // Add confirmation dialog
    const deleteForm = document.querySelector('form');
    const patientName = document.querySelector('.patient-name').textContent;

    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show confirmation dialog
            const confirmed = confirm(`¿Está seguro que desea eliminar al paciente "${patientName}"? Esta acción no se puede deshacer.`);
            
            if (confirmed) {
                deleteForm.submit();
            }
        });
    }

    // Add animation on page load
    const deleteContainer = document.querySelector('.delete-container');
    if (deleteContainer) {
        deleteContainer.classList.add('aos-animate');
    }

    // Add button hover effects
    const buttons = document.querySelectorAll('.form-actions button, .form-actions a');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add keyboard navigation support
    const actionButtons = Array.from(document.querySelectorAll('.form-actions button, .form-actions a'));
    let currentFocusIndex = 0;

    actionButtons.forEach((button, index) => {
        button.addEventListener('keydown', function(e) {
            switch(e.key) {
                case 'ArrowRight':
                case 'ArrowDown':
                    e.preventDefault();
                    currentFocusIndex = (currentFocusIndex + 1) % actionButtons.length;
                    actionButtons[currentFocusIndex].focus();
                    break;
                case 'ArrowLeft':
                case 'ArrowUp':
                    e.preventDefault();
                    currentFocusIndex = (currentFocusIndex - 1 + actionButtons.length) % actionButtons.length;
                    actionButtons[currentFocusIndex].focus();
                    break;
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    this.click();
                    break;
            }
        });
    });

    // Add touch event support for mobile devices
    let touchStartY = 0;
    const deleteContent = document.querySelector('.delete-content');

    if (deleteContent) {
        deleteContent.addEventListener('touchstart', function(e) {
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        deleteContent.addEventListener('touchmove', function(e) {
            const touchY = e.touches[0].clientY;
            const deltaY = touchY - touchStartY;

            // Prevent scroll if trying to scroll down when already at top
            if (deltaY > 0 && deleteContent.scrollTop === 0) {
                e.preventDefault();
            }
        }, { passive: false });
    }
});
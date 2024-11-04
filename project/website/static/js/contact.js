// static/js/contact.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.contact-form');
    const submitButton = document.querySelector('.submit-button');
    const buttonText = document.querySelector('.button-text');
    const buttonLoader = document.querySelector('.button-loader');

    if (form) {
        form.addEventListener('submit', function(e) {
            // Show loading state
            submitButton.disabled = true;
            buttonText.style.opacity = '0';
            buttonLoader.style.display = 'block';
        });
    }

    // Add smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
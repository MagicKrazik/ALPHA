document.addEventListener('DOMContentLoaded', function() {
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    // Ensure the toggle button has the correct initial HTML structure
    navbarToggle.innerHTML = `
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
    `;

    // Toggle mobile menu
    navbarToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        navbarMenu.classList.toggle('active');
    });

    // Handle dropdown menus
    dropdownToggles.forEach(toggle => {
        // Wrap the dropdown toggle and menu in a container if not already wrapped
        if (!toggle.parentElement.classList.contains('dropdown-container')) {
            const dropdownContainer = document.createElement('div');
            dropdownContainer.className = 'dropdown-container';
            toggle.parentNode.insertBefore(dropdownContainer, toggle);
            dropdownContainer.appendChild(toggle);
            
            // Move the dropdown menu into the container
            const dropdownMenu = toggle.nextElementSibling;
            if (dropdownMenu) {
                dropdownMenu.classList.add('dropdown-menu');
                dropdownContainer.appendChild(dropdownMenu);
            }
        }

        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Close all other dropdowns first
            dropdownToggles.forEach(otherToggle => {
                if (otherToggle !== toggle) {
                    otherToggle.classList.remove('active');
                }
            });

            // Toggle current dropdown
            this.classList.toggle('active');
        });

        // Add animation delay to dropdown items
        const dropdownItems = toggle.nextElementSibling?.querySelectorAll('a');
        dropdownItems?.forEach((item, index) => {
            item.style.setProperty('--item-index', index);
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        const isDropdownClick = event.target.closest('.dropdown-container');
        
        if (!isDropdownClick) {
            dropdownToggles.forEach(toggle => {
                toggle.classList.remove('active');
            });
        }

        // Also close mobile menu when clicking outside
        if (!navbarMenu.contains(event.target) && !navbarToggle.contains(event.target)) {
            navbarMenu.classList.remove('active');
            navbarToggle.classList.remove('active');
        }
    });

    // Handle keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close all dropdowns
            dropdownToggles.forEach(toggle => {
                toggle.classList.remove('active');
            });
            // Close mobile menu
            navbarMenu.classList.remove('active');
            navbarToggle.classList.remove('active');
        }
    });

    // Close menu when clicking on a nav link (except dropdown toggles)
    const navLinks = document.querySelectorAll('.navbar-menu a:not(.dropdown-toggle)');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navbarMenu.classList.remove('active');
            navbarToggle.classList.remove('active');
            // Also close any open dropdowns
            dropdownToggles.forEach(toggle => {
                toggle.classList.remove('active');
            });
        });
    });

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Close mobile menu and dropdowns on window resize
            if (window.innerWidth > 960) {
                navbarMenu.classList.remove('active');
                navbarToggle.classList.remove('active');
                dropdownToggles.forEach(toggle => {
                    toggle.classList.remove('active');
                });
            }
        }, 250);
    });
});
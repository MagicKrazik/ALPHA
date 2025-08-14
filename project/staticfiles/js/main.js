// Main JavaScript for ALPHA Project 2025
(function() {
    'use strict';

    // DOM Ready
    document.addEventListener('DOMContentLoaded', function() {
        initNavigation();
        initAlerts();
        initBackToTop();
        initDropdowns();
        initAccessibility();
        initPerformanceOptimizations();
    });

    // Navigation functionality
    function initNavigation() {
        const navbar = document.querySelector('.navbar');
        const navbarToggle = document.querySelector('.navbar-toggle');
        const navbarMenu = document.querySelector('.navbar-menu');
        
        if (!navbar || !navbarToggle || !navbarMenu) return;

        // Mobile menu toggle
        navbarToggle.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            this.setAttribute('aria-expanded', !isExpanded);
            this.classList.toggle('active');
            navbarMenu.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            document.body.style.overflow = navbarMenu.classList.contains('active') ? 'hidden' : '';
        });

        // Close mobile menu when clicking on links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    navbarToggle.classList.remove('active');
                    navbarMenu.classList.remove('active');
                    navbarToggle.setAttribute('aria-expanded', 'false');
                    document.body.style.overflow = '';
                }
            });
        });

        // Close mobile menu on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navbarToggle.classList.remove('active');
                navbarMenu.classList.remove('active');
                navbarToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            }
        });

        // Close mobile menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navbarMenu.classList.contains('active')) {
                navbarToggle.classList.remove('active');
                navbarMenu.classList.remove('active');
                navbarToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            }
        });

        // Navbar scroll behavior
        let lastScrollY = 0;
        let ticking = false;

        function updateNavbar() {
            const scrollY = window.pageYOffset;
            
            // Add background blur when scrolled
            if (scrollY > 50) {
                navbar.style.background = 'rgba(43, 69, 112, 0.95)';
                navbar.style.backdropFilter = 'blur(20px)';
            } else {
                navbar.style.background = 'var(--primary-color)';
                navbar.style.backdropFilter = 'none';
            }

            // Hide/show navbar on scroll (desktop only)
            if (window.innerWidth > 768) {
                if (scrollY > lastScrollY && scrollY > 200) {
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    navbar.style.transform = 'translateY(0)';
                }
            }

            lastScrollY = scrollY;
            ticking = false;
        }

        function requestTick() {
            if (!ticking) {
                requestAnimationFrame(updateNavbar);
                ticking = true;
            }
        }

        window.addEventListener('scroll', requestTick, { passive: true });
    }

    // Alert system
    function initAlerts() {
        const alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) return;

        // Auto-dismiss alerts after 5 seconds
        const alerts = alertContainer.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const closeBtn = alert.querySelector('.alert-close');
            
            // Close button functionality
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    dismissAlert(alert);
                });
            }

            // Auto-dismiss
            setTimeout(() => {
                if (alert.parentNode) {
                    dismissAlert(alert);
                }
            }, 5000);
        });

        function dismissAlert(alert) {
            alert.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 300);
        }

        // Add slideOutRight animation
        if (!document.querySelector('#alert-animations')) {
            const style = document.createElement('style');
            style.id = 'alert-animations';
            style.textContent = `
                @keyframes slideOutRight {
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Back to top button
    function initBackToTop() {
        const backToTopBtn = document.getElementById('backToTop');
        if (!backToTopBtn) return;

        let ticking = false;

        function updateBackToTop() {
            const scrollY = window.pageYOffset;
            
            if (scrollY > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }

            ticking = false;
        }

        function requestTick() {
            if (!ticking) {
                requestAnimationFrame(updateBackToTop);
                ticking = true;
            }
        }

        window.addEventListener('scroll', requestTick, { passive: true });

        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Dropdown functionality
    function initDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown');
        
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            if (!toggle) return;

            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const isExpanded = this.getAttribute('aria-expanded') === 'true';
                
                // Close all other dropdowns
                dropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        const otherToggle = otherDropdown.querySelector('.dropdown-toggle');
                        if (otherToggle) {
                            otherToggle.setAttribute('aria-expanded', 'false');
                        }
                    }
                });
                
                // Toggle current dropdown
                this.setAttribute('aria-expanded', !isExpanded);
            });

            // Close dropdown on outside click
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });

            // Close dropdown on escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });
        });
    }

    // Accessibility enhancements
    function initAccessibility() {
        // Add keyboard navigation for buttons with click handlers
        const clickableElements = document.querySelectorAll('[role="button"]:not(button):not(a)');
        
        clickableElements.forEach(element => {
            element.setAttribute('tabindex', '0');
            
            element.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.click();
                }
            });
        });

        // Improve form accessibility
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                // Add aria-describedby for error messages
                const errorElement = form.querySelector(`[data-error-for="${input.name}"]`);
                if (errorElement) {
                    input.setAttribute('aria-describedby', errorElement.id);
                }
                
                // Mark required fields
                if (input.hasAttribute('required')) {
                    input.setAttribute('aria-required', 'true');
                }
            });
        });

        // Announce page changes for screen readers
        const pageTitle = document.title;
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = `Página cargada: ${pageTitle}`;
        document.body.appendChild(announcement);

        // Remove announcement after screen readers have had time to read it
        setTimeout(() => {
            if (announcement.parentNode) {
                announcement.parentNode.removeChild(announcement);
            }
        }, 1000);
    }

    // Performance optimizations
    function initPerformanceOptimizations() {
        // Lazy load images
        const images = document.querySelectorAll('img[data-src]');
        if (images.length > 0 && 'IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px'
            });

            images.forEach(img => imageObserver.observe(img));
        }

        // Preload critical resources on interaction
        let interactionEvents = ['mousedown', 'touchstart'];
        let hasInteracted = false;

        function preloadOnInteraction() {
            if (hasInteracted) return;
            hasInteracted = true;

            // Preload critical resources
            const criticalResources = [
                '/static/css/home.css',
                '/static/js/home.js'
            ];

            criticalResources.forEach(resource => {
                const link = document.createElement('link');
                link.rel = 'prefetch';
                link.href = resource;
                document.head.appendChild(link);
            });

            // Remove event listeners
            interactionEvents.forEach(event => {
                document.removeEventListener(event, preloadOnInteraction, { passive: true });
            });
        }

        // Add interaction listeners
        interactionEvents.forEach(event => {
            document.addEventListener(event, preloadOnInteraction, { passive: true });
        });

        // Connection-aware loading
        if ('connection' in navigator) {
            const connection = navigator.connection;
            
            // Reduce animations on slow connections
            if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                document.documentElement.classList.add('reduce-motion');
                
                // Add CSS to reduce animations
                const style = document.createElement('style');
                style.textContent = `
                    .reduce-motion * {
                        animation-duration: 0.01ms !important;
                        transition-duration: 0.01ms !important;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    }

    // Utility functions
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Global notification system
    window.showNotification = function(message, type = 'info', duration = 5000) {
        const alertContainer = document.getElementById('alertContainer') || createAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible`;
        alert.innerHTML = `
            <button type="button" class="alert-close" aria-label="Cerrar alerta">
                <i class="fas fa-times" aria-hidden="true"></i>
            </button>
            <div class="alert-content">
                <i class="alert-icon fas fa-${getAlertIcon(type)}" aria-hidden="true"></i>
                ${message}
            </div>
        `;

        alertContainer.appendChild(alert);

        // Add event listener to close button
        const closeBtn = alert.querySelector('.alert-close');
        closeBtn.addEventListener('click', () => {
            dismissAlert(alert);
        });

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                if (alert.parentNode) {
                    dismissAlert(alert);
                }
            }, duration);
        }

        return alert;
    };

    function createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'alertContainer';
        container.className = 'alert-container';
        container.setAttribute('role', 'alert');
        container.setAttribute('aria-live', 'polite');
        container.setAttribute('aria-atomic', 'true');
        document.body.appendChild(container);
        return container;
    }

    function getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    function dismissAlert(alert) {
        alert.style.animation = 'slideOutRight 0.3s ease forwards';
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 300);
    }

    // Form validation utilities
    window.FormValidator = {
        email: function(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },
        
        phone: function(phone) {
            const re = /^[\+]?[0-9\s\-\(\)]{10,}$/;
            return re.test(phone.replace(/\s/g, ''));
        },
        
        required: function(value) {
            return value && value.trim().length > 0;
        },
        
        minLength: function(value, min) {
            return value && value.length >= min;
        },
        
        maxLength: function(value, max) {
            return !value || value.length <= max;
        }
    };

    // Export utilities to global scope
    window.AlphaUtils = {
        debounce,
        throttle,
        showNotification: window.showNotification,
        FormValidator: window.FormValidator
    };

    // Service Worker registration
    if ('serviceWorker' in navigator && location.protocol === 'https:') {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('ServiceWorker registration successful');
                })
                .catch(function(error) {
                    console.log('ServiceWorker registration failed:', error);
                });
        });
    }

    // Error handling
    window.addEventListener('error', function(e) {
        console.error('JavaScript error:', e.error);
        
        // Show user-friendly error message for critical errors
        if (e.error && e.error.message && !e.error.message.includes('Script error')) {
            window.showNotification(
                'Se produjo un error inesperado. Por favor, recarga la página.',
                'error',
                10000
            );
        }
    });

    // Unhandled promise rejection handling
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        e.preventDefault();
    });

})();
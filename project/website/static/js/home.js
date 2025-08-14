document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            once: true,
            offset: 50,
            easing: 'ease-out-cubic'
        });
    }

    // Particle system for hero background
    initParticleSystem();
    
    // Counter animations
    initCounterAnimations();
    
    // Smooth scrolling
    initSmoothScrolling();
    
    // Navbar behavior on scroll
    initNavbarScrollBehavior();
    
    // Interactive elements
    initInteractiveElements();
    
    // Newsletter form
    initNewsletterForm();
    
    // Performance optimizations
    initPerformanceOptimizations();
    
    // Intersection observers for animations
    initIntersectionObservers();
});

// Particle System
function initParticleSystem() {
    const particleContainer = document.getElementById('particles');
    if (!particleContainer) return;
    
    // Create floating particles
    function createParticle() {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random size and position
        const size = Math.random() * 6 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
        particle.style.animationDelay = Math.random() * 5 + 's';
        
        particleContainer.appendChild(particle);
        
        // Remove particle after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 25000);
    }
    
    // Create particles periodically
    function startParticleGeneration() {
        createParticle();
        setTimeout(startParticleGeneration, Math.random() * 2000 + 1000);
    }
    
    // Only start particles if not reduced motion preference
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        startParticleGeneration();
    }
}

// Counter Animations
function initCounterAnimations() {
    const counters = document.querySelectorAll('.counter');
    
    const animateCounter = (counter) => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                counter.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    };
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                entry.target.classList.add('animated');
                animateCounter(entry.target);
            }
        });
    }, observerOptions);
    
    counters.forEach(counter => counterObserver.observe(counter));
}

// Smooth Scrolling
function initSmoothScrolling() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Scroll indicator
    const scrollIndicator = document.querySelector('.scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', () => {
            const nextSection = document.querySelector('#innovation');
            if (nextSection) {
                nextSection.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    }
}

// Navbar Scroll Behavior
function initNavbarScrollBehavior() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    let lastScroll = 0;
    let ticking = false;
    
    const updateNavbar = () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            navbar.style.background = 'rgba(43, 69, 112, 0.95)';
            navbar.style.backdropFilter = 'blur(20px)';
            navbar.style.boxShadow = '0 2px 20px rgba(43, 69, 112, 0.1)';
        } else {
            navbar.style.background = 'var(--primary-color)';
            navbar.style.backdropFilter = 'none';
            navbar.style.boxShadow = 'none';
        }
        
        // Hide/show navbar on scroll
        if (currentScroll > lastScroll && currentScroll > 200) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;
        ticking = false;
    };
    
    const requestTick = () => {
        if (!ticking) {
            requestAnimationFrame(updateNavbar);
            ticking = true;
        }
    };
    
    window.addEventListener('scroll', requestTick, { passive: true });
}

// Interactive Elements
function initInteractiveElements() {
    // Card hover effects with performance optimization
    const cards = document.querySelectorAll('.innovation-card, .step-card, .impact-stat');
    
    const handleCardInteraction = (card, isHovering) => {
        if (window.matchMedia('(hover: hover)').matches) {
            card.style.willChange = isHovering ? 'transform, box-shadow' : 'auto';
            
            if (isHovering) {
                card.style.transform = 'translateY(-8px)';
                card.style.boxShadow = 'var(--shadow-heavy)';
            } else {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = 'var(--shadow-light)';
            }
        }
    };
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => handleCardInteraction(card, true));
        card.addEventListener('mouseleave', () => handleCardInteraction(card, false));
        
        // Add focus handling for keyboard navigation
        card.addEventListener('focus', () => handleCardInteraction(card, true));
        card.addEventListener('blur', () => handleCardInteraction(card, false));
    });
    
    // Button ripple effects
    initRippleEffects();
    
    // Neural network animation
    initNeuralNetworkAnimation();
    
    // Typing animation for hero text
    initTypingAnimation();
}

// Ripple Effects for Buttons
function initRippleEffects() {
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary, .step-cta');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
                z-index: 1;
            `;
            
            // Ensure button has relative positioning
            if (getComputedStyle(this).position === 'static') {
                this.style.position = 'relative';
            }
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                if (ripple.parentNode) {
                    ripple.parentNode.removeChild(ripple);
                }
            }, 600);
        });
    });
    
    // Add ripple animation CSS
    if (!document.querySelector('#ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Neural Network Animation
function initNeuralNetworkAnimation() {
    const nodes = document.querySelectorAll('.node');
    const connections = document.querySelectorAll('.connection');
    
    if (nodes.length === 0) return;
    
    let animationIndex = 0;
    
    const animateNetwork = () => {
        // Reset all nodes
        nodes.forEach(node => node.classList.remove('active'));
        connections.forEach(connection => connection.classList.remove('active'));
        
        // Activate current node and connections
        if (nodes[animationIndex]) {
            nodes[animationIndex].classList.add('active');
            
            // Activate random connections
            const activeConnections = Math.floor(Math.random() * connections.length / 2) + 1;
            for (let i = 0; i < activeConnections; i++) {
                const randomConnection = Math.floor(Math.random() * connections.length);
                connections[randomConnection].classList.add('active');
            }
        }
        
        animationIndex = (animationIndex + 1) % nodes.length;
    };
    
    // Only animate if not reduced motion
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        setInterval(animateNetwork, 1500);
        animateNetwork(); // Initial call
    }
}

// Typing Animation
function initTypingAnimation() {
    const typingElements = document.querySelectorAll('[data-typing]');
    
    typingElements.forEach(element => {
        const text = element.textContent;
        const speed = parseInt(element.dataset.typingSpeed) || 50;
        
        element.textContent = '';
        element.style.borderRight = '2px solid currentColor';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, speed);
            } else {
                // Blinking cursor effect
                setTimeout(() => {
                    element.style.borderRight = 'none';
                }, 1000);
            }
        };
        
        // Start typing when element is in view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !element.classList.contains('typed')) {
                    element.classList.add('typed');
                    typeWriter();
                }
            });
        });
        
        observer.observe(element);
    });
}

// Newsletter Form
function initNewsletterForm() {
    const newsletterForm = document.querySelector('.newsletter-form');
    if (!newsletterForm) return;
    
    newsletterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = this.querySelector('input[type="email"]').value;
        const button = this.querySelector('.btn-newsletter');
        const originalContent = button.innerHTML;
        
        // Validate email
        if (!isValidEmail(email)) {
            showNotification('Por favor, ingrese un email válido', 'error');
            return;
        }
        
        // Show loading state
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        button.disabled = true;
        
        // Simulate API call
        setTimeout(() => {
            button.innerHTML = '<i class="fas fa-check"></i>';
            this.querySelector('input[type="email"]').value = '';
            showNotification('¡Suscripción exitosa! Revisar su email.', 'success');
            
            setTimeout(() => {
                button.innerHTML = originalContent;
                button.disabled = false;
            }, 2000);
        }, 1500);
    });
}

// Utility Functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? 'var(--success-color)' : 
                   type === 'error' ? 'var(--accent-color)' : 'var(--primary-color)',
        color: 'white',
        padding: '1rem 2rem',
        borderRadius: 'var(--border-radius)',
        boxShadow: 'var(--shadow-medium)',
        zIndex: '10000',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        maxWidth: '300px',
        wordWrap: 'break-word'
    });
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after delay
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Performance Optimizations
function initPerformanceOptimizations() {
    // Lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
    
    // Preload critical resources
    preloadCriticalResources();
    
    // Optimize scroll events
    optimizeScrollEvents();
}

function preloadCriticalResources() {
    // Preload hero background image if it exists
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        const bgImage = getComputedStyle(heroSection).backgroundImage;
        if (bgImage && bgImage !== 'none') {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = bgImage.slice(5, -2); // Remove url(" and ")
            document.head.appendChild(link);
        }
    }
}

function optimizeScrollEvents() {
    let ticking = false;
    
    const handleScroll = () => {
        // Update scroll progress indicator
        updateScrollProgress();
        
        // Parallax effects for performance-conscious devices
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && 
            !window.matchMedia('(max-width: 768px)').matches) {
            updateParallaxElements();
        }
        
        ticking = false;
    };
    
    const requestScrollTick = () => {
        if (!ticking) {
            requestAnimationFrame(handleScroll);
            ticking = true;
        }
    };
    
    window.addEventListener('scroll', requestScrollTick, { passive: true });
}

function updateScrollProgress() {
    const scrolled = window.pageYOffset;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (scrolled / maxScroll) * 100;
    
    // Update any progress indicators
    const progressBars = document.querySelectorAll('.scroll-progress');
    progressBars.forEach(bar => {
        bar.style.transform = `scaleX(${progress / 100})`;
    });
}

function updateParallaxElements() {
    const scrolled = window.pageYOffset;
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    parallaxElements.forEach(element => {
        const speed = element.dataset.parallax || 0.5;
        const yPos = -(scrolled * speed);
        element.style.transform = `translateY(${yPos}px)`;
    });
}

// Intersection Observers for Advanced Animations
function initIntersectionObservers() {
    // Staggered animations for grid items
    const gridItems = document.querySelectorAll('.innovation-grid > *, .steps-modern > *');
    
    const staggerObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
                staggerObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    gridItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        staggerObserver.observe(item);
    });
    
    // Reveal animations for sections
    const sections = document.querySelectorAll('section');
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                // Trigger any section-specific animations
                triggerSectionAnimations(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    sections.forEach(section => sectionObserver.observe(section));
}

function triggerSectionAnimations(section) {
    // Custom animations for specific sections
    if (section.classList.contains('ai-features-section')) {
        animateNeuralNetwork();
    }
    
    if (section.classList.contains('impact-section')) {
        animateImpactMetrics();
    }
}

function animateNeuralNetwork() {
    const network = document.querySelector('.neural-network');
    if (network && !network.classList.contains('animated')) {
        network.classList.add('animated');
        // Additional neural network animations
    }
}

function animateImpactMetrics() {
    const metrics = document.querySelectorAll('.impact-stat');
    metrics.forEach((metric, index) => {
        setTimeout(() => {
            metric.style.transform = 'scale(1.05)';
            setTimeout(() => {
                metric.style.transform = 'scale(1)';
            }, 200);
        }, index * 150);
    });
}

// Error handling and fallbacks
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Graceful fallback for critical functionality
});

// Accessibility enhancements
function initAccessibilityEnhancements() {
    // Skip to content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Saltar al contenido principal';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: var(--primary-color);
        color: white;
        padding: 8px;
        text-decoration: none;
        z-index: 100;
        border-radius: 4px;
    `;
    
    skipLink.addEventListener('focus', () => {
        skipLink.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Keyboard navigation for interactive elements
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            const target = e.target;
            if (target.classList.contains('card') || target.getAttribute('role') === 'button') {
                target.click();
                e.preventDefault();
            }
        }
    });
}

// Initialize accessibility on load
document.addEventListener('DOMContentLoaded', initAccessibilityEnhancements);

// Export functions for potential use in other scripts
window.AlphaHome = {
    initParticleSystem,
    showNotification,
    initCounterAnimations
};
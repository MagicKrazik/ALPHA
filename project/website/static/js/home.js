document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS animation library
    AOS.init({
        duration: 800,
        once: true,
        offset: 100,
        easing: 'ease-out'
    });

    // Handle video background
    const videoContainer = document.querySelector('.hero-video-container');
    const video = document.querySelector('.hero-video');
    
    if (video) {
        // Add loaded class when video is ready
        video.addEventListener('loadeddata', function() {
            videoContainer.classList.add('loaded');
        });

        // Handle video playback based on visibility
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    video.play().catch(function(error) {
                        console.log("Video play failed:", error);
                    });
                } else {
                    video.pause();
                }
            });
        }, { threshold: 0.1 });

        observer.observe(video);

        // Fallback if video fails to load
        video.addEventListener('error', function() {
            videoContainer.style.background = 'var(--gradient-primary)';
        });
    }

    // Smooth scroll functionality
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

    // Navbar scroll behavior
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        // Add/remove background blur on scroll
        if (currentScroll > 50) {
            navbar.style.backgroundColor = 'rgba(43, 69, 112, 0.95)';
            navbar.style.backdropFilter = 'blur(8px)';
        } else {
            navbar.style.backgroundColor = 'var(--primary-color)';
            navbar.style.backdropFilter = 'none';
        }

        lastScroll = currentScroll;
    });

    // Add hover effects for cards
    const cards = document.querySelectorAll('.phase-card, .benefit-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add intersection observer for fade-in animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for fade-in
    document.querySelectorAll('.phase-card, .benefit-card, .step-card').forEach(card => {
        observer.observe(card);
    });

    // Handle mobile devices
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
    }

    // Performance optimization for mobile
    if (window.matchMedia('(max-width: 768px)').matches) {
        const video = document.querySelector('.hero-video');
        if (video) {
            video.setAttribute('playsinline', '');
            video.setAttribute('preload', 'metadata');
        }
    }
});
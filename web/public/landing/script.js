document.addEventListener('DOMContentLoaded', () => {
    // Smooth scroll functionality
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Intersection Observer for animations
    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -80px 0px' };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card, .stack-card, .stat-card, .panel, .steps li').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(24px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.topbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            if (currentScroll > 100) {
                navbar.style.background = 'rgba(255, 255, 255, 0.9)';
                navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.08)';
            } else {
                navbar.style.background = 'rgba(255, 255, 255, 0.8)';
                navbar.style.boxShadow = 'none';
            }
        });
    }

    // Add hover effect to interface cards
    document.querySelectorAll('.interface-card').forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        });
        card.addEventListener('mouseleave', function () {
            this.style.transition = 'all 0.3s ease';
        });
    });

    // Parallax effect for hero section
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroText = document.querySelector('.hero-text');
        const heroVisual = document.querySelector('.hero-visual');

        if (heroText) {
            heroText.style.transform = `translateY(${scrolled * 0.2}px)`;
            heroText.style.opacity = Math.max(0, 1 - scrolled / 600);
        }
        if (heroVisual) {
            heroVisual.style.transform = `translateY(${scrolled * 0.15}px)`;
        }
    });

    // Adjust particle opacity on scroll
    window.addEventListener('scroll', () => {
        const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        const particles = document.querySelector('.bg-particles');
        if (particles) {
            particles.style.opacity = 1 - (scrollPercent / 180);
        }
    });
});

// Console Easter Egg
console.log('%c🚀 ICGL - Iterative Co-Governance Loop', 'color: #6366f1; font-size: 20px; font-weight: bold;');
console.log('%cBuilt with ❤️ for better governance', 'color: #8b5cf6; font-size: 14px;');
console.log('%c\n🎯 Three powerful interfaces:\n  1. Static UI - Fast & Simple\n  2. Admin Tools - Developer Focused\n  3. Production App - Full Featured\n', 'color: #cbd5e1; font-size: 12px;');

// Add random stars effect
function createStars() {
    const particlesContainer = document.querySelector('.bg-particles');
    if (!particlesContainer) return;

    setInterval(() => {
        const star = document.createElement('div');
        star.style.position = 'absolute';
        star.style.width = '2px';
        star.style.height = '2px';
        star.style.background = 'rgba(255, 255, 255, 0.8)';
        star.style.borderRadius = '50%';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animation = 'twinkle 3s ease-in-out';

        particlesContainer.appendChild(star);

        setTimeout(() => star.remove(), 3000);
    }, 3000);
}

// Add twinkle animation
const style = document.createElement('style');
style.textContent = `
    @keyframes twinkle {
        0%, 100% { opacity: 0; transform: scale(0); }
        50% { opacity: 1; transform: scale(1); }
    }
`;
document.head.appendChild(style);

createStars();

// Log page load time
window.addEventListener('load', () => {
    const loadTime = performance.now();
    console.log(`%c⚡ Page loaded in ${loadTime.toFixed(2)}ms`, 'color: #10b981; font-weight: bold;');
});

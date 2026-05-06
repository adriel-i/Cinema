// Funciones globales del sistema de cine

class CineMax {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTooltips();
        this.setupNotifications();
        this.setupDarkMode();
    }

    setupEventListeners() {
        // Smooth scroll para enlaces internos
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
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

        // Animación de elementos al hacer scroll
        this.setupScrollAnimations();
    }

    setupTooltips() {
        // Inicializar tooltips de Bootstrap si están disponibles
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    setupNotifications() {
        // Sistema de notificaciones personalizado
        this.showNotification = function(message, type = 'info', duration = 5000) {
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(notification);
            
            // Auto-eliminar después del tiempo especificado
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, duration);
        };
    }

    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        // Observar elementos con clase .animate-on-scroll
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    // Utilidades
    formatCurrency(amount) {
        return new Intl.NumberFormat('es-AR', {
            style: 'currency',
            currency: 'ARS'
        }).format(amount);
    }

    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        return new Date(date).toLocaleDateString('es-AR', { ...defaultOptions, ...options });
    }

    formatTime(time) {
        return new Date(`2000-01-01T${time}`).toLocaleTimeString('es-AR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    debounce(func, wait) {
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

    // Validaciones
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    validatePhone(phone) {
        const re = /^[+]?[\d\s-()]+$/;
        return re.test(phone);
    }

    // Loading states
    setLoading(element, loading = true) {
        if (loading) {
            element.classList.add('loading');
            element.disabled = true;
        } else {
            element.classList.remove('loading');
            element.disabled = false;
        }
    }

    // AJAX helper
    async ajaxRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('AJAX request failed:', error);
            throw error;
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // Gestión de asientos (utilidad para selección de asientos)
    setupSeatSelection() {
        const seats = document.querySelectorAll('.seat-selectable');
        const selectedSeats = new Set();
        
        seats.forEach(seat => {
            seat.addEventListener('click', () => {
                const seatId = seat.dataset.seatId;
                
                if (selectedSeats.has(seatId)) {
                    selectedSeats.delete(seatId);
                    seat.classList.remove('selected');
                } else {
                    selectedSeats.add(seatId);
                    seat.classList.add('selected');
                }
                
                this.updateSelectedSeatsDisplay(selectedSeats);
            });
        });
    }

    updateSelectedSeatsDisplay(selectedSeats) {
        const display = document.getElementById('selected-seats-display');
        if (display) {
            if (selectedSeats.size > 0) {
                display.textContent = Array.from(selectedSeats).join(', ');
            } else {
                display.textContent = 'No hay asientos seleccionados';
            }
        }
    }

    // Sistema de búsqueda en tiempo real
    setupLiveSearch(searchInput, resultsContainer, searchUrl) {
        const searchFunction = this.debounce(async (query) => {
            if (query.length < 2) {
                resultsContainer.innerHTML = '';
                return;
            }

            try {
                const results = await this.ajaxRequest(`${searchUrl}?q=${encodeURIComponent(query)}`);
                this.displaySearchResults(results, resultsContainer);
            } catch (error) {
                console.error('Search failed:', error);
            }
        }, 300);

        searchInput.addEventListener('input', (e) => {
            searchFunction(e.target.value);
        });
    }

    displaySearchResults(results, container) {
        if (results.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No se encontraron resultados</div>';
            return;
        }

        container.innerHTML = results.map(result => `
            <div class="search-result-item p-3 border-bottom">
                <h6>${result.title}</h6>
                <p class="text-muted mb-0">${result.description}</p>
                <a href="${result.url}" class="btn btn-sm btn-outline-primary mt-2">Ver más</a>
            </div>
        `).join('');
    }

    // Gestión de favoritos
    toggleFavorite(movieId, button) {
        const isFavorite = button.classList.contains('favorited');
        
        this.ajaxRequest(`/api/movies/${movieId}/favorite/`, {
            method: 'POST',
            body: JSON.stringify({ action: isFavorite ? 'remove' : 'add' })
        })
        .then(data => {
            if (data.success) {
                button.classList.toggle('favorited');
                button.innerHTML = isFavorite ? 
                    '<i class="far fa-heart"></i> Agregar a favoritos' : 
                    '<i class="fas fa-heart"></i> En favoritos';
            }
        })
        .catch(error => {
            this.showNotification('Error al actualizar favoritos', 'error');
        });
    }

    // Sistema de calificación
    setupRatingSystem(movieId) {
        const stars = document.querySelectorAll('.rating-star');
        
        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                const rating = index + 1;
                this.submitRating(movieId, rating);
            });
            
            star.addEventListener('mouseenter', () => {
                stars.forEach((s, i) => {
                    s.classList.toggle('hovered', i <= index);
                });
            });
        });
        
        document.querySelector('.rating-container').addEventListener('mouseleave', () => {
            stars.forEach(star => {
                star.classList.remove('hovered');
            });
        });
    }

    submitRating(movieId, rating) {
        this.ajaxRequest(`/api/movies/${movieId}/rate/`, {
            method: 'POST',
            body: JSON.stringify({ rating })
        })
        .then(data => {
            if (data.success) {
                this.showNotification('¡Gracias por tu calificación!', 'success');
                this.updateRatingDisplay(data.new_rating);
            }
        })
        .catch(error => {
            this.showNotification('Error al enviar calificación', 'error');
        });
    }

    updateRatingDisplay(newRating) {
        const display = document.querySelector('.rating-display');
        if (display) {
            display.textContent = newRating.toFixed(1);
        }
    }

    // Utilidad para contador regresivo
    startCountdown(elementId, targetTime, onComplete) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const updateCountdown = () => {
            const now = new Date().getTime();
            const distance = targetTime - now;

            if (distance < 0) {
                element.textContent = 'Tiempo expirado';
                if (onComplete) onComplete();
                return;
            }

            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            element.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        };

        updateCountdown();
        const interval = setInterval(updateCountdown, 1000);

        return interval;
    }

    // Sistema de notificaciones push (simulado)
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    showPushNotification(title, options = {}) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                icon: '/static/images/logo.png',
                badge: '/static/images/badge.png',
                ...options
            });
        }
    }

    // Dark mode functionality
    setupDarkMode() {
        console.log('Setting up dark mode...');
        const darkModeToggle = document.getElementById('darkModeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const html = document.documentElement;
        
        console.log('Dark mode toggle found:', darkModeToggle);
        console.log('Theme icon found:', themeIcon);
        
        // Load saved theme or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        html.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme, themeIcon);
        console.log('Initial theme set to:', savedTheme);
        
        // Mostrar contenido después de aplicar el tema
        document.body.classList.add('theme-loaded');
        
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', () => {
                console.log('Dark mode toggle clicked!');
                const currentTheme = html.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                
                console.log('Changing theme from', currentTheme, 'to', newTheme);
                html.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                this.updateThemeIcon(newTheme, themeIcon);
            });
        } else {
            console.error('Dark mode toggle button not found!');
        }
    }
    
    updateThemeIcon(theme, iconElement) {
        if (iconElement) {
            if (theme === 'dark') {
                iconElement.classList.remove('fa-moon');
                iconElement.classList.add('fa-sun');
            } else {
                iconElement.classList.remove('fa-sun');
                iconElement.classList.add('fa-moon');
            }
        }
    }
}

// Exportar para uso global
window.CineMax = CineMax;

// Utilidades adicionales
const Utils = {
    // Copiar al portapapeles
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            window.cinemax.showNotification('¡Copiado al portapapeles!', 'success');
        }).catch(err => {
            console.error('Error al copiar:', err);
        });
    },

    // Compartir en redes sociales
    shareOnSocial(platform, url, title) {
        const shareUrls = {
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
            twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
            whatsapp: `https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`
        };

        if (shareUrls[platform]) {
            window.open(shareUrls[platform], '_blank', 'width=600,height=400');
        }
    },

    // Descargar ticket
    downloadTicket(ticketId) {
        window.open(`/api/tickets/${ticketId}/download/`, '_blank');
    },

    // Imprimir ticket
    printTicket(ticketId) {
        window.open(`/tickets/${ticketId}/print/`, '_blank');
    }
};

// Hacer utilidades disponibles globalmente
window.Utils = Utils;

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing CineMax...');
    window.cinemax = new CineMax();
    console.log('CineMax initialized:', window.cinemax);
    
    // Solicitar permiso para notificaciones push
    window.cinemax.requestNotificationPermission();
    
    // Configurar componentes específicos si existen en la página
    if (document.querySelector('.seat-selectable')) {
        window.cinemax.setupSeatSelection();
    }
    
    if (document.querySelector('.rating-container')) {
        const movieId = document.querySelector('.rating-container').dataset.movieId;
        window.cinemax.setupRatingSystem(movieId);
    }
    
    if (document.querySelector('#live-search')) {
        const searchInput = document.querySelector('#live-search');
        const resultsContainer = document.querySelector('#search-results');
        const searchUrl = '/api/search/';
        window.cinemax.setupLiveSearch(searchInput, resultsContainer, searchUrl);
    }
});

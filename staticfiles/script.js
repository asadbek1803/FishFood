/* ==========================================
   MAIN SCRIPT - CLEAN MODULAR CODE 2025
   ========================================== */

const CART_KEY = 'fishfood_cart';

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initHeroSlider();
    initCartSystem();
    initFAQ();
    initAnimations();
});

/* ==========================================
   NAVBAR
   ========================================== */
function initNavbar() {
    const navbar = document.getElementById('navbar');
    const toggler = document.getElementById('navToggler');
    const navLinks = document.getElementById('navLinks');

    if (!navbar || !toggler || !navLinks) return;

    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile menu toggle
    toggler.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        const icon = toggler.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        }
        document.body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : '';
    });

    // Close on nav link click
    navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            const icon = toggler.querySelector('i');
            if (icon) {
                icon.classList.add('fa-bars');
                icon.classList.remove('fa-times');
            }
            document.body.style.overflow = '';
        });
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!navbar.contains(e.target) && navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            const icon = toggler.querySelector('i');
            if (icon) {
                icon.classList.add('fa-bars');
                icon.classList.remove('fa-times');
            }
            document.body.style.overflow = '';
        }
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            const icon = toggler.querySelector('i');
            if (icon) {
                icon.classList.add('fa-bars');
                icon.classList.remove('fa-times');
            }
            document.body.style.overflow = '';
        }
    });
}

/* ==========================================
   HERO SLIDER - NEON EFFECTS
   ========================================== */
function initHeroSlider() {
    const slider = document.getElementById('heroSlider');
    const dotsContainer = document.getElementById('sliderDots');
    const prevBtn = document.getElementById('prevSlide');
    const nextBtn = document.getElementById('nextSlide');

    if (!slider) return;

    const slides = slider.querySelectorAll('.hero-slide');
    if (slides.length === 0) return;

    let currentSlide = 0;
    let autoplayInterval;

    // Create dots
    if (dotsContainer) {
        slides.forEach((_, index) => {
            const dot = document.createElement('div');
            dot.className = 'slider-dot';
            if (index === 0) dot.classList.add('active');
            dot.addEventListener('click', () => goToSlide(index));
            dotsContainer.appendChild(dot);
        });
    }

    const dots = dotsContainer ? dotsContainer.querySelectorAll('.slider-dot') : [];

    function goToSlide(index) {
        if (index < 0 || index >= slides.length) return;

        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        // Pause previous video
        const prevVideo = slides[currentSlide].querySelector('video');
        if (prevVideo) {
            prevVideo.pause();
            prevVideo.currentTime = 0;
        }

        slides[index].classList.add('active');
        if (dots[index]) dots[index].classList.add('active');

        // Play new video
        const nextVideo = slides[index].querySelector('video');
        if (nextVideo) {
            nextVideo.currentTime = 0;
            nextVideo.play().catch(() => {});
        }

        currentSlide = index;
        resetAutoplay();
    }

    function nextSlide() {
        goToSlide((currentSlide + 1) % slides.length);
    }

    function prevSlide() {
        goToSlide((currentSlide - 1 + slides.length) % slides.length);
    }

    function resetAutoplay() {
        clearInterval(autoplayInterval);
        if (slides.length > 1) {
            autoplayInterval = setInterval(nextSlide, 7000);
        }
    }

    // Navigation buttons
    if (nextBtn) nextBtn.addEventListener('click', nextSlide);
    if (prevBtn) prevBtn.addEventListener('click', prevSlide);

    // Touch swipe
    let touchStartX = 0;
    slider.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });

    slider.addEventListener('touchend', (e) => {
        const touchEndX = e.changedTouches[0].screenX;
        if (touchEndX < touchStartX - 50) nextSlide();
        if (touchEndX > touchStartX + 50) prevSlide();
    });

    // Pause on hover
    slider.addEventListener('mouseenter', () => clearInterval(autoplayInterval));
    slider.addEventListener('mouseleave', resetAutoplay);

    // Start autoplay
    resetAutoplay();
}

/* ==========================================
   CART SYSTEM
   ========================================== */
function initCartSystem() {
    let cart = getCart();

    const cartBtn = document.getElementById('openCart');
    const cartModal = document.getElementById('cartModal');
    const closeBtn = document.querySelector('.close-modal');
    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotalEl = document.getElementById('cartTotal');
    const checkoutBtn = document.getElementById('checkoutBtn');
    const orderForm = document.getElementById('orderForm');

    // Open modal
    if (cartBtn) {
        cartBtn.addEventListener('click', () => {
            renderCart();
            if (cartModal) {
                cartModal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        });
    }

    // Close modal
    const closeModal = () => {
        if (cartModal) {
            cartModal.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cartModal) {
        cartModal.addEventListener('click', (e) => {
            if (e.target === cartModal) closeModal();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && cartModal && cartModal.classList.contains('active')) {
            closeModal();
        }
    });

    // Add to cart
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-add-cart');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        const id = btn.getAttribute('data-id') || btn.dataset.id;
        const name = btn.getAttribute('data-name') || btn.dataset.name;
        const price = parseFloat(btn.getAttribute('data-price') || btn.dataset.price) || 0;

        if (!id || !name || price <= 0) {
            showNotification('Mahsulot ma\'lumotlari topilmadi', 'error');
            return;
        }

        const productCard = btn.closest('.product-card');
        let qtyInput = null;
        if (productCard) {
            qtyInput = productCard.querySelector('.qty-input') || 
                      productCard.querySelector(`#quantity_${id}`);
        }
        if (!qtyInput) {
            qtyInput = document.getElementById(`quantity_${id}`);
        }

        const quantity = qtyInput ? parseFloat(qtyInput.value) || 1 : 1;
        addToCart(id, name, price, quantity);

        // Visual feedback
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> <span>Qo\'shildi</span>';
        btn.style.background = 'var(--gradient-primary)';
        btn.style.color = '#fff';
        btn.disabled = true;

        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.style.background = '';
            btn.style.color = '';
            btn.disabled = false;
        }, 2000);

        if (qtyInput) qtyInput.value = 1;
    });

    // Quantity buttons
    document.addEventListener('click', (e) => {
        const increaseBtn = e.target.closest('.increase');
        const decreaseBtn = e.target.closest('.decrease');

        if (increaseBtn) {
            const id = increaseBtn.getAttribute('data-id');
            const input = document.getElementById(`quantity_${id}`) || 
                         increaseBtn.parentElement.querySelector('.qty-input');
            if (input) {
                input.value = (parseFloat(input.value) + 0.5).toFixed(1);
            }
        }

        if (decreaseBtn) {
            const id = decreaseBtn.getAttribute('data-id');
            const input = document.getElementById(`quantity_${id}`) || 
                         decreaseBtn.parentElement.querySelector('.qty-input');
            if (input) {
                const current = parseFloat(input.value) || 0;
                if (current > 0.5) {
                    input.value = (current - 0.5).toFixed(1);
                }
            }
        }
    });

    function getCart() {
        try {
            return JSON.parse(localStorage.getItem(CART_KEY)) || [];
        } catch {
            return [];
        }
    }

    function saveCart() {
        try {
            localStorage.setItem(CART_KEY, JSON.stringify(cart));
            updateBadge();
        } catch (e) {
            console.error('Cart save error:', e);
        }
    }

    function addToCart(id, name, price, quantity) {
        if (!Array.isArray(cart)) cart = [];
        const idStr = String(id);
        const existing = cart.find(item => item.id === idStr);

        if (existing) {
            existing.quantity = parseFloat(existing.quantity || 0) + parseFloat(quantity || 1);
        } else {
            cart.push({
                id: idStr,
                name: String(name || 'Noma\'lum mahsulot'),
                price: parseFloat(price || 0),
                quantity: parseFloat(quantity || 1)
            });
        }

        saveCart();
        showNotification(`${name} savatga qo'shildi!`, 'success');
        updateBadge();
    }

    function removeFromCart(id) {
        const item = cart.find(i => i.id === String(id));
        cart = cart.filter(item => item.id !== String(id));
        saveCart();
        renderCart();
        if (item) showNotification(`${item.name} o'chirildi`, 'info');
    }

    function updateQuantity(id, newQuantity) {
        const item = cart.find(i => i.id === String(id));
        if (item && newQuantity > 0) {
            item.quantity = parseFloat(newQuantity);
            saveCart();
            renderCart();
        } else if (item && newQuantity <= 0) {
            removeFromCart(id);
        }
    }

    function updateBadge() {
        const count = cart.reduce((sum, item) => sum + parseFloat(item.quantity || 0), 0);
        const badge = document.getElementById('cartBadge');
        if (badge) {
            badge.textContent = Math.ceil(count);
            badge.classList.toggle('show', count > 0);
        }
    }

    function renderCart() {
        if (!cartItemsContainer) return;
        cartItemsContainer.innerHTML = '';
        let total = 0;

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = `
                <div style="text-align:center; padding:3rem 1rem; color:var(--text-muted);">
                    <i class="fas fa-shopping-cart" style="font-size:4rem; opacity:0.3; margin-bottom:1rem;"></i>
                    <p style="font-size:1.1rem;">Savatingiz bo'sh</p>
                </div>
            `;
        } else {
            cart.forEach(item => {
                const itemTotal = parseFloat(item.price || 0) * parseFloat(item.quantity || 0);
                total += itemTotal;

                const div = document.createElement('div');
                div.className = 'cart-item';
                div.innerHTML = `
                    <div style="flex: 1;">
                        <div class="cart-item-title">${escapeHtml(item.name)}</div>
                        <div style="font-size:0.9rem; color:var(--text-muted); margin-top:4px;">
                            ${parseFloat(item.price || 0).toLocaleString()} so'm × 
                            <input type="number" class="qty-update" value="${parseFloat(item.quantity || 0)}" 
                                   min="0.5" step="0.5" data-id="${escapeHtml(item.id)}"
                                   style="width:70px; display:inline-block; background:rgba(0,0,0,0.3); 
                                   border:1px solid rgba(255,255,255,0.1); color:#fff; padding:6px 10px; 
                                   border-radius:8px; text-align:center; font-size:0.95rem; margin: 0 4px;">
                            kg
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:15px;">
                        <span style="color:var(--success); font-weight:700; font-size:1.1rem;">
                            ${itemTotal.toLocaleString()} so'm
                        </span>
                        <button class="remove-btn" data-id="${escapeHtml(item.id)}" 
                                style="color:var(--danger); background:rgba(239, 68, 68, 0.1); 
                                border:1px solid var(--danger); width:36px; height:36px; border-radius:8px; 
                                cursor:pointer; transition:all 0.3s; display:flex; align-items:center; 
                                justify-content:center;" aria-label="O'chirish">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;

                const qtyInput = div.querySelector('.qty-update');
                if (qtyInput) {
                    qtyInput.addEventListener('change', (e) => {
                        const newQty = parseFloat(e.target.value);
                        if (newQty <= 0) {
                            removeFromCart(item.id);
                        } else {
                            updateQuantity(item.id, newQty);
                        }
                    });
                }

                const removeBtn = div.querySelector('.remove-btn');
                if (removeBtn) {
                    removeBtn.addEventListener('click', () => removeFromCart(item.id));
                }

                cartItemsContainer.appendChild(div);
            });
        }

        if (cartTotalEl) {
            cartTotalEl.textContent = total.toLocaleString();
        }
    }

    // Checkout
    if (orderForm) {
        orderForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (cart.length === 0) {
                showNotification('Savatingiz bo\'sh!', 'warning');
                return;
            }

            if (!orderForm.checkValidity()) {
                orderForm.reportValidity();
                return;
            }

            const formData = new FormData(orderForm);
            const orderData = {
                name: formData.get('full_name') || '',
                phone: formData.get('phone') || '',
                region: formData.get('region') || 'Toshkent',
                district: formData.get('district') || 'Shahar',
                address: formData.get('address') || '',
                payment: formData.get('payment_method') || 'cash',
                notes: formData.get('notes') || '',
                items: cart.map(item => ({
                    id: item.id,
                    quantity: parseFloat(item.quantity || 0),
                    name: item.name
                }))
            };

            const btn = checkoutBtn;
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Yuborilmoqda...';
            btn.disabled = true;

            try {
                const response = await fetch('/store/api/order/create/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(orderData)
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    showNotification(`✅ Buyurtma qabul qilindi! ID: #${result.data?.order_id || 'OK'}`, 'success');
                    cart = [];
                    saveCart();
                    renderCart();
                    closeModal();
                    orderForm.reset();
                } else {
                    throw new Error(result.message || 'Server xatosi');
                }
            } catch (error) {
                showNotification(`❌ Xatolik: ${error.message || 'Iltimos qayta urinib ko\'ring'}`, 'error');
            } finally {
                btn.innerHTML = originalHTML;
                btn.disabled = false;
            }
        });
    }

    updateBadge();
}

/* ==========================================
   FAQ
   ========================================== */
function initFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        if (question) {
            question.addEventListener('click', () => {
                item.classList.toggle('active');
            });
        }
    });
}

/* ==========================================
   ANIMATIONS
   ========================================== */
function initAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.service-card, .product-card, .testimonial-card, .mission-card, .value-card, .team-card, .stat-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(el);
    });
}

/* ==========================================
   NOTIFICATIONS
   ========================================== */
function showNotification(message, type = 'info') {
    const existing = document.querySelectorAll('.notification');
    existing.forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    const colors = {
        success: 'var(--success)',
        error: 'var(--danger)',
        warning: 'var(--warning)',
        info: 'var(--primary)'
    };

    notification.innerHTML = `
        <i class="fas ${icons[type] || icons.info}" style="color: ${colors[type] || colors.info}; font-size: 1.3rem;"></i>
        <span>${escapeHtml(message)}</span>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
        z-index: 3000;
        max-width: 400px;
        animation: slideInRight 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.4s';
        setTimeout(() => notification.remove(), 400);
    }, 4000);
}

// Add animations
if (!document.getElementById('notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

/* ==========================================
   UTILITIES
   ========================================== */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#' || href === '#!') return;
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            const offsetTop = target.offsetTop - 80;
            window.scrollTo({ top: offsetTop, behavior: 'smooth' });
        }
    });
});


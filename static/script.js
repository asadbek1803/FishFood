// Sea FoodISH - Main JavaScript File with Backend Integration

// Global variables
let cart = JSON.parse(localStorage.getItem('seafoodish_cart')) || [];
let currentSlide = 0;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sea FoodISH - Website loaded! 🐟');
    
    // Initialize cart
    updateCartBadge();
    updateCartModal();
    
    // Initialize slider
    initializeSlider();
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Initialize intersection observer for animations
    initializeAnimations();
    
    // Navbar scroll effect
    initializeNavbarScroll();
});

// Get CSRF token for Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize slider
function initializeSlider() {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.slider-dot');
    
    if (slides.length === 0) return;
    
    // Set first slide as active
    slides[0].classList.add('active');
    if (dots.length > 0) dots[0].classList.add('active');
    
    // Add click events to dots
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            changeSlide(index);
        });
    });
    
    // Auto slide every 5 seconds
    setInterval(() => {
        changeSlide((currentSlide + 1) % slides.length);
    }, 5000);
}

// Change slide
function changeSlide(index) {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.slider-dot');
    
    if (!slides.length) return;
    
    // Remove active class from current slide
    slides[currentSlide].classList.remove('active');
    if (dots.length > 0) dots[currentSlide].classList.remove('active');
    
    // Update current slide index
    currentSlide = index;
    
    // Add active class to new slide
    slides[currentSlide].classList.add('active');
    if (dots.length > 0) dots[currentSlide].classList.add('active');
    
    // Add animation
    slides[currentSlide].style.animation = 'fadeIn 0.8s ease-in-out';
    setTimeout(() => {
        slides[currentSlide].style.animation = '';
    }, 800);
}

// Update cart badge
function updateCartBadge() {
    const badge = document.getElementById('cartBadge');
    if (badge) {
        const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
        badge.textContent = totalItems.toFixed(1);
        badge.style.display = totalItems > 0 ? 'flex' : 'none';
    }
}

// Increase quantity
function increaseQty(id) {
    const input = document.getElementById(`quantity_${id}`);
    if (input) {
        let currentValue = parseFloat(input.value) || 1;
        input.value = (currentValue + 0.5).toFixed(1);
    }
}

// Decrease quantity
function decreaseQty(id) {
    const input = document.getElementById(`quantity_${id}`);
    if (input) {
        let currentValue = parseFloat(input.value) || 1;
        if (currentValue > 0.5) {
            input.value = (currentValue - 0.5).toFixed(1);
        }
    }
}

// Add product to cart (for shop page)
function addProductToCart(productId) {
    const quantityInput = document.getElementById(`quantity_${productId}`);
    const quantity = parseFloat(quantityInput?.value) || 1;
    
    // Get product info from data attribute
    const productElement = document.querySelector(`[data-product-id="${productId}"]`);
    if (!productElement) {
        showMessage('Mahsulot topilmadi', 'error');
        return;
    }
    
    const productName = productElement.dataset.productName;
    const productPrice = parseFloat(productElement.dataset.productPrice);
    
    if (!productName || !productPrice) {
        showMessage('Mahsulot ma\'lumotlari topilmadi', 'error');
        return;
    }
    
    // Check if product already in cart
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            id: productId,
            name: productName,
            price: productPrice,
            quantity: quantity
        });
    }
    
    // Save to localStorage
    localStorage.setItem('seafoodish_cart', JSON.stringify(cart));
    
    // Update badge and cart
    updateCartBadge();
    updateCartModal();
    
    // Show success message
    showMessage(`${productName} (${quantity} kg) savatga qo'shildi!`, 'success');
    
    // Reset quantity
    if (quantityInput) {
        quantityInput.value = 1;
    }
    
    // Animation
    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
        cartIcon.style.transform = 'scale(1.2)';
        setTimeout(() => {
            cartIcon.style.transform = 'scale(1)';
        }, 300);
    }
}

// Remove from cart
function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    localStorage.setItem('seafoodish_cart', JSON.stringify(cart));
    updateCartBadge();
    updateCartModal();
    showMessage('Mahsulot savatdan olib tashlandi', 'info');
}

// Update cart quantity
function updateCartQuantity(productId, newQuantity) {
    if (newQuantity < 0.5) {
        removeFromCart(productId);
        return;
    }
    
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = parseFloat(newQuantity.toFixed(1));
        localStorage.setItem('seafoodish_cart', JSON.stringify(cart));
        updateCartBadge();
        updateCartModal();
    }
}

// Open cart modal
function openCart() {
    const modal = document.getElementById('cartModal');
    if (modal) {
        updateCartModal();
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Add animation
        const content = modal.querySelector('.order-content');
        if (content) {
            content.style.animation = 'modalAppear 0.3s ease-out';
        }
    }
}

// Close cart modal
function closeCart() {
    const modal = document.getElementById('cartModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
}

// Update cart modal
function updateCartModal() {
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    if (!cartItems) return;
    
    if (cart.length === 0) {
        cartItems.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-shopping-cart fa-3x"></i>
                <h4>Savat bo'sh</h4>
                <p>Savatga mahsulot qo'shing</p>
            </div>
        `;
        if (cartTotal) cartTotal.textContent = '0';
        return;
    }
    
    let total = 0;
    cartItems.innerHTML = '';
    
    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        const itemHTML = `
            <div class="cart-item" data-item-id="${item.id}">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">${item.price.toLocaleString()} so'm x ${item.quantity} kg</div>
                </div>
                <div class="cart-item-quantity">
                    <button onclick="updateCartQuantity('${item.id}', ${item.quantity - 0.5})">-</button>
                    <span>${item.quantity.toFixed(1)}</span>
                    <button onclick="updateCartQuantity('${item.id}', ${item.quantity + 0.5})">+</button>
                </div>
                <div class="cart-item-total">${itemTotal.toLocaleString()} so'm</div>
                <button class="cart-item-remove" onclick="removeFromCart('${item.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        cartItems.innerHTML += itemHTML;
    });
    
    if (cartTotal) cartTotal.textContent = total.toLocaleString();
}

// Checkout function
function checkout() {
    const cart = JSON.parse(localStorage.getItem('seafoodish_cart')) || [];
    if (cart.length === 0) {
        showMessage('Savat bo\'sh. Iltimos, mahsulot tanlang.', 'error');
        return;
    }
    
    // Create and show checkout modal
    const checkoutModal = document.getElementById('checkoutModal') || createCheckoutModal();
    checkoutModal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

// Create checkout modal with region selection
function createCheckoutModal() {
    const modalHTML = `
        <div class="order-modal" id="checkoutModal">
            <div class="order-content">
                <h3><i class="fas fa-receipt"></i> Buyurtma berish</h3>
                <form id="checkoutForm">
                    <div class="form-group">
                        <label for="fullName">To'liq ism *</label>
                        <input type="text" id="fullName" required placeholder="Ism va familiyangiz">
                    </div>
                    <div class="form-group">
                        <label for="phone">Telefon raqam *</label>
                        <input type="tel" id="phone" required placeholder="+998 XX XXX XX XX">
                    </div>
                    
                    <div class="form-group">
                        <label for="region">Viloyat *</label>
                        <select id="region" required onchange="updateDistricts()">
                            <option value="">Viloyatni tanlang</option>
                            <option value="Toshkent shahri">Toshkent shahri</option>
                            <option value="Toshkent viloyati">Toshkent viloyati</option>
                            <option value="Samarqand">Samarqand</option>
                            <option value="Buxoro">Buxoro</option>
                            <option value="Andijon">Andijon</option>
                            <option value="Farg'ona">Farg'ona</option>
                            <option value="Namangan">Namangan</option>
                            <option value="Sirdaryo">Sirdaryo</option>
                            <option value="Jizzax">Jizzax</option>
                            <option value="Surxondaryo">Surxondaryo</option>
                            <option value="Qashqadaryo">Qashqadaryo</option>
                            <option value="Navoiy">Navoiy</option>
                            <option value="Xorazm">Xorazm</option>
                            <option value="Qoraqalpog'iston">Qoraqalpog'iston</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="district">Tuman / Shahar *</label>
                        <select id="district" required>
                            <option value="">Avval viloyatni tanlang</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="address">To'liq manzil *</label>
                        <textarea id="address" required rows="3" placeholder="Ko'cha, uy, xonadon raqami"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="payment">To'lov usuli *</label>
                        <select id="payment" required>
                            <option value="">Tanlang</option>
                            <option value="cash">Naqd pul</option>
                            <option value="card">Karta orqali</option>
                            <option value="click">Click</option>
                            <option value="payme">Payme</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="notes">Qo'shimcha izoh (ixtiyoriy)</label>
                        <textarea id="notes" rows="2" placeholder="Yetkazib berish haqida qo'shimcha ma'lumot"></textarea>
                    </div>
                    
                    <div class="cart-summary">
                        <div id="checkoutItems"></div>
                        <div class="total-price">
                            Jami: <span id="checkoutTotal">0</span> so'm
                        </div>
                    </div>
                    
                    <button type="submit" class="btn-submit">
                        <i class="fas fa-check"></i> Buyurtmani tasdiqlash
                    </button>
                    <button type="button" class="btn-close-modal" onclick="closeCheckout()">
                        <i class="fas fa-times"></i> Bekor qilish
                    </button>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Update checkout items
    updateCheckoutItems();
    
    // Add form submit event
    const form = document.getElementById('checkoutForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitOrder();
    });
    
    return document.getElementById('checkoutModal');
}

// Uzbekistan districts data
const districtsData = {
    "Toshkent shahri": ["Yunusobod", "Mirzo Ulug'bek", "Yakkasaroy", "Shayxontohur", "Olmazor", "Bektemir", "Mirobod", "Sergeli", "Chilonzor", "Uchtepa", "Yang hayot", "Mirabad"],
    "Toshkent viloyati": ["Angren", "Bekobod", "Olmaliq", "Chirchiq", "Yangiyo'l", "O'rtachirchiq", "Piskent", "Parkent", "Ohangaron", "Quyi chirchiq", "Zangiota", "Qibray", "Yuqori chirchiq", "Bo'stonliq", "Bo'ka"],
    "Samarqand": ["Samarqand shahri", "Kattaqo'rg'on", "Urgut", "Bulung'ur", "Jomboy", "Ishtixon", "Payariq", "Pastdarg'om", "Toyloq", "Oqdaryo", "Nurobod", "Narpay", "Qo'shrabot"],
    "Buxoro": ["Buxoro shahri", "Kogon", "Romitan", "Vobkent", "Jondor", "Shofirkon", "Qorako'l", "Peshku", "G'ijduvon", "Qorovulbozor"],
    "Andijon": ["Andijon shahri", "Xonobod", "Asaka", "Shahrixon", "Qo'rg'ontepa", "Baliqchi", "Oltinko'l", "Jalaquduq", "Izboskan", "Paxtaobod", "Marhamat", "Buloqboshi", "Xo'jaobod"],
    "Farg'ona": ["Farg'ona shahri", "Marg'ilon", "Quva", "Quvasoy", "Rishton", "Beshariq", "O'zbekiston", "Bog'dod", "Dang'ara", "Furqat", "Qo'shtepa", "Yozyovon", "Uchko'prik", "So'x", "Toshloq"],
    "Namangan": ["Namangan shahri", "Kosonsoy", "Chortoq", "Chust", "Pop", "To'raqo'rg'on", "Uchqo'rg'on", "Mingbuloq", "Norin", "Yangiqo'rg'on"],
    "Sirdaryo": ["Guliston", "Yangiyer", "Sayxunobod", "Sardoba", "Boyovut", "Xovos", "Oqoltin", "Sirdaryo", "Mirzaobod", "Shirin"],
    "Jizzax": ["Jizzax shahri", "Gagarin", "Do'stlik", "Paxtakor", "Forish", "Baxmal", "Zarbdor", "Zafarobod", "Zomin", "Mirzacho'l", "Yangiobod"],
    "Surxondaryo": ["Termiz", "Denov", "Sherobod", "Sho'rchi", "Qumqo'rg'on", "Jarqo'rg'on", "Angor", "Bandixon", "Boysun", "Muzrabot", "Oltinsoy", "Sariosiyo", "Uzun"],
    "Qashqadaryo": ["Qarshi", "Shahrisabz", "Kitob", "Koson", "Muborak", "Mirishkor", "Nishon", "Kasbi", "Chiroqchi", "Dehqonobod", "Ko'kdala", "Yakkabog'", "G'uzor", "Qamashi"],
    "Navoiy": ["Navoiy shahri", "Zarafshon", "Uchquduq", "Qiziltepa", "Tomdi", "Xatirchi", "Nurota", "Konimex", "Navbahor"],
    "Xorazm": ["Urganch", "Xiva", "Bog'ot", "Gurlan", "Shovot", "Xonqa", "Hazorasp", "Yangibozor", "Qo'shkupir", "Tuproqqala"],
    "Qoraqalpog'iston": ["Nukus", "Xo'jayli", "Qo'ng'irot", "Chimboy", "Taxtako'pir", "To'rtko'l", "Beruniy", "Mo'ynoq", "Qorao'zak", "Ellikqala"]
};

// Update districts based on selected region
function updateDistricts() {
    const regionSelect = document.getElementById('region');
    const districtSelect = document.getElementById('district');
    const selectedRegion = regionSelect.value;
    
    districtSelect.innerHTML = '<option value="">Tuman / shaharni tanlang</option>';
    
    if (selectedRegion && districtsData[selectedRegion]) {
        districtsData[selectedRegion].forEach(district => {
            const option = document.createElement('option');
            option.value = district;
            option.textContent = district;
            districtSelect.appendChild(option);
        });
    } else {
        districtSelect.innerHTML = '<option value="">Avval viloyatni tanlang</option>';
    }
}

// Update checkout items
function updateCheckoutItems() {
    const checkoutItems = document.getElementById('checkoutItems');
    const checkoutTotal = document.getElementById('checkoutTotal');
    
    if (!checkoutItems) return;
    
    const cart = JSON.parse(localStorage.getItem('seafoodish_cart')) || [];
    
    let total = 0;
    checkoutItems.innerHTML = '';
    
    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        checkoutItems.innerHTML += `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">${item.quantity} kg x ${item.price.toLocaleString()} so'm</div>
                </div>
                <div class="cart-item-total">${itemTotal.toLocaleString()} so'm</div>
            </div>
        `;
    });
    
    if (checkoutTotal) checkoutTotal.textContent = total.toLocaleString();
}

// Close checkout modal
function closeCheckout() {
    const modal = document.getElementById('checkoutModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
}

// Submit order - BACKEND bilan integratsiya
// submitOrder() — 100% ishlaydigan versiya (2025-yil uchun)
async function submitOrder() {
    const fullName = document.getElementById('fullName').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const region = document.getElementById('region').value;
    const district = document.getElementById('district').value;
    const address = document.getElementById('address').value.trim();
    const payment = document.getElementById('payment').value;
    const notes = document.getElementById('notes').value.trim();

    // Validatsiya
    if (!fullName || !phone || !region || !district || !address || !payment) {
        showMessage('Barcha majburiy maydonlarni to\'ldiring!', 'error');
        return;
    }

    const cleanPhone = phone.replace(/\D/g, '');
    if (cleanPhone.length < 9 || cleanPhone.length > 12) {
        showMessage('Telefon raqam noto\'g\'ri!', 'error');
        return;
    }

    const cart = JSON.parse(localStorage.getItem('seafoodish_cart')) || [];
    if (cart.length === 0) {
        showMessage('Savat bo\'sh!', 'error');
        return;
    }

    const orderData = {
        name: fullName,
        phone: cleanPhone,
        region: region,
        district: district,
        address: address,
        payment: payment,
        notes: notes,
        items: cart.map(item => ({
            id: parseInt(item.id),
            quantity: parseFloat(item.quantity)
        }))
    };

    const submitBtn = document.querySelector('#checkoutForm .btn-submit');
    const original = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Jo\'natilmoqda...';
    submitBtn.disabled = true;

    try {
        const response = await fetch('/store/api/order/create/', {  // ← TO‘G‘RI URL!
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') || '',  // ← CSRF muhim!
            },
            body: JSON.stringify(orderData)
        });

        const data = await response.json();

        submitBtn.innerHTML = original;
        submitBtn.disabled = false;

        if (response.ok) {
            localStorage.removeItem('seafoodish_cart');
            updateCartBadge();
            closeCheckout();
            showMessage(`Buyurtma qabul qilindi! Raqami: ${data.data?.order_id || '—'}`, 'success');
        } else {
            showMessage(data.message || 'Xatolik yuz berdi', 'error');
        }
    } catch (err) {
        submitBtn.innerHTML = original;
        submitBtn.disabled = false;
        console.error('Fetch xatosi:', err);
        showMessage('Serverga ulanib bo‘lmadi. URL yoki internetni tekshiring!', 'error');
    }
}

// Show message
function showMessage(text, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    const message = document.createElement('div');
    message.className = `message ${type}-message`;
    
    // Icon based on type
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    message.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${text.replace(/\n/g, '<br>')}</span>
    `;
    
    document.body.appendChild(message);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => message.remove(), 300);
    }, 4000);
}

// Initialize event listeners
function initializeEventListeners() {
    // Cart icon click
    const cartIcon = document.getElementById('cartIcon');
    if (cartIcon) {
        cartIcon.addEventListener('click', openCart);
    }
    
    // Close cart button
    const closeCartBtn = document.getElementById('closeCartBtn');
    if (closeCartBtn) {
        closeCartBtn.addEventListener('click', closeCart);
    }
    
    // Checkout button
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', checkout);
    }
    
    // Close modal when clicking outside
    document.addEventListener('click', function(e) {
        const cartModal = document.getElementById('cartModal');
        const checkoutModal = document.getElementById('checkoutModal');
        
        if (cartModal && cartModal.classList.contains('show') && 
            e.target === cartModal) {
            closeCart();
        }
        
        if (checkoutModal && checkoutModal.classList.contains('show') && 
            e.target === checkoutModal) {
            closeCheckout();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeCart();
            closeCheckout();
        }
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
            this.classList.toggle('active');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!mobileMenu.contains(e.target) && 
                !mobileMenuBtn.contains(e.target) && 
                mobileMenu.classList.contains('show')) {
                mobileMenu.classList.remove('show');
                mobileMenuBtn.classList.remove('active');
            }
        });
    }
}

// Initialize animations
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.fade-in, .slide-up, .scale-in').forEach(el => {
        observer.observe(el);
    });
}

// Initialize navbar scroll effect
function initializeNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 50) {
            navbar.classList.add('scrolled');
            
            if (scrollTop > lastScrollTop) {
                // Scroll down
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scroll up
                navbar.style.transform = 'translateY(0)';
            }
        } else {
            navbar.classList.remove('scrolled');
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
}

window.increaseQty = increaseQty;
window.decreaseQty = decreaseQty;
window.addProductToCart = addProductToCart;
window.removeFromCart = removeFromCart;
window.updateCartQuantity = updateCartQuantity;
window.openCart = openCart;
window.closeCart = closeCart;
window.checkout = checkout;
window.closeCheckout = closeCheckout;
window.changeSlide = changeSlide;
window.updateDistricts = updateDistricts;
window.updateCheckoutItems = updateCheckoutItems;
window.submitOrder = submitOrder;
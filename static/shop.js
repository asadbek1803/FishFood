// Shop page specific JavaScript

// Cart operations

// shop.js faylining eng boshiga qoʻshing (boshqa kodlardan oldin)
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

function increaseQty(id) {
    const input = document.getElementById(`quantity_${id}`);
    if (input) {
        let currentValue = parseFloat(input.value) || 1;
        input.value = (currentValue + 0.5).toFixed(1);
    }
}

function decreaseQty(id) {
    const input = document.getElementById(`quantity_${id}`);
    if (input) {
        let currentValue = parseFloat(input.value) || 1;
        if (currentValue > 0.5) {
            input.value = (currentValue - 0.5).toFixed(1);
        }
    }
}

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
    
    // Get cart from localStorage or initialize
    let cart = JSON.parse(localStorage.getItem('seafoodish_cart')) || [];
    
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
    
    // Update badge
    updateCartBadge();
    
    // Show success message
    showMessage(`${productName} (${quantity} kg) savatga qo'shildi!`, 'success');
    
    // Reset quantity
    if (quantityInput) {
        quantityInput.value = 1;
    }
}

// Update cart badge
function updateCartBadge() {
    const badge = document.getElementById('cartBadge');
    if (badge) {
        const cart = JSON.parse(localStorage.getItem('seafoodish_cart')) || [];
        const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
        badge.textContent = totalItems.toFixed(1);
        badge.style.display = totalItems > 0 ? 'flex' : 'none';
    }
}

// Show message
function showMessage(text, type = 'info') {
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    const message = document.createElement('div');
    message.className = `message ${type}-message`;
    message.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${text}</span>
    `;
    
    document.body.appendChild(message);
    setTimeout(() => message.remove(), 3000);
}

// Open cart modal
function openCart() {
    const modal = document.getElementById('cartModal');
    if (modal) {
        updateCartModal();
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
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
    
    const cart = JSON.parse(localStorage.getItem('seafoodish_cart')) || [];
    
    if (cart.length === 0) {
        cartItems.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-shopping-cart"></i>
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
                    <button class="decrease-cart-item" data-id="${item.id}">-</button>
                    <span>${item.quantity}</span>
                    <button class="increase-cart-item" data-id="${item.id}">+</button>
                </div>
                <div class="cart-item-total">${itemTotal.toLocaleString()} so'm</div>
                <button class="cart-item-remove" data-id="${item.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        cartItems.innerHTML += itemHTML;
    });
    
    if (cartTotal) cartTotal.textContent = total.toLocaleString();
    
    // Add event listeners to cart item buttons
    document.querySelectorAll('.decrease-cart-item').forEach(btn => {
        btn.addEventListener('click', function() {
            updateCartItemQuantity(this.dataset.id, -0.5);
        });
    });
    
    document.querySelectorAll('.increase-cart-item').forEach(btn => {
        btn.addEventListener('click', function() {
            updateCartItemQuantity(this.dataset.id, 0.5);
        });
    });
    
    document.querySelectorAll('.cart-item-remove').forEach(btn => {
        btn.addEventListener('click', function() {
            removeFromCart(this.dataset.id);
        });
    });
}

// Update cart item quantity
function updateCartItemQuantity(productId, change) {
    let cart = JSON.parse(localStorage.getItem('seafoodish_cart')) || [];
    const item = cart.find(item => item.id == productId);
    
    if (item) {
        item.quantity = parseFloat(item.quantity) + change;
        
        if (item.quantity < 0.5) {
            cart = cart.filter(item => item.id != productId);
            showMessage('Mahsulot savatdan olib tashlandi', 'info');
        } else {
            item.quantity = parseFloat(item.quantity.toFixed(1));
        }
        
        localStorage.setItem('seafoodish_cart', JSON.stringify(cart));
        updateCartBadge();
        updateCartModal();
    }
}

// Remove from cart
function removeFromCart(productId) {
    let cart = JSON.parse(localStorage.getItem('seafoodish_cart')) || [];
    cart = cart.filter(item => item.id != productId);
    localStorage.setItem('seafoodish_cart', JSON.stringify(cart));
    updateCartBadge();
    updateCartModal();
    showMessage('Mahsulot savatdan olib tashlandi', 'info');
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

// Submit order - BACKEND bilan bog'lanish
// submitOrder() — 100% ishlaydigan versiya (2025-yil uchun)
async function submitOrder() {
    const fullName = document.getElementById('fullName').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const region = document.getElementById('region').value;
    const district = document.getElementById('district').value;
    const address = document.getElementById('address').value.trim();
    const payment = document.getElementById('payment').value;
    const notes = document.getElementById('notes')?.value.trim() || '';

    if (!fullName || !phone || !region || !district || !address || !payment) {
        showMessage('Barcha majburiy maydonlarni to\'ldiring!', 'error');
        return;
    }

    const cleanPhone = phone.replace(/\D/g, '');
    if (cleanPhone.length < 9) {
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
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Jo\'natilmoqda...';
    submitBtn.disabled = true;

    try {
        // CSRF tokenni olish (ikkala usul bilan)
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                         (document.cookie.split('; ').find(row => row.startsWith('csrftoken=')) || '=')?.split('=')[1];

        const response = await fetch('/store/api/order/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken || ''
            },
            body: JSON.stringify(orderData)
        });

        const data = await response.json();

        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;

        if (response.ok) {
            localStorage.removeItem('seafoodish_cart');
            updateCartBadge();
            updateCartModal();
            closeCheckout();

            showMessage(`
                Buyurtma qabul qilindi!<br>
                Raqami: <b>${data.data?.order_id || '—'}</b><br>
                Tez orada siz bilan bog'lanamiz
            `, 'success');

            setTimeout(() => {
                const modal = document.getElementById('checkoutModal');
                if (modal) modal.remove();
            }, 1000);
        } else {
            showMessage(data.message || 'Xatolik yuz berdi', 'error');
        }
    } catch (err) {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        console.error('Buyurtma yuborishda xato:', err);
        showMessage('Serverga ulanib bo\'lmadi. Internetni tekshiring!', 'error');
    }
}
// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Shop page loaded! 🛒');
    
    // Initialize cart badge
    updateCartBadge();
    updateCartModal();
    
    // Category filter
    const filterButtons = document.querySelectorAll('.btn-filter');
    const productItems = document.querySelectorAll('.product-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const categoryId = this.dataset.category;
            
            productItems.forEach(item => {
                if (categoryId === 'all' || item.dataset.category === categoryId) {
                    item.style.display = 'block';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                    }, 10);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
    
    // Quantity buttons
    document.querySelectorAll('.increase-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            increaseQty(this.dataset.id);
        });
    });
    
    document.querySelectorAll('.decrease-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            decreaseQty(this.dataset.id);
        });
    });
    
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            addProductToCart(this.dataset.id);
        });
    });
    
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
        
        if (cartModal && cartModal.classList.contains('show') && e.target === cartModal) {
            closeCart();
        }
        
        if (checkoutModal && checkoutModal.classList.contains('show') && e.target === checkoutModal) {
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
});
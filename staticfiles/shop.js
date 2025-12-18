/* ==========================================
   SHOP PAGE SCRIPT - CLEAN CODE 2025
   ========================================== */

document.addEventListener('DOMContentLoaded', () => {
    initShopFilters();
    initSearch();
    initSort();
});

/* ==========================================
   CATEGORY FILTERS
   ========================================== */
function initShopFilters() {
    const filterBtns = document.querySelectorAll('.category-btn');
    const productCards = document.querySelectorAll('.product-card');

    if (!filterBtns.length || !productCards.length) return;

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const category = this.getAttribute('data-category');

            productCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');

                if (category === 'all' || cardCategory === category) {
                    card.style.display = '';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.offsetHeight; // Trigger reflow
                    requestAnimationFrame(() => {
                        card.style.transition = 'all 0.5s ease-out';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    });
                } else {
                    card.style.transition = 'all 0.3s ease-out';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
}

/* ==========================================
   SEARCH
   ========================================== */
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    let searchTimeout;

    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimeout);

        searchTimeout = setTimeout(() => {
            const query = this.value.toLowerCase().trim();
            const productCards = document.querySelectorAll('.product-card');

            if (!query) {
                productCards.forEach(card => {
                    card.style.display = '';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                });
                return;
            }

            productCards.forEach(card => {
                const name = (card.getAttribute('data-product-name') || '').toLowerCase();
                const text = card.textContent.toLowerCase();

                if (name.includes(query) || text.includes(query)) {
                    card.style.display = '';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.offsetHeight; // Trigger reflow
                    requestAnimationFrame(() => {
                        card.style.transition = 'all 0.4s ease-out';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    });
                } else {
                    card.style.transition = 'all 0.3s ease-out';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        }, 300);
    });

    // Clear on escape
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            this.dispatchEvent(new Event('input'));
        }
    });
}

/* ==========================================
   SORT
   ========================================== */
function initSort() {
    const sortSelect = document.getElementById('sortSelect');
    if (!sortSelect) return;

    sortSelect.addEventListener('change', function () {
        const value = this.value;
        const grid = document.getElementById('productsGrid');
        if (!grid) return;

        const cards = Array.from(document.querySelectorAll('.product-card:not([style*="display: none"])'));

        if (cards.length === 0) return;

        cards.sort((a, b) => {
            const priceA = parseFloat(a.getAttribute('data-product-price')) || 0;
            const priceB = parseFloat(b.getAttribute('data-product-price')) || 0;
            const nameA = (a.getAttribute('data-product-name') || '').toLowerCase();
            const nameB = (b.getAttribute('data-product-name') || '').toLowerCase();

            switch (value) {
                case 'price-asc':
                    return priceA - priceB;
                case 'price-desc':
                    return priceB - priceA;
                case 'name-asc':
                    return nameA.localeCompare(nameB, 'uz');
                case 'name-desc':
                    return nameB.localeCompare(nameA, 'uz');
                default:
                    return 0;
            }
        });

        // Animate sorted cards
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.4s ease-out';

            setTimeout(() => {
                grid.appendChild(card);
                requestAnimationFrame(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                });
            }, index * 50);
        });
    });
}


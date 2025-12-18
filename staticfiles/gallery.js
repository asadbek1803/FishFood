/* ==========================================
   GALLERY PAGE SCRIPT - CLEAN CODE 2025
   ========================================== */

document.addEventListener('DOMContentLoaded', () => {
    initGalleryFilters();
    initGalleryItems();
    initModals();
});

/* ==========================================
   GALLERY FILTERS
   ========================================== */
function initGalleryFilters() {
    const filterBtns = document.querySelectorAll('.gallery-filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');

    if (!filterBtns.length || !galleryItems.length) return;

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const category = this.getAttribute('data-category');

            galleryItems.forEach(item => {
                const itemCategory = item.getAttribute('data-category') || 'all';

                if (category === 'all' || itemCategory === category) {
                    item.style.display = '';
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    item.offsetHeight; // Trigger reflow
                    requestAnimationFrame(() => {
                        item.style.transition = 'all 0.5s ease-out';
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                    });
                } else {
                    item.style.transition = 'all 0.3s ease-out';
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
}

/* ==========================================
   GALLERY ITEMS CLICK
   ========================================== */
function initGalleryItems() {
    const galleryCards = document.querySelectorAll('.gallery-card');

    galleryCards.forEach(card => {
        card.addEventListener('click', function () {
            const item = this.closest('.gallery-item');
            const mediaType = item.getAttribute('data-media-type');
            const mediaUrl = item.getAttribute('data-media-url');

            if (!mediaUrl) return;

            if (mediaType === 'video') {
                openVideoModal(mediaUrl);
            } else {
                openImageModal(mediaUrl, item.querySelector('img')?.alt || 'Image');
            }
        });
    });
}

/* ==========================================
   MODALS
   ========================================== */
function initModals() {
    const videoModal = document.getElementById('videoModal');
    const imageModal = document.getElementById('imageModal');
    const videoClose = document.querySelector('.video-modal-close');
    const imageClose = document.querySelector('.image-modal-close');

    // Close video modal
    if (videoClose) {
        videoClose.addEventListener('click', () => closeVideoModal());
    }

    if (videoModal) {
        videoModal.addEventListener('click', (e) => {
            if (e.target === videoModal) closeVideoModal();
        });
    }

    // Close image modal
    if (imageClose) {
        imageClose.addEventListener('click', () => closeImageModal());
    }

    if (imageModal) {
        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal) closeImageModal();
        });
    }

    // Close on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeVideoModal();
            closeImageModal();
        }
    });
}

function openVideoModal(url) {
    const videoModal = document.getElementById('videoModal');
    const videoContainer = document.getElementById('videoContainer');

    if (!videoModal || !videoContainer) return;

    // Clear previous content
    videoContainer.innerHTML = '';

    // Check if it's a YouTube/Vimeo URL or direct video file
    if (url.includes('youtube.com') || url.includes('youtu.be') || url.includes('vimeo.com')) {
        // YouTube/Vimeo embed
        let embedUrl = url;
        
        if (url.includes('youtube.com/watch?v=')) {
            const videoId = url.split('v=')[1].split('&')[0];
            embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
        } else if (url.includes('youtu.be/')) {
            const videoId = url.split('youtu.be/')[1].split('?')[0];
            embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
        } else if (url.includes('vimeo.com/')) {
            const videoId = url.split('vimeo.com/')[1].split('?')[0];
            embedUrl = `https://player.vimeo.com/video/${videoId}?autoplay=1`;
        }

        const iframe = document.createElement('iframe');
        iframe.src = embedUrl;
        iframe.allow = 'autoplay; fullscreen';
        iframe.allowFullscreen = true;
        videoContainer.appendChild(iframe);
    } else {
        // Direct video file
        const video = document.createElement('video');
        video.src = url;
        video.controls = true;
        video.autoplay = true;
        video.style.width = '100%';
        video.style.height = '100%';
        videoContainer.appendChild(video);
    }

    videoModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeVideoModal() {
    const videoModal = document.getElementById('videoModal');
    const videoContainer = document.getElementById('videoContainer');

    if (videoModal) {
        videoModal.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (videoContainer) {
        // Stop video playback
        const video = videoContainer.querySelector('video');
        const iframe = videoContainer.querySelector('iframe');
        
        if (video) {
            video.pause();
            video.src = '';
        }
        
        if (iframe) {
            iframe.src = '';
        }
        
        videoContainer.innerHTML = '';
    }
}

function openImageModal(url, alt) {
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');

    if (!imageModal || !modalImage) return;

    modalImage.src = url;
    modalImage.alt = alt || 'Image';
    imageModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeImageModal() {
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');

    if (imageModal) {
        imageModal.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (modalImage) {
        modalImage.src = '';
    }
}


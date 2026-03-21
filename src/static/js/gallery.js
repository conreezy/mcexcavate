(function () {
    function initializeGallery(viewer) {
        const mainImage = viewer.querySelector('[data-gallery-main-image]');
        const track = viewer.querySelector('[data-gallery-track]');
        const previousButton = viewer.querySelector('[data-gallery-prev]');
        const nextButton = viewer.querySelector('[data-gallery-next]');
        const thumbnails = Array.from(viewer.querySelectorAll('[data-gallery-thumbnail]'));
        const visibleThumbnails = 3;

        if (!mainImage || !track || !thumbnails.length) {
            return;
        }

        let activeIndex = Math.max(
            thumbnails.findIndex((thumbnail) => thumbnail.classList.contains('is-active')),
            0
        );

        function getGapSize() {
            const trackStyles = window.getComputedStyle(track);
            return parseFloat(trackStyles.columnGap || trackStyles.gap || '0');
        }

        function updateThumbnailWindow() {
            if (thumbnails.length <= visibleThumbnails) {
                track.style.transform = 'translateX(0)';
                return;
            }

            const thumbnailWidth = thumbnails[0].getBoundingClientRect().width;
            const offset = (thumbnailWidth + getGapSize()) * Math.min(
                Math.max(activeIndex - 1, 0),
                thumbnails.length - visibleThumbnails
            );

            track.style.transform = `translateX(-${offset}px)`;
        }

        function render() {
            const activeThumbnail = thumbnails[activeIndex];
            mainImage.src = activeThumbnail.dataset.imageUrl;
            mainImage.alt = activeThumbnail.dataset.imageAlt || '';

            thumbnails.forEach((thumbnail, index) => {
                const isActive = index === activeIndex;
                thumbnail.classList.toggle('is-active', isActive);
                thumbnail.setAttribute('aria-pressed', isActive ? 'true' : 'false');
            });

            updateThumbnailWindow();
        }

        if (previousButton) {
            previousButton.addEventListener('click', function () {
                activeIndex = (activeIndex - 1 + thumbnails.length) % thumbnails.length;
                render();
            });
        }

        if (nextButton) {
            nextButton.addEventListener('click', function () {
                activeIndex = (activeIndex + 1) % thumbnails.length;
                render();
            });
        }

        thumbnails.forEach((thumbnail) => {
            thumbnail.addEventListener('click', function () {
                activeIndex = Number(thumbnail.dataset.index || 0);
                render();
            });
        });

        window.addEventListener('resize', updateThumbnailWindow);
        render();
    }

    document.querySelectorAll('[data-gallery-viewer]').forEach(initializeGallery);
})();

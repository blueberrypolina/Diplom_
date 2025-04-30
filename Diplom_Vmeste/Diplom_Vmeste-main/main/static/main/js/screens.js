let currentScreenIndex = 0;
    const screens = document.querySelectorAll('.screen');
    const totalScreens = screens.length;
    let isAnimating = false;

    function updateScreens() {
        screens.forEach((screen, index) => {
            screen.classList.remove('active', 'prev', 'next');
            if (index === currentScreenIndex) {
                screen.classList.add('active');
            } else if (index < currentScreenIndex) {
                screen.classList.add('prev');
            } else {
                screen.classList.add('next');
            }
        });
    }

    function animateContent() {
        const activeScreen = screens[currentScreenIndex];
        const elements = activeScreen.querySelectorAll('.container, .wrapper');
        elements.forEach(el => el.classList.add('animated-text'));
    }

    function handleScroll(e) {
        if (isAnimating) return;

        const direction = Math.sign(e.deltaY);
        const newIndex = currentScreenIndex + direction;

        if (newIndex >= 0 && newIndex < totalScreens) {
            isAnimating = true;
            currentScreenIndex = newIndex;
            updateScreens();
            animateContent();

            setTimeout(() => {
                isAnimating = false;
            }, 800);
        }
    }
    // Initial setup
    updateScreens();
    animateContent();
    window.addEventListener('wheel', handleScroll);
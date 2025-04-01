document.addEventListener('DOMContentLoaded', () => {
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const mainNav = document.querySelector('.main-nav');

  // Mobile menu toggle
  mobileMenuToggle.addEventListener('click', () => {
    mainNav.classList.toggle('active');
    document.body.classList.toggle('menu-open');
    
    // Toggle hamburger animation
    mobileMenuToggle.classList.toggle('active');
    const spans = mobileMenuToggle.querySelectorAll('span');
    if (mobileMenuToggle.classList.contains('active')) {
      spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
    } else {
      spans[0].style.transform = 'none';
      spans[1].style.opacity = '1';
      spans[2].style.transform = 'none';
    }
  });

  // Close mobile menu when clicking outside
  document.addEventListener('click', (e) => {
    if (mainNav.classList.contains('active') && 
        !mainNav.contains(e.target) && 
        !mobileMenuToggle.contains(e.target)) {
      mainNav.classList.remove('active');
      document.body.classList.remove('menu-open');
      mobileMenuToggle.classList.remove('active');
      const spans = mobileMenuToggle.querySelectorAll('span');
      spans[0].style.transform = 'none';
      spans[1].style.opacity = '1';
      spans[2].style.transform = 'none';
    }
  });
}); 
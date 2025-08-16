// Theme toggle functionality for all pages

document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
});

function initializeTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Set initial theme
    setTheme(savedTheme);
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

function setTheme(theme) {
    const html = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');
    
    html.setAttribute('data-bs-theme', theme);
    
    if (theme === 'light') {
        themeToggle.innerHTML = '<i class="fas fa-moon me-2"></i>Dark Mode';
        document.body.classList.add('light-mode');
    } else {
        themeToggle.innerHTML = '<i class="fas fa-sun me-2"></i>Light Mode';
        document.body.classList.remove('light-mode');
    }
}
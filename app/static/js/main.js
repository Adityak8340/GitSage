document.addEventListener('DOMContentLoaded', () => {
    // Handle repo form submission
    const repoForm = document.getElementById('repo-form');
    if (repoForm) {
        repoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const url = document.getElementById('repo-url').value.trim();
            const match = url.match(/github\.com\/([^/]+)\/([^/]+)/);
            if (match) {
                window.location.href = `/repo/${match[1]}/${match[2]}`;
            } else {
                alert('Please enter a valid GitHub repository URL');
            }
        });
    }

    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    if (themeToggle) {
        themeToggle.checked = (savedTheme === 'dark');
        themeToggle.addEventListener('change', () => {
            const theme = themeToggle.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        });
    }

    // Smooth scroll for anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelector(anchor.getAttribute('href'))?.scrollIntoView({ behavior: 'smooth' });
        });
    });
});
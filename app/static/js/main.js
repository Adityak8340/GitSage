document.addEventListener('DOMContentLoaded', () => {
    const repoForm = document.getElementById('repo-form');
    
    if (repoForm) {
        repoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const repoUrl = document.getElementById('repo-url').value;
            
            // Extract owner and repo name from URL
            const [owner, repo] = parseGitHubUrl(repoUrl);
            if (owner && repo) {
                window.location.href = `/repo/${owner}/${repo}`;
            }
        });
    }

    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    
    // Set initial theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeToggle.checked = savedTheme === 'dark';

    themeToggle.addEventListener('change', () => {
        const theme = themeToggle.checked ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Add theme transition animation
        document.documentElement.style.transition = 'background-color 0.3s ease';
        setTimeout(() => {
            document.documentElement.style.transition = '';
        }, 300);
    });
});

// Add smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

function parseGitHubUrl(url) {
    try {
        const pattern = /github\.com\/([^\/]+)\/([^\/]+)/;
        const match = url.match(pattern);
        return match ? [match[1], match[2]] : [null, null];
    } catch (error) {
        console.error('Error parsing GitHub URL:', error);
        return [null, null];
    }
}
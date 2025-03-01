// Global variables
let repoOwner = '';
let repoName = '';
let repoContext = '';

// Initialize repository viewer
document.addEventListener('DOMContentLoaded', function() {
    console.log('Repository viewer initializing...');
    
    // Extract repo owner and name from URL
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length >= 4 && pathParts[1] === 'repo') {
        repoOwner = pathParts[2];
        repoName = pathParts[3];
        console.log(`Repository: ${repoOwner}/${repoName}`);
        
        // Initialize tree view
        initTreeView();
        
        // Preload repository context for chat
        preloadRepoContext();
    }
});

// Preload repository context
async function preloadRepoContext() {
    try {
        const response = await fetch(`/repo/${repoOwner}/${repoName}/context`);
        if (response.ok) {
            const data = await response.json();
            repoContext = data.context;
            console.log('Repository context loaded successfully');
            
            // Store context in sessionStorage for persistence
            sessionStorage.setItem('repoContext', repoContext);
            
            // Notify chat.js that context is available
            window.dispatchEvent(new CustomEvent('repoContextLoaded', { detail: { context: repoContext } }));
        } else {
            console.error('Failed to load repository context');
        }
    } catch (error) {
        console.error('Error loading repository context:', error);
    }
}

// Initialize tree view
async function initTreeView() {
    const treeContainer = document.getElementById('directory-tree');
    if (!treeContainer) return;
    
    try {
        const response = await fetch(`/repo/${repoOwner}/${repoName}/tree`);
        const data = await response.json();
        
        if (data && data.length > 0) {
            treeContainer.innerHTML = ''; // Clear loading message
            renderTree(data, treeContainer);
        } else {
            treeContainer.innerHTML = '<div class="error">No files found</div>';
        }
    } catch (error) {
        treeContainer.innerHTML = `<div class="error">Error loading files: ${error.message}</div>`;
    }
}

// Render tree recursively
function renderTree(nodes, container, level = 0) {
    nodes.sort((a, b) => {
        // Directories first, then alphabetically
        if (a.type === 'dir' && b.type === 'file') return -1;
        if (a.type === 'file' && b.type === 'dir') return 1;
        return a.name.localeCompare(b.name);
    });
    
    for (const node of nodes) {
        const item = document.createElement('div');
        const indent = '  '.repeat(level);
        const icon = node.type === 'dir' ? '📁' : getFileIcon(node.name);
        
        if (node.type === 'dir') {
            item.classList.add('folder');
            item.innerHTML = `
                <div class="folder-header">
                    ${indent}${icon} ${node.name}
                </div>
                <div class="folder-content"></div>
            `;
            
            item.querySelector('.folder-header').addEventListener('click', function() {
                item.classList.toggle('open');
            });
            
            container.appendChild(item);
            renderTree(node.children, item.querySelector('.folder-content'), level + 1);
        } else {
            item.classList.add('file');
            item.setAttribute('data-path', node.path);
            item.innerHTML = `${indent}${icon} ${node.name}`;
            
            item.addEventListener('click', function() {
                loadFile(node.path);
                
                // Highlight selected file
                document.querySelectorAll('.file').forEach(f => f.classList.remove('selected'));
                item.classList.add('selected');
            });
            
            container.appendChild(item);
        }
    }
}

// Get appropriate icon for file type
function getFileIcon(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    
    const icons = {
        'py': '🐍',
        'js': '📜',
        'html': '🌐',
        'css': '🎨',
        'json': '📋',
        'md': '📝',
        'txt': '📄',
        'jpg': '🖼️',
        'png': '🖼️',
        'gif': '🖼️'
    };
    
    return icons[extension] || '📄';
}

// Load file content
async function loadFile(path) {
    const codeContent = document.getElementById('code-content');
    const currentFilePath = document.getElementById('current-file-path');
    
    if (!codeContent || !currentFilePath) return;
    
    currentFilePath.textContent = path;
    codeContent.textContent = 'Loading...';
    
    try {
        const response = await fetch(`/repo/${repoOwner}/${repoName}/contents/${path}`);
        const data = await response.json();
        
        if (data.content) {
            codeContent.textContent = data.content;
            
            // Highlight code if hljs is available
            if (window.hljs) {
                hljs.highlightElement(codeContent);
            }
            
            // Signal that a new file has been loaded (for chat.js)
            window.dispatchEvent(new CustomEvent('fileLoaded', { 
                detail: { 
                    path: path, 
                    content: data.content 
                }
            }));
        } else {
            codeContent.textContent = 'Unable to load file content';
        }
    } catch (error) {
        codeContent.textContent = `Error loading file: ${error.message}`;
    }
}

// Export for chat.js
window.getRepoInfo = function() {
    return {
        owner: repoOwner,
        name: repoName,
        context: repoContext || sessionStorage.getItem('repoContext') || ''
    };
};
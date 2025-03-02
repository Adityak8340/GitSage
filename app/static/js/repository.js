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
        
        // Check if it's a binary file
        if (data.is_binary) {
            displayBinaryFile(data, codeContent);
            
            // Don't pass binary files to chat context
            window.dispatchEvent(new CustomEvent('fileLoaded', { 
                detail: { 
                    path: path, 
                    content: `[Binary file: ${data.name} (${formatFileSize(data.size)})]`,
                    is_binary: true
                }
            }));
        } else {
            // It's a text file
            if (data.content) {
                codeContent.textContent = data.content;
                
                // Highlight code if hljs is available
                if (window.hljs) {
                    hljs.highlightElement(codeContent);
                    
                    // Fix blue text colors after highlighting (for f-strings etc)
                    setTimeout(() => {
                        // Target all blue-colored spans and force them yellow
                        const blueSpans = codeContent.querySelectorAll('span[style*="color: blue"], span[style*="color:#0000FF"], span.hljs-string');
                        blueSpans.forEach(span => {
                            span.style.color = '#ffcb6b';
                        });
                        console.log(`Fixed colors for ${blueSpans.length} spans in ${path}`);
                    }, 100);
                }
                
                // Signal that a new file has been loaded
                window.dispatchEvent(new CustomEvent('fileLoaded', { 
                    detail: { 
                        path: path, 
                        content: data.content,
                        is_binary: false
                    }
                }));
            } else {
                codeContent.textContent = 'Unable to load file content';
            }
        }
    } catch (error) {
        codeContent.textContent = `Error loading file: ${error.message}`;
    }
}

// Display binary file information
function displayBinaryFile(fileInfo, container) {
    const fileType = fileInfo.type;
    const downloadUrl = fileInfo.download_url;
    const fileSize = formatFileSize(fileInfo.size);
    
    // Completely rewritten HTML structure with minimal whitespace
    let content = `<div class="binary-file-container">`;
    
    // Add preview for supported types
    if (fileType === 'image') {
        content += `<div class="image-preview">
            <img src="${downloadUrl}" alt="${fileInfo.name}" style="max-width: 100%; max-height: 400px;">
        </div>`;
    }
    
    content += `<div class="binary-file-info">
        <h3>Binary File</h3>
        <table class="binary-file-table">
            <tr><td><strong>Name:</strong></td><td>${fileInfo.name}</td></tr>
            <tr><td><strong>Type:</strong></td><td>${fileType}</td></tr>
            <tr><td><strong>Size:</strong></td><td>${fileSize}</td></tr>
        </table>
        <a href="${downloadUrl}" target="_blank" class="download-link">View Raw File</a>
        <small class="file-note">Binary files cannot be displayed directly in the code viewer</small>
    </div>
</div>`;
    
    container.innerHTML = content;
}

// Format file size in human-readable format
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    else if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    else return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
}

// Export for chat.js
window.getRepoInfo = function() {
    return {
        owner: repoOwner,
        name: repoName,
        context: repoContext || sessionStorage.getItem('repoContext') || ''
    };
};
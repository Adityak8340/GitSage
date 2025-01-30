document.addEventListener('DOMContentLoaded', async () => {
    // Get repository info from URL
    const pathParts = window.location.pathname.split('/');
    window.owner = pathParts[2];
    window.repo = pathParts[3];

    // Load directory tree
    await loadDirectoryTree();
    
    // Setup file search
    setupFileSearch();
    
    // Setup chat interface
    setupChatInterface();
});

async function loadDirectoryTree() {
    try {
        const response = await fetch(`/repo/${window.owner}/${window.repo}/tree`);
        const tree = await response.json();
        renderDirectoryTree(tree);
        
        // Add click handlers for files
        document.querySelectorAll('.file').forEach(file => {
            file.addEventListener('click', async () => {
                const filePath = file.dataset.path;
                await loadFileContent(filePath);
                
                // Highlight active file
                document.querySelectorAll('.file').forEach(f => f.classList.remove('active'));
                file.classList.add('active');
            });
        });
    } catch (error) {
        console.error('Error loading directory tree:', error);
        showError('Failed to load repository structure');
    }
}

function renderDirectoryTree(tree) {
    const treeView = document.getElementById('tree-view');
    treeView.innerHTML = createTreeHTML(tree);
    
    // Add click handlers for folders
    document.querySelectorAll('.folder').forEach(folder => {
        folder.addEventListener('click', (e) => {
            e.preventDefault();
            folder.classList.toggle('open');
        });
    });
}

function createTreeHTML(item) {
    if (Array.isArray(item)) {
        return item.map(i => createTreeHTML(i)).join('');
    }
    
    if (item.type === 'dir') {
        return `
            <div class="folder">
                <span class="folder-name">📁 ${item.name}</span>
                <div class="folder-content">${createTreeHTML(item.children)}</div>
            </div>
        `;
    }
    
    return `
        <div class="file" data-path="${item.path}">
            <span class="file-name">📄 ${item.name}</span>
        </div>
    `;
}

async function loadFileContent(path) {
    try {
        const codeDisplay = document.getElementById('code-display');
        const currentPath = document.getElementById('current-file-path');
        
        // Show loading state
        codeDisplay.innerHTML = '<div class="loading">Loading file content...</div>';
        currentPath.textContent = path;
        
        const response = await fetch(`/repo/${window.owner}/${window.repo}/contents/${path}`);
        if (!response.ok) throw new Error('Failed to fetch file content');
        
        const data = await response.json();
        
        // Display code with syntax highlighting
        const language = getLanguageFromPath(path);
        codeDisplay.innerHTML = `<pre><code class="language-${language}">${escapeHtml(data.content)}</code></pre>`;
        
        // Initialize syntax highlighting
        if (window.Prism) {
            Prism.highlightElement(codeDisplay.querySelector('code'));
        }
        
        // Store current file context for chat
        window.currentFile = { path, content: data.content };
        
        // Get and display explanation
        await updateExplanation(data.content, path);
        
        // Clear chat messages and show new file message
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = '';
        appendMessage('system', `📄 Now viewing: ${path}\nYou can ask questions about this file.`);
    } catch (error) {
        console.error('Error loading file:', error);
        showError(`Failed to load file: ${error.message}`);
    }
}

async function updateExplanation(code, path) {
    try {
        const response = await fetch('/repo/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, path })
        });
        const data = await response.json();
        
        // Convert markdown to HTML and display with proper formatting
        const explanationHtml = marked.parse(data.text);
        document.getElementById('code-explanation').innerHTML = `
            <h3>Code Explanation</h3>
            <div class="markdown-body">${explanationHtml}</div>
        `;
    } catch (error) {
        console.error('Error getting explanation:', error);
        document.getElementById('code-explanation').innerHTML = 
            '<div class="error">Failed to load explanation</div>';
    }
}

function setupFileSearch() {
    const searchInput = document.getElementById('file-search');
    const fileTypeFilter = document.getElementById('file-type-filter');
    
    searchInput.addEventListener('input', filterFiles);
    fileTypeFilter.addEventListener('change', filterFiles);
}

function filterFiles() {
    const searchTerm = document.getElementById('file-search').value.toLowerCase();
    const fileType = document.getElementById('file-type-filter').value;
    
    document.querySelectorAll('.file').forEach(file => {
        const fileName = file.querySelector('.file-name').textContent.toLowerCase();
        const matchesSearch = fileName.includes(searchTerm);
        const matchesType = !fileType || fileName.endsWith(fileType);
        
        file.style.display = matchesSearch && matchesType ? 'block' : 'none';
    });
}

function setupChatInterface() {
    const chatForm = document.querySelector('.chat-input-form');
    const chatInput = document.getElementById('chat-query');
    const chatMessages = document.getElementById('chat-messages');
    
    // Clear chat messages and show initial message
    chatMessages.innerHTML = '';
    appendMessage('system', 'Select a file from the tree view on the left to start asking questions about the code.');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = chatInput.value.trim();
        if (!query) return;
        
        // Check if a file is selected
        if (!window.currentFile) {
            appendMessage('error', '⚠️ Please select a file first by clicking on it in the tree view.');
            return;
        }
        
        try {
            // Show user message
            appendMessage('user', query);
            chatInput.value = '';
            chatInput.disabled = true;
            
            // Add loading message
            appendMessage('loading', '🤔 Analyzing code and generating response...', false);
            
            const response = await fetch('/repo/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    context: {
                        path: window.currentFile.path,
                        content: window.currentFile.content
                    }
                })
            });
            
            // Remove all loading messages
            document.querySelectorAll('.loading-message').forEach(el => el.remove());
            
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Parse markdown and display AI response
            const aiResponse = marked.parse(data.text);
            appendMessage('ai', aiResponse, true);
        } catch (error) {
            console.error('Chat error:', error);
            appendMessage('error', '❌ Error: ' + (error.message || 'Failed to process your question'));
        } finally {
            chatInput.disabled = false;
            chatInput.focus();
            
            // Remove loading messages if any remain
            document.querySelectorAll('.loading-message').forEach(el => el.remove());
        }
    });
}

async function askQuestion(query) {
    try {
        const response = await fetch('/repo/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                context: window.currentFile || {}
            })
        });
        
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        
        appendMessage('ai', data.text);
    } catch (error) {
        console.error('Error getting answer:', error);
        appendMessage('error', 'Sorry, I encountered an error while processing your question.');
    }
}

function appendMessage(type, content, isHtml = false) {
    const messages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message`;
    if (type === 'loading') {
        messageDiv.className += ' loading-message';
    }
    
    if (isHtml) {
        messageDiv.innerHTML = content;
    } else {
        messageDiv.textContent = content;
    }
    
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
    return messageDiv;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.querySelector('.main-content').prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function getLanguageFromPath(path) {
    const ext = path.split('.').pop().toLowerCase();
    const languageMap = {
        'py': 'python',
        'js': 'javascript',
        'html': 'html',
        'css': 'css',
        'md': 'markdown',
        // Add more mappings as needed
    };
    return languageMap[ext] || 'plaintext';
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
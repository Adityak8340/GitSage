/**
 * Simple chat functionality for GitSage
 */

// Initialize when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Chat.js: Initializing');
    
    // Find the chat form
    const chatForm = document.getElementById('chat-form');
    
    if (!chatForm) {
        console.error('Chat.js: Chat form not found!');
        return;
    }
    
    console.log('Chat.js: Found chat form');
    
    // Get repository information
    const pathParts = window.location.pathname.split('/');
    let repoOwner = '';
    let repoName = '';
    
    if (pathParts.length >= 4 && pathParts[1] === 'repo') {
        repoOwner = pathParts[2];
        repoName = pathParts[3];
        console.log(`Chat.js: Repository identified as ${repoOwner}/${repoName}`);
    }
    
    // Display a welcome message
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages && !chatMessages.hasChildNodes()) {
        const welcomeMessage = document.createElement('div');
        welcomeMessage.className = 'ai-message';
        welcomeMessage.textContent = 'Hello! I\'m GitSage. Ask me questions about this repository.';
        chatMessages.appendChild(welcomeMessage);
    }
    
    // Add event listener for form submission
    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log('Chat.js: Form submitted');
        
        const chatInput = document.getElementById('chat-input');
        if (!chatInput) {
            console.error('Chat.js: Chat input not found!');
            return;
        }
        
        const query = chatInput.value.trim();
        if (!query) {
            console.log('Chat.js: Empty query');
            return;
        }
        
        console.log(`Chat.js: Processing query: "${query}"`);
        chatInput.value = '';
        
        // Get selected file context if available
        const codeContent = document.getElementById('code-content');
        const currentFilePath = document.getElementById('current-file-path');
        
        let fileContext = {};
        if (codeContent && currentFilePath && currentFilePath.textContent) {
            fileContext = {
                path: currentFilePath.textContent,
                content: codeContent.textContent
            };
        }
        
        // Add the user's message to the chat
        if (chatMessages) {
            const userMessage = document.createElement('div');
            userMessage.className = 'user-message';
            userMessage.textContent = query;
            chatMessages.appendChild(userMessage);
            
            const aiMessage = document.createElement('div');
            aiMessage.className = 'ai-message';
            aiMessage.textContent = 'Thinking...';
            chatMessages.appendChild(aiMessage);
            
            // Scroll to the bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Send the request
            console.log('Chat.js: Sending request to server');
            fetch('/repo/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    context: fileContext,
                    repo_owner: repoOwner,
                    repo_name: repoName
                })
            })
            .then(response => {
                console.log(`Chat.js: Response received, status: ${response.status}`);
                if (!response.ok) {
                    throw new Error(`Server responded with status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Chat.js: Data parsed successfully');
                aiMessage.innerHTML = formatResponse(data.text);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => {
                console.error('Chat.js: Error:', error);
                aiMessage.className = 'ai-message error';
                aiMessage.textContent = `Error: ${error.message}`;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            });
        }
    });
});

// Format the response with enhanced markdown support
function formatResponse(text) {
    if (!text) return '';
    
    // Handle code blocks with language specification
    text = text.replace(/```([a-zA-Z0-9]*)\n([\s\S]*?)```/g, function(match, lang, code) {
        return `<pre class="code-block${lang ? ' language-' + lang : ''}"><code>${escapeHtml(code)}</code></pre>`;
    });
    
    // Format inline code
    text = text.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
    
    // Format bold text
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\_\_([^_]+)\_\_/g, '<strong>$1</strong>');
    
    // Format italic text
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    text = text.replace(/\_([^_]+)\_/g, '<em>$1</em>');
    
    // Format headers (must do this before line breaks)
    text = text.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    text = text.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    text = text.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
    
    // Format unordered lists
    text = text.replace(/^[\s]*?[\-\*] (.*?)$/gm, '<li>$1</li>');
    
    // Format ordered lists
    text = text.replace(/^[\s]*?\d+\. (.*?)$/gm, '<li>$1</li>');
    
    // Group list items (must be careful with this regex)
    text = text.replace(/(<li>.*?<\/li>)(\s*<li>.*?<\/li>)+/gs, '<ul>$&</ul>');
    
    // Format links
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // Add line breaks (must be last)
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Helper function to escape HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

console.log('Chat.js loaded');

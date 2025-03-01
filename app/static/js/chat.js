/**
 * Enhanced chat functionality for GitSage
 */

let repoOwner = '';
let repoName = '';

// Get repository information from URL
function initChat() {
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length >= 4 && pathParts[1] === 'repo') {
        repoOwner = pathParts[2];
        repoName = pathParts[3];
        console.log(`Chat initialized for repository: ${repoOwner}/${repoName}`);
    } else {
        console.log('Not viewing a specific repository');
    }
    
    // Setup chat form submission
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
        console.log('Chat form listener attached');
    } else {
        console.error('Chat form not found in the DOM');
    }
}

// Handle chat form submission
async function handleChatSubmit(event) {
    event.preventDefault();
    console.log('Chat form submitted');
    
    const queryInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    
    if (!queryInput || !queryInput.value.trim()) {
        console.log('Empty query, not sending');
        return;
    }
    
    const query = queryInput.value.trim();
    queryInput.value = '';
    
    // Show loading indicator
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message';
    messageElement.innerHTML = `
        <div class="user-message">You: ${query}</div>
        <div class="ai-message loading">GitSage is thinking...</div>
    `;
    chatMessages.appendChild(messageElement);
    
    // Get selected file context if any
    const codeContent = document.getElementById('code-content');
    const currentFilePath = document.getElementById('current-file-path');
    
    let fileContext = {};
    
    if (codeContent && codeContent.textContent.trim() !== 'Select a file to view its contents' && currentFilePath) {
        fileContext = {
            path: currentFilePath.textContent || '',
            content: codeContent.textContent || ''
        };
    }
    
    console.log('Sending chat request with context:', {
        query,
        fileContext,
        repoOwner,
        repoName
    });
    
    try {
        const response = await fetch('/repo/chat', {
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
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update the loading message with the response
        const aiMessageElement = messageElement.querySelector('.ai-message');
        aiMessageElement.classList.remove('loading');
        aiMessageElement.innerHTML = `GitSage: ${formatResponse(data.text)}`;
    } catch (error) {
        console.error('Chat error:', error);
        const aiMessageElement = messageElement.querySelector('.ai-message');
        aiMessageElement.classList.remove('loading');
        aiMessageElement.classList.add('error');
        aiMessageElement.textContent = `Error: ${error.message}`;
    }
}

// Format response with markdown
function formatResponse(text) {
    // Simple markdown-like formatting
    // Replace code blocks
    text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // Replace inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Replace line breaks with <br>
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing chat');
    initChat();
});

// For debugging
console.log('Chat.js loaded');

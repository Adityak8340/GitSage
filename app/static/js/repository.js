document.addEventListener('DOMContentLoaded', async () => {
    const [ , , owner, repo ] = window.location.pathname.split('/');

    // Fetch and render directory tree
    try {
        const treeData = await (await fetch(`/repo/${owner}/${repo}/tree`)).json();
        document.getElementById('directory-tree').innerHTML = buildTreeHTML(treeData);
        setupTree();
    } catch (err) {
        console.error('Error loading tree:', err);
    }

    // Setup chat form
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = document.getElementById('chat-input')?.value.trim();
            if (!query) return;
            await sendChat(query);
        });
    }
});

function buildTreeHTML(items) {
    return items.map(i => {
        if (i.type === 'dir') {
            return `
                <div class="folder" data-path="${i.path}">
                    <div class="folder-name">📁 ${i.name}</div>
                    <div class="folder-content">${i.children.length ? buildTreeHTML(i.children) : 'Empty folder'}</div>
                </div>
            `;
        } 
        return `<div class="file" data-path="${i.path}">📄 ${i.name}</div>`;
    }).join('');
}

function setupTree() {
    // Toggle folder open/close
    document.querySelectorAll('.folder-name').forEach(el => {
        el.addEventListener('click', (e) => {
            e.stopPropagation();
            el.parentElement.classList.toggle('open');
        });
    });
    // Load file content
    document.querySelectorAll('.file').forEach(el => {
        el.addEventListener('click', () => loadFile(el.dataset.path));
    });
}

async function loadFile(path) {
    const [ , , owner, repo ] = window.location.pathname.split('/');
    const codeElem = document.getElementById('code-content');
    document.getElementById('current-file-path').textContent = path;
    codeElem.textContent = 'Loading...';

    try {
        const data = await (await fetch(`/repo/${owner}/${repo}/contents/${path}`)).json();
        if (data.content) {
            codeElem.className = '';
            const ext = path.split('.').pop().toLowerCase();
            codeElem.textContent = data.content;
            codeElem.classList.add(`language-${getLanguage(ext)}`);
            hljs.highlightElement(codeElem);
        } else {
            codeElem.textContent = 'Unable to load content.';
        }
    } catch (err) {
        codeElem.textContent = 'Error loading file.';
    }
}

function getLanguage(ext) {
    const map = {
        js: 'javascript', py: 'python', ts: 'typescript', c: 'c', cpp: 'cpp',
        html: 'html', css: 'css', json: 'json', md: 'markdown', go: 'go',
        java: 'java', php: 'php', rb: 'ruby', sh: 'bash', yml: 'yaml'
    };
    return map[ext] || 'plaintext';
}

// Chat
async function sendChat(query) {
    const messages = document.getElementById('chat-messages');
    const filePath = document.getElementById('current-file-path').textContent;
    const codeContent = document.getElementById('code-content').textContent;
    messages.innerHTML += `<div class="user-message">${escapeHtml(query)}</div><div class="loading-message">Thinking...</div>`;

    try {
        const res = await fetch('/repo/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, context: { path: filePath, content: codeContent } })
        });
        document.querySelector('.loading-message')?.remove();
        if (res.ok) {
            const data = await res.json();
            messages.innerHTML += `<div class="ai-message">${toMarkdownHtml(data.text)}</div>`;
            messages.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
        } else {
            messages.innerHTML += `<div class="error-message">Chat error.</div>`;
        }
    } catch (err) {
        document.querySelector('.loading-message')?.remove();
        messages.innerHTML += `<div class="error-message">Chat failed.</div>`;
    }
}

// Simple helpers
function escapeHtml(text) {
    return text.replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[s]));
}
function toMarkdownHtml(md) {
    return marked.parse(md || '', { gfm: true, breaks: true });
}
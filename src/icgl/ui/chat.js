// ICGL Sovereign Chat - Client JavaScript

const API_BASE = 'http://127.0.0.1:8000';
const SESSION_ID = `web-${Date.now().toString(16)}`;

// State
let chatState = {
    awaitingSign: false,
    adrId: null,
    session: SESSION_ID
};

let lastHttpMessageSignature = null;
let lastHttpMessageAt = 0;

// DOM Elements
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const suggestionsContainer = document.getElementById('suggestions');
const contextBar = document.getElementById('context-bar');
const contextToggle = document.getElementById('context-toggle');
const contextClose = document.getElementById('context-close');
const statusIndicator = document.getElementById('status');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    adjustTextareaHeight();
    initWebsocket();
});

function setupEventListeners() {
    // Send message
    sendBtn.addEventListener('click', sendMessage);

    // Send on Ctrl+Enter
    userInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            sendMessage();
        }
    });

    // Auto-resize textarea
    userInput.addEventListener('input', adjustTextareaHeight);

    // Context bar toggle
    contextToggle.addEventListener('click', () => {
        contextBar.classList.toggle('collapsed');
    });

    contextClose.addEventListener('click', () => {
        contextBar.classList.add('collapsed');
    });
}

let chatSocket = null;
function initWebsocket() {
    try {
        const wsUrl = API_BASE.replace('http', 'ws') + '/ws/chat';
        chatSocket = new WebSocket(wsUrl);
        chatSocket.onopen = () => {
            statusIndicator.textContent = 'Live';
        };
        chatSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // Ignore broadcasts for other sessions if session_id present
            if (data.state && data.state.session_id && data.state.session_id !== SESSION_ID) return;
            if (data.state && data.state.session_id === SESSION_ID) {
                const signature = buildMessageSignature(data);
                if (signature && lastHttpMessageSignature && signature === lastHttpMessageSignature && (Date.now() - lastHttpMessageAt) < 3000) {
                    return;
                }
            }
            if (data.messages) {
                data.messages.forEach(msg => addMessage(msg.role || 'assistant', msg.text || msg.content, msg.blocks));
            }
            if (data.state) updateState(data.state);
            if (data.suggestions) renderSuggestions(data.suggestions);
        };
        chatSocket.onerror = () => statusIndicator.textContent = 'WS error';
        chatSocket.onclose = () => {
            statusIndicator.textContent = 'Ready';
        };
    } catch (e) {
        console.warn('WebSocket init failed', e);
    }
}

function adjustTextareaHeight() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Clear input
    userInput.value = '';
    adjustTextareaHeight();

    // Add user message to UI
    addMessage('user', message);

    // Show loading
    const loadingEl = showLoading();

    // Disable send button
    sendBtn.disabled = true;
    statusIndicator.textContent = 'Thinking...';

    try {
        // Call API
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: SESSION_ID,
                context: {
                    human_id: 'user',
                    mode: 'auto'
                }
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        lastHttpMessageSignature = buildMessageSignature(data);
        lastHttpMessageAt = Date.now();

        // Remove loading
        loadingEl.remove();

        // Render messages
        data.messages.forEach(msg => {
            addMessage(msg.role, msg.text || msg.content, msg.blocks);
        });

        // Update state
        if (data.state) {
            updateState(data.state);
        }

        // Render suggestions
        if (data.suggestions && data.suggestions.length > 0) {
            renderSuggestions(data.suggestions);
        }

        statusIndicator.textContent = 'Ready';

    } catch (error) {
        loadingEl.remove();
        addMessage('system', `❌ Error: ${error.message}`);
        statusIndicator.textContent = 'Error';
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function buildMessageSignature(payload) {
    if (!payload || !payload.messages || payload.messages.length === 0) return '';
    return payload.messages.map(msg => {
        const text = msg.text || msg.content || '';
        const blockTypes = (msg.blocks || []).map(block => block.type).join(',');
        return `${msg.role || 'assistant'}|${text}|${blockTypes}`;
    }).join('||');
}

function addMessage(role, content, blocks = []) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role}`;

    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';

    // Render content (support markdown-like formatting)
    contentEl.innerHTML = formatContent(content);

    // Render blocks
    if (blocks && blocks.length > 0) {
        blocks.forEach(block => {
            const blockEl = renderBlock(block);
            contentEl.appendChild(blockEl);
        });
    }

    messageEl.appendChild(contentEl);
    messagesContainer.appendChild(messageEl);

    // Scroll to bottom
    scrollToBottom();
}

function formatContent(content) {
    // Simple markdown-like formatting
    return content
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>')
        .replace(/^- (.+)$/gm, '<li>$1</li>');
}

function renderBlock(block) {
    const blockEl = document.createElement('div');
    blockEl.className = 'message-block';

    // Header
    const headerEl = document.createElement('div');
    headerEl.className = `block-header ${block.collapsed ? 'collapsed' : ''}`;

    const titleEl = document.createElement('span');
    titleEl.className = 'block-title';
    titleEl.textContent = block.title || getBlockTitle(block.type);

    const toggleEl = document.createElement('span');
    toggleEl.className = 'block-toggle';
    toggleEl.textContent = '▼';

    headerEl.appendChild(titleEl);
    headerEl.appendChild(toggleEl);

    // Content
    const contentEl = document.createElement('div');
    contentEl.className = `block-content ${block.collapsed ? '' : 'expanded'}`;

    // Render based on type
    if (block.type === 'analysis') {
        contentEl.innerHTML = renderAnalysisBlock(block.data);
    } else if (block.type === 'alerts') {
        contentEl.innerHTML = renderAlertsBlock(block.data);
    } else if (block.type === 'actions') {
        contentEl.appendChild(renderActionsBlock(block.data));
    } else if (block.type === 'adr') {
        contentEl.innerHTML = renderAdrBlock(block.data);
    } else if (block.type === 'memory') {
        contentEl.innerHTML = renderMemoryBlock(block.data);
    } else {
        contentEl.innerHTML = `<pre>${JSON.stringify(block.data, null, 2)}</pre>`;
    }

    // Toggle functionality
    headerEl.addEventListener('click', () => {
        headerEl.classList.toggle('collapsed');
        contentEl.classList.toggle('expanded');
    });

    blockEl.appendChild(headerEl);
    blockEl.appendChild(contentEl);

    return blockEl;
}

function getBlockTitle(type) {
    const titles = {
        'analysis': '🧠 Multi-Agent Analysis',
        'alerts': '⚠️ Sentinel Alerts',
        'actions': '⚡ Actions',
        'adr': '📜 ADR',
        'metrics': '📊 Metrics',
        'memory': '📜 Memory'
    };
    return titles[type] || '📄 Details';
}

function renderAnalysisBlock(data) {
    let html = '';
    if (data.confidence !== undefined) {
        html += `<p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(0)}%</p>`;
    }
    if (data.consensus && data.consensus.length > 0) {
        html += '<p><strong>Consensus recommendations:</strong></p><ul>';
        data.consensus.forEach(rec => html += `<li>${rec}</li>`);
        html += '</ul>';
    }
    if (data.concerns && data.concerns.length > 0) {
        html += '<p><strong>Concerns:</strong></p><ul>';
        data.concerns.forEach(risk => html += `<li>⚠️ ${risk}</li>`);
        html += '</ul>';
    }
    return html || '<p class="muted">No analysis details available.</p>';
}

function renderAlertsBlock(data) {
    let html = '';

    const alerts = data.alerts || data.signals || [];
    if (alerts.length === 0) return '<p class="muted">No alerts</p>';
    html += '<ul class="alerts-list">';
    alerts.forEach(alert => {
        const sev = (alert.severity || alert.level || 'info').toString().toUpperCase();
        const msg = alert.message || alert.text || JSON.stringify(alert);
        html += `<li class="sev-${sev}">⚠️ [${sev}] ${msg}</li>`;
    });
    html += '</ul>';
    return html;
}

function renderActionsBlock(data) {
    const container = document.createElement('div');
    container.className = 'actions-block';

    if (data.actions && data.actions.length > 0) {
        data.actions.forEach(action => {
            const btn = document.createElement('button');
            btn.className = 'action-btn';
            btn.textContent = action.label;
            btn.addEventListener('click', () => handleAction(action));
            container.appendChild(btn);
        });
    }

    return container;
}

function renderAdrBlock(data) {
    let html = `<p><strong>ID:</strong> ${data.id}</p>`;
    html += `<p><strong>Status:</strong> ${data.status}</p>`;
    if (data.decision) {
        html += `<p><strong>Decision:</strong> ${data.decision}</p>`;
    }
    return html;
}

function renderMemoryBlock(data) {
    const matches = data.matches || [];
    if (matches.length === 0) return '<p class="muted">No similar memories found.</p>';
    let html = '<ul class="memory-list">';
    matches.forEach(m => {
        html += `<li><strong>${m.title || m.id}</strong> (score ${m.score})<br>${m.snippet || ''}</li>`;
    });
    html += '</ul>';
    return html;
}

function handleAction(action) {
    if (action.action === 'submit_signature') {
        const rationale = prompt('Add rationale for this decision:');
        if (rationale !== null) sendMessage(`${action.value || 'Approve'}: ${rationale}`);
    } else if (action.action === 'experiment') {
        sendMessage('Start experiment');
    } else if (action.action === 'review') {
        sendMessage(`Show session ${action.session_id}`);
    } else {
        sendMessage(action.label || 'Run analysis');
    }
}

function renderSuggestions(suggestions) {
    suggestionsContainer.innerHTML = '';

    suggestions.forEach(suggestion => {
        const chip = document.createElement('button');
        chip.className = 'suggestion-chip';
        chip.textContent = suggestion;
        chip.addEventListener('click', () => {
            userInput.value = suggestion;
            userInput.focus();
        });
        suggestionsContainer.appendChild(chip);
    });
}

function showLoading() {
    const loadingEl = document.createElement('div');
    loadingEl.className = 'message system';
    loadingEl.innerHTML = `
        <div class="message-content">
            <div class="loading-indicator">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(loadingEl);
    scrollToBottom();
    return loadingEl;
}

function updateState(state) {
    chatState = { ...chatState, ...state };

    // Update context bar
    if (state.waiting_for_human !== undefined) {
        document.getElementById('ctx-awaiting').textContent = state.waiting_for_human ? 'Yes' : 'No';
    }
    if (state.mode) {
        document.getElementById('ctx-mode').textContent = state.mode;
    }
    if (state.alert_level) {
        statusIndicator.textContent = `Alert: ${state.alert_level}`;
    }

    if (state.adr_id) {
        chatState.adrId = state.adr_id;
    }

    if (state.refactor_session) {
        document.getElementById('ctx-session').textContent = state.refactor_session;
        chatState.session = state.refactor_session;
    } else {
        document.getElementById('ctx-session').textContent = chatState.session;
    }
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

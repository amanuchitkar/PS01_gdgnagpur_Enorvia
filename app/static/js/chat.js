let conversationId = null;
let messageCount = 0;

async function initConversation() {
    try {
        // Check if a conversation was already started from the check-in flow
        if (typeof INITIAL_CONVERSATION_ID !== 'undefined' && INITIAL_CONVERSATION_ID) {
            conversationId = INITIAL_CONVERSATION_ID;
            // Load the existing greeting message from the check-in
            await loadExistingMessages();
        } else {
            const response = await fetch('/api/conversation/start', { method: 'POST' });
            const data = await response.json();
            conversationId = data.conversation_id;
        }
    } catch (error) {
        console.error('Failed to start conversation:', error);
        showError('Failed to connect. Please refresh the page.');
    }
}

async function loadExistingMessages() {
    try {
        const response = await fetch(`/api/conversation/${conversationId}/messages`);
        if (!response.ok) return;
        const data = await response.json();

        if (data.messages && data.messages.length > 0) {
            // Replace the default welcome message with the check-in greeting
            const container = document.getElementById('chat-container');
            container.innerHTML = '';
            data.messages.forEach(msg => {
                addMessage(msg.role, msg.content);
            });
        }
    } catch (e) {
        // Silently fail — the default welcome message is fine as fallback
        console.warn('Could not load existing messages:', e);
    }
}

async function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    if (!message || !conversationId) return;

    input.value = '';
    addMessage('user', message);
    showTypingIndicator();
    disableInput(true);

    try {
        const response = await fetch('/api/conversation/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conversation_id: conversationId, message }),
        });

        if (!response.ok) throw new Error('Failed to send message');
        const data = await response.json();

        removeTypingIndicator();
        addMessage('assistant', data.ai_response);
        updateEmotionBar(data);
        messageCount++;

        if (messageCount >= 2) {
            document.getElementById('end-btn').classList.remove('hidden');
        }
    } catch (error) {
        removeTypingIndicator();
        addMessage('assistant', "I'm having trouble connecting right now. Could you try sending that again?");
        console.error('Error:', error);
    } finally {
        disableInput(false);
        input.focus();
    }
}

function addMessage(role, content) {
    const container = document.getElementById('chat-container');
    const div = document.createElement('div');
    div.className = `flex gap-3 fade-in ${role === 'user' ? 'justify-end' : ''}`;

    if (role === 'assistant') {
        div.innerHTML = `
            <div class="w-8 h-8 bg-gradient-to-br from-primary-400 to-calm-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                </svg>
            </div>
            <div class="bg-white rounded-2xl rounded-tl-md p-4 shadow-sm max-w-[80%]">
                <p class="text-gray-700 text-sm leading-relaxed">${escapeHtml(content)}</p>
            </div>`;
    } else {
        div.innerHTML = `
            <div class="bg-gradient-to-r from-primary-500 to-calm-500 rounded-2xl rounded-tr-md p-4 shadow-sm max-w-[80%]">
                <p class="text-white text-sm leading-relaxed">${escapeHtml(content)}</p>
            </div>`;
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const container = document.getElementById('chat-container');
    const div = document.createElement('div');
    div.id = 'typing-indicator';
    div.className = 'flex gap-3 fade-in';
    div.innerHTML = `
        <div class="w-8 h-8 bg-gradient-to-br from-primary-400 to-calm-500 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
            </svg>
        </div>
        <div class="bg-white rounded-2xl rounded-tl-md p-4 shadow-sm">
            <div class="typing-indicator flex gap-1">
                <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
            </div>
        </div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function updateEmotionBar(data) {
    const bar = document.getElementById('emotion-bar');
    bar.classList.remove('hidden');

    document.getElementById('current-emotion').textContent = data.emotion || '—';
    const stressScore = data.stress_score || 0;
    document.getElementById('stress-bar').style.width = `${stressScore}%`;
    document.getElementById('stress-value').textContent = stressScore;

    // Color the stress bar based on level
    const stressBar = document.getElementById('stress-bar');
    if (stressScore > 70) {
        stressBar.className = 'h-full bg-gradient-to-r from-warm-400 to-red-500 rounded-full transition-all duration-500';
    } else if (stressScore > 40) {
        stressBar.className = 'h-full bg-gradient-to-r from-yellow-400 to-warm-400 rounded-full transition-all duration-500';
    } else {
        stressBar.className = 'h-full bg-gradient-to-r from-primary-400 to-calm-400 rounded-full transition-all duration-500';
    }
}

async function endConversation() {
    if (!conversationId) return;

    const btn = document.getElementById('end-btn');
    btn.disabled = true;
    btn.textContent = 'Generating insights...';

    try {
        const response = await fetch('/api/conversation/end', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conversation_id: conversationId }),
        });

        if (!response.ok) throw new Error('Failed to end conversation');

        // Navigate to dashboard
        window.location.href = `/dashboard/${conversationId}`;
    } catch (error) {
        console.error('Error ending conversation:', error);
        btn.disabled = false;
        btn.textContent = 'End & View Insights';
        showError('Failed to generate insights. Please try again.');
    }
}

function disableInput(disabled) {
    document.getElementById('message-input').disabled = disabled;
    document.getElementById('send-btn').disabled = disabled;
}

function showError(message) {
    const container = document.getElementById('chat-container');
    const div = document.createElement('div');
    div.className = 'flex justify-center fade-in';
    div.innerHTML = `<p class="text-xs text-red-500 bg-red-50 px-3 py-1.5 rounded-full">${escapeHtml(message)}</p>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initConversation);

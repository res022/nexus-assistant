// Chat functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const questionInput = document.getElementById('questionInput');
    const sourceSelect = document.getElementById('sourceSelect');
    const submitBtn = document.getElementById('submitBtn');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const chatMessages = document.getElementById('chatMessages');
    const loadingIndicator = document.getElementById('loadingIndicator');

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    scrollToBottom();

    // Handle Enter key to send (Shift+Enter for new line)
    questionInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (questionInput.value.trim()) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Update loading message based on source selection
    sourceSelect.addEventListener('change', function() {
        if (sourceSelect.value === 'rules') {
            loadingIndicator.innerHTML = '<span class="spinner"></span> AI ფიქრობს და ეძებს რელევანტურ წესებს...';
        } else {
            loadingIndicator.innerHTML = '<span class="spinner"></span> AI ფიქრობს და ეძებს რელევანტურ კანონებს...';
        }
    });

    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const question = questionInput.value.trim();
        const source = sourceSelect.value;
        if (!question) return;

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> იგზავნება...';
        questionInput.disabled = true;
        loadingIndicator.style.display = 'block';
        addMessage('user', question);
        questionInput.value = '';

        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    source: source
                })
            });
            const data = await response.json();
            if (data.error) {
                addMessage('ai', '❌ შეცდომა: ' + (data.message || 'დაფიქსირდა შეცდომა'));
            } else {
                addMessage('ai', data.answer, data.sources, data.source_type);
            }
        } catch (error) {
            addMessage('ai', '❌ შეცდომა კავშირში');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '📤 გაგზავნა';
            questionInput.disabled = false;
            loadingIndicator.style.display = 'none';
            questionInput.focus();
        }
    });

    clearHistoryBtn.addEventListener('click', async function() {
        if (!confirm('დარწმუნებული ხართ?')) return;
        await fetch('/api/clear-history', { method: 'POST' });
        location.reload();
    });

    function addMessage(type, content, sources, sourceType) {
        const div = document.createElement('div');
        div.className = 'message ' + type + '-message';
        let html = '<div class="message-content">' + content + '</div>';
        // Sources removed - don't display them
        div.innerHTML = html;
        const empty = chatMessages.querySelector('.empty-chat');
        if (empty) empty.remove();
        chatMessages.appendChild(div);
        scrollToBottom();
    }
});

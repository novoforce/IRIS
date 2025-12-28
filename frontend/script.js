document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');

    // Focus input on load
    userInput.focus();

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = userInput.value.trim();
        if (!query) return;

        // 1. Add User Message
        appendMessage('user', query);
        userInput.value = '';

        // 2. Add Loading Indicator
        const loadingId = appendLoading();

        try {
            // 3. Call API
            // Note: Assuming API is running on localhost:8000
            const response = await fetch('http://localhost:8000/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();

            // 4. Remove Loading and Add Bot Response
            removeMessage(loadingId);
            appendBotResponse(data);

        } catch (error) {
            removeMessage(loadingId);
            appendMessage('bot', `Sorry, something went wrong. (${error.message})`);
        }
    });

    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;

        msgDiv.appendChild(contentDiv);
        chatHistory.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv.id = 'msg-' + Date.now();
    }

    function appendLoading() {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message';
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        msgDiv.appendChild(contentDiv);
        const id = 'loading-' + Date.now();
        msgDiv.id = id;
        chatHistory.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function appendBotResponse(data) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        let html = '';

        // Reasoning (if available in logs or data)
        // We'll try to find "Reasoning:" inside logs or use a generic success message
        const resultString = JSON.stringify(data.result, null, 2);

        html += `<div>Here is what I found:</div>`;

        // Formatted Result
        if (Array.isArray(data.result) && data.result.length > 0) {
            // Simple Table for array results
            html += generateTableHtml(data.result);
        } else {
            html += `<pre style="background:rgba(0,0,0,0.2);padding:10px;border-radius:6px;overflow-x:auto;">${resultString}</pre>`;
        }

        // SQL Badge
        if (data.sql) {
            html += `<div class="sql-badge">SQL: ${data.sql}</div>`;
        }

        // Latency
        if (data.latency) {
            html += `<div style="font-size:0.75rem;color:#888;margin-top:5px;">Time: ${data.latency.toFixed(2)}s</div>`;
        }

        contentDiv.innerHTML = html;
        msgDiv.appendChild(contentDiv);
        chatHistory.appendChild(msgDiv);
        scrollToBottom();
    }

    function generateTableHtml(dataArray) {
        if (!dataArray || dataArray.length === 0) return '';
        const headers = Object.keys(dataArray[0]);

        let table = '<table style="width:100%;border-collapse:collapse;margin-top:10px;font-size:0.9rem;">';

        // Header
        table += '<thead><tr style="border-bottom:1px solid rgba(255,255,255,0.2);">';
        headers.forEach(h => {
            table += `<th style="text-align:left;padding:8px;color:#a1a1aa;">${h}</th>`;
        });
        table += '</tr></thead>';

        // Body
        table += '<tbody>';
        dataArray.forEach(row => {
            table += '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">';
            headers.forEach(h => {
                table += `<td style="padding:8px;">${row[h]}</td>`;
            });
            table += '</tr>';
        });
        table += '</tbody></table>';
        return table;
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});

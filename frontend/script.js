document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const themeToggle = document.getElementById('theme-toggle');

    // Theme Toggle Logic
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

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
            // Append button placeholder
            html += `<button class="download-btn" id="dl-btn-${Date.now()}">⬇ Download CSV</button>`;
        } else {
            html += `<pre style="background:rgba(0,0,0,0.2);padding:10px;border-radius:6px;overflow-x:auto;">${resultString}</pre>`;
        }

        // SQL Badge
        if (data.sql) {
            html += `<div class="sql-badge">SQL: ${data.sql}</div>`;
        }

        // SQL Reasoning (Dropdown)
        if (data.sql_reasoning) {
            html += `
                <details class="reasoning-details">
                    <summary class="reasoning-summary">Show Reasoning</summary>
                    <div class="reasoning-content">${data.sql_reasoning}</div>
                </details>
            `;
        }

        // Latency
        if (data.latency) {
            html += `<div style="font-size:0.75rem;color:#888;margin-top:5px;">Time: ${data.latency.toFixed(2)}s</div>`;
        }

        contentDiv.innerHTML = html;
        msgDiv.appendChild(contentDiv);
        contentDiv.innerHTML = html;
        msgDiv.appendChild(contentDiv);
        chatHistory.appendChild(msgDiv);

        // Attach Event Listeners (e.g., Download Button)
        const dlBtn = msgDiv.querySelector('.download-btn');
        if (dlBtn && Array.isArray(data.result)) {
            dlBtn.addEventListener('click', () => {
                downloadCSV(data.result, `iris_data_${Date.now()}.csv`);
            });
        }

        scrollToBottom();
    }

    function downloadCSV(dataArray, filename) {
        if (!dataArray || !dataArray.length) return;

        const headers = Object.keys(dataArray[0]);
        const csvRows = [];

        // Header
        csvRows.push(headers.join(','));

        // Rows
        for (const row of dataArray) {
            const values = headers.map(header => {
                const escaped = ('' + row[header]).replace(/"/g, '\\"');
                return `"${escaped}"`;
            });
            csvRows.push(values.join(','));
        }

        const csvString = csvRows.join('\n');
        const blob = new Blob([csvString], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', filename);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    function generateTableHtml(dataArray) {
        if (!dataArray || dataArray.length === 0) return '';
        const headers = Object.keys(dataArray[0]);

        let table = '<div class="table-container"><table>';

        // Header
        table += '<thead><tr>';
        headers.forEach(h => {
            // Basic formatting for headers
            table += `<th>${h}</th>`;
        });
        table += '</tr></thead>';

        // Body
        table += '<tbody>';
        dataArray.forEach(row => {
            table += '<tr>';
            headers.forEach(h => {
                table += `<td>${row[h]}</td>`;
            });
            table += '</tr>';
        });
        table += '</tbody></table></div>';
        return table;
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});

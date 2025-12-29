document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const themeToggle = document.getElementById('theme-toggle');
    const sessionList = document.getElementById('session-list');
    const newChatBtn = document.getElementById('new-chat-btn');

    // Generate or retrieve Session ID
    let sessionId = localStorage.getItem('chat_session_id');
    if (!sessionId) {
        startNewChat();
    } else {
        // If we have a session, try to load it (or just load list)
        loadSessions();
        // Note: We don't automatically load history to avoid jarring UX, 
        // but we could. For now, we stick to current session logic.
    }

    // New Chat Button
    newChatBtn.addEventListener('click', () => {
        startNewChat();
    });

    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');

    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    async function startNewChat() {
        sessionId = crypto.randomUUID();
        localStorage.setItem('chat_session_id', sessionId);

        // Clear UI
        chatHistory.innerHTML = '';
        appendBotResponse({ result: "Starting a new conversation..." }); // Temporary msg
        setTimeout(() => {
            chatHistory.innerHTML = `
                <div class="message bot-message">
                    <div class="message-content">
                        Hello! I am IRIS, your Intelligent Retail Insights System.
                        <br>Ask me anything about your sales data.
                    </div>
                </div>`;
        }, 500);

        // Ideally verify with backend or register session
        try {
            await fetch('http://localhost:8000/sessions', { method: 'POST' });
        } catch (e) { console.error("Failed to register session", e); }

        await loadSessions();
        highlightSession(sessionId);
    }

    async function loadSessions() {
        try {
            const res = await fetch('http://localhost:8000/sessions');
            if (res.ok) {
                const sessions = await res.json();
                renderSessionList(sessions);
            }
        } catch (e) { console.error("Failed to load sessions", e); }
    }

    function renderSessionList(sessions) {
        sessionList.innerHTML = '';
        // Sort by recency (if we had timestamp, for now just list)
        // Reverse to show newest (if list is chronological)
        sessions.reverse().forEach(s => {
            const div = document.createElement('div');
            div.className = 'session-item';
            div.textContent = `Session ${s.id.substring(0, 8)}...`;
            div.title = s.id;
            if (s.id === sessionId) div.classList.add('active');

            div.addEventListener('click', () => loadSessionHistory(s.id));
            sessionList.appendChild(div);
        });
    }

    async function loadSessionHistory(id) {
        if (id === sessionId) return; // Already here

        sessionId = id;
        localStorage.setItem('chat_session_id', sessionId);
        highlightSession(id);

        // Clear and Load
        chatHistory.innerHTML = '';
        const loadingId = appendLoading();

        try {
            const res = await fetch(`http://localhost:8000/sessions/${id}`);
            if (res.ok) {
                const history = await res.json();
                removeMessage(loadingId);

                if (history.length === 0) {
                    // Empty session (maybe new)
                    chatHistory.innerHTML = `<div class="message bot-message"><div class="message-content">New Conversation</div></div>`;
                } else {
                    history.forEach(msg => {
                        const sender = msg.role === 'user' ? 'user' : 'bot';
                        // For bot, we might need to parse rich content if we saved it rich.
                        // Currently API returns simple text 'content'. 
                        // If it was SQL result, it might be raw string in text.
                        // For simplicity, just append text. 
                        appendMessage(sender, msg.content);
                    });
                }
            } else {
                throw new Error("Failed to load");
            }
        } catch (e) {
            removeMessage(loadingId);
            appendMessage('bot', "Could not load history for this session.");
        }
    }

    function highlightSession(id) {
        document.querySelectorAll('.session-item').forEach(el => {
            el.classList.remove('active');
            if (el.title === id) el.classList.add('active');
        });
    }

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

        // Refresh session list just in case (e.g. if this was first msg)
        // Optimization: Debounce or only do it once per session start

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
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();

            // 4. Remove Loading and Add Bot Response
            removeMessage(loadingId);
            appendBotResponse(data);

            // Reload sessions list to show update (create new if needed)
            loadSessions();

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

    // System Status Polling
    const statusIndicator = document.querySelector('.status-indicator');
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');

    async function checkSystemStatus() {
        try {
            // Note: Assuming API is running on localhost:8000
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000); // 2s timeout

            const response = await fetch('http://localhost:8000/', {
                method: 'GET',
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (response.ok) {
                setOnline();
            } else {
                setOffline();
            }
        } catch (error) {
            setOffline();
        }
    }

    function setOnline() {
        statusIndicator.classList.remove('offline');
        statusDot.classList.remove('offline');
        statusText.textContent = 'System Online';
    }

    function setOffline() {
        statusIndicator.classList.add('offline');
        statusDot.classList.add('offline');
        statusText.textContent = 'System Offline';
    }

    // Check immediately and then every 5 seconds
    checkSystemStatus();
    setInterval(checkSystemStatus, 5000);
});

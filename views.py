from fastapi.responses import HTMLResponse


def render_home() -> HTMLResponse:
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Investing Advisor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: #0f1117;
            color: #e2e8f0;
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        /* ── Sidebar ── */
        .sidebar {
            width: 270px;
            min-width: 270px;
            background: #161b27;
            border-right: 1px solid #1e2535;
            display: flex;
            flex-direction: column;
            padding: 20px 14px;
            gap: 16px;
            overflow: hidden;
        }
        .tools-scroll {
            flex: 1;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: #1e2535 transparent;
        }
        .logo { display: flex; align-items: center; gap: 10px; padding: 0 6px; }
        .logo-icon {
            width: 34px; height: 34px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 9px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1em; flex-shrink: 0;
        }
        .logo-text h1 { font-size: 0.92em; font-weight: 700; color: #f1f5f9; }
        .logo-text p { font-size: 0.7em; color: #64748b; margin-top: 1px; }

        .divider { height: 1px; background: #1e2535; margin: 0 6px; }

        .section-label {
            font-size: 0.65em; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.1em;
            color: #475569; padding: 0 6px;
        }

        /* MCP Server badge */
        .mcp-server {
            background: #0f2744;
            border: 1px solid #1e3a5f;
            border-radius: 10px;
            padding: 12px;
        }
        .mcp-server .server-row {
            display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
        }
        .server-dot {
            width: 7px; height: 7px; border-radius: 50%;
            background: #22c55e; box-shadow: 0 0 5px #22c55e; flex-shrink: 0;
        }
        .server-name { font-size: 0.8em; font-weight: 600; color: #93c5fd; }
        .server-url { font-size: 0.68em; color: #475569; word-break: break-all; margin-top: 2px; }

        /* Tools list */
        .tools-list { display: flex; flex-direction: column; gap: 3px; }
        .tool-item {
            display: flex; align-items: center; gap: 8px;
            padding: 7px 8px; border-radius: 7px;
            font-size: 0.78em; color: #64748b;
            border: 1px solid transparent;
            transition: all 0.25s;
        }
        .tool-item.active {
            background: #1e2d45; border-color: #3b82f6; color: #93c5fd;
        }
        .tool-item.active .tool-dot { background: #3b82f6; box-shadow: 0 0 6px #3b82f6; }
        .tool-dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: #1e2535; flex-shrink: 0; transition: all 0.3s;
        }
        .tool-name { font-weight: 500; font-size: 0.95em; }

        /* ── Main area ── */
        .main {
            flex: 1; display: flex; flex-direction: column; overflow: hidden;
        }

        /* Chat + Flow panel split */
        .content {
            flex: 1; display: flex; overflow: hidden;
        }

        /* Chat */
        .chat-col {
            flex: 1; display: flex; flex-direction: column; overflow: hidden;
            border-right: 1px solid #1e2535;
        }
        .chat-header {
            padding: 14px 20px; border-bottom: 1px solid #1e2535;
            display: flex; align-items: center; gap: 8px;
            font-size: 0.85em; color: #94a3b8;
        }
        .status-dot {
            width: 7px; height: 7px; border-radius: 50%;
            background: #22c55e; box-shadow: 0 0 5px #22c55e;
        }
        .messages {
            flex: 1; overflow-y: auto; padding: 20px;
            display: flex; flex-direction: column; gap: 14px;
            scrollbar-width: thin; scrollbar-color: #1e2535 transparent;
        }
        .empty-state {
            flex: 1; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            gap: 10px; color: #475569; text-align: center;
        }
        .empty-icon { font-size: 2em; }
        .empty-state h2 { font-size: 1em; color: #94a3b8; font-weight: 600; }
        .empty-state p { font-size: 0.82em; max-width: 280px; line-height: 1.6; }
        .suggestions {
            display: flex; flex-wrap: wrap; gap: 6px;
            justify-content: center; margin-top: 6px;
        }
        .suggestion {
            background: #161b27; border: 1px solid #1e2535;
            color: #94a3b8; padding: 6px 12px; border-radius: 20px;
            font-size: 0.78em; cursor: pointer; transition: all 0.15s;
        }
        .suggestion:hover { border-color: #3b82f6; color: #93c5fd; background: #1e2d45; }

        .msg-row { display: flex; flex-direction: column; gap: 4px; animation: fadeUp 0.2s ease; }
        @keyframes fadeUp { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }

        .bubble {
            max-width: 80%; padding: 11px 14px; border-radius: 14px;
            font-size: 0.88em; line-height: 1.65; white-space: pre-wrap;
        }
        .bubble.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white; border-bottom-right-radius: 4px;
        }
        .bubble.assistant {
            align-self: flex-start; background: #161b27;
            color: #e2e8f0; border: 1px solid #1e2535; border-bottom-left-radius: 4px;
        }
        .bubble.typing {
            align-self: flex-start; background: #161b27;
            border: 1px solid #1e2535; color: #475569; font-style: italic;
        }

        .input-bar {
            padding: 14px 20px; border-top: 1px solid #1e2535;
            display: flex; gap: 8px; align-items: flex-end;
        }
        .input-wrap {
            flex: 1; background: #161b27; border: 1px solid #1e2535;
            border-radius: 12px; padding: 10px 14px; transition: border-color 0.2s;
        }
        .input-wrap:focus-within { border-color: #6366f1; }
        textarea {
            width: 100%; background: none; border: none; outline: none;
            color: #e2e8f0; font-size: 0.88em; font-family: inherit;
            resize: none; line-height: 1.5; max-height: 100px; overflow-y: auto;
        }
        textarea::placeholder { color: #334155; }
        .send-btn {
            width: 40px; height: 40px; border-radius: 10px; border: none;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white; font-size: 1em; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            transition: opacity 0.2s; flex-shrink: 0;
        }
        .send-btn:disabled { opacity: 0.35; cursor: default; }
        .send-btn:not(:disabled):hover { opacity: 0.85; }

        /* ── Flow panel ── */
        .flow-col {
            width: 300px; min-width: 300px;
            display: flex; flex-direction: column; overflow: hidden;
        }
        .flow-header {
            padding: 14px 18px; border-bottom: 1px solid #1e2535;
            font-size: 0.8em; color: #64748b; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.06em;
        }
        .flow-body {
            flex: 1; overflow-y: auto; padding: 16px;
            display: flex; flex-direction: column; gap: 6px;
            scrollbar-width: thin; scrollbar-color: #1e2535 transparent;
        }
        .flow-empty {
            flex: 1; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            color: #1e2535; font-size: 0.8em; gap: 8px; text-align: center;
            padding: 20px;
        }
        .flow-empty-icon { font-size: 2em; }

        /* Step cards */
        .step {
            background: #161b27; border: 1px solid #1e2535;
            border-radius: 10px; padding: 10px 12px;
            animation: fadeUp 0.25s ease;
            transition: border-color 0.3s;
        }
        .step.active { border-color: #6366f1; }
        .step.done { border-color: #1e2535; opacity: 0.7; }

        .step-header {
            display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
        }
        .step-num {
            width: 20px; height: 20px; border-radius: 50%;
            background: #1e2535; border: 1px solid #334155;
            font-size: 0.65em; font-weight: 700; color: #64748b;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0; transition: all 0.3s;
        }
        .step.active .step-num { background: #6366f1; border-color: #6366f1; color: white; }
        .step.done .step-num { background: #22c55e; border-color: #22c55e; color: white; }
        .step-title { font-size: 0.78em; font-weight: 600; color: #94a3b8; }
        .step.active .step-title { color: #c7d2fe; }

        .step-body { font-size: 0.73em; color: #475569; line-height: 1.5; padding-left: 28px; }
        .step-body .tag {
            display: inline-block; background: #0f2744;
            border: 1px solid #1e3a5f; color: #60a5fa;
            padding: 1px 7px; border-radius: 4px; margin: 2px 2px 0 0;
            font-family: monospace; font-size: 0.95em;
        }
        .step-body .val { color: #a78bfa; }

        .connector {
            width: 1px; height: 10px; background: #1e2535;
            margin: 0 auto; margin-left: 19px;
        }
    </style>
</head>
<body>

<!-- Sidebar -->
<div class="sidebar">
    <div class="logo">
        <div class="logo-icon">📈</div>
        <div class="logo-text">
            <h1>Investing Advisor</h1>
            <p>Claude + MCP</p>
        </div>
    </div>

    <div class="divider"></div>

    <div class="section-label">MCP Server</div>
    <div class="mcp-server">
        <div class="server-row">
            <div class="server-dot"></div>
            <div class="server-name">Financial Datasets</div>
        </div>
        <div class="server-url">mcp.financialdatasets.ai/api</div>
    </div>

    <div class="section-label">Available Tools</div>
    <div class="tools-scroll">
        <div class="tools-list" id="toolsList">
            <div style="font-size:0.75em;color:#334155;padding:6px 8px;">Loading…</div>
        </div>
    </div>
</div>

<!-- Main -->
<div class="main">
    <div class="content">

        <!-- Chat -->
        <div class="chat-col">
            <div class="chat-header">
                <div class="status-dot"></div>
                <span>AI Advisor</span>
            </div>

            <div class="messages" id="messages">
                <div class="empty-state" id="emptyState">
                    <div class="empty-icon">💬</div>
                    <h2>Ask me anything about stocks</h2>
                    <p>Watch the flow panel on the right to see MCP in action step by step.</p>
                    <div class="suggestions">
                        <div class="suggestion" onclick="ask(this)">What's Apple's stock price?</div>
                        <div class="suggestion" onclick="ask(this)">Analyze NVDA</div>
                        <div class="suggestion" onclick="ask(this)">Tesla income statement</div>
                        <div class="suggestion" onclick="ask(this)">Microsoft insider trades</div>
                    </div>
                </div>
            </div>

            <div class="input-bar">
                <div class="input-wrap">
                    <textarea id="input" rows="1" placeholder="Ask about any stock…"
                        oninput="autoResize(this)"
                        onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea>
                </div>
                <button class="send-btn" id="sendBtn" onclick="send()">↑</button>
            </div>
        </div>

        <!-- Flow panel -->
        <div class="flow-col">
            <div class="flow-header">⚡ MCP Flow</div>
            <div class="flow-body" id="flowBody">
                <div class="flow-empty" id="flowEmpty">
                    <div class="flow-empty-icon">🔄</div>
                    Ask a question to see the MCP flow here step by step.
                </div>
            </div>
        </div>

    </div>
</div>

<script>
    const messages = document.getElementById('messages');
    const input    = document.getElementById('input');
    const sendBtn  = document.getElementById('sendBtn');
    const flowBody = document.getElementById('flowBody');

    // Load tools into sidebar
    fetch('/api/tools').then(r => r.json()).then(tools => {
        document.getElementById('toolsList').innerHTML = tools.map(t => `
            <div class="tool-item" id="tool-${t.name}">
                <div class="tool-dot"></div>
                <div class="tool-name">${t.name}</div>
            </div>`).join('');
    });

    function autoResize(el) {
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 100) + 'px';
    }

    function ask(el) { input.value = el.textContent; send(); }

    function clearEmpty() { document.getElementById('emptyState')?.remove(); }

    function addBubble(text, role) {
        clearEmpty();
        const row = document.createElement('div');
        row.className = 'msg-row';
        const b = document.createElement('div');
        b.className = 'bubble ' + role;
        b.textContent = text;
        row.appendChild(b);
        messages.appendChild(row);
        messages.scrollTop = messages.scrollHeight;
        return { row, bubble: b };
    }

    // Flow panel helpers
    let stepCount = 0;
    function resetFlow() {
        stepCount = 0;
        document.getElementById('flowEmpty')?.remove();
        flowBody.innerHTML = '';
    }

    function addStep(title, bodyHTML, state = 'active') {
        stepCount++;
        const num = stepCount;

        if (flowBody.children.length > 0) {
            const conn = document.createElement('div');
            conn.className = 'connector';
            flowBody.appendChild(conn);
        }

        const el = document.createElement('div');
        el.className = `step ${state}`;
        el.id = `step-${num}`;
        el.innerHTML = `
            <div class="step-header">
                <div class="step-num">${num}</div>
                <div class="step-title">${title}</div>
            </div>
            <div class="step-body">${bodyHTML}</div>`;
        flowBody.appendChild(el);
        flowBody.scrollTop = flowBody.scrollHeight;
        return el;
    }

    function completeStep(el) {
        el.classList.remove('active');
        el.classList.add('done');
    }

    function highlightTools(names, on) {
        document.querySelectorAll('.tool-item').forEach(el => el.classList.remove('active'));
        if (on) names.forEach(n => document.getElementById('tool-' + n)?.classList.add('active'));
    }

    async function send() {
        const message = input.value.trim();
        if (!message) return;

        input.value = '';
        input.style.height = 'auto';
        sendBtn.disabled = true;

        addBubble(message, 'user');
        const { row: typingRow } = addBubble('Thinking…', 'typing');

        // Reset flow panel
        resetFlow();

        // Step 1
        const s1 = addStep('User question', `<span class="val">"${message}"</span>`);

        // Step 2
        await sleep(400);
        completeStep(s1);
        const s2 = addStep('Ask MCP server for tools',
            `POST <span class="tag">mcp.financialdatasets.ai</span><br>session.list_tools()`);

        // Step 3
        await sleep(600);
        completeStep(s2);
        const s3 = addStep('Send question + tools to Claude',
            `model <span class="tag">claude-sonnet-4-6</span><br>Claude decides which tools to call`);

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'message=' + encodeURIComponent(message)
            });
            const data = await res.json();

            typingRow.remove();

            if (data.error) {
                completeStep(s3);
                addBubble('Error: ' + data.error, 'assistant');
                return;
            }

            // Step 4 — show which tools Claude called
            completeStep(s3);
            const toolTags = data.tools.length
                ? data.tools.map(t => `<span class="tag">${t}</span>`).join(' ')
                : '<span style="color:#475569">No tools needed</span>';
            const s4 = addStep('Claude calls MCP tools',
                `${toolTags}<br><span style="color:#334155;font-size:0.9em">Fetching live data in parallel</span>`);

            // Highlight tools in sidebar
            highlightTools(data.tools, true);

            // Step 5
            await sleep(400);
            completeStep(s4);
            const s5 = addStep('MCP returns live data',
                `<span class="tag">mcp.financialdatasets.ai</span><br>Real-time market data received`);

            await sleep(400);
            completeStep(s5);

            // Step 6
            const s6 = addStep('Claude writes final answer', 'Synthesizing data into response…');
            await sleep(300);
            completeStep(s6);

            addBubble(data.message, 'assistant');

            setTimeout(() => highlightTools([], false), 5000);

        } catch (e) {
            typingRow.remove();
            addBubble('Something went wrong. Please try again.', 'assistant');
        }

        sendBtn.disabled = false;
        input.focus();
    }

    function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
</script>
</body>
</html>""")

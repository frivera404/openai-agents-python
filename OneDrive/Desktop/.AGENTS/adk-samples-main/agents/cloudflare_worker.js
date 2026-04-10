// Cloudflare Worker: Agent Command & Communication Platform
// Serves a simple HTML UI at GET / and accepts commands at POST /command
// Environment variables (set in the Worker):
// - WORKER_WEBHOOK_URL
// - WORKER_WEBHOOK_SECRET
// - CLAWCODE_API_URL

const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Agent Command & Communication Platform</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    textarea { width: 100%; height: 150px; }
    button { padding: 0.5rem 1rem; margin-top: 0.5rem; }
    #response { margin-top: 1rem; white-space: pre-wrap; font-family: monospace; }
  </style>
</head>
<body>
  <h1>Agent Command & Communication Platform</h1>
  <p>Enter a command below to direct ClawCode agents or trigger deployments:</p>
  <textarea id="cmd" placeholder="e.g. deploy-agent backend-developer"></textarea>
  <br />
  <button id="send">Send Command</button>
  <div id="response"></div>
  <script>
    document.getElementById('send').addEventListener('click', async () => {
      const command = document.getElementById('cmd').value.trim();
      if (!command) { alert('Please enter a command.'); return; }
      const res = await fetch('/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      });
      let data;
      try { data = await res.json(); } catch (_) { data = { error: 'Invalid response' }; }
      document.getElementById('response').textContent = JSON.stringify(data, null, 2);
    });
  </script>
</body>
</html>`;

const jsonResponse = (obj, init = {}) => new Response(JSON.stringify(obj), Object.assign({ headers: { 'Content-Type': 'application/json' } }, init));

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === 'GET' && url.pathname === '/') {
      return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
    }

    if (request.method === 'POST' && url.pathname === '/command') {
      let body;
      try {
        body = await request.json();
      } catch (err) {
        return jsonResponse({ error: 'Invalid JSON payload' }, { status: 400 });
      }
      const command = body && body.command;
      if (!command || typeof command !== 'string' || !command.trim()) {
        return jsonResponse({ error: 'Missing command' }, { status: 400 });
      }

      const payload = {
        event: 'agent_command',
        command: command.trim(),
        timestamp: new Date().toISOString(),
      };

      // Forward to webhook if configured (don't block on errors)
      if (env.WORKER_WEBHOOK_URL) {
        const headers = { 'Content-Type': 'application/json' };
        if (env.WORKER_WEBHOOK_SECRET) headers['X-Webhook-Secret'] = env.WORKER_WEBHOOK_SECRET;
        try {
          await fetch(env.WORKER_WEBHOOK_URL, { method: 'POST', headers, body: JSON.stringify(payload) });
        } catch (e) {
          // swallow errors intentionally
        }
      }

      // Optionally forward to CLAWCODE API and capture a result
      let result = null;
      if (env.CLAWCODE_API_URL) {
        try {
          const resp = await fetch(env.CLAWCODE_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command.trim() }),
          });
          const contentType = resp.headers.get('content-type') || '';
          if (contentType.includes('application/json')) {
            result = await resp.json();
          } else {
            result = await resp.text();
          }
        } catch (err) {
          result = `Error forwarding to ClawCode: ${err.message || err}`;
        }
      }

      return jsonResponse({ status: 'received', command: command.trim(), result });
    }

    return new Response('Not Found', { status: 404 });
  },
};

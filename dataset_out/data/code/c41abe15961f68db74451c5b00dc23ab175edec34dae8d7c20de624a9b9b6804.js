const fs = require('fs');

const url = 'http://localhost:3002/api/agent/launch';
const body = {
  agentId: 'customer-service',
  prompt: 'Node capture - ping',
  model: 'gpt-4.1',
  temperature: 0.0,
};

(async () => {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const text = await res.text();
    fs.writeFileSync('server_post.log', text, { encoding: 'utf8' });
    console.log('WROTE: server_post.log');
    console.log(text);
  } catch (err) {
    const msg = `ERROR: ${err.stack || err}`;
    fs.writeFileSync('server_post.log', msg, { encoding: 'utf8' });
    console.error(msg);
    process.exit(1);
  }
})();

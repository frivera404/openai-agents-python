// ============================================================
// BristolBot Pro — Cloudflare Worker
// Product: Confidence funnel → bristoltalks.com/productconfidence
// Cloudflare features: Workers + D1 (chat history) + Claude Sonnet
// Deploy: wrangler deploy --config wrangler-bristolbot-pro.toml
// Bindings needed: DB (D1), ANTHROPIC_KEY (secret)
// ============================================================

const PRO_MODEL = "claude-sonnet-4-6";
const FREE_MODEL = "claude-haiku-4-5-20251001";

const BRISTOL_SYSTEM = `You are BristolBot Pro — the premium AI assistant for BristolTalks.com, Bristol Connecticut's community platform.

You are a deep expert on all things Bristol CT: history, government, businesses, events, development projects, neighborhoods, and civic life.

KEY FACTS:
- Bristol CT population ~60,000, Hartford County, central CT
- Nicknamed "Clock City", "Bell City", "Mum City"
- ESPN HQ at 935 Middle St, founded Sept 7 1979 by Bill Rasmussen
- Barnes Group founded 1857 by Wallace Barnes
- Lake Compounce est. 1846, oldest continuously operating amusement park in America
- Mayor's Office: (860) 584-6210 | City Hall: (860) 584-6100
- Bristol Hospital: (860) 585-3000 | Police non-emergency: (860) 584-3011

BUSINESS MODE INSTRUCTIONS:
When the user asks business-related questions, provide detailed research including:
- Local market context (who else is in this space in Bristol)
- Relevant city permits/regulations (point to Building Dept at 860-584-6185)
- Funding opportunities (Bristol Development Authority, CT DECD)
- Practical next steps with specific Bristol contacts

Keep answers focused on Bristol CT. For business research be thorough and detailed.
For general questions be concise (under 150 words unless asked for detail).`;

export default {
  async fetch(req, env) {
    const url = new URL(req.url);

    if (req.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (url.pathname === "/api/chat" && req.method === "POST") {
      return handleChat(req, env);
    }

    if (url.pathname === "/api/history" && req.method === "GET") {
      return handleHistory(req, env);
    }

    if (url.pathname === "/api/health") {
      return new Response(JSON.stringify({ ok: true, product: "BristolBot Pro", version: "1.0" }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response(PRO_HTML, {
      headers: { "Content-Type": "text/html;charset=UTF-8", "Cache-Control": "public, max-age=60" }
    });
  }
};

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
  };
}

async function handleChat(req, env) {
  let body;
  try { body = await req.json(); } catch {
    return jsonError("Bad JSON", 400);
  }

  const { messages, sessionId, isPro } = body;
  if (!messages || !messages.length) return jsonError("messages required", 400);
  if (!env.ANTHROPIC_KEY) return jsonError("AI not configured", 500);

  const model = isPro ? PRO_MODEL : FREE_MODEL;

  const upstream = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": env.ANTHROPIC_KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model,
      max_tokens: isPro ? 1200 : 600,
      system: BRISTOL_SYSTEM,
      messages
    })
  });

  const data = await upstream.json();
  const reply = data.content && data.content[0] ? data.content[0].text : null;
  if (!reply) return jsonError("AI response empty", 502);

  // Save to D1 if sessionId provided
  if (sessionId && env.DB) {
    const lastMsg = messages[messages.length - 1];
    try {
      await env.DB.prepare(
        "INSERT INTO pro_chat_history (session_id, role, content, model, created_at) VALUES (?, ?, ?, ?, ?)"
      ).bind(sessionId, "user", lastMsg.content, model, new Date().toISOString()).run();

      await env.DB.prepare(
        "INSERT INTO pro_chat_history (session_id, role, content, model, created_at) VALUES (?, ?, ?, ?, ?)"
      ).bind(sessionId, "assistant", reply, model, new Date().toISOString()).run();
    } catch {
      // Non-fatal if table doesn't exist
    }
  }

  return new Response(JSON.stringify({ ok: true, reply, model }), {
    headers: { ...corsHeaders(), "Content-Type": "application/json" }
  });
}

async function handleHistory(req, env) {
  const url = new URL(req.url);
  const sessionId = url.searchParams.get("sessionId");
  if (!sessionId) return jsonError("sessionId required", 400);

  if (!env.DB) return new Response(JSON.stringify({ ok: true, history: [] }), {
    headers: { ...corsHeaders(), "Content-Type": "application/json" }
  });

  try {
    const rows = await env.DB.prepare(
      "SELECT role, content FROM pro_chat_history WHERE session_id = ? ORDER BY created_at ASC LIMIT 100"
    ).bind(sessionId).all();

    return new Response(JSON.stringify({ ok: true, history: rows.results || [] }), {
      headers: { ...corsHeaders(), "Content-Type": "application/json" }
    });
  } catch {
    return new Response(JSON.stringify({ ok: true, history: [] }), {
      headers: { ...corsHeaders(), "Content-Type": "application/json" }
    });
  }
}

function jsonError(msg, status) {
  return new Response(JSON.stringify({ error: msg }), {
    status, headers: { ...corsHeaders(), "Content-Type": "application/json" }
  });
}

// ── BristolBot Pro HTML ───────────────────────────────────────

const PRO_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>BristolBot Pro — Your Personal Bristol CT AI Assistant</title>
<meta name="description" content="BristolBot Pro: AI assistant with chat history, Claude Sonnet, and Bristol business research mode."/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
:root{--gold:#f59e0b;--gold-bright:#fbbf24;--gold-glow:rgba(245,158,11,0.25);--bg:#080808;--bg2:#0c0c0d;--card:#0f0f10;--border:rgba(245,158,11,0.15);--border-sub:rgba(255,255,255,0.07);--text:#e9e9eb;--text-mid:#9898a5;--text-dim:#5a5a62;--white:#ffffff;--gradient:linear-gradient(135deg,#f59e0b,#d97706);--r:10px;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',system-ui,sans-serif;display:flex;flex-direction:column}
header{background:rgba(8,8,8,0.95);border-bottom:1px solid var(--border-sub);padding:0 20px;height:56px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.logo{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;color:var(--gold)}
.logo span{color:var(--text-dim);font-weight:400;font-size:12px}
.mode-toggle{display:flex;gap:6px}
.mode-btn{background:rgba(255,255,255,0.05);border:1px solid var(--border);color:var(--text-mid);padding:5px 12px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;transition:all .2s;font-family:'DM Sans',sans-serif}
.mode-btn.active{background:rgba(245,158,11,0.1);border-color:rgba(245,158,11,0.3);color:var(--gold)}
.chat-area{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:75%;padding:12px 16px;border-radius:12px;font-size:14px;line-height:1.6}
.msg.user{background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);color:var(--white);align-self:flex-end;border-radius:12px 12px 2px 12px}
.msg.bot{background:var(--card);border:1px solid var(--border-sub);color:var(--text);align-self:flex-start;border-radius:12px 12px 12px 2px}
.msg.loading{color:var(--text-dim);font-style:italic}
.msg-model{font-size:10px;color:var(--text-dim);margin-top:5px;font-weight:600;letter-spacing:.05em;text-transform:uppercase}
.chat-footer{border-top:1px solid var(--border-sub);padding:16px 20px;background:var(--bg);flex-shrink:0}
.chat-row{display:flex;gap:10px}
textarea.chat-in{flex:1;background:rgba(255,255,255,0.04);border:1px solid rgba(245,158,11,0.2);border-radius:8px;padding:10px 14px;color:var(--white);font-size:14px;font-family:'DM Sans',sans-serif;outline:none;resize:none;min-height:44px;max-height:120px;transition:border-color .2s;line-height:1.5}
textarea.chat-in:focus{border-color:var(--gold)}
.send-btn{background:var(--gradient);color:#000;border:none;padding:10px 18px;border-radius:8px;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:14px;cursor:pointer;transition:opacity .2s;white-space:nowrap;align-self:flex-end}
.send-btn:hover{opacity:.9}
.send-btn:disabled{opacity:.4;cursor:not-allowed}
.footer-note{font-size:11px;color:var(--text-dim);margin-top:8px;text-align:center}
.sugs{display:flex;flex-wrap:wrap;gap:7px;padding:0 0 12px}
.sug{background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:999px;padding:5px 12px;font-size:12px;color:var(--text-mid);cursor:pointer;transition:all .2s;white-space:nowrap}
.sug:hover{background:rgba(245,158,11,0.08);border-color:rgba(245,158,11,0.2);color:var(--gold)}
.history-badge{background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);border-radius:999px;padding:3px 10px;font-size:11px;color:var(--gold);font-weight:600}
</style>
</head>
<body>
<header>
  <div class="logo">BristolBot <span>PRO BETA</span></div>
  <div style="display:flex;align-items:center;gap:10px">
    <div class="history-badge" id="hist-badge" style="display:none">&#128190; History On</div>
    <div class="mode-toggle">
      <button class="mode-btn active" id="btn-general" onclick="setMode('general')">General</button>
      <button class="mode-btn" id="btn-business" onclick="setMode('business')">Business</button>
    </div>
  </div>
</header>

<div class="chat-area" id="chat-area">
  <div class="sugs" id="sugs">
    <div class="sug" onclick="sendMsg(this.textContent)">What's happening in Bristol this week?</div>
    <div class="sug" onclick="sendMsg(this.textContent)">Tell me about ESPN's history in Bristol</div>
    <div class="sug" onclick="sendMsg(this.textContent)">How do I get a business permit in Bristol CT?</div>
    <div class="sug" onclick="sendMsg(this.textContent)">Best places to eat in Bristol CT?</div>
    <div class="sug" onclick="sendMsg(this.textContent)">What is Lake Compounce?</div>
  </div>
  <div class="msg bot">
    <div>Hello! I'm BristolBot Pro &mdash; your AI assistant for all things Bristol CT. I have deep knowledge of local history, businesses, government, events, and more.</div>
    <div class="msg-model">Claude Sonnet &middot; Pro Mode</div>
  </div>
</div>

<div class="chat-footer">
  <div class="chat-row">
    <textarea class="chat-in" id="chat-in" rows="1" placeholder="Ask anything about Bristol CT…"></textarea>
    <button class="send-btn" id="send-btn" onclick="sendFromInput()">Send</button>
  </div>
  <div class="footer-note">BristolBot Pro &middot; Powered by Claude Sonnet + Cloudflare Workers + D1 &middot; <a href="https://bristoltalks-site.riveraf30.workers.dev/productconfidence" style="color:var(--gold)">Upgrade to Pro &rarr;</a></div>
</div>

<script>
var chatHistory=[];
var mode='general';
var sessionId=localStorage.getItem('bbpro_session')||(function(){var id='s'+Date.now().toString(36);localStorage.setItem('bbpro_session',id);return id;})();

// Show history badge if returning user
if(localStorage.getItem('bbpro_msgs')){
  document.getElementById('hist-badge').style.display='inline-flex';
}

function setMode(m){
  mode=m;
  document.getElementById('btn-general').className='mode-btn'+(m==='general'?' active':'');
  document.getElementById('btn-business').className='mode-btn'+(m==='business'?' active':'');
  var placeholder=m==='business'?'Research Bristol market, permits, competitors…':'Ask anything about Bristol CT…';
  document.getElementById('chat-in').placeholder=placeholder;
}

function sendFromInput(){
  var v=document.getElementById('chat-in').value.trim();
  if(v){document.getElementById('chat-in').value='';sendMsg(v);}
}

document.getElementById('chat-in').addEventListener('keydown',function(e){
  if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendFromInput();}
});

async function sendMsg(text){
  document.getElementById('sugs').style.display='none';
  var area=document.getElementById('chat-area');
  var um=document.createElement('div');um.className='msg user';um.textContent=text;area.appendChild(um);
  chatHistory.push({role:'user',content:(mode==='business'?'[BUSINESS MODE] ':'')+text});

  var lm=document.createElement('div');lm.className='msg bot loading';lm.textContent='Thinking…';area.appendChild(lm);
  area.scrollTop=area.scrollHeight;

  var btn=document.getElementById('send-btn');btn.disabled=true;

  try{
    var res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({messages:chatHistory,sessionId:sessionId,isPro:true})});
    var data=await res.json();
    if(data.ok){
      chatHistory.push({role:'assistant',content:data.reply});
      lm.className='msg bot';
      lm.innerHTML='<div>'+escHtml(data.reply)+'</div><div class="msg-model">'+data.model+'</div>';
      localStorage.setItem('bbpro_msgs','1');
      document.getElementById('hist-badge').style.display='inline-flex';
    }else{
      lm.textContent='Error: '+(data.error||'Unknown error');
    }
  }catch(e){
    lm.textContent='Connection error. Please try again.';
  }
  btn.disabled=false;area.scrollTop=area.scrollHeight;
}

function escHtml(t){
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
}
</script>
</body>
</html>`;

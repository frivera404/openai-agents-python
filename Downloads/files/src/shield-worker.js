// ============================================================
// BusinessShield AI — Cloudflare Worker
// Product: Protect funnel → bristoltalks.com/productprotect
// Cloudflare features: Workers + D1 + Turnstile + Claude Haiku
// Deploy: wrangler deploy --config wrangler-shield.toml
// Bindings needed: DB (D1), ANTHROPIC_KEY (secret), TURNSTILE_SECRET (secret)
// ============================================================

export default {
  async fetch(req, env) {
    const url = new URL(req.url);

    if (req.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (url.pathname === "/api/scan" && req.method === "POST") {
      return handleScan(req, env);
    }

    if (url.pathname === "/api/health") {
      return new Response(JSON.stringify({ ok: true, product: "BusinessShield AI", version: "1.0" }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response(SHIELD_HTML, {
      headers: { "Content-Type": "text/html;charset=UTF-8", "Cache-Control": "public, max-age=300" }
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

async function handleScan(req, env) {
  let body;
  try { body = await req.json(); } catch {
    return jsonError("Bad JSON", 400);
  }

  const { businessName, email, turnstileToken } = body;
  if (!businessName || !email) return jsonError("businessName and email required", 400);

  // Verify Turnstile token if secret is configured
  if (env.TURNSTILE_SECRET && turnstileToken) {
    const formData = new FormData();
    formData.append("secret", env.TURNSTILE_SECRET);
    formData.append("response", turnstileToken);
    const verifyRes = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST", body: formData
    });
    const verifyData = await verifyRes.json();
    if (!verifyData.success) return jsonError("Bot check failed", 403);
  }

  // Store scan request in D1
  if (env.DB) {
    try {
      await env.DB.prepare(
        "INSERT INTO shield_scans (business_name, email, scanned_at) VALUES (?, ?, ?)"
      ).bind(businessName, email, new Date().toISOString()).run();
    } catch {
      // Table may not exist yet — non-fatal, continue to AI scan
    }
  }

  // Run AI risk analysis
  if (!env.ANTHROPIC_KEY) return jsonError("AI not configured", 500);

  const prompt = `You are a business risk analyst for small businesses in Bristol, Connecticut.

Analyze the following local business and identify their top 3 online business risks for 2025-2026.

Business: "${businessName}"
Location: Bristol, CT

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{
  "risks": [
    {"title": "Risk name", "severity": "High|Medium|Low", "description": "2 sentence explanation", "action": "One specific thing to do this week"},
    {"title": "Risk name", "severity": "High|Medium|Low", "description": "2 sentence explanation", "action": "One specific thing to do this week"},
    {"title": "Risk name", "severity": "High|Medium|Low", "description": "2 sentence explanation", "action": "One specific thing to do this week"}
  ],
  "score": 72
}

The score is 0-100 where 100 = fully protected, 0 = completely exposed.`;

  const upstream = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": env.ANTHROPIC_KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 600,
      messages: [{ role: "user", content: prompt }]
    })
  });

  const data = await upstream.json();
  const text = data.content && data.content[0] ? data.content[0].text : null;
  if (!text) return jsonError("AI scan failed", 502);

  let scanResult;
  try {
    scanResult = JSON.parse(text);
  } catch {
    return jsonError("AI response parse error", 502);
  }

  return new Response(JSON.stringify({ ok: true, scan: scanResult, business: businessName }), {
    headers: { ...corsHeaders(), "Content-Type": "application/json" }
  });
}

function jsonError(msg, status) {
  return new Response(JSON.stringify({ error: msg }), {
    status,
    headers: { ...corsHeaders(), "Content-Type": "application/json" }
  });
}

// ── Shield HTML ──────────────────────────────────────────────

const SHIELD_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>BusinessShield AI — Free Business Risk Scan</title>
<meta name="description" content="Run a free AI-powered risk scan for your Bristol CT business. Powered by Claude AI and Cloudflare."/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
:root{--gold:#f59e0b;--gold-bright:#fbbf24;--gold-glow:rgba(245,158,11,0.25);--bg:#080808;--card:#0f0f10;--border:rgba(245,158,11,0.15);--text:#e9e9eb;--text-mid:#9898a5;--text-dim:#5a5a62;--white:#ffffff;--gradient:linear-gradient(135deg,#f59e0b,#d97706);--r:10px;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',system-ui,sans-serif;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding:40px 20px}
.wrap{width:100%;max-width:560px}
.logo{font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:700;color:var(--gold);margin-bottom:40px;text-align:center}
.logo span{color:var(--text-mid);font-weight:400;font-size:13px;display:block;margin-top:4px}
h1{font-family:'Space Grotesk',sans-serif;font-size:clamp(28px,5vw,40px);font-weight:700;color:var(--white);text-align:center;margin-bottom:12px;line-height:1.2}
h1 em{background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-style:normal}
.sub{color:var(--text-mid);text-align:center;font-size:15px;line-height:1.6;margin-bottom:36px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:28px;margin-bottom:20px}
label{display:block;font-size:13px;font-weight:600;color:var(--text-mid);margin-bottom:6px;letter-spacing:.04em;text-transform:uppercase}
input{width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(245,158,11,0.2);border-radius:7px;padding:12px 14px;color:var(--white);font-size:14px;font-family:'DM Sans',sans-serif;outline:none;transition:border-color .2s;margin-bottom:16px}
input:focus{border-color:var(--gold)}
.btn{width:100%;background:var(--gradient);color:#000;border:none;padding:14px;border-radius:8px;font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;cursor:pointer;transition:opacity .2s,box-shadow .2s;letter-spacing:.03em}
.btn:hover{opacity:.9;box-shadow:0 4px 20px var(--gold-glow)}
.btn:disabled{opacity:.5;cursor:not-allowed}
.note{font-size:12px;color:var(--text-dim);text-align:center;margin-top:10px}
#result{display:none}
.score-ring{width:120px;height:120px;margin:0 auto 24px;position:relative}
.score-ring svg{transform:rotate(-90deg)}
.score-num{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;color:var(--white)}
.risk-item{border-left:3px solid var(--gold);padding:14px 16px;margin-bottom:12px;background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0}
.risk-sev{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px}
.sev-high{color:#f87171}.sev-medium{color:var(--gold)}.sev-low{color:#4ade80}
.risk-title{font-weight:700;font-size:15px;color:var(--white);margin-bottom:6px}
.risk-desc{font-size:13px;color:var(--text-mid);margin-bottom:8px;line-height:1.5}
.risk-action{font-size:12px;color:var(--gold);font-weight:600}
.risk-action::before{content:'→ Action: '}
.cta-card{background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.3);border-radius:var(--r);padding:24px;text-align:center;margin-top:20px}
.cta-card h3{font-family:'Space Grotesk',sans-serif;color:var(--white);margin-bottom:8px;font-size:18px}
.cta-card p{color:var(--text-mid);font-size:14px;margin-bottom:16px}
.cta-btn{display:inline-block;background:var(--gradient);color:#000;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:14px;padding:12px 28px;border-radius:8px;text-decoration:none;cursor:pointer}
.err{color:#f87171;font-size:13px;margin-bottom:12px;padding:10px;background:rgba(239,68,68,0.08);border-radius:6px;display:none}
</style>
</head>
<body>
<div class="wrap">
  <div class="logo">BusinessShield AI<span>by R Unlimited LLC &middot; Bristol CT</span></div>
  <h1>Free Business<br><em>Risk Scan</em></h1>
  <p class="sub">Enter your business name and email. Claude AI analyzes your online exposure in under 30 seconds &mdash; free, no account needed.</p>

  <div class="card" id="scan-form">
    <div class="err" id="err-msg"></div>
    <label for="biz-name">Business Name</label>
    <input id="biz-name" placeholder="e.g. Mike's Auto Repair" autocomplete="organization"/>
    <label for="biz-email">Your Email</label>
    <input id="biz-email" type="email" placeholder="you@yourbusiness.com" autocomplete="email"/>
    <button class="btn" id="scan-btn" onclick="runScan()">Run Free Risk Scan &rarr;</button>
    <p class="note">Powered by Claude AI + Cloudflare Workers. No spam, ever.</p>
  </div>

  <div class="card" id="result">
    <div style="text-align:center;margin-bottom:20px">
      <div style="font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--text-mid);margin-bottom:8px">Protection Score</div>
      <div class="score-ring">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
          <circle id="score-arc" cx="60" cy="60" r="52" fill="none" stroke="url(#grad)" stroke-width="10" stroke-linecap="round" stroke-dasharray="0 327"/>
          <defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#d97706"/></linearGradient></defs>
        </svg>
        <div class="score-num" id="score-num">--</div>
      </div>
    </div>
    <div id="risks-list"></div>
    <div class="cta-card">
      <h3>Want us to fix these?</h3>
      <p>BusinessShield Pro monitors your risks weekly and alerts you instantly. Setup included free with first month.</p>
      <a class="cta-btn" href="https://bristoltalks-site.riveraf30.workers.dev/productprotect">Get BusinessShield Pro &rarr;</a>
    </div>
  </div>
</div>

<script>
async function runScan(){
  var name=document.getElementById('biz-name').value.trim();
  var email=document.getElementById('biz-email').value.trim();
  var err=document.getElementById('err-msg');
  err.style.display='none';
  if(!name||!email){err.style.display='block';err.textContent='Business name and email are required.';return;}
  var btn=document.getElementById('scan-btn');
  btn.disabled=true;btn.textContent='Scanning your business…';
  try{
    var res=await fetch('/api/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({businessName:name,email:email})});
    var data=await res.json();
    if(!data.ok){err.style.display='block';err.textContent=data.error||'Scan failed. Try again.';btn.disabled=false;btn.textContent='Run Free Risk Scan →';return;}
    showResult(data.scan);
  }catch(e){
    err.style.display='block';err.textContent='Connection error. Please try again.';
    btn.disabled=false;btn.textContent='Run Free Risk Scan →';
  }
}
function showResult(scan){
  document.getElementById('scan-form').style.display='none';
  var result=document.getElementById('result');result.style.display='block';
  var score=scan.score||50;
  var circumference=2*Math.PI*52;
  var arc=document.getElementById('score-arc');
  arc.setAttribute('stroke-dasharray',(circumference*score/100)+' '+circumference);
  document.getElementById('score-num').textContent=score;
  var list=document.getElementById('risks-list');list.innerHTML='';
  (scan.risks||[]).forEach(function(r){
    var d=document.createElement('div');d.className='risk-item';
    d.innerHTML='<div class="risk-sev sev-'+r.severity.toLowerCase()+'">'+r.severity+' Risk</div>'
      +'<div class="risk-title">'+r.title+'</div>'
      +'<div class="risk-desc">'+r.description+'</div>'
      +'<div class="risk-action">'+r.action+'</div>';
    list.appendChild(d);
  });
}
</script>
</body>
</html>`;

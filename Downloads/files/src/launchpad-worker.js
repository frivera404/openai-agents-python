// ============================================================
// Bristol LaunchPad — Cloudflare Worker
// Product: Freedom funnel → bristoltalks.com/productfreedom
// Cloudflare features: Workers + D1 + KV + Claude Haiku
// Deploy: wrangler deploy --config wrangler-launchpad.toml
// Bindings needed: DB (D1), CACHE (KV), ANTHROPIC_KEY (secret)
// ============================================================

export default {
  async fetch(req, env) {
    const url = new URL(req.url);

    if (req.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (url.pathname === "/api/submit" && req.method === "POST") {
      return handleSubmit(req, env);
    }

    if (url.pathname === "/api/preview" && req.method === "POST") {
      return handlePreview(req, env);
    }

    if (url.pathname === "/api/health") {
      return new Response(JSON.stringify({ ok: true, product: "Bristol LaunchPad", version: "1.0" }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response(LAUNCHPAD_HTML, {
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

async function handlePreview(req, env) {
  let body;
  try { body = await req.json(); } catch {
    return jsonError("Bad JSON", 400);
  }

  const { businessName, category, description } = body;
  if (!businessName) return jsonError("businessName required", 400);

  // Check KV cache first
  const cacheKey = "preview:" + businessName.toLowerCase().replace(/\s+/g, "-");
  if (env.CACHE) {
    const cached = await env.CACHE.get(cacheKey);
    if (cached) {
      return new Response(cached, {
        headers: { ...corsHeaders(), "Content-Type": "application/json", "X-Cache": "HIT" }
      });
    }
  }

  if (!env.ANTHROPIC_KEY) return jsonError("AI not configured", 500);

  const prompt = `Write a professional business listing for the Bristol CT community directory.

Business: "${businessName}"
Category: "${category || "Local Business"}"
Description from owner: "${description || "A local Bristol CT business serving the community."}"

Return ONLY a JSON object (no markdown):
{
  "tagline": "One punchy sentence under 12 words",
  "about": "2-3 sentence business description, warm and professional, mentions Bristol CT",
  "services": ["service 1", "service 2", "service 3"],
  "cta": "Call-to-action button text (5 words max)"
}`;

  const upstream = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": env.ANTHROPIC_KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 400,
      messages: [{ role: "user", content: prompt }]
    })
  });

  const data = await upstream.json();
  const text = data.content && data.content[0] ? data.content[0].text : null;
  if (!text) return jsonError("AI preview failed", 502);

  let preview;
  try { preview = JSON.parse(text); } catch {
    return jsonError("AI response parse error", 502);
  }

  const responseBody = JSON.stringify({ ok: true, preview, businessName });

  // Cache in KV for 1 hour
  if (env.CACHE) {
    await env.CACHE.put(cacheKey, responseBody, { expirationTtl: 3600 });
  }

  return new Response(responseBody, {
    headers: { ...corsHeaders(), "Content-Type": "application/json", "X-Cache": "MISS" }
  });
}

async function handleSubmit(req, env) {
  let body;
  try { body = await req.json(); } catch {
    return jsonError("Bad JSON", 400);
  }

  const { businessName, ownerName, email, phone, category, description } = body;
  if (!businessName || !email) return jsonError("businessName and email required", 400);

  if (env.DB) {
    try {
      await env.DB.prepare(
        "INSERT INTO launchpad_listings (business_name, owner_name, email, phone, category, description, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
      ).bind(
        businessName, ownerName || null, email,
        phone || null, category || null, description || null,
        new Date().toISOString()
      ).run();
    } catch {
      // Non-fatal if table doesn't exist yet
    }
  }

  return new Response(JSON.stringify({ ok: true, message: "Listing submitted! Fernando will contact you within 24 hours." }), {
    headers: { ...corsHeaders(), "Content-Type": "application/json" }
  });
}

function jsonError(msg, status) {
  return new Response(JSON.stringify({ error: msg }), {
    status, headers: { ...corsHeaders(), "Content-Type": "application/json" }
  });
}

// ── LaunchPad HTML ────────────────────────────────────────────

const LAUNCHPAD_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Bristol LaunchPad — Get Your Business Listed in 24 Hours</title>
<meta name="description" content="Get your Bristol CT business online fast. AI-written listing, Bristol directory, Cloudflare-powered speed."/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
:root{--gold:#f59e0b;--gold-bright:#fbbf24;--gold-glow:rgba(245,158,11,0.25);--bg:#080808;--card:#0f0f10;--border:rgba(245,158,11,0.15);--text:#e9e9eb;--text-mid:#9898a5;--text-dim:#5a5a62;--white:#ffffff;--green:#4ade80;--gradient:linear-gradient(135deg,#f59e0b,#d97706);--r:10px;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',system-ui,sans-serif;min-height:100vh;padding:40px 20px}
.wrap{width:100%;max-width:600px;margin:0 auto}
.logo{font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:700;color:var(--gold);margin-bottom:40px;text-align:center}
.logo span{color:var(--text-mid);font-weight:400;font-size:13px;display:block;margin-top:4px}
h1{font-family:'Space Grotesk',sans-serif;font-size:clamp(26px,5vw,38px);font-weight:700;color:var(--white);text-align:center;margin-bottom:12px;line-height:1.2}
h1 em{background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-style:normal}
.sub{color:var(--text-mid);text-align:center;font-size:15px;line-height:1.6;margin-bottom:36px}
.steps{display:flex;justify-content:center;gap:0;margin-bottom:32px}
.step{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--text-dim);font-weight:600}
.step.active{color:var(--gold)}
.step-num{width:24px;height:24px;border-radius:50%;background:rgba(255,255,255,0.05);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;flex-shrink:0}
.step.active .step-num{background:var(--gradient);border-color:transparent;color:#000}
.step-sep{width:24px;height:1px;background:var(--border);margin:0 4px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:28px;margin-bottom:20px}
label{display:block;font-size:12px;font-weight:600;color:var(--text-mid);margin-bottom:5px;letter-spacing:.05em;text-transform:uppercase}
input,select,textarea{width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(245,158,11,0.2);border-radius:7px;padding:11px 13px;color:var(--white);font-size:14px;font-family:'DM Sans',sans-serif;outline:none;transition:border-color .2s;margin-bottom:14px}
input:focus,select:focus,textarea:focus{border-color:var(--gold)}
select option{background:#111;color:var(--white)}
textarea{resize:vertical;min-height:80px}
.btn{width:100%;background:var(--gradient);color:#000;border:none;padding:13px;border-radius:8px;font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;cursor:pointer;transition:opacity .2s,box-shadow .2s}
.btn:hover{opacity:.9;box-shadow:0 4px 20px var(--gold-glow)}
.btn:disabled{opacity:.5;cursor:not-allowed}
.btn-ghost{width:100%;background:transparent;color:var(--text-mid);border:1px solid var(--border);padding:11px;border-radius:8px;font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:600;cursor:pointer;margin-top:10px;transition:all .2s}
.btn-ghost:hover{color:var(--white);border-color:rgba(255,255,255,0.2)}
.note{font-size:12px;color:var(--text-dim);text-align:center;margin-top:10px}
.err{color:#f87171;font-size:13px;margin-bottom:12px;padding:10px;background:rgba(239,68,68,0.08);border-radius:6px;display:none}
.preview-card{background:rgba(245,158,11,0.04);border:1px solid rgba(245,158,11,0.25);border-radius:var(--r);padding:20px;margin-bottom:16px}
.preview-tag{font-size:10px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);margin-bottom:10px}
.preview-biz{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;color:var(--white);margin-bottom:4px}
.preview-tagline{font-size:14px;color:var(--gold);margin-bottom:12px;font-weight:500}
.preview-about{font-size:14px;color:var(--text-mid);line-height:1.6;margin-bottom:12px}
.preview-services{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.svc-tag{background:rgba(255,255,255,0.05);border:1px solid var(--border);border-radius:999px;padding:4px 10px;font-size:12px;color:var(--text-mid)}
.success-icon{font-size:48px;text-align:center;margin-bottom:16px}
#step1,#step2,#step3{display:none}
#step1{display:block}
</style>
</head>
<body>
<div class="wrap">
  <div class="logo">Bristol LaunchPad<span>by R Unlimited LLC &middot; Bristol CT</span></div>
  <h1>Your Business Listed<br><em>in 24 Hours</em></h1>
  <p class="sub">Fill in the form, preview your AI-written listing, and submit. Fernando gets it live in the Bristol directory within a day.</p>

  <div class="steps">
    <div class="step active" id="s1"><div class="step-num">1</div><span>Your Info</span></div>
    <div class="step-sep"></div>
    <div class="step" id="s2"><div class="step-num">2</div><span>Preview</span></div>
    <div class="step-sep"></div>
    <div class="step" id="s3"><div class="step-num">3</div><span>Submit</span></div>
  </div>

  <!-- Step 1: Business Info -->
  <div id="step1" class="card">
    <div class="err" id="err1"></div>
    <label>Business Name *</label>
    <input id="f-biz" placeholder="e.g. Bristol Auto Glass"/>
    <label>Category</label>
    <select id="f-cat">
      <option value="">Select a category</option>
      <option>Auto &amp; Transportation</option>
      <option>Food &amp; Dining</option>
      <option>Health &amp; Wellness</option>
      <option>Home Services</option>
      <option>Professional Services</option>
      <option>Retail &amp; Shopping</option>
      <option>Community &amp; Nonprofit</option>
      <option>Other</option>
    </select>
    <label>Tell us about your business (optional)</label>
    <textarea id="f-desc" placeholder="What you do, who you serve, what makes you different..."></textarea>
    <button class="btn" onclick="goPreview()">Preview My Listing &rarr;</button>
    <p class="note">AI writes your copy in seconds. Free preview, no commitment.</p>
  </div>

  <!-- Step 2: AI Preview -->
  <div id="step2">
    <div id="preview-area"></div>
    <div class="card">
      <p style="font-size:14px;color:var(--text-mid);margin-bottom:16px">Looks good? Add your contact info and we go live.</p>
      <label>Your Name *</label>
      <input id="f-name" placeholder="Business owner name"/>
      <label>Email *</label>
      <input id="f-email" type="email" placeholder="you@yourbusiness.com"/>
      <label>Phone (optional)</label>
      <input id="f-phone" type="tel" placeholder="(860) 555-0000"/>
      <div class="err" id="err2"></div>
      <button class="btn" onclick="submitListing()">Submit Listing &rarr;</button>
      <button class="btn-ghost" onclick="backToStep1()">&#8592; Edit Business Info</button>
    </div>
  </div>

  <!-- Step 3: Success -->
  <div id="step3" class="card" style="text-align:center">
    <div class="success-icon">&#10003;</div>
    <h2 style="font-family:'Space Grotesk',sans-serif;color:var(--white);margin-bottom:12px">You're in the queue!</h2>
    <p style="color:var(--text-mid);font-size:15px;line-height:1.6;margin-bottom:20px">Fernando will review your listing and have it live in the Bristol directory within 24 hours. Check your email for a confirmation.</p>
    <a href="https://bristoltalks-site.riveraf30.workers.dev/business" style="display:inline-block;background:var(--gradient);color:#000;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:14px;padding:12px 28px;border-radius:8px;text-decoration:none">Browse Bristol Directory &rarr;</a>
  </div>
</div>

<script>
var previewData=null;
async function goPreview(){
  var biz=document.getElementById('f-biz').value.trim();
  var cat=document.getElementById('f-cat').value;
  var desc=document.getElementById('f-desc').value.trim();
  var err=document.getElementById('err1');
  err.style.display='none';
  if(!biz){err.style.display='block';err.textContent='Business name is required.';return;}
  var btn=event.target;btn.disabled=true;btn.textContent='Writing your listing…';
  try{
    var res=await fetch('/api/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({businessName:biz,category:cat,description:desc})});
    var data=await res.json();
    if(!data.ok){err.style.display='block';err.textContent=data.error||'Preview failed.';btn.disabled=false;btn.textContent='Preview My Listing →';return;}
    previewData=data.preview;
    renderPreview(biz,data.preview);
    document.getElementById('step1').style.display='none';
    document.getElementById('step2').style.display='block';
    document.getElementById('s2').classList.add('active');
  }catch(e){
    err.style.display='block';err.textContent='Connection error. Try again.';
    btn.disabled=false;btn.textContent='Preview My Listing →';
  }
}
function renderPreview(biz,p){
  var svcs=(p.services||[]).map(function(s){return '<span class="svc-tag">'+s+'</span>';}).join('');
  document.getElementById('preview-area').innerHTML='<div class="preview-card"><div class="preview-tag">Your Bristol Directory Listing</div><div class="preview-biz">'+biz+'</div><div class="preview-tagline">'+p.tagline+'</div><div class="preview-about">'+p.about+'</div><div class="preview-services">'+svcs+'</div></div>';
}
function backToStep1(){
  document.getElementById('step2').style.display='none';
  document.getElementById('step1').style.display='block';
  document.getElementById('s2').classList.remove('active');
}
async function submitListing(){
  var name=document.getElementById('f-name').value.trim();
  var email=document.getElementById('f-email').value.trim();
  var phone=document.getElementById('f-phone').value.trim();
  var err=document.getElementById('err2');
  err.style.display='none';
  if(!name||!email){err.style.display='block';err.textContent='Name and email are required.';return;}
  var btn=event.target;btn.disabled=true;btn.textContent='Submitting…';
  try{
    var res=await fetch('/api/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({businessName:document.getElementById('f-biz').value.trim(),ownerName:name,email:email,phone:phone,category:document.getElementById('f-cat').value,description:document.getElementById('f-desc').value.trim()})});
    var data=await res.json();
    if(data.ok){
      document.getElementById('step2').style.display='none';
      document.getElementById('step3').style.display='block';
      document.getElementById('s3').classList.add('active');
    }else{err.style.display='block';err.textContent=data.error||'Submit failed.';btn.disabled=false;btn.textContent='Submit Listing →';}
  }catch(e){
    err.style.display='block';err.textContent='Connection error. Try again.';
    btn.disabled=false;btn.textContent='Submit Listing →';
  }
}
</script>
</body>
</html>`;

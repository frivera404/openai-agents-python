// ============================================================
// BristolTalks.com — Cloudflare Worker  v4.0  (Digital Dawn Theme)
// Deploy: wrangler deploy  |  Secret: ANTHROPIC_KEY
// ============================================================

const MODEL = "claude-haiku-4-5-20251001";

const ALLOWED_ORIGINS = [
  "https://bristoltalks.com",
  "https://www.bristoltalks.com",
  "https://app.bristoltalks.com",
  "https://bristoltalks-site.riveraf30.workers.dev",
  "https://protectnow.wed2c.com",
  "https://freedom.wed2c.com",
  "https://confidence.scacto.com"
];

function cors(origin) {
  const o = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": o,
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin"
  };
}

const BRISTOL_SYSTEM = `You are BristolBot — the AI assistant for BristolTalks.com, Bristol Connecticut's community platform. You are an expert on all things Bristol CT.

HISTORY: Originally "New Cambridge", incorporated 1785. Nicknamed "Clock City" (world's clockmaking capital 1800s), "Bell City" (spring-driven doorbells), "Mum City" (chrysanthemum capital). Population ~60,000. Located in Hartford County, central CT.

KEY COMPANIES & INSTITUTIONS:
- ESPN: Founded Sept 7, 1979 by Bill Rasmussen after being fired from the Hartford Whalers. HQ at 935 Middle St on 120 acres, 18 buildings, 1.3M sq ft. ~3,600 Bristol employees. 80% owned by Disney/ABC, 20% Hearst.
- Barnes Group: Founded 1857 by Wallace Barnes starting with hoop-skirt wire as payment for clock work. Now global aerospace/industrial manufacturer. Still headquartered in Bristol.
- Lake Compounce: Founded 1846. Oldest continuously operating amusement park in America. Still open every summer.
- E. Ingraham Company: Founded 1843. One of world's largest clock manufacturers. Operated 130+ years.
- Sessions Clock Co. (J.H. Sessions & Son): Founded 1827. Major American clockmaker.
- New Departure: Invented the coaster brake for bicycles, then mastered ball bearings. 11,000 Bristol workers made precision bearings for WWII planes/ships/tanks. Became part of GM in 1919. Closed 1994.
- The Bristol Company: Founded 1889 by Prof. William H. Bristol. Made industrial instruments, invented Bristolphone (early sound film). Sold 1985.
- Bristol Hospital: Major healthcare employer.
- American Clock & Watch Museum: Est. 1952. Over 6,000 timepieces.
- New England Carousel Museum: Preserves antique carousel art.
- Firefly Brewing: Local craft brewery.

NEIGHBORHOODS: Federal Hill, Forestville, Edgewood, Chippens Hill.

IMPORTANT CONTACTS:
- Emergency: 911
- Police (non-emergency): (860) 584-3011
- Fire (non-emergency): (860) 584-6030
- City Hall: (860) 584-6100
- Mayor's Office: (860) 584-6210
- Bristol Hospital: (860) 585-3000
- Public Library: (860) 584-7787
- DPW (roads/potholes): (860) 584-6175
- Building Department: (860) 584-6185
- Parks & Recreation: (860) 584-6160
- ESPN main: (860) 766-2000
- Lake Compounce: (860) 583-3300
- American Clock & Watch Museum: (860) 583-6070

CITY RESOURCES:
- City website: bristolct.gov
- Bristol Press (local news): bristolpress.com
- Annual events: Mum Festival (fall), Lake Compounce summer season

Answer ONLY Bristol CT questions. Be helpful, proud of this city, and direct. Keep answers under 150 words unless the user asks for detail. If asked about something outside Bristol CT, politely redirect.`;

async function handleChat(req, env, origin) {
  if (!env.ANTHROPIC_KEY) {
    return new Response(JSON.stringify({ error: "ANTHROPIC_KEY not configured." }), {
      status: 500, headers: { ...cors(origin), "Content-Type": "application/json" }
    });
  }
  let body;
  try { body = await req.json(); }
  catch { return new Response("Bad JSON", { status: 400, headers: cors(origin) }); }

  const upstream = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": env.ANTHROPIC_KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: MODEL, max_tokens: 600,
      system: BRISTOL_SYSTEM,
      messages: body.messages || []
    })
  });
  const data = await upstream.json();
  return new Response(JSON.stringify(data), {
    status: upstream.status,
    headers: { ...cors(origin), "Content-Type": "application/json" }
  });
}

async function handleLeads(req, env, origin) {
  let body;
  try { body = await req.json(); } catch { return new Response(JSON.stringify({ error: "Bad JSON" }), { status: 400, headers: { ...cors(origin), "Content-Type": "application/json" } }); }
  const { name, email, phone, service, message, source, utm_source, utm_campaign, utm_medium, product } = body;
  if (!email) return new Response(JSON.stringify({ error: "email is required" }), { status: 400, headers: { ...cors(origin), "Content-Type": "application/json" } });
  try {
    await env.DB.prepare(
      "INSERT INTO leads (name, email, phone, service, message, source, utm_source, utm_campaign, utm_medium, product) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    ).bind(
      name || null, email,
      phone || null, service || null, message || null,
      source || origin || null, utm_source || null, utm_campaign || null, utm_medium || null, product || null
    ).run();
    return new Response(JSON.stringify({ ok: true }), { headers: { ...cors(origin), "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: "Database error" }), { status: 500, headers: { ...cors(origin), "Content-Type": "application/json" } });
  }
}

async function handlePosts(req, env, origin) {
  const cached = await env.CACHE.get("wp_posts");
  if (cached) return new Response(cached, { headers: { ...cors(origin), "Content-Type": "application/json", "X-Cache": "HIT" } });
  try {
    const res = await fetch("https://bristoltalks.com/wp-json/wp/v2/posts?per_page=6&_fields=id,title,excerpt,link,date");
    const data = await res.text();
    await env.CACHE.put("wp_posts", data, { expirationTtl: 300 });
    return new Response(data, { headers: { ...cors(origin), "Content-Type": "application/json", "X-Cache": "MISS" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: "Failed to fetch posts" }), { status: 502, headers: { ...cors(origin), "Content-Type": "application/json" } });
  }
}

async function handleCheckout(req, env, origin) {
  if (!env.STRIPE_SECRET_KEY) return new Response(JSON.stringify({ error: "Stripe not configured" }), { status: 500, headers: { ...cors(origin), "Content-Type": "application/json" } });
  let body;
  try { body = await req.json(); } catch { return new Response(JSON.stringify({ error: "Bad JSON" }), { status: 400, headers: { ...cors(origin), "Content-Type": "application/json" } }); }
  const products = {
    setup:   { name: "BristolTalks Setup Package",      amount: 15000, mode: "payment" },
    monthly: { name: "BristolTalks Monthly Maintenance", amount: 4900,  mode: "subscription" },
    toolkit: { name: "BristolTalks Digital Toolkit",    amount: 2700,  mode: "payment" }
  };
  const product = products[body.priceId];
  if (!product) return new Response(JSON.stringify({ error: "Invalid priceId" }), { status: 400, headers: { ...cors(origin), "Content-Type": "application/json" } });
  const lineItems = [{ price_data: { currency: "usd", unit_amount: product.amount, product_data: { name: product.name }, ...(product.mode === "subscription" ? { recurring: { interval: "month" } } : {}) }, quantity: 1 }];
  const params = new URLSearchParams({ mode: product.mode, success_url: "https://bristoltalks.com/?checkout=success", cancel_url: "https://bristoltalks.com/?checkout=cancel" });
  lineItems.forEach((item, i) => {
    Object.entries(item.price_data).forEach(([k, v]) => { if (typeof v === "object") Object.entries(v).forEach(([k2, v2]) => { if (typeof v2 === "object") Object.entries(v2).forEach(([k3, v3]) => params.append(`line_items[${i}][price_data][${k}][${k2}][${k3}]`, v3)); else params.append(`line_items[${i}][price_data][${k}][${k2}]`, v2); }); else params.append(`line_items[${i}][price_data][${k}]`, v); });
    params.append(`line_items[${i}][quantity]`, "1");
  });
  try {
    const res = await fetch("https://api.stripe.com/v1/checkout/sessions", { method: "POST", headers: { "Authorization": `Bearer ${env.STRIPE_SECRET_KEY}`, "Content-Type": "application/x-www-form-urlencoded" }, body: params.toString() });
    const data = await res.json();
    if (!res.ok) return new Response(JSON.stringify({ error: data.error?.message || "Stripe error" }), { status: 502, headers: { ...cors(origin), "Content-Type": "application/json" } });
    return new Response(JSON.stringify({ url: data.url }), { headers: { ...cors(origin), "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: "Stripe request failed" }), { status: 502, headers: { ...cors(origin), "Content-Type": "application/json" } });
  }
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = req.headers.get("Origin") || "";
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
    if (url.pathname === "/api/chat"     && req.method === "POST") return handleChat(req, env, origin);
    if (url.pathname === "/api/leads"    && req.method === "POST") return handleLeads(req, env, origin);
    if (url.pathname === "/api/posts"    && req.method === "GET")  return handlePosts(req, env, origin);
    if (url.pathname === "/api/checkout" && req.method === "POST") return handleCheckout(req, env, origin);
    if (url.pathname === "/api/health") return new Response(JSON.stringify({ ok: true, ts: Date.now(), version: "5.0" }), { headers: { "Content-Type": "application/json" } });
    // Funnel entry points — serve main HTML directly (initPage reads pathname)
    return new Response(HTML, {
      headers: { "Content-Type": "text/html;charset=UTF-8", "Cache-Control": "public, max-age=60", "X-Content-Type-Options": "nosniff" }
    });
  }
};

// ============================================================
// SITE HTML — BristolTalks Digital Dawn Theme v4.0
// ============================================================

const HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>BristolTalks — Bristol CT Community Intelligence</title>
<meta name="description" content="Bristol CT's AI-powered community platform. News, history, civic data, and BristolBot AI."/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display:ital@0;1&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
:root{
  --gold:#f59e0b;--gold-bright:#fbbf24;--gold-dim:#92700a;
  --gold-glow:rgba(245,158,11,0.25);--gold-soft:rgba(245,158,11,0.08);
  --amber:#d97706;--bg:#080808;--bg2:#0f0f10;--bg3:#0c0c0d;
  --card:#0f0f10;--card2:#131315;
  --border:rgba(245,158,11,0.15);--border-sub:rgba(255,255,255,0.07);
  --text:#e9e9eb;--text-dim:#5a5a62;--text-mid:#9898a5;--white:#ffffff;
  --gradient:linear-gradient(135deg,#f59e0b,#d97706);
  --max:1280px;--r:10px;--r2:16px;--glass:rgba(255,255,255,0.04);--glass2:rgba(255,255,255,0.07);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',system-ui,sans-serif;min-height:100vh;overflow-x:hidden;-webkit-font-smoothing:antialiased}
a{color:var(--gold);text-decoration:none;transition:color .2s}a:hover{color:var(--gold-bright)}
p,h1,h2,h3,h4{margin:0}

/* ── Ticker ── */
.ticker{background:var(--gradient);color:#040404;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;height:26px;display:flex;align-items:center;overflow:hidden;position:relative;z-index:10}
.ticker-inner{display:flex;white-space:nowrap;animation:tick 55s linear infinite}
.ticker-seg{padding:0 60px}.ticker-seg::after{content:'◆';margin-left:60px;opacity:.5}
@keyframes tick{from{transform:translateX(0)}to{transform:translateX(-50%)}}

/* ── Header ── */
header{background:rgba(8,8,8,0.95);border-bottom:1px solid var(--border-sub);position:sticky;top:0;z-index:100;backdrop-filter:blur(12px)}
.header-inner{max-width:var(--max);margin:0 auto;padding:0 24px;height:64px;display:flex;align-items:center;justify-content:space-between}
.logo{text-decoration:none;display:flex;align-items:center;gap:4px;cursor:pointer;flex-shrink:0}
.logo-mark{font-family:'DM Serif Display',serif;font-size:22px;color:var(--white);line-height:1}
.logo-mark em{font-style:italic;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.logo-dot{width:6px;height:6px;background:var(--gold);border-radius:50%;margin-left:1px;margin-bottom:2px;box-shadow:0 0 8px var(--gold-glow);flex-shrink:0}
.desk-nav{display:flex;align-items:center;gap:2px;flex:1;margin:0 20px;overflow-x:auto;scrollbar-width:none}
.desk-nav::-webkit-scrollbar{display:none}
.desk-nav a{color:var(--text-mid);font-size:13px;font-weight:500;padding:6px 12px;border-radius:6px;white-space:nowrap;transition:all .2s;cursor:pointer}
.desk-nav a:hover,.desk-nav a.active{color:var(--white);background:rgba(255,255,255,0.05)}
.desk-nav a.active{color:var(--gold)}
.nav-cta{background:var(--gradient);color:#000;border:none;padding:8px 18px;border-radius:6px;font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:700;cursor:pointer;transition:opacity .2s,box-shadow .2s;white-space:nowrap;flex-shrink:0}
.nav-cta:hover{opacity:.9;box-shadow:0 4px 20px var(--gold-glow)}
.hamburger{display:none;background:none;border:1px solid var(--border);color:var(--text-mid);padding:6px 10px;border-radius:6px;cursor:pointer;font-size:14px}
.mnav{display:none;position:fixed;top:90px;left:0;right:0;z-index:99;background:rgba(8,8,8,0.97);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:14px;flex-direction:column;gap:4px}
.mnav.open{display:flex}.mnav a{padding:10px 14px;border-radius:8px;font-size:14px;font-weight:500;color:var(--text-mid);cursor:pointer;transition:all .2s}
.mnav a:hover{background:var(--glass2);color:var(--white)}

/* ── Hero (inner pages — centered) ── */
.hero{padding:clamp(48px,7vw,100px) 24px clamp(40px,5vw,70px);text-align:center;max-width:var(--max);margin:0 auto}
.kicker{display:inline-flex;align-items:center;gap:8px;padding:5px 14px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:18px}
.kicker-gold{background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);color:var(--gold)}
.kicker-green{background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);color:#4ade80}
.kicker-green::before{content:'';width:6px;height:6px;border-radius:50%;background:#4ade80;animation:pulse-g 1.5s ease-in-out infinite}
.kicker-purple{background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);color:var(--gold)}
.kicker-red{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#f87171}
@keyframes pulse-g{0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.4)}50%{box-shadow:0 0 0 5px rgba(34,197,94,0)}}
h1.display{font-family:'DM Serif Display',serif;font-size:clamp(40px,6.5vw,80px);font-weight:400;line-height:1.05;letter-spacing:-.03em;color:var(--white)}
.grad-text{font-style:italic;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:block}
.hero-sub{max-width:620px;margin:18px auto 0;color:var(--text-mid);font-size:clamp(15px,1.6vw,19px);line-height:1.65}
.hero-actions{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:28px}

/* ── Home Hero (split layout) ── */
.hero-home{max-width:var(--max);margin:0 auto;padding:56px 24px 40px;display:grid;grid-template-columns:1fr 460px;gap:56px;align-items:center}
.hero-eyebrow{display:inline-flex;align-items:center;gap:8px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);border-radius:100px;padding:4px 14px 4px 10px;margin-bottom:22px}
.eyebrow-dot{width:6px;height:6px;background:var(--gold);border-radius:50%;box-shadow:0 0 6px var(--gold);animation:breathe 2s ease-in-out infinite}
.eyebrow-text{font-size:12px;font-weight:600;color:var(--gold);letter-spacing:.5px}
@keyframes breathe{0%,100%{opacity:1}50%{opacity:.4}}
.hero-home h1{font-family:'DM Serif Display',serif;font-size:clamp(42px,5vw,64px);font-weight:400;line-height:1.05;color:var(--white);margin-bottom:18px;letter-spacing:-.03em}
.hero-home h1 em{font-style:italic;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-home .hero-sub{margin:0 0 28px;text-align:left;max-width:420px}
.hero-home .hero-actions{justify-content:flex-start}
.hero-trust{margin-top:24px;display:flex;gap:20px;flex-wrap:wrap}
.trust-item{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-dim)}
.trust-check{width:16px;height:16px;background:rgba(245,158,11,0.1);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:9px;color:var(--gold)}

/* ── Buttons ── */
.btn-gold{background:var(--gradient);color:#000;border:none;padding:12px 24px;border-radius:8px;font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:700;cursor:pointer;transition:all .2s;box-shadow:0 0 24px rgba(245,158,11,0.15)}
.btn-gold:hover{box-shadow:0 0 36px rgba(245,158,11,0.3);transform:translateY(-1px)}
.btn-ghost{background:transparent;color:var(--text-mid);border:1px solid var(--border-sub);padding:12px 24px;border-radius:8px;font-size:14px;font-weight:500;cursor:pointer;transition:all .2s}
.btn-ghost:hover{border-color:rgba(255,255,255,0.2);color:var(--white)}
.btn-outline{background:var(--glass);border:1px solid var(--border);color:var(--text-mid);padding:12px 24px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;transition:all .2s}
.btn-outline:hover{border-color:var(--border);color:var(--text)}

/* ── Featured card (home hero right) ── */
.featured-card{background:var(--card2);border:1px solid var(--border-sub);border-radius:var(--r2);overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);cursor:pointer}
.featured-img{width:100%;height:240px;background:linear-gradient(135deg,#1a1200,#120d00,#1a1400);position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden}
.featured-img::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 100%,rgba(245,158,11,0.12) 0%,transparent 70%)}
.img-badge{position:absolute;top:14px;left:14px;background:var(--gradient);color:#000;font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:4px 10px;border-radius:4px}
.featured-body{padding:22px}
.featured-cat{font-size:11px;font-weight:600;color:var(--gold);letter-spacing:2px;text-transform:uppercase;margin-bottom:8px}
.featured-title{font-family:'DM Serif Display',serif;font-size:19px;color:var(--white);line-height:1.3;margin-bottom:12px}
.featured-meta{font-size:11px;color:var(--text-dim)}

/* ── Stats strip ── */
.stats-strip{border-top:1px solid var(--border-sub);border-bottom:1px solid var(--border-sub);background:var(--bg2)}
.stats-inner{max-width:var(--max);margin:0 auto;padding:24px;display:grid;grid-template-columns:repeat(5,1fr);gap:16px}
.stat{text-align:center;padding:6px}
.stat-num{font-family:'Space Grotesk',sans-serif;font-size:clamp(24px,3.5vw,36px);font-weight:700;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:block;line-height:1;margin-bottom:4px}
.stat-label{font-size:11px;color:var(--text-dim);letter-spacing:1px;text-transform:uppercase}

/* ── Content + Sidebar ── */
.content-layout{max-width:var(--max);margin:0 auto;padding:48px 24px;display:grid;grid-template-columns:1fr 300px;gap:40px}
.section-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:22px}
.section-head h2{font-family:'DM Serif Display',serif;font-size:22px;font-weight:400;color:var(--white)}
.section-head h2 em{font-style:italic;color:var(--gold)}
.see-all{font-size:13px;font-weight:600;color:var(--gold);cursor:pointer}

/* ── Story cards ── */
.story-featured{background:var(--card2);border:1px solid var(--border-sub);border-radius:var(--r2);overflow:hidden;margin-bottom:20px;cursor:pointer;transition:border-color .2s,box-shadow .2s;display:grid;grid-template-columns:1fr 1fr}
.story-featured:hover{border-color:rgba(245,158,11,0.3);box-shadow:0 8px 32px rgba(0,0,0,0.4)}
.story-img{min-height:200px;background:linear-gradient(135deg,#1a1100,#120d00);position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden}
.story-img::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(245,158,11,0.06) 0%,transparent 70%)}
.story-body{padding:24px;display:flex;flex-direction:column;justify-content:center}
.story-cat{font-size:11px;font-weight:700;color:var(--gold);letter-spacing:2px;text-transform:uppercase;margin-bottom:10px}
.story-title{font-family:'DM Serif Display',serif;font-size:20px;color:var(--white);line-height:1.3;margin-bottom:10px}
.story-excerpt{font-size:13px;color:var(--text-mid);line-height:1.6;margin-bottom:12px}
.story-meta{font-size:11px;color:var(--text-dim)}
.stories-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:28px}
.sc{background:var(--card2);border:1px solid var(--border-sub);border-radius:var(--r);overflow:hidden;cursor:pointer;transition:all .2s}
.sc:hover{border-color:rgba(245,158,11,0.25);transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,0.3)}
.sc-img{height:110px;background:linear-gradient(135deg,#120d00,#1a1100);position:relative;display:flex;align-items:center;justify-content:center}
.sc-cat{position:absolute;bottom:7px;left:10px;font-size:9px;font-weight:700;color:var(--gold);letter-spacing:1.5px;text-transform:uppercase}
.sc-body{padding:12px}
.sc-title{font-family:'DM Serif Display',serif;font-size:14px;color:var(--white);line-height:1.3;margin-bottom:6px}
.sc-meta{font-size:10px;color:var(--text-dim)}

/* ── Video section ── */
.video-row{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.vc{background:var(--card2);border:1px solid var(--border-sub);border-radius:var(--r);overflow:hidden;cursor:pointer;transition:all .2s}
.vc:hover{border-color:rgba(245,158,11,0.25);box-shadow:0 6px 20px rgba(0,0,0,0.3)}
.vc-thumb{height:130px;background:linear-gradient(135deg,#150e00,#1a1200);position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden}
.vc-thumb::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(245,158,11,0.05) 0%,transparent 70%)}
.vc-play{width:38px;height:38px;background:rgba(245,158,11,0.85);border-radius:50%;display:flex;align-items:center;justify-content:center;z-index:1}
.vc-play::after{content:'▶';color:#000;font-size:13px;margin-left:2px}
.vc-dur{position:absolute;bottom:7px;right:7px;background:rgba(0,0,0,0.75);color:var(--gold);font-family:'Space Grotesk',sans-serif;font-size:10px;padding:2px 5px;border-radius:3px;z-index:1}
.vc-body{padding:12px}
.vc-title{font-family:'DM Serif Display',serif;font-size:13px;color:var(--white);line-height:1.3;margin-bottom:5px}
.vc-meta{font-size:10px;color:var(--text-dim)}

/* ── Sidebar Widgets ── */
.widget{background:var(--card2);border:1px solid var(--border-sub);border-radius:var(--r2);overflow:hidden;margin-bottom:18px}
.widget-title{padding:14px 18px;border-bottom:1px solid var(--border-sub);font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:700;color:var(--white);letter-spacing:.3px;display:flex;align-items:center;gap:8px}
.wt-accent{width:3px;height:14px;background:var(--gradient);border-radius:2px;flex-shrink:0}
.widget-body{padding:14px 18px}
.ai-header{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.ai-avatar{width:34px;height:34px;background:var(--gradient);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0}
.ai-name{font-size:13px;font-weight:600;color:var(--white)}
.ai-status{font-size:10px;color:var(--gold);display:flex;align-items:center;gap:4px}
.ai-status::before{content:'●'}
.w-bubble{background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.1);border-radius:8px;padding:9px 11px;font-size:12px;color:var(--text-mid);line-height:1.55;margin-bottom:8px}
.w-bubble.user{background:var(--glass);border-color:var(--border-sub);font-style:italic}
.w-open-btn{width:100%;background:var(--gradient);border:none;border-radius:6px;color:#000;padding:9px;font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:700;cursor:pointer;margin-top:10px;transition:opacity .2s}
.w-open-btn:hover{opacity:.9}
.event-list{list-style:none}
.event-item{display:flex;gap:10px;padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.04)}
.event-item:last-child{border-bottom:none}
.event-date{min-width:40px;height:40px;background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.15);border-radius:7px;display:flex;flex-direction:column;align-items:center;justify-content:center;flex-shrink:0}
.e-month{font-size:8px;color:var(--gold);font-weight:700;letter-spacing:1px;text-transform:uppercase}
.e-day{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;color:var(--white);line-height:1}
.event-name{font-size:12px;font-weight:600;color:var(--text);line-height:1.3;margin-bottom:2px}
.event-loc{font-size:10px;color:var(--text-dim)}
.nl-widget{background:linear-gradient(135deg,rgba(245,158,11,0.06),rgba(217,119,6,0.03));border-color:rgba(245,158,11,0.2)}
.nl-text{font-size:12px;color:var(--text-mid);line-height:1.6;margin-bottom:12px}

/* ── General SPA layout helpers ── */
.shell{max-width:var(--max);margin:0 auto;padding:0 24px}
.section{padding:clamp(36px,5vw,64px) 0}
.sec-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-bottom:20px}
.sec-title{font-size:clamp(20px,2.5vw,28px);font-weight:400;font-family:'DM Serif Display',serif;color:var(--white)}
.sec-link{font-size:13px;font-weight:700;color:var(--gold);cursor:pointer}
.sec-link:hover{color:var(--gold-bright)}
#app{animation:fadein .3s ease}
@keyframes fadein{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* ── Cards ── */
.card{background:var(--glass);border:1px solid var(--border);border-radius:var(--r2);padding:22px;transition:transform .2s,border-color .2s,background .2s;cursor:pointer}
.card:hover{transform:translateY(-3px);border-color:rgba(245,158,11,0.3);background:var(--glass2)}
.card-tag{display:inline-flex;padding:3px 8px;border-radius:999px;font-size:10px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px}
.tag-yang{background:rgba(245,158,11,0.15);color:var(--gold-bright)}
.tag-yin{background:rgba(217,119,6,0.12);color:#fcd34d}
.tag-green{background:rgba(34,197,94,0.12);color:#4ade80}
.tag-red{background:rgba(239,68,68,0.12);color:#f87171}
.card-meta{font-size:11px;color:var(--text-dim);font-weight:600;letter-spacing:.04em;margin-bottom:6px}
.card h3{font-size:15px;font-weight:400;font-family:'DM Serif Display',serif;line-height:1.3;color:var(--text)}
.card p{margin-top:7px;color:var(--text-mid);font-size:13px;line-height:1.5}
.grid2{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}

/* ── Timeline ── */
.timeline{position:relative;padding-left:30px}
.timeline::before{content:'';position:absolute;left:9px;top:0;bottom:0;width:2px;background:var(--gradient)}
.tl-item{position:relative;margin-bottom:28px}
.tl-dot{position:absolute;left:-25px;top:4px;width:13px;height:13px;border-radius:50%;background:var(--gold);border:2px solid var(--bg);box-shadow:0 0 10px rgba(245,158,11,0.4)}
.tl-year{font-size:11px;font-weight:700;letter-spacing:.1em;color:var(--gold);margin-bottom:3px;font-family:'Space Grotesk',sans-serif}
.tl-title{font-size:15px;font-weight:400;font-family:'DM Serif Display',serif;margin-bottom:3px;color:var(--text)}
.tl-desc{font-size:12px;color:var(--text-mid);line-height:1.5}

/* ── Q&A ── */
.qa-item{background:var(--glass);border:1px solid var(--border);border-radius:var(--r2);padding:18px;margin-bottom:10px}
.qa-q{display:flex;gap:10px;align-items:flex-start}
.qa-qmark{width:26px;height:26px;flex:0 0 auto;border-radius:8px;background:rgba(245,158,11,0.12);color:var(--gold);display:grid;place-items:center;font-size:12px;font-weight:900;font-family:'Space Grotesk',sans-serif}
.qa-amark{width:26px;height:26px;flex:0 0 auto;border-radius:8px;background:rgba(245,158,11,0.18);color:var(--gold-bright);display:grid;place-items:center;font-size:12px;font-weight:900;font-family:'Space Grotesk',sans-serif}
.qa-answer{display:flex;gap:10px;margin-top:10px;padding:10px;border-radius:10px;background:rgba(0,0,0,0.2)}

/* ── Directory ── */
.dir-row{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border)}
.dir-row:last-child{border-bottom:none}
.dir-name{font-weight:600;font-size:13px;color:var(--text)}
.dir-phone{font-size:13px;color:var(--gold);font-weight:600;font-family:'Space Grotesk',monospace}
.emergency-banner{background:linear-gradient(135deg,rgba(239,68,68,0.2),rgba(239,68,68,0.05));border:1px solid rgba(239,68,68,0.35);border-radius:var(--r2);padding:18px 22px;margin-bottom:22px;display:flex;align-items:center;gap:16px}
.emergency-num{font-size:clamp(28px,5vw,50px);font-weight:700;color:#f87171;letter-spacing:-.04em;font-family:'Space Grotesk',sans-serif}

/* ── Neighborhoods ── */
.nbhd-card{background:var(--glass);border:1px solid var(--border);border-radius:var(--r2);overflow:hidden;transition:transform .2s,border-color .2s;cursor:pointer}
.nbhd-card:hover{transform:translateY(-4px);border-color:rgba(245,158,11,0.3)}
.nbhd-header{padding:22px 22px 14px}.nbhd-icon{font-size:34px;margin-bottom:10px}
.nbhd-name{font-size:20px;font-weight:400;font-family:'DM Serif Display',serif;color:var(--white)}
.nbhd-tag{display:inline-block;margin-top:5px;padding:3px 7px;border-radius:5px;font-size:10px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.nbhd-body{padding:0 22px 22px}
.nbhd-stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}
.nbhd-stat{background:rgba(0,0,0,0.2);border-radius:8px;padding:9px}
.nbhd-stat strong{display:block;font-size:17px;font-weight:700;color:var(--gold);font-family:'Space Grotesk',sans-serif}
.nbhd-stat span{font-size:10px;color:var(--text-dim);font-weight:700;text-transform:uppercase;letter-spacing:.06em}

/* ── Events ── */
.evt-card{display:flex;gap:14px;background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:14px;transition:border-color .2s,background .2s;cursor:pointer}
.evt-card:hover{border-color:rgba(245,158,11,0.3);background:var(--glass2)}
.evt-date{flex:0 0 48px;text-align:center;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);border-radius:9px;padding:7px 4px}
.evt-month{font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:var(--gold);font-family:'Space Grotesk',sans-serif}
.evt-day{font-size:22px;font-weight:700;line-height:1;color:var(--gold-bright);font-family:'Space Grotesk',sans-serif}
.evt-info{flex:1}.evt-title{font-size:13px;font-weight:700;color:var(--text)}
.evt-desc{font-size:11px;color:var(--text-mid);margin-top:2px}

/* ── Progress bars ── */
.prog-wrap{margin-top:10px}
.prog-label{display:flex;justify-content:space-between;font-size:11px;font-weight:700;color:var(--text-dim);margin-bottom:4px}
.prog-track{height:5px;background:var(--glass2);border-radius:999px;overflow:hidden}
.prog-fill{height:100%;border-radius:999px;background:var(--gradient);animation:grow 1s ease forwards}
@keyframes grow{from{width:0}}

/* ── Stat cells (home stats) ── */
.stat-cell{background:var(--bg2);padding:20px;text-align:center}

/* ── Floating Chat ── */
.chat-fab{position:fixed;bottom:24px;right:24px;z-index:200;width:52px;height:52px;border-radius:50%;background:var(--gradient);border:none;color:#000;font-size:20px;cursor:pointer;box-shadow:0 8px 28px rgba(245,158,11,0.4);transition:transform .2s;display:flex;align-items:center;justify-content:center}
.chat-fab:hover{transform:scale(1.08)}
.chat-panel{position:fixed;bottom:86px;right:24px;z-index:200;width:340px;max-width:calc(100vw - 32px);background:rgba(8,8,8,0.97);backdrop-filter:blur(24px);border:1px solid var(--border);border-radius:var(--r2);overflow:hidden;display:none;flex-direction:column;box-shadow:0 28px 72px rgba(0,0,0,0.7)}
.chat-panel.open{display:flex}
.chat-head{padding:14px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.chat-head-title{font-weight:400;font-size:15px;font-family:'DM Serif Display',serif;color:var(--white)}
.chat-head-sub{font-size:11px;color:var(--text-dim);margin-top:1px}
.chat-close{background:none;border:none;color:var(--text-mid);font-size:17px;cursor:pointer;padding:4px}
.chat-messages{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:9px;max-height:300px}
.chat-msg{padding:9px 12px;border-radius:12px;font-size:13px;line-height:1.5;max-width:88%}
.chat-msg.user{background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.25);align-self:flex-end;color:var(--gold-bright)}
.chat-msg.bot{background:var(--glass);border:1px solid var(--border);align-self:flex-start;color:var(--text-mid)}
.chat-msg.loading{color:var(--text-dim);font-style:italic}
.chat-input-row{padding:10px;border-top:1px solid var(--border);display:flex;gap:7px}
.chat-input{flex:1;background:var(--glass);border:1px solid var(--border);border-radius:7px;padding:9px 12px;color:var(--text);font-size:13px;font-family:'DM Sans',sans-serif;outline:none}
.chat-input:focus{border-color:var(--gold)}
.chat-send{background:var(--gradient);border:none;color:#000;border-radius:6px;padding:8px 12px;font-size:13px;font-weight:700;cursor:pointer;font-family:'Space Grotesk',sans-serif}
.chat-suggestions{padding:7px 10px;display:flex;flex-wrap:wrap;gap:5px;border-bottom:1px solid var(--border)}
.chat-sug{padding:4px 9px;border-radius:999px;background:var(--glass);border:1px solid var(--border);font-size:11px;font-weight:600;color:var(--text-mid);cursor:pointer;transition:color .2s,border-color .2s}
.chat-sug:hover{color:var(--text);border-color:var(--gold)}

/* ── Footer ── */
footer{background:var(--bg3);border-top:1px solid var(--border-sub);padding:52px 24px 24px}
.footer-inner{max-width:var(--max);margin:0 auto}
.footer-top{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:44px;padding-bottom:44px;border-bottom:1px solid var(--border-sub);margin-bottom:20px}
.footer-logo{font-family:'DM Serif Display',serif;font-size:26px;color:var(--white);margin-bottom:7px}
.footer-logo em{font-style:italic;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.footer-desc{font-size:13px;color:var(--text-dim);line-height:1.7;margin-bottom:18px}
.social-row{display:flex;gap:7px}
.social-btn{width:32px;height:32px;background:rgba(255,255,255,0.05);border:1px solid var(--border-sub);border-radius:6px;display:flex;align-items:center;justify-content:center;color:var(--text-dim);font-size:12px;cursor:pointer;transition:all .2s}
.social-btn:hover{border-color:rgba(245,158,11,0.3);color:var(--gold);background:rgba(245,158,11,0.06)}
.footer-col-title{font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;color:var(--white);margin-bottom:14px;letter-spacing:.3px}
.footer-col-links{list-style:none}
.footer-col-links li{margin-bottom:9px}
.footer-col-links a,.footer-col-links span{color:var(--text-dim);font-size:13px;cursor:pointer;transition:color .2s}
.footer-col-links a:hover,.footer-col-links span:hover{color:var(--gold)}
.footer-bottom{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--text-dim)}
.footer-bottom-links{display:flex;gap:14px}
.footer-bottom-links span{cursor:pointer;transition:color .2s}
.footer-bottom-links span:hover{color:var(--gold)}

/* ── Responsive ── */
@media(max-width:1100px){.grid4{grid-template-columns:repeat(2,1fr)}.footer-top{grid-template-columns:1fr 1fr;gap:28px}}
@media(max-width:900px){.hero-home{grid-template-columns:1fr;gap:36px}.hero-right{display:none}.content-layout{grid-template-columns:1fr}.sidebar{display:none}.stats-inner{grid-template-columns:repeat(3,1fr)}.stories-grid{grid-template-columns:repeat(2,1fr)}.video-row{grid-template-columns:1fr}}
@media(max-width:780px){.story-featured{grid-template-columns:1fr}.story-img{min-height:160px}}
@media(max-width:640px){.grid2,.grid3,.grid4{grid-template-columns:1fr}.hamburger{display:block}.desk-nav,.nav-cta{display:none}.footer-top{grid-template-columns:1fr}.stories-grid{grid-template-columns:1fr}.stats-inner{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>

<!-- Ticker -->
<div class="ticker"><div class="ticker-inner"><span class="ticker-seg">Centre Square confirms first commercial tenants Spring 2026</span><span class="ticker-seg">Bristol Mum Festival 60th Annual — September 2026 on Federal Hill</span><span class="ticker-seg">Pequabuck River Greenway secures $2.3M state grant</span><span class="ticker-seg">Route 6 safety study recommends 5 new pedestrian crossings near Forestville</span><span class="ticker-seg">Lake Compounce 2026 season opened April 26 — new family ride revealed</span><span class="ticker-seg">CT Food Truck Battles Festival — May 16 in Bristol</span><span class="ticker-seg">Bristol Farmers Market opens June 20 — Federal Hill downtown</span><span class="ticker-seg">BristolBot AI available 24/7 — ask anything about Bristol CT</span><span class="ticker-seg">Centre Square confirms first commercial tenants Spring 2026</span><span class="ticker-seg">Bristol Mum Festival 60th Annual — September 2026 on Federal Hill</span><span class="ticker-seg">Pequabuck River Greenway secures $2.3M state grant</span><span class="ticker-seg">Route 6 safety study recommends 5 new pedestrian crossings near Forestville</span><span class="ticker-seg">Lake Compounce 2026 season opened April 26 — new family ride revealed</span><span class="ticker-seg">CT Food Truck Battles Festival — May 16 in Bristol</span><span class="ticker-seg">Bristol Farmers Market opens June 20 — Federal Hill downtown</span><span class="ticker-seg">BristolBot AI available 24/7 — ask anything about Bristol CT</span></div></div>

<!-- Header -->
<header>
  <div class="header-inner">
    <a class="logo" onclick="go('home')">
      <span class="logo-mark">Bristol<em>Talks</em></span>
      <span class="logo-dot"></span>
    </a>
    <nav class="desk-nav" id="desk-nav">
      <a onclick="go('home')">Home</a>
      <a onclick="go('news')">News</a>
      <a onclick="go('engage')">Engage</a>
      <a onclick="go('projects')">Projects</a>
      <a onclick="go('history')">History</a>
      <a onclick="go('neighborhoods')">Neighborhoods</a>
      <a onclick="go('events')">Events</a>
      <a onclick="go('directory')">Directory</a>
      <a onclick="go('government')">Government</a>
      <a onclick="go('business')">Business</a>
      <a onclick="go('services')">Services</a>
      <a onclick="go('about')">About</a>
      <a onclick="go('connect')">Connect</a>
      <a onclick="go('ai')">BristolBot AI</a>
    </nav>
    <button class="nav-cta" onclick="document.getElementById('chat-panel').classList.add('open')">Talk to BristolBot</button>
    <button class="hamburger" id="hamburger">☰</button>
  </div>
</header>

<!-- Mobile nav -->
<div class="mnav" id="mnav">
  <a onclick="go('home');closeMnav()">Home</a>
  <a onclick="go('news');closeMnav()">News</a>
  <a onclick="go('engage');closeMnav()">Engage</a>
  <a onclick="go('projects');closeMnav()">Projects</a>
  <a onclick="go('history');closeMnav()">History</a>
  <a onclick="go('neighborhoods');closeMnav()">Neighborhoods</a>
  <a onclick="go('events');closeMnav()">Events</a>
  <a onclick="go('directory');closeMnav()">Directory</a>
  <a onclick="go('government');closeMnav()">Government</a>
  <a onclick="go('business');closeMnav()">Business</a>
  <a onclick="go('services');closeMnav()">Services</a>
  <a onclick="go('about');closeMnav()">About</a>
  <a onclick="go('connect');closeMnav()">Connect</a>
  <a onclick="go('ai');closeMnav()">BristolBot AI</a>
</div>

<main id="app"></main>

<!-- Footer -->
<footer>
  <div class="footer-inner">
    <div class="footer-top">
      <div>
        <div class="footer-logo">Bristol<em>Talks</em></div>
        <p class="footer-desc">Bristol, Connecticut's AI-powered community intelligence platform. Keeping residents, businesses, and local leaders connected and informed.</p>
        <div class="social-row">
          <div class="social-btn">𝕏</div>
          <div class="social-btn">f</div>
          <div class="social-btn">in</div>
        </div>
      </div>
      <div>
        <div class="footer-col-title">Coverage</div>
        <ul class="footer-col-links">
          <li><span onclick="go('news')">Local News</span></li>
          <li><span onclick="go('government')">Government</span></li>
          <li><span onclick="go('business')">Business</span></li>
          <li><span onclick="go('events')">Events</span></li>
        </ul>
      </div>
      <div>
        <div class="footer-col-title">Community</div>
        <ul class="footer-col-links">
          <li><span onclick="go('events')">Events Calendar</span></li>
          <li><span onclick="go('neighborhoods')">Neighborhoods</span></li>
          <li><span onclick="go('history')">Bristol History</span></li>
          <li><span onclick="go('directory')">Directory</span></li>
        </ul>
      </div>
      <div>
        <div class="footer-col-title">Platform</div>
        <ul class="footer-col-links">
          <li><span onclick="go('ai')">BristolBot AI</span></li>
          <li><span onclick="go('engage')">Community Q&amp;A</span></li>
          <li><span onclick="go('about')">About</span></li>
          <li><span onclick="go('connect')">Contact</span></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 BristolTalks.com — R Unlimited LLC · Bristol, Connecticut</span>
      <div class="footer-bottom-links">
        <span onclick="go('about')">About</span>
        <span onclick="go('connect')">Contact</span>
      </div>
    </div>
  </div>
</footer>

<!-- Floating BristolBot -->
<button class="chat-fab" id="chat-fab">🤖</button>
<div class="chat-panel" id="chat-panel">
  <div class="chat-head">
    <div>
      <div class="chat-head-title">BristolBot AI</div>
      <div class="chat-head-sub">Bristol CT expert · Powered by Claude</div>
    </div>
    <button class="chat-close" id="chat-close">✕</button>
  </div>
  <div class="chat-suggestions" id="chat-sug-list">
    <span class="chat-sug" onclick="chatSend('Who founded ESPN?')">Who founded ESPN?</span>
    <span class="chat-sug" onclick="chatSend('Best neighborhood for families?')">Best neighborhood?</span>
    <span class="chat-sug" onclick="chatSend('How do I commute to Hartford?')">Commute to Hartford?</span>
    <span class="chat-sug" onclick="chatSend('What is Bristol known for?')">Bristol known for?</span>
  </div>
  <div class="chat-messages" id="chat-msgs">
    <div class="chat-msg bot">Hi! I am BristolBot — your AI guide to Bristol CT. Ask me anything about the city.</div>
  </div>
  <div class="chat-input-row">
    <input class="chat-input" id="chat-input" placeholder="Ask about Bristol CT..." autocomplete="off"/>
    <button class="chat-send" id="chat-send">Send</button>
  </div>
</div>

<script>
var chatHistory=[];
function go(page){
  var pages={home:pageHome,news:pageNews,engage:pageEngage,ai:pageAI,projects:pageProjects,history:pageHistory,neighborhoods:pageNeighborhoods,events:pageEvents,directory:pageDirectory,government:pageGovernment,business:pageBusiness,services:pageServices,about:pageAbout,connect:pageConnect,funnelprotect:pageFunnelProtect,funnelfreedom:pageFunnelFreedom,funnelconfidence:pageFunnelConfidence,productprotect:pageProductProtect,'businessshield-ai':pageProductProtect,productfreedom:pageProductFreedom,productconfidence:pageProductConfidence};
  document.getElementById('app').innerHTML='<div style="animation:fadein .3s ease">'+(pages[page]||pageHome)()+'</div>';
  document.querySelectorAll('.desk-nav a,.mnav a').forEach(function(a){
    a.classList.remove('active');
    var t=a.textContent.trim().toLowerCase().replace('bristolbot ai','ai');
    if(t===page||(page==='home'&&t==='home'))a.classList.add('active');
  });
  window.scrollTo(0,0);history.pushState({p:page},'','/'+(page==='home'?'':page));setTimeout(runCounters,80);
}
function closeMnav(){document.getElementById('mnav').classList.remove('open');}
document.getElementById('hamburger').onclick=function(){document.getElementById('mnav').classList.toggle('open');};
document.getElementById('chat-fab').onclick=function(){document.getElementById('chat-panel').classList.toggle('open');};
document.getElementById('chat-close').onclick=function(){document.getElementById('chat-panel').classList.remove('open');};
document.getElementById('chat-send').onclick=function(){var v=document.getElementById('chat-input').value.trim();if(v)chatSend(v);};
document.getElementById('chat-input').onkeydown=function(e){if(e.key==='Enter'){var v=this.value.trim();if(v)chatSend(v);}};
function chatSend(msg){
  var msgs=document.getElementById('chat-msgs');document.getElementById('chat-input').value='';
  document.getElementById('chat-panel').classList.add('open');document.getElementById('chat-sug-list').style.display='none';
  var um=document.createElement('div');um.className='chat-msg user';um.textContent=msg;msgs.appendChild(um);
  chatHistory.push({role:'user',content:msg});
  var lm=document.createElement('div');lm.className='chat-msg loading';lm.textContent='BristolBot is thinking…';msgs.appendChild(lm);msgs.scrollTop=msgs.scrollHeight;
  fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:chatHistory})})
    .then(function(r){return r.json();}).then(function(d){var reply=d.content&&d.content[0]?d.content[0].text:'Sorry, no response.';chatHistory.push({role:'assistant',content:reply});lm.className='chat-msg bot';lm.textContent=reply;msgs.scrollTop=msgs.scrollHeight;})
    .catch(function(){lm.className='chat-msg bot';lm.textContent='Connection error.';});
}
function C(tag,cls,meta,title,body){return '<div class="card"><div class="card-tag '+cls+'">'+tag+'</div><div class="card-meta">'+meta+'</div><h3>'+title+'</h3><p>'+body+'</p></div>';}

// ── Home Page — Digital Dawn Layout ──
function pageHome(){
  return '<div class="hero-home">'
    +'<div>'
    +'<div class="hero-eyebrow"><span class="eyebrow-dot"></span><span class="eyebrow-text">Bristol, Connecticut — Powered by AI</span></div>'
    +'<h1>Your Community,<br><em>Intelligently</em><br>Connected</h1>'
    +'<p class="hero-sub">BristolTalks brings you real-time local news, events, and a 24/7 AI assistant built specifically for Bristol, CT — helping residents, businesses, and community leaders stay informed.</p>'
    +'<div class="hero-actions"><button class="btn-gold" onclick="document.getElementById(&#39;chat-panel&#39;).classList.add(&#39;open&#39;)">Talk to BristolBot</button><button class="btn-ghost" onclick="go(&#39;news&#39;)">Explore Local News</button></div>'
    +'<div class="hero-trust"><div class="trust-item"><div class="trust-check">✓</div><span>24/7 AI assistance</span></div><div class="trust-item"><div class="trust-check">✓</div><span>Real-time updates</span></div><div class="trust-item"><div class="trust-check">✓</div><span>Bristol-focused</span></div></div>'
    +'</div>'
    +'<div class="hero-right"><div class="featured-card"><div class="featured-img"><div class="img-badge">Top Story</div></div><div class="featured-body"><div class="featured-cat">Development</div><div class="featured-title">Centre Square Confirms First Commercial Tenants for Spring 2026</div><div class="featured-meta">May 13, 2026 · 4 min read</div></div></div></div>'
    +'</div>'
    +'<div class="stats-strip"><div class="stats-inner">'
    +'<div class="stat"><span class="stat-num" data-count="8">0</span><span class="stat-label">Stories Today</span></div>'
    +'<div class="stat"><span class="stat-num" data-count="60000">0</span><span class="stat-label">Bristol Residents</span></div>'
    +'<div class="stat"><span class="stat-num" data-count="241">0</span><span class="stat-label">Years of History</span></div>'
    +'<div class="stat"><span class="stat-num" data-count="3600">0</span><span class="stat-label">ESPN Employees</span></div>'
    +'<div class="stat"><span class="stat-num">24/7</span><span class="stat-label">AI Availability</span></div>'
    +'</div></div>'
    +'<div class="content-layout"><main>'
    // Latest News
    +'<div class="section-head"><h2>Latest <em>News</em></h2><span class="see-all" onclick="go(&#39;news&#39;)">See all stories →</span></div>'
    +'<div class="story-featured"><div class="story-img"></div><div class="story-body"><div class="story-cat">Government</div><div class="story-title">City Council Votes on $12M Downtown Revitalization Plan</div><div class="story-excerpt">Bristol&#39;s City Council is set to decide on a landmark investment in downtown infrastructure, housing, and public spaces — the largest such proposal in over a decade.</div><div class="story-meta">May 13, 2026 · 4 min read</div></div></div>'
    +'<div class="stories-grid">'
    +'<div class="sc"><div class="sc-img"><div class="sc-cat">Community</div></div><div class="sc-body"><div class="sc-title">Pequabuck River Greenway Secures $2.3M State Grant</div><div class="sc-meta">May 12 · 3 min read</div></div></div>'
    +'<div class="sc"><div class="sc-img"><div class="sc-cat">Business</div></div><div class="sc-body"><div class="sc-title">Barnes Group Posts Record Q1 Aerospace Revenue</div><div class="sc-meta">May 11 · 2 min read</div></div></div>'
    +'<div class="sc"><div class="sc-img"><div class="sc-cat">History</div></div><div class="sc-body"><div class="sc-title">ESPN at 47: Bristol&#39;s Journey to Sports Broadcasting Capital</div><div class="sc-meta">May 10 · 5 min read</div></div></div>'
    +'</div>'
    // Video
    +'<div class="section-head" style="margin-top:8px"><h2>Video <em>Stories</em></h2><span class="see-all" onclick="go(&#39;news&#39;)">All stories →</span></div>'
    +'<div class="video-row">'
    +'<div class="vc"><div class="vc-thumb"><div class="vc-play"></div><div class="vc-dur">3:42</div></div><div class="vc-body"><div class="vc-title">Mayor&#39;s Address on Bristol&#39;s Smart City Initiative</div><div class="vc-meta">May 12, 2026</div></div></div>'
    +'<div class="vc"><div class="vc-thumb"><div class="vc-play"></div><div class="vc-dur">5:18</div></div><div class="vc-body"><div class="vc-title">Downtown Bristol: 50 Years of Change</div><div class="vc-meta">May 10, 2026</div></div></div>'
    +'<div class="vc"><div class="vc-thumb"><div class="vc-play"></div><div class="vc-dur">4:05</div></div><div class="vc-body"><div class="vc-title">BristolBot in Action: AI Helping Residents</div><div class="vc-meta">May 9, 2026</div></div></div>'
    +'<div class="vc"><div class="vc-thumb"><div class="vc-play"></div><div class="vc-dur">2:55</div></div><div class="vc-body"><div class="vc-title">Community Heroes: Bristol Residents Making a Difference</div><div class="vc-meta">May 8, 2026</div></div></div>'
    +'</div>'
    +'</main>'
    // Sidebar
    +'<aside class="sidebar">'
    +'<div class="widget"><div class="widget-title"><div class="wt-accent"></div>BristolBot AI</div><div class="widget-body">'
    +'<div class="ai-header"><div class="ai-avatar">🤖</div><div><div class="ai-name">BristolBot</div><div class="ai-status">Online now</div></div></div>'
    +'<div class="w-bubble">Hello! I&#39;m BristolBot — your AI guide to Bristol, CT. Ask me about local news, events, history, or services.</div>'
    +'<div class="w-bubble user">"What&#39;s happening in Bristol this week?"</div>'
    +'<div class="w-bubble">Lake Compounce is open, the Farmers Market opens June 20, and City Council meets on 2nd & 4th Tuesdays at 7PM in City Hall.</div>'
    +'<button class="w-open-btn" onclick="document.getElementById(&#39;chat-panel&#39;).classList.add(&#39;open&#39;)">Open BristolBot Chat →</button>'
    +'</div></div>'
    +'<div class="widget"><div class="widget-title"><div class="wt-accent"></div>Upcoming Events</div><div class="widget-body">'
    +'<ul class="event-list">'
    +'<li class="event-item"><div class="event-date"><span class="e-month">MAY</span><span class="e-day">16</span></div><div><div class="event-name">CT Food Truck Battles</div><div class="event-loc">Downtown Bristol</div></div></li>'
    +'<li class="event-item"><div class="event-date"><span class="e-month">MAY</span><span class="e-day">17</span></div><div><div class="event-name">Bristol Founders Day</div><div class="event-loc">City Hall Plaza</div></div></li>'
    +'<li class="event-item"><div class="event-date"><span class="e-month">JUL</span><span class="e-day">4</span></div><div><div class="event-name">Fourth of July Parade</div><div class="event-loc">Downtown route</div></div></li>'
    +'<li class="event-item"><div class="event-date"><span class="e-month">SEP</span><span class="e-day">TBD</span></div><div><div class="event-name">Mum Festival — 60th Annual</div><div class="event-loc">Federal Hill</div></div></li>'
    +'</ul>'
    +'</div></div>'
    +'<div class="widget nl-widget"><div class="widget-title"><div class="wt-accent"></div>Bristol AI Weekly</div><div class="widget-body">'
    +'<p class="nl-text">Get the Bristol AI Weekly newsletter — local news, events, and AI updates delivered every Monday.</p>'
    +'<a href="mailto:riveraf30@gmail.com?subject=Subscribe: Bristol AI Weekly" style="display:block;width:100%;background:var(--gradient);border:none;border-radius:6px;color:#000;padding:10px;font-family:&#39;Space Grotesk&#39;,sans-serif;font-size:13px;font-weight:700;cursor:pointer;text-align:center;text-decoration:none">Subscribe Free →</a>'
    +'</div></div>'
    +'</aside>'
    +'</div>';
}

function pageNews(){
  setTimeout(function(){
    var grid=document.getElementById('wp-posts-grid');
    if(!grid)return;
    fetch('/api/posts').then(function(r){return r.json();}).then(function(posts){
      if(!Array.isArray(posts)||!posts.length){grid.innerHTML='<p style="color:var(--text-dim);font-size:13px">No posts found.</p>';return;}
      grid.innerHTML=posts.map(function(p){
        var title=p.title&&p.title.rendered?p.title.rendered.replace(/<[^>]+>/g,''):'Untitled';
        var excerpt=p.excerpt&&p.excerpt.rendered?p.excerpt.rendered.replace(/<[^>]+>/g,'').substring(0,120)+'…':'';
        var date=p.date?new Date(p.date).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'}):'';
        return '<a href="'+p.link+'" target="_blank" rel="noopener" style="text-decoration:none"><div class="card" style="margin-bottom:10px"><div class="card-tag tag-yang">BristolTalks.com</div><div class="card-meta">'+date+'</div><h3>'+title+'</h3><p>'+excerpt+'</p></div></a>';
      }).join('');
    }).catch(function(){grid.innerHTML='<p style="color:var(--text-dim);font-size:13px">Unable to load posts — check back soon.</p>';});
  },0);
  return '<div class="hero"><div class="kicker kicker-gold">Yang · Active Signal · Bristol CT</div><h1 class="display">What&#39;s Happening<br><span class="grad-text">In Bristol</span></h1><p class="hero-sub">Live coverage of local government, development, transport, culture, and community.</p></div>'
  +'<section class="section"><div class="shell">'
  +'<div class="section-head"><h2>From <em>BristolTalks.com</em></h2><a href="https://bristoltalks.com" target="_blank" rel="noopener" style="font-size:13px;font-weight:700;color:var(--gold)">Visit site →</a></div>'
  +'<div id="wp-posts-grid"><div style="color:var(--text-dim);font-size:13px;padding:20px 0">Loading latest posts…</div></div>'
  +'<div class="section-head" style="margin-top:32px"><h2>More <em>Stories</em></h2></div>'
  +'<div class="grid3">'+C('Local','tag-yang','Just Now','Centre Square Confirms First Commercial Tenants for Spring 2026','Three regional retailers and a 200-seat restaurant signed — the most significant downtown investment in over a decade.')+C('Green','tag-green','Today','Pequabuck River Greenway Secures $2.3M State Grant','CT DEEP grant funds the next 1.8-mile section, completing a continuous path from Page Park to the Plainville town line.')+C('Transport','tag-yang','Today','Route 6 Corridor Study Recommends New Pedestrian Crossings Near Forestville','The CCRCOG study identifies five priority crossing points to improve safety between West Street and Forestville.')+C('Culture','tag-yang','This Week','Bristol Mum Festival 2026 Confirms 60th Annual — Parade Route Announced','Full pre-pandemic format returns: carnival, parade, and Mum Pageant on Federal Hill.')+C('Parks','tag-yang','April 26','Lake Compounce 2026 Season Opened — New Ride Teased','America&#39;s oldest continuously operating amusement park (since 1846) launched its 180th season.')+C('Food','tag-green','May 16','CT Food Truck Battles Festival Coming to Bristol May 16','The popular statewide food truck competition comes to Bristol — dozens of vendors competing.')+C('Community','tag-yang','June 20','Bristol Farmers Market Opens June 20','Opens its 2026 season June 20. Local produce, artisan goods, and food vendors every Saturday through fall.')+C('Government','tag-yang','This Week','Mayor Discusses 2026-27 Budget — Focus on Infrastructure','Proposed $168M budget increases DPW road resurfacing by 12% and adds 6 firefighter positions.')+C('Business','tag-yang','This Week','Barnes Group Reports Record Q1 Aerospace Revenue','The 167-year-old Bristol company posts $412M quarterly revenue driven by defense contracts.')+'</div>'
  +'</div></section>';
}

function pageEngage(){
  return '<div class="hero"><div class="kicker kicker-purple">Yin · Reflective Signal · Community Voice</div><h1 class="display">What Bristol<br><span class="grad-text">Is Asking</span></h1><p class="hero-sub">Real questions from real residents. AI-assisted answers. The collective intelligence of Bristol CT.</p><div class="hero-actions"><button class="btn-gold" onclick="document.getElementById(&#39;chat-panel&#39;).classList.add(&#39;open&#39;)">Ask BristolBot AI ↗</button></div></div>'
  +'<section class="section"><div class="shell"><div class="qa-item"><div class="qa-q"><div class="qa-qmark">Q</div><div><h3 style="font-size:15px;font-weight:700">Best Bristol neighborhood for young families — Forestville, Federal Hill, or West End?</h3><p style="font-size:11px;color:var(--text-dim);margin-top:3px">@steph_m · 3h ago · 8 answers · Trending</p></div></div><div class="qa-answer"><div class="qa-amark">A</div><p style="font-size:13px;color:var(--text-mid)">Forestville is the consistent top answer — quieter streets, Page Park, strong school community, and Route 6 access. Federal Hill suits those wanting walkable downtown distance.</p></div></div><div class="qa-item"><div class="qa-q"><div class="qa-qmark">Q</div><div><h3 style="font-size:15px;font-weight:700">When does Lake Compounce open for the 2026 season?</h3><p style="font-size:11px;color:var(--text-dim);margin-top:3px">@parkpass2026 · 5h ago · 3 answers</p></div></div><div class="qa-answer"><div class="qa-amark">A</div><p style="font-size:13px;color:var(--text-mid)">Lake Compounce opened April 26, 2026 for its 180th season. Season passes available at lakecompounce.com. (860) 583-3300.</p></div></div><div class="qa-item"><div class="qa-q"><div class="qa-qmark">Q</div><div><h3 style="font-size:15px;font-weight:700">How do I commute to Hartford from Bristol without a car?</h3><p style="font-size:11px;color:var(--text-dim);margin-top:3px">@new_to_bristol · 9h ago · 5 answers</p></div></div><div class="qa-answer"><div class="qa-amark">A</div><p style="font-size:13px;color:var(--text-mid)">Take CTtransit Route 81 from downtown Bristol to New Britain (~25 min), then CTfastrak BRT into Hartford. Total trip: ~60 min. Passes at bristolct.gov/transit.</p></div></div><div class="qa-item"><div class="qa-q"><div class="qa-qmark">Q</div><div><h3 style="font-size:15px;font-weight:700">Is the Memorial Boulevard School / Theatre actually open and operating?</h3><p style="font-size:11px;color:var(--text-dim);margin-top:3px">@curious_resident · 12h ago · 6 answers</p></div></div><div class="qa-answer"><div class="qa-amark">A</div><p style="font-size:13px;color:var(--text-mid)">Ask BristolBot for the current status — use the AI chat for the most accurate and up-to-date answer on Memorial Boulevard School / Theatre.</p></div></div></div></section>';
}

function pageAI(){
  return '<div class="hero"><div class="kicker kicker-purple">Powered by Claude AI · Available 24/7</div><h1 class="display">BristolBot<br><span class="grad-text">AI Assistant</span></h1><p class="hero-sub">Your intelligent guide to everything Bristol CT — instant answers powered by Claude AI with deep local knowledge.</p></div>'
  +'<section class="section"><div class="shell"><div style="display:grid;grid-template-columns:1fr 300px;gap:24px;align-items:start"><div><div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r2);overflow:hidden"><div style="padding:18px 22px;border-bottom:1px solid var(--border);background:rgba(245,158,11,0.06)"><h3 style="font-weight:400;font-family:&#39;DM Serif Display&#39;,serif;color:var(--white)">BristolBot Chat</h3><p style="font-size:12px;color:var(--text-dim);margin-top:3px">Powered by Claude · Expert on Bristol CT</p></div><div id="ai-msgs" style="min-height:300px;max-height:440px;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:10px"><div class="chat-msg bot" style="max-width:100%">Hello! I am BristolBot — your AI expert on all things Bristol CT. Ask me about history, neighborhoods, ESPN, Lake Compounce, city services, commuting, or anything Bristol.</div></div><div style="padding:12px;border-top:1px solid var(--border)"><div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px"><span class="chat-sug" onclick="aiPage(&#39;Who founded ESPN?&#39;)">Who founded ESPN?</span><span class="chat-sug" onclick="aiPage(&#39;Tell me about Bristol clock history&#39;)">Clock history</span><span class="chat-sug" onclick="aiPage(&#39;What neighborhoods are in Bristol?&#39;)">Neighborhoods</span><span class="chat-sug" onclick="aiPage(&#39;How old is Lake Compounce?&#39;)">Lake Compounce</span></div><div style="display:flex;gap:8px"><input id="ai-pg-input" class="chat-input" placeholder="Ask anything about Bristol CT..." autocomplete="off" style="flex:1" onkeydown="if(event.key===&#39;Enter&#39;){aiPage(this.value);}"/><button class="chat-send" onclick="aiPage(document.getElementById(&#39;ai-pg-input&#39;).value)">Send</button></div></div></div></div><div><div class="card" style="margin-bottom:14px"><div class="card-tag tag-yang">Bristol Fast Facts</div><div class="dir-row"><div class="dir-name">Founded</div><div class="dir-phone">1785</div></div><div class="dir-row"><div class="dir-name">Population</div><div class="dir-phone">~60,000</div></div><div class="dir-row"><div class="dir-name">County</div><div class="dir-phone">Hartford</div></div><div class="dir-row"><div class="dir-name">Nicknames</div><div style="font-size:12px;color:var(--text-mid);font-weight:600">Clock, Bell, Mum City</div></div><div class="dir-row"><div class="dir-name">Largest Employer</div><div class="dir-phone">ESPN (3,600)</div></div></div><div class="card"><div class="card-tag tag-yin">Try Asking</div><div style="display:flex;flex-direction:column;gap:7px;margin-top:4px"><span class="chat-sug" style="text-align:left" onclick="aiPage(&#39;What is the Mum Festival?&#39;)">What is the Mum Festival?</span><span class="chat-sug" style="text-align:left" onclick="aiPage(&#39;How do I report a pothole?&#39;)">How do I report a pothole?</span><span class="chat-sug" style="text-align:left" onclick="aiPage(&#39;Tell me about Barnes Group&#39;)">Tell me about Barnes Group</span><span class="chat-sug" style="text-align:left" onclick="aiPage(&#39;What was New Departure?&#39;)">What was New Departure?</span></div></div></div></div></div></section>';
}

var aiPageHistory=[];
function aiPage(msg){
  if(!msg||!msg.trim())return;
  var msgs=document.getElementById('ai-msgs');if(!msgs)return;
  var inp=document.getElementById('ai-pg-input');if(inp)inp.value='';
  var um=document.createElement('div');um.className='chat-msg user';um.style.maxWidth='100%';um.textContent=msg;msgs.appendChild(um);
  aiPageHistory.push({role:'user',content:msg});
  var lm=document.createElement('div');lm.className='chat-msg loading';lm.style.maxWidth='100%';lm.textContent='BristolBot is thinking…';msgs.appendChild(lm);msgs.scrollTop=msgs.scrollHeight;
  fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:aiPageHistory})})
    .then(function(r){return r.json();}).then(function(d){var reply=d.content&&d.content[0]?d.content[0].text:'Sorry, no response.';aiPageHistory.push({role:'assistant',content:reply});lm.className='chat-msg bot';lm.style.maxWidth='100%';lm.textContent=reply;msgs.scrollTop=msgs.scrollHeight;})
    .catch(function(){lm.className='chat-msg bot';lm.textContent='Connection error.';});
}

function pageProjects(){
  return '<div class="hero"><div class="kicker kicker-gold">Active · City Infrastructure 2026</div><h1 class="display">Bristol City<br><span class="grad-text">Projects</span></h1><p class="hero-sub">Track every active infrastructure investment and community initiative across Bristol CT.</p></div>'
  +'<section class="section"><div class="shell"><div class="grid2"><div class="card"><div class="card-tag tag-yang">Major Development</div><h3>Centre Square Mixed-Use Redevelopment</h3><p>$42M downtown investment. 80 apartments, 25,000 sq ft retail, 200-seat restaurant. First tenants confirmed Spring 2026.</p><div class="prog-wrap"><div class="prog-label"><span>PROGRESS</span><span>65%</span></div><div class="prog-track"><div class="prog-fill" style="width:65%"></div></div></div></div><div class="card"><div class="card-tag tag-yang">Road Safety</div><h3>Route 6 Corridor Safety Improvements</h3><p>5 priority pedestrian crossings near Forestville. Signal upgrades and raised crosswalks. Entering design phase.</p><div class="prog-wrap"><div class="prog-label"><span>PROGRESS</span><span>40%</span></div><div class="prog-track"><div class="prog-fill" style="width:40%"></div></div></div></div><div class="card"><div class="card-tag tag-green">Near Complete</div><h3>Memorial Boulevard Resurfacing</h3><p>1.4-mile resurfacing from Rt-229 to downtown. New bike lanes and ADA curb cuts. Final paving layer pending weather.</p><div class="prog-wrap"><div class="prog-label"><span>PROGRESS</span><span>85%</span></div><div class="prog-track"><div class="prog-fill" style="width:85%"></div></div></div></div><div class="card"><div class="card-tag tag-yin">Education</div><h3>Chippens Hill Middle School Renovation</h3><p>$8.2M capital project. HVAC, structural upgrades, science wing. Construction begins Summer 2026.</p><div class="prog-wrap"><div class="prog-label"><span>PROGRESS</span><span>25%</span></div><div class="prog-track"><div class="prog-fill" style="width:25%"></div></div></div></div><div class="card"><div class="card-tag tag-green">Near Complete</div><h3>Forestville Community Garden Expansion</h3><p>20 new raised beds, irrigation, composting station at Page Park. Community-led installation ongoing.</p><div class="prog-wrap"><div class="prog-label"><span>PROGRESS</span><span>90%</span></div><div class="prog-track"><div class="prog-fill" style="width:90%"></div></div></div></div><div class="card"><div class="card-tag tag-green">Funded</div><h3>Pequabuck River Greenway — Forestville to Plainville</h3><p>$2.3M CT DEEP grant secured. 1.8-mile section completing a continuous path from Page Park to the Plainville town line.</p><div class="prog-wrap"><div class="prog-label"><span>PROGRESS</span><span>20%</span></div><div class="prog-track"><div class="prog-fill" style="width:20%"></div></div></div></div></div></div></section>';
}

function pageHistory(){
  return '<div class="hero"><div class="kicker kicker-gold">Est. 1785 · 241 Years of Story</div><h1 class="display">Bristol CT<br><span class="grad-text">History</span></h1><p class="hero-sub">From New Cambridge to Clock City to ESPN — Bristol&#39;s 241-year story is one of American industrial genius and community pride.</p></div>'
  +'<section class="section"><div class="shell"><div class="timeline"><div class="tl-item"><div class="tl-dot"></div><div class="tl-year">1785</div><div class="tl-title">Incorporated as Bristol</div><div class="tl-desc">Originally called "New Cambridge," Bristol officially incorporates on May 17, 1785.</div></div><div class="tl-item"><div class="tl-dot"></div><div class="tl-year">1800s — Clock City</div><div class="tl-title">World Clockmaking Capital</div><div class="tl-desc">Sessions Clock Co. (1827) and E. Ingraham (1843) produce millions of timepieces annually. The nickname "Clock City" is born.</div></div><div class="tl-item"><div class="tl-dot"></div><div class="tl-year">1846</div><div class="tl-title">Lake Compounce Opens</div><div class="tl-desc">Founded in 1846, Lake Compounce becomes America&#39;s oldest continuously operating amusement park — now in its 180th season.</div></div><div class="tl-item"><div class="tl-dot"></div><div class="tl-year">1857</div><div class="tl-title">Barnes Group Founded</div><div class="tl-desc">Wallace Barnes starts from clock-work wire, building what becomes Barnes Group — a global aerospace manufacturer still headquartered in Bristol 167 years later.</div></div><div class="tl-item"><div class="tl-dot"></div><div class="tl-year">1889</div><div class="tl-title">The Bristol Company Founded</div><div class="tl-desc">Prof. William H. Bristol founds The Bristol Company, inventing the Bristolphone (early sound film) and the first public address speakers at Yankee Stadium.</div></div><div class="tl-item"><div class="tl-dot"></div><div class="tl-year">WWI–WWII</div><div class="tl-title">New Departure — Wartime Giant</div><div class="tl-desc">11,000 Bristol workers produce precision ball bearings for Allied planes, ships, and tanks. GM acquires New Departure in 1919.</div></div><div class="tl-item"><div class="tl-dot"></div><div class="tl-year">1952</div><div class="tl-title">American Clock & Watch Museum Opens</div><div class="tl-desc">Preserving Bristol&#39;s clockmaking legacy with 6,000+ American-made timepieces — the largest such collection in the United States.</div></div><div class="tl-item"><div class="tl-dot"></div><div class="tl-year">Sept 7, 1979</div><div class="tl-title">ESPN Founded in Bristol</div><div class="tl-desc">Bill Rasmussen launches ESPN from Bristol after losing his job with the Hartford Whalers. The 24-hour sports network grows into a global media empire from 935 Middle Street.</div></div><div class="tl-item"><div class="tl-dot"></div><div class="tl-year">2026</div><div class="tl-title">BristolTalks Launches</div><div class="tl-desc">Bristol&#39;s AI-powered community platform goes live. The Clock City ticks on.</div></div></div></div></section>';
}

function pageNeighborhoods(){
  return '<div class="hero"><div class="kicker kicker-green">4 Neighborhoods · 1 City</div><h1 class="display">Bristol<br><span class="grad-text">Neighborhoods</span></h1><p class="hero-sub">Four distinct communities, each with its own character, history, and strengths.</p></div>'
  +'<section class="section"><div class="shell"><div class="grid2"><div class="nbhd-card"><div class="nbhd-header"><div class="nbhd-icon">🏛️</div><div class="nbhd-name">Federal Hill</div><div class="nbhd-tag tag-yang">Historic Core</div></div><div class="nbhd-body"><p style="font-size:13px;color:var(--text-mid);line-height:1.6">Bristol&#39;s historic downtown heart. City Hall, the public library, and the American Clock & Watch Museum anchor this walkable neighborhood. Close to the Centre Square redevelopment.</p><div class="nbhd-stats"><div class="nbhd-stat"><strong>0.8mi</strong><span>To City Hall</span></div><div class="nbhd-stat"><strong>1785</strong><span>Est.</span></div></div></div></div><div class="nbhd-card"><div class="nbhd-header"><div class="nbhd-icon">🌲</div><div class="nbhd-name">Forestville</div><div class="nbhd-tag tag-green">Family-Friendly</div></div><div class="nbhd-body"><p style="font-size:13px;color:var(--text-mid);line-height:1.6">Bristol&#39;s most family-recommended neighborhood. Quieter residential streets, Page Park, strong school community, and convenient Route 6 access.</p><div class="nbhd-stats"><div class="nbhd-stat"><strong>Page Park</strong><span>Centerpiece</span></div><div class="nbhd-stat"><strong>#1</strong><span>Family Pick</span></div></div></div></div><div class="nbhd-card"><div class="nbhd-header"><div class="nbhd-icon">🏠</div><div class="nbhd-name">Edgewood</div><div class="nbhd-tag tag-yin">Mixed Residential</div></div><div class="nbhd-body"><p style="font-size:13px;color:var(--text-mid);line-height:1.6">A diverse residential corridor along Route 229. A mix of single-family homes, multi-family properties, and local businesses. Convenient access to Route 6 and I-84.</p><div class="nbhd-stats"><div class="nbhd-stat"><strong>Rt 229</strong><span>Main Corridor</span></div><div class="nbhd-stat"><strong>I-84</strong><span>Nearby</span></div></div></div></div><div class="nbhd-card"><div class="nbhd-header"><div class="nbhd-icon">⚙️</div><div class="nbhd-name">Chippens Hill</div><div class="nbhd-tag tag-yang">Northern Bristol</div></div><div class="nbhd-body"><p style="font-size:13px;color:var(--text-mid);line-height:1.6">Northern Bristol with newer residential development and the historic GM/New Departure factory site — the largest industrial building under one roof in New England.</p><div class="nbhd-stats"><div class="nbhd-stat"><strong>1.4M sqft</strong><span>GM Factory Site</span></div><div class="nbhd-stat"><strong>North</strong><span>Position</span></div></div></div></div></div></div></section>';
}

function pageEvents(){
  return '<div class="hero"><div class="kicker kicker-gold">2026 Community Calendar</div><h1 class="display">Bristol<br><span class="grad-text">Events</span></h1><p class="hero-sub">From the Mum Festival to Food Truck Battles — everything happening in Bristol CT in 2026.</p></div>'
  +'<section class="section"><div class="shell"><div style="display:flex;flex-direction:column;gap:10px">'
  +'<div class="evt-card"><div class="evt-date"><div class="evt-month">APR</div><div class="evt-day">26</div></div><div class="evt-info"><div class="evt-title">Lake Compounce 2026 Season — Opened April 26</div><div class="evt-desc">America&#39;s oldest amusement park launched its 180th season. New family attraction revealed. (860) 583-3300.</div></div><div class="card-tag tag-yang" style="align-self:center;margin-left:auto;flex-shrink:0;margin-bottom:0">Open Now</div></div>'
  +'<div class="evt-card"><div class="evt-date"><div class="evt-month">MAY</div><div class="evt-day">16</div></div><div class="evt-info"><div class="evt-title">CT Food Truck Battles Festival — Bristol</div><div class="evt-desc">Popular statewide food truck competition comes to Bristol. Dozens of vendors competing. Downtown Bristol.</div></div><div class="card-tag tag-yang" style="align-self:center;margin-left:auto;flex-shrink:0;margin-bottom:0">Food</div></div>'
  +'<div class="evt-card"><div class="evt-date"><div class="evt-month">MAY</div><div class="evt-day">17</div></div><div class="evt-info"><div class="evt-title">Bristol Founders Day — 241st Anniversary</div><div class="evt-desc">Civic ceremonies marking Bristol&#39;s May 17, 1785 incorporation. City Hall Plaza with historical exhibits and community programming.</div></div><div class="card-tag tag-green" style="align-self:center;margin-left:auto;flex-shrink:0;margin-bottom:0">Free</div></div>'
  +'<div class="evt-card"><div class="evt-date"><div class="evt-month">JUN</div><div class="evt-day">20</div></div><div class="evt-info"><div class="evt-title">Bristol Farmers Market Opening Day 2026</div><div class="evt-desc">Opens its 2026 season. Local produce, artisan goods, and food vendors every Saturday through fall. Federal Hill area.</div></div><div class="card-tag tag-yang" style="align-self:center;margin-left:auto;flex-shrink:0;margin-bottom:0">Weekly</div></div>'
  +'<div class="evt-card"><div class="evt-date"><div class="evt-month">2nd/4th</div><div class="evt-day" style="font-size:16px">TUE</div></div><div class="evt-info"><div class="evt-title">City Council Regular Meetings</div><div class="evt-desc">Open to public. City Hall Council Chambers, 111 North Main St. 7:00 PM. Agendas at bristolct.gov.</div></div><div class="card-tag tag-yin" style="align-self:center;margin-left:auto;flex-shrink:0;margin-bottom:0">Public</div></div>'
  +'<div class="evt-card"><div class="evt-date"><div class="evt-month">JUL</div><div class="evt-day">4</div></div><div class="evt-info"><div class="evt-title">Bristol Fourth of July Parade</div><div class="evt-desc">One of Connecticut&#39;s largest Independence Day parades. Downtown route, marching bands, community floats. Fireworks at dusk.</div></div><div class="card-tag tag-yang" style="align-self:center;margin-left:auto;flex-shrink:0;margin-bottom:0">Free</div></div>'
  +'<div class="evt-card"><div class="evt-date"><div class="evt-month">SEP</div><div class="evt-day" style="font-size:16px">TBD</div></div><div class="evt-info"><div class="evt-title">Bristol Mum Festival — 60th Annual</div><div class="evt-desc">September festival on Federal Hill. Full pre-pandemic format: chrysanthemum show, carnival, parade, and Mum Pageant.</div></div><div class="card-tag tag-yang" style="align-self:center;margin-left:auto;flex-shrink:0;margin-bottom:0">Major</div></div>'
  +'</div></div></section>';
}

function pageDirectory(){
  return '<div class="hero"><div class="kicker kicker-red">Emergency · City Services · Contacts</div><h1 class="display">Bristol<br><span class="grad-text">Directory</span></h1><p class="hero-sub">Every phone number and department you need in Bristol CT — organized for fast access.</p></div>'
  +'<section class="section"><div class="shell"><div class="emergency-banner"><div><div class="emergency-num">911</div><div style="font-size:11px;color:#f87171;font-weight:700;letter-spacing:.08em;text-transform:uppercase">Emergency — Fire · Police · Medical</div></div><p style="font-size:13px;color:var(--text-mid);flex:1">For life-threatening emergencies only. For non-emergency issues — use the contacts below.</p></div><div class="grid2"><div class="card"><div class="card-tag tag-red">Public Safety</div><div class="dir-row"><div class="dir-name">Police (Non-Emergency)</div><div class="dir-phone">(860) 584-3011</div></div><div class="dir-row"><div class="dir-name">Fire (Non-Emergency)</div><div class="dir-phone">(860) 584-6030</div></div><div class="dir-row"><div class="dir-name">Bristol Hospital</div><div class="dir-phone">(860) 585-3000</div></div></div><div class="card"><div class="card-tag tag-yang">City Hall</div><div class="dir-row"><div class="dir-name">City Hall Main</div><div class="dir-phone">(860) 584-6100</div></div><div class="dir-row"><div class="dir-name">Mayor&#39;s Office</div><div class="dir-phone">(860) 584-6210</div></div><div class="dir-row"><div class="dir-name">Building Department</div><div class="dir-phone">(860) 584-6185</div></div></div><div class="card"><div class="card-tag tag-yin">Public Works & Parks</div><div class="dir-row"><div class="dir-name">DPW (Roads/Potholes)</div><div class="dir-phone">(860) 584-6175</div></div><div class="dir-row"><div class="dir-name">Parks & Recreation</div><div class="dir-phone">(860) 584-6160</div></div><div class="dir-row"><div class="dir-name">Public Library</div><div class="dir-phone">(860) 584-7787</div></div></div><div class="card"><div class="card-tag tag-yin">Key Businesses</div><div class="dir-row"><div class="dir-name">ESPN Main</div><div class="dir-phone">(860) 766-2000</div></div><div class="dir-row"><div class="dir-name">Lake Compounce</div><div class="dir-phone">(860) 583-3300</div></div><div class="dir-row"><div class="dir-name">Clock & Watch Museum</div><div class="dir-phone">(860) 583-6070</div></div></div></div><div style="margin-top:14px;padding:14px 18px;background:var(--glass);border:1px solid var(--border);border-radius:var(--r);font-size:13px;color:var(--text-mid)">City website: <strong style="color:var(--gold)">bristolct.gov</strong> · Bristol Press: <strong style="color:var(--gold)">bristolpress.com</strong></div></div></section>';
}

function pageGovernment(){
  return '<div class="hero"><div class="kicker kicker-gold">City of Bristol · Hartford County CT</div><h1 class="display">Bristol<br><span class="grad-text">Government</span></h1><p class="hero-sub">Your elected officials, city departments, online services, and the civic infrastructure that runs Bristol CT.</p></div>'
  +'<section class="section"><div class="shell"><div class="grid3">'+C('Executive','tag-yang','City Hall · 111 North Main St','Mayor&#39;s Office','The Mayor leads city administration, proposes the annual budget, and represents Bristol externally. (860) 584-6210 · bristolct.gov')+C('Legislative','tag-yang','2nd & 4th Tuesday 7PM','City Council','12-member elected council. Regular meetings open to the public. Agendas posted at bristolct.gov. Council Chambers, City Hall.')+C('Finance','tag-yin','Proposed FY2026-27','$168M City Budget','12% increase in DPW road funding. 6 new firefighter positions. Education remains largest expenditure at 62% of total.')+C('Public Works','tag-yin','(860) 584-6175','DPW — Roads & Infrastructure','Road maintenance, snow removal, waste collection. Report potholes at (860) 584-6175 or bristolct.gov/dpw.')+C('Online','tag-green','Available 24/7','bristolct.gov','Pay taxes, apply for permits, view meeting agendas, submit service requests, and access all city department portals.')+C('Public Safety','tag-yang','Emergency: 911','Police & Fire Departments','Bristol PD and Bristol Fire serve 24/7. Non-emergency police: (860) 584-3011. Non-emergency fire: (860) 584-6030.')+'</div></div></section>';
}

function pageBusiness(){
  return '<div class="hero"><div class="kicker kicker-gold">Bristol CT Economy</div><h1 class="display">Business &<br><span class="grad-text">Industry</span></h1><p class="hero-sub">From the world&#39;s greatest sports network to America&#39;s oldest amusement park — Bristol punches far above its weight.</p></div>'
  +'<section class="section"><div class="shell"><div style="background:linear-gradient(135deg,rgba(245,158,11,0.12),rgba(245,158,11,0.04));border:1px solid rgba(245,158,11,0.25);border-radius:var(--r2);padding:clamp(24px,4vw,44px);margin-bottom:22px"><div class="card-tag tag-yang" style="margin-bottom:14px">Founded Sept 7, 1979 · 935 Middle Street · Bristol CT</div><h2 style="font-size:clamp(28px,4vw,52px);font-weight:900;letter-spacing:-.05em;color:var(--white)">ESPN</h2><p style="color:var(--text-mid);margin-top:10px;font-size:15px;line-height:1.6;max-width:640px">The worldwide leader in sports. Founded by Bill Rasmussen after losing his job with the Hartford Whalers, ESPN launched from Bristol and never left. The 120-acre Bristol campus houses 18 buildings, 1.3 million square feet, and approximately 3,600 employees.</p><div class="grid4" style="margin-top:20px"><div style="background:rgba(245,158,11,0.1);border-radius:var(--r);border:1px solid rgba(245,158,11,0.2);padding:16px;text-align:center"><div class="stat-num" data-count="3600">0</div><div class="stat-label">Bristol Employees</div></div><div style="background:rgba(245,158,11,0.1);border-radius:var(--r);border:1px solid rgba(245,158,11,0.2);padding:16px;text-align:center"><div class="stat-num">120</div><div class="stat-label">Acre Campus</div></div><div style="background:rgba(245,158,11,0.1);border-radius:var(--r);border:1px solid rgba(245,158,11,0.2);padding:16px;text-align:center"><div class="stat-num">1979</div><div class="stat-label">Founded</div></div><div style="background:rgba(245,158,11,0.1);border-radius:var(--r);border:1px solid rgba(245,158,11,0.2);padding:16px;text-align:center"><div class="stat-num">80%</div><div class="stat-label">Disney Owned</div></div></div></div>'
  +'<div class="grid3">'+C('Since 1846 · Route 229','tag-yang','','Lake Compounce','America&#39;s oldest continuously operating amusement park. 180 seasons strong. New family coaster for 2026. (860) 583-3300.')+C('Since 1857 · NYSE: B','tag-yang','','Barnes Group','Founded from clock-work wire by Wallace Barnes. Now a global aerospace and industrial manufacturer still headquartered in Bristol after 167 years.')+C('Healthcare','tag-green','','Bristol Hospital','Major Bristol employer and healthcare anchor. Full-service hospital with emergency, surgical, and specialty care. (860) 585-3000.')+C('Local Craft','tag-yin','','Firefly Brewing','Bristol&#39;s craft brewery. Rotating seasonal taps and the Bristol 1785 Anniversary Lager celebrating 241 years of city history.')+C('Cultural','tag-yin','','American Clock & Watch Museum','Founded 1952. Over 6,000 American-made timepieces preserving Bristol&#39;s Clock City legacy. (860) 583-6070.')+C('Cultural','tag-yin','','New England Carousel Museum','Dedicated to preserving antique carousel art and the craftsmanship of the golden age of carousels.')+'</div></div></section>';
}

function pageAbout(){
  return '<div class="hero"><div class="kicker kicker-purple">R Unlimited LLC · Bristol CT</div><h1 class="display">About<br><span class="grad-text">BristolTalks</span></h1><p class="hero-sub">Bristol Connecticut&#39;s AI-powered community intelligence platform — built for residents, businesses, and civic leaders.</p></div>'
  +'<section class="section"><div class="shell"><div class="grid2">'+C('The Mission','tag-yang','','One Platform, Whole City','BristolTalks was built so Bristol CT has a modern, AI-powered community platform that makes local information fast, beautiful, and actionable. No paywalls. No algorithms hiding local news. Just Bristol, clearly presented.')+C('Technology','tag-green','','Cloudflare + Claude AI','BristolTalks runs on Cloudflare Workers — serverless edge infrastructure. BristolBot is powered by Anthropic&#39;s Claude AI with deep Bristol CT knowledge baked in.')+C('The Builder','tag-yang','','R Unlimited LLC · Bristol CT','BristolTalks is built and operated by R Unlimited LLC, a Bristol-based AI company building AI-powered tools for local communities, small businesses, and civic organizations across Connecticut.')+C('Contact','tag-yin','riveraf30@gmail.com','Get in Touch','Story tip, feedback, partnership idea, or business inquiry — reach the BristolTalks team at riveraf30@gmail.com.')+'</div></div></section>';
}

function pageConnect(){
  return '<div class="hero"><div class="kicker kicker-green">Get in Touch · Join the Community</div><h1 class="display">Connect With<br><span class="grad-text">BristolTalks</span></h1><p class="hero-sub">Story tip, question, feedback, or partnership idea? We want to hear from Bristol.</p></div>'
  +'<section class="section"><div class="shell"><div class="grid2"><div class="card"><div class="card-tag tag-green">Contact</div><h3>Reach the BristolTalks Team</h3><p style="margin-bottom:14px">For story tips, corrections, partnerships, or feedback:</p><div class="dir-row"><div class="dir-name">Email</div><div class="dir-phone">riveraf30@gmail.com</div></div><div class="dir-row"><div class="dir-name">Platform</div><div class="dir-phone">bristoltalks.com</div></div><div class="dir-row"><div class="dir-name">Operated by</div><div style="font-size:12px;color:var(--text-mid);font-weight:600">R Unlimited LLC · Bristol CT</div></div></div><div class="card"><div class="card-tag tag-yin">BristolBot AI</div><h3>Ask BristolBot Any Time</h3><p style="margin-bottom:14px">The fastest way to get Bristol CT answers — BristolBot is available 24/7 and expert on everything Bristol.</p><button class="btn-gold" onclick="document.getElementById(&#39;chat-panel&#39;).classList.add(&#39;open&#39;)">Open BristolBot ↗</button></div>'+C('Story Tips','tag-yang','','Share What You Know','Know about a Bristol project, business opening, community event, or civic issue? Email riveraf30@gmail.com with subject "Story Tip."')+C('Partnerships','tag-yin','','Work With BristolTalks','Bristol businesses, nonprofits, and civic organizations interested in reaching the Bristol CT community — we offer community sponsorships and custom AI integrations.')+'</div></div></section>';
}

function pageFunnelProtect(){
  return '<div class="hero"><div class="kicker kicker-gold">R Unlimited LLC &middot; Bristol CT</div><h1 class="display">Protect Your Business<br><span class="grad-text">With AI</span></h1><p class="hero-sub">Bristol CT businesses are moving to AI-powered tools. Get ahead &mdash; protect your revenue, your time, and your competitive edge.</p></div>'
  +'<section class="section"><div class="shell"><div class="grid3" style="margin-bottom:40px">'
  +'<div class="card"><div class="card-tag tag-yang">Save Time</div><h3 style="color:var(--white);margin:12px 0 8px">AI handles the busywork</h3><p style="color:var(--text-muted);font-size:14px">Automate content, emails, and customer replies so you focus on what matters.</p></div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.04)"><div class="card-tag tag-gold">Stay Competitive</div><h3 style="color:var(--white);margin:12px 0 8px">Don&#39;t get left behind</h3><p style="color:var(--text-muted);font-size:14px">Local competitors are already using AI. We make it simple for Bristol businesses to catch up and pull ahead.</p></div>'
  +'<div class="card"><div class="card-tag tag-yang">No Tech Skills</div><h3 style="color:var(--white);margin:12px 0 8px">We set it all up</h3><p style="color:var(--text-muted);font-size:14px">Full onboarding included. You run your business &mdash; we handle the AI integration.</p></div>'
  +'</div><div style="text-align:center"><button class="btn-gold" style="font-size:16px;padding:16px 36px" onclick="go(&#39;productprotect&#39;)">See BusinessShield AI &rarr;</button><p style="color:var(--text-muted);font-size:13px;margin-top:12px">From $97/mo &middot; Powered by Cloudflare + Claude AI</p></div></div></section>';
}

function pageFunnelFreedom(){
  return '<div class="hero"><div class="kicker kicker-gold">R Unlimited LLC &middot; Bristol CT</div><h1 class="display">Build the Business<br><span class="grad-text">You Imagined</span></h1><p class="hero-sub">Freedom means building on your own terms. BristolTalks gives local entrepreneurs the AI tools and community network to grow independently.</p></div>'
  +'<section class="section"><div class="shell"><div class="grid3" style="margin-bottom:40px">'
  +'<div class="card"><div class="card-tag tag-yang">Community</div><h3 style="color:var(--white);margin:12px 0 8px">Bristol Business Network</h3><p style="color:var(--text-muted);font-size:14px">Connect with 400+ local businesses, nonprofits, and community organizations.</p></div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.04)"><div class="card-tag tag-gold">AI Tools</div><h3 style="color:var(--white);margin:12px 0 8px">Your AI business partner</h3><p style="color:var(--text-muted);font-size:14px">BristolBot knows Bristol CT inside and out &mdash; use it to research, plan, and grow your business.</p></div>'
  +'<div class="card"><div class="card-tag tag-yang">Visibility</div><h3 style="color:var(--white);margin:12px 0 8px">Get found in Bristol</h3><p style="color:var(--text-muted);font-size:14px">List your business in the Bristol directory and reach the community where they are already searching.</p></div>'
  +'</div><div style="text-align:center"><button class="btn-gold" style="font-size:16px;padding:16px 36px" onclick="go(&#39;productfreedom&#39;)">See Bristol LaunchPad &rarr;</button><p style="color:var(--text-muted);font-size:13px;margin-top:12px">$149 setup &middot; $49/mo &middot; Go live in 24 hours</p></div></div></section>';
}

function pageFunnelConfidence(){
  return '<div class="hero"><div class="kicker kicker-gold">Powered by Claude AI &middot; Available 24/7</div><h1 class="display">AI That Gives You<br><span class="grad-text">Confidence</span></h1><p class="hero-sub">Get instant, accurate answers about Bristol CT &mdash; local news, government, events, businesses, and more. Powered by Claude AI with deep local knowledge.</p></div>'
  +'<section class="section"><div class="shell"><div class="grid3" style="margin-bottom:40px">'
  +'<div class="card"><div class="card-tag tag-yang">Instant Answers</div><h3 style="color:var(--white);margin:12px 0 8px">Ask anything about Bristol</h3><p style="color:var(--text-muted);font-size:14px">History, events, businesses, city services &mdash; BristolBot knows it all and answers in seconds.</p></div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.04)"><div class="card-tag tag-gold">Always On</div><h3 style="color:var(--white);margin:12px 0 8px">Available 24/7</h3><p style="color:var(--text-muted);font-size:14px">No waiting for office hours. BristolBot answers at midnight just as well as at noon.</p></div>'
  +'<div class="card"><div class="card-tag tag-yang">Local Expert</div><h3 style="color:var(--white);margin:12px 0 8px">Deep Bristol knowledge</h3><p style="color:var(--text-muted);font-size:14px">Trained on Bristol CT data &mdash; not generic AI answers. Real local intelligence for real Bristol questions.</p></div>'
  +'</div><div style="text-align:center"><button class="btn-gold" style="font-size:16px;padding:16px 36px" onclick="go(&#39;productconfidence&#39;)">See BristolBot Pro &rarr;</button><p style="color:var(--text-muted);font-size:13px;margin-top:12px">$29/mo &middot; Chat history &middot; Priority AI access</p></div></div></section>';
}

function pageProductProtect(){
  return '<div class="hero"><div class="kicker kicker-gold">BusinessShield AI &middot; Powered by Cloudflare + Claude</div><h1 class="display">AI Protection for<br><span class="grad-text">Your Business</span></h1><p class="hero-sub">BusinessShield scans your online presence for risks, monitors competitors, and delivers weekly AI threat reports &mdash; all running on Cloudflare&#39;s global network. Zero server management.</p></div>'
  +'<section class="section"><div class="shell">'
  +'<div class="grid3" style="margin-bottom:32px">'
  +'<div class="card"><div class="card-tag tag-yang">AI Risk Scanner</div><h3 style="color:var(--white);margin:12px 0 8px">Weekly threat analysis</h3><p style="color:var(--text-mid);font-size:14px;margin-bottom:12px">Claude AI scans your business name, reviews, and online footprint every week. Get a plain-English report of risks and what to do about them.</p><div style="font-size:12px;color:var(--text-dim)">Powered by: Workers + D1 + Claude Haiku</div></div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.04)"><div class="card-tag tag-gold">Cloudflare Shield</div><h3 style="color:var(--white);margin:12px 0 8px">Bot &amp; spam protection</h3><p style="color:var(--text-mid);font-size:14px;margin-bottom:12px">Cloudflare Turnstile blocks bots from your contact forms and booking pages. No annoying CAPTCHAs &mdash; invisible protection that just works.</p><div style="font-size:12px;color:var(--text-dim)">Powered by: Cloudflare Turnstile + Workers</div></div>'
  +'<div class="card"><div class="card-tag tag-yang">Instant Alerts</div><h3 style="color:var(--white);margin:12px 0 8px">Know before it hurts</h3><p style="color:var(--text-mid);font-size:14px;margin-bottom:12px">New negative review? Competitor undercutting your price? Get notified instantly via email so you can respond fast &mdash; not days later.</p><div style="font-size:12px;color:var(--text-dim)">Powered by: Workers + D1 + Email Routing</div></div>'
  +'</div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.5);background:rgba(245,158,11,0.06);max-width:560px;margin:0 auto 24px;text-align:center">'
  +'<div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--gradient);color:#000;font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;padding:4px 14px;border-radius:999px;white-space:nowrap">Most Popular</div>'
  +'<div class="card-tag tag-gold" style="margin-top:8px">Monthly Plan</div>'
  +'<h3 style="font-size:48px;font-weight:900;font-family:&quot;Space Grotesk&quot;,sans-serif;color:var(--white);margin:12px 0 4px">$97<span style="font-size:18px;font-weight:400;color:var(--text-mid)">/mo</span></h3>'
  +'<p style="color:var(--text-mid);font-size:14px;margin-bottom:20px">Everything included. Cancel anytime.</p>'
  +'<ul style="list-style:none;margin-bottom:24px;font-size:14px;color:var(--text-mid);text-align:left;display:inline-block">'
  +'<li style="padding:5px 0">&#10003; Weekly AI threat report</li>'
  +'<li style="padding:5px 0">&#10003; Cloudflare bot protection</li>'
  +'<li style="padding:5px 0">&#10003; Competitor price monitoring</li>'
  +'<li style="padding:5px 0">&#10003; Review alert notifications</li>'
  +'<li style="padding:5px 0">&#10003; Monthly strategy call with Fernando</li>'
  +'</ul>'
  +'<button class="btn-gold" style="width:100%;font-size:16px;padding:14px" onclick="(function(){var s=document.getElementById(&#39;lead-service&#39;);if(s){for(var i=0;i&lt;s.options.length;i++){if(s.options[i].value===&#39;setup&#39;){s.options[i].selected=true;break;}}}go(&#39;connect&#39;);})()">Get BusinessShield &rarr;</button>'
  +'<p style="font-size:12px;color:var(--text-dim);margin-top:10px">Setup &mdash; free with first month &middot; No contracts</p>'
  +'</div>'
  +'<div class="card" style="text-align:center;max-width:560px;margin:0 auto"><h3>Want to see it in action?</h3><p style="margin:10px 0 16px;color:var(--text-mid)">Run a free business risk scan right now &mdash; no account needed. Takes 60 seconds.</p><a href="https://shield.bristoltalks.com" style="display:inline-block" onclick="event.preventDefault();go(&#39;connect&#39;)"><button class="btn-gold">Run Free Scan &rarr;</button></a></div>'
  +'</div></section>';
}

function pageProductFreedom(){
  return '<div class="hero"><div class="kicker kicker-gold">Bristol LaunchPad &middot; Powered by Cloudflare</div><h1 class="display">Your Business Online<br><span class="grad-text">in 24 Hours</span></h1><p class="hero-sub">Bristol LaunchPad builds your business presence on Cloudflare&#39;s global network &mdash; fast, reliable, and optimized for Bristol CT searches. No tech skills needed.</p></div>'
  +'<section class="section"><div class="shell">'
  +'<div class="grid3" style="margin-bottom:32px">'
  +'<div class="card"><div class="card-tag tag-yang">Instant Listing</div><h3 style="color:var(--white);margin:12px 0 8px">Bristol directory profile</h3><p style="color:var(--text-mid);font-size:14px;margin-bottom:12px">Your business listed in the BristolTalks directory &mdash; the community goes there first when they need local services. Get found where it counts.</p><div style="font-size:12px;color:var(--text-dim)">Powered by: Workers + D1 + KV Cache</div></div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.04)"><div class="card-tag tag-gold">AI Content</div><h3 style="color:var(--white);margin:12px 0 8px">We write it for you</h3><p style="color:var(--text-mid);font-size:14px;margin-bottom:12px">Claude AI generates your business description, service list, and FAQ based on a 10-minute intake call. Professional copy, zero writing on your part.</p><div style="font-size:12px;color:var(--text-dim)">Powered by: Claude Haiku + Workers</div></div>'
  +'<div class="card"><div class="card-tag tag-yang">Lightning Fast</div><h3 style="color:var(--white);margin:12px 0 8px">Cloudflare global network</h3><p style="color:var(--text-mid);font-size:14px;margin-bottom:12px">Your page loads in under 100ms anywhere in the world. Cloudflare KV caches your content at 300+ edge locations &mdash; no slow hosting bills.</p><div style="font-size:12px;color:var(--text-dim)">Powered by: Cloudflare Workers + KV</div></div>'
  +'</div>'
  +'<div class="grid2" style="max-width:820px;margin:0 auto 24px;gap:16px">'
  +'<div class="card" style="text-align:center">'
  +'<div class="card-tag tag-yang">One-Time Setup</div>'
  +'<h3 style="font-size:42px;font-weight:900;font-family:&quot;Space Grotesk&quot;,sans-serif;color:var(--white);margin:12px 0 4px">$149</h3>'
  +'<p style="color:var(--text-mid);font-size:13px;margin-bottom:16px">Full setup, done for you</p>'
  +'<ul style="list-style:none;margin-bottom:20px;font-size:13px;color:var(--text-mid);text-align:left">'
  +'<li style="padding:4px 0">&#10003; Intake call with Fernando</li>'
  +'<li style="padding:4px 0">&#10003; AI-written business copy</li>'
  +'<li style="padding:4px 0">&#10003; Bristol directory listing</li>'
  +'<li style="padding:4px 0">&#10003; Live in 24 hours</li>'
  +'</ul>'
  +'<button class="btn-gold" style="width:100%" onclick="go(&#39;connect&#39;)">Get Setup &rarr;</button>'
  +'</div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.5);background:rgba(245,158,11,0.06);text-align:center;position:relative">'
  +'<div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--gradient);color:#000;font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;padding:4px 14px;border-radius:999px;white-space:nowrap">Best Value</div>'
  +'<div class="card-tag tag-gold" style="margin-top:8px">Monthly</div>'
  +'<h3 style="font-size:42px;font-weight:900;font-family:&quot;Space Grotesk&quot;,sans-serif;color:var(--white);margin:12px 0 4px">$49<span style="font-size:16px;font-weight:400;color:var(--text-mid)">/mo</span></h3>'
  +'<p style="color:var(--text-mid);font-size:13px;margin-bottom:16px">After setup &middot; Cancel anytime</p>'
  +'<ul style="list-style:none;margin-bottom:20px;font-size:13px;color:var(--text-mid);text-align:left">'
  +'<li style="padding:4px 0">&#10003; Monthly content refresh</li>'
  +'<li style="padding:4px 0">&#10003; Listing stays current</li>'
  +'<li style="padding:4px 0">&#10003; Performance reports</li>'
  +'<li style="padding:4px 0">&#10003; Priority support</li>'
  +'</ul>'
  +'<button class="btn-gold" style="width:100%" onclick="go(&#39;connect&#39;)">Start LaunchPad &rarr;</button>'
  +'</div>'
  +'</div>'
  +'</div></section>';
}

function pageProductConfidence(){
  return '<div class="hero"><div class="kicker kicker-gold">BristolBot Pro &middot; Claude AI &middot; Always On</div><h1 class="display">Your Personal<br><span class="grad-text">Bristol AI Assistant</span></h1><p class="hero-sub">BristolBot Pro saves your conversations, gives priority AI access, and unlocks Bristol business research mode &mdash; for residents and business owners who rely on AI every day.</p></div>'
  +'<section class="section"><div class="shell">'
  +'<div class="grid3" style="margin-bottom:32px">'
  +'<div class="card"><div class="card-tag tag-yang">Chat History</div><h3 style="color:var(--white);margin:12px 0 8px">Conversations that remember</h3><p style="color:var(--text-mid);font-size:14px;margin-bottom:12px">Every chat saved to your D1 database. Pick up exactly where you left off &mdash; research threads, business plans, city questions &mdash; all preserved across sessions.</p><div style="font-size:12px;color:var(--text-dim)">Powered by: Cloudflare D1 + Workers</div></div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.04)"><div class="card-tag tag-gold">Priority AI</div><h3 style="color:var(--white);margin:12px 0 8px">Faster, deeper answers</h3><p style="color:var(--text-mid);font-size:14px;margin-bottom:12px">Pro users get Claude Sonnet instead of Haiku &mdash; more nuanced, more detailed, better reasoning. Ask it to draft a business plan or analyze a city ordinance.</p><div style="font-size:12px;color:var(--text-dim)">Powered by: Claude Sonnet + Workers</div></div>'
  +'<div class="card"><div class="card-tag tag-yang">Business Mode</div><h3 style="color:var(--white);margin:12px 0 8px">Bristol business intelligence</h3><p style="color:var(--text-mid);font-size:14px;margin-bottom:12px">Switch to Business Mode for competitive research, local market data, permit guidance, and city contract lookups &mdash; all sourced from Bristol CT public records.</p><div style="font-size:12px;color:var(--text-dim)">Powered by: Workers + KV + D1</div></div>'
  +'</div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.5);background:rgba(245,158,11,0.06);max-width:480px;margin:0 auto 24px;text-align:center;position:relative">'
  +'<div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--gradient);color:#000;font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;padding:4px 14px;border-radius:999px;white-space:nowrap">Limited Beta</div>'
  +'<div class="card-tag tag-gold" style="margin-top:8px">Pro Plan</div>'
  +'<h3 style="font-size:48px;font-weight:900;font-family:&quot;Space Grotesk&quot;,sans-serif;color:var(--white);margin:12px 0 4px">$29<span style="font-size:18px;font-weight:400;color:var(--text-mid)">/mo</span></h3>'
  +'<p style="color:var(--text-mid);font-size:14px;margin-bottom:20px">First 30 days free &middot; Cancel anytime</p>'
  +'<ul style="list-style:none;margin-bottom:24px;font-size:14px;color:var(--text-mid);text-align:left;display:inline-block">'
  +'<li style="padding:5px 0">&#10003; Unlimited chat history (D1 storage)</li>'
  +'<li style="padding:5px 0">&#10003; Claude Sonnet (vs free Haiku)</li>'
  +'<li style="padding:5px 0">&#10003; Bristol Business Mode</li>'
  +'<li style="padding:5px 0">&#10003; Priority response queue</li>'
  +'<li style="padding:5px 0">&#10003; Monthly Bristol briefing digest</li>'
  +'</ul>'
  +'<button class="btn-gold" style="width:100%;font-size:16px;padding:14px" onclick="go(&#39;connect&#39;)">Start Free Trial &rarr;</button>'
  +'<p style="font-size:12px;color:var(--text-dim);margin-top:10px">No credit card for trial &middot; Bristol residents only (beta)</p>'
  +'</div>'
  +'<div class="card" style="text-align:center;max-width:480px;margin:0 auto">'
  +'<h3>Try the free version first</h3><p style="margin:10px 0 16px;color:var(--text-mid)">BristolBot is free and available right now. No account, no signup &mdash; just ask.</p>'
  +'<button class="btn-gold" onclick="document.getElementById(&#39;chat-panel&#39;).classList.add(&#39;open&#39;)">Open BristolBot &rarr;</button>'
  +'</div>'
  +'</div></section>';
}

function pageServices(){
  return '<div class="hero"><div class="kicker kicker-gold">R Unlimited LLC · Bristol CT</div><h1 class="display">AI Services for<br><span class="grad-text">Local Business</span></h1><p class="hero-sub">Simple, affordable AI integrations for Bristol CT businesses, nonprofits, and community organizations. No tech background required.</p></div>'
  +'<section class="section"><div class="shell">'
  +'<div class="grid3" style="margin-bottom:32px">'
  +'<div class="card" style="border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.04)">'
  +'<div class="card-tag tag-yang">One-Time Setup</div>'
  +'<h3 style="font-size:36px;font-weight:900;font-family:&quot;Space Grotesk&quot;,sans-serif;color:var(--white);margin-bottom:4px">$150</h3>'
  +'<div style="font-size:13px;color:var(--text-mid);margin-bottom:16px">Complete setup package</div>'
  +'<h3 style="margin-bottom:10px">BristolTalks Setup Package</h3>'
  +'<p style="margin-bottom:20px">Full platform onboarding: AI assistant configuration, content integration, and launch support. Everything to get your business on the BristolTalks platform.</p>'
  +'<ul style="list-style:none;margin-bottom:20px;font-size:13px;color:var(--text-mid)">'
  +'<li style="padding:4px 0">✓ AI assistant setup</li><li style="padding:4px 0">✓ Content integration</li><li style="padding:4px 0">✓ Launch support</li><li style="padding:4px 0">✓ 30-day follow-up</li>'
  +'</ul>'
  +'<button class="btn-gold" style="width:100%" onclick="checkout(&quot;setup&quot;)">Get Started — $150 →</button>'
  +'</div>'
  +'<div class="card" style="border-color:rgba(245,158,11,0.5);background:rgba(245,158,11,0.07);position:relative">'
  +'<div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--gradient);color:#000;font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;padding:4px 14px;border-radius:999px">Most Popular</div>'
  +'<div class="card-tag tag-yang" style="margin-top:8px">Monthly</div>'
  +'<h3 style="font-size:36px;font-weight:900;font-family:&quot;Space Grotesk&quot;,sans-serif;color:var(--white);margin-bottom:4px">$49<span style="font-size:16px;font-weight:400;color:var(--text-mid)">/mo</span></h3>'
  +'<div style="font-size:13px;color:var(--text-mid);margin-bottom:16px">Cancel any time</div>'
  +'<h3 style="margin-bottom:10px">Monthly Maintenance</h3>'
  +'<p style="margin-bottom:20px">Ongoing AI platform management: content updates, performance monitoring, and community engagement support every month.</p>'
  +'<ul style="list-style:none;margin-bottom:20px;font-size:13px;color:var(--text-mid)">'
  +'<li style="padding:4px 0">✓ Monthly content refresh</li><li style="padding:4px 0">✓ Performance reports</li><li style="padding:4px 0">✓ Priority support</li><li style="padding:4px 0">✓ Quarterly strategy call</li>'
  +'</ul>'
  +'<button class="btn-gold" style="width:100%" onclick="checkout(&quot;monthly&quot;)">Subscribe — $49/mo →</button>'
  +'</div>'
  +'<div class="card">'
  +'<div class="card-tag tag-yin">Digital Download</div>'
  +'<h3 style="font-size:36px;font-weight:900;font-family:&quot;Space Grotesk&quot;,sans-serif;color:var(--white);margin-bottom:4px">$27</h3>'
  +'<div style="font-size:13px;color:var(--text-mid);margin-bottom:16px">Instant access</div>'
  +'<h3 style="margin-bottom:10px">Digital Toolkit</h3>'
  +'<p style="margin-bottom:20px">AI prompt library, local business templates, and a Bristol CT marketing guide — everything a small business needs to get started with AI today.</p>'
  +'<ul style="list-style:none;margin-bottom:20px;font-size:13px;color:var(--text-mid)">'
  +'<li style="padding:4px 0">✓ 50+ AI prompts</li><li style="padding:4px 0">✓ Business templates</li><li style="padding:4px 0">✓ Marketing guide</li><li style="padding:4px 0">✓ Lifetime updates</li>'
  +'</ul>'
  +'<button class="btn-gold" style="width:100%" onclick="checkout(&quot;toolkit&quot;)">Buy Now — $27 →</button>'
  +'</div>'
  +'</div>'
  +'<div id="checkout-msg" style="display:none;padding:14px;border-radius:10px;margin-bottom:20px;font-size:14px;font-weight:600;text-align:center"></div>'
  +'<div class="card" style="text-align:center"><h3>Not sure which plan is right for you?</h3><p style="margin:10px 0 16px">Book a free 20-minute call with Fernando at R Unlimited LLC — we&#39;ll figure out the best fit for your Bristol business.</p><button class="btn-gold" onclick="go(&quot;connect&quot;)">Book a Free Call →</button></div>'
  +'</div></section>';
}

function pageConnect(){
  return '<div class="hero"><div class="kicker kicker-green">Get in Touch · Join the Community</div><h1 class="display">Connect With<br><span class="grad-text">BristolTalks</span></h1><p class="hero-sub">Story tip, question, feedback, or partnership idea? We want to hear from Bristol.</p></div>'
  +'<section class="section"><div class="shell"><div class="grid2">'
  +'<div>'
  +'<div class="card" style="margin-bottom:16px">'
  +'<div class="card-tag tag-green">Send a Message</div>'
  +'<h3 style="margin-bottom:16px">Get in Touch</h3>'
  +'<div id="lead-msg" style="display:none;padding:12px;border-radius:8px;margin-bottom:14px;font-size:13px;font-weight:600"></div>'
  +'<div style="display:flex;flex-direction:column;gap:10px">'
  +'<input id="lead-name" placeholder="Your name *" style="background:var(--glass);border:1px solid var(--border);border-radius:7px;padding:10px 12px;color:var(--text);font-size:13px;font-family:&quot;DM Sans&quot;,sans-serif;outline:none" onfocus="this.style.borderColor=&quot;var(--gold)&quot;" onblur="this.style.borderColor=&quot;var(--border)&quot;"/>'
  +'<input id="lead-email" type="email" placeholder="Email address *" style="background:var(--glass);border:1px solid var(--border);border-radius:7px;padding:10px 12px;color:var(--text);font-size:13px;font-family:&quot;DM Sans&quot;,sans-serif;outline:none" onfocus="this.style.borderColor=&quot;var(--gold)&quot;" onblur="this.style.borderColor=&quot;var(--border)&quot;"/>'
  +'<input id="lead-phone" placeholder="Phone (optional)" style="background:var(--glass);border:1px solid var(--border);border-radius:7px;padding:10px 12px;color:var(--text);font-size:13px;font-family:&quot;DM Sans&quot;,sans-serif;outline:none" onfocus="this.style.borderColor=&quot;var(--gold)&quot;" onblur="this.style.borderColor=&quot;var(--border)&quot;"/>'
  +'<select id="lead-service" style="background:var(--glass);border:1px solid var(--border);border-radius:7px;padding:10px 12px;color:var(--text-mid);font-size:13px;font-family:&quot;DM Sans&quot;,sans-serif;outline:none;cursor:pointer"><option value="">What can we help with? (optional)</option><option value="setup">Setup Package ($150)</option><option value="monthly">Monthly Maintenance ($49/mo)</option><option value="toolkit">Digital Toolkit ($27)</option><option value="story">Story Tip</option><option value="partnership">Partnership / Sponsorship</option><option value="other">Other</option></select>'
  +'<textarea id="lead-message" placeholder="Message (optional)" rows="4" style="background:var(--glass);border:1px solid var(--border);border-radius:7px;padding:10px 12px;color:var(--text);font-size:13px;font-family:&quot;DM Sans&quot;,sans-serif;outline:none;resize:vertical"></textarea>'
  +'<button class="btn-gold" id="lead-submit" onclick="submitLead()">Send Message →</button>'
  +'</div></div>'
  +'</div>'
  +'<div>'
  +'<div class="card" style="margin-bottom:16px"><div class="card-tag tag-yin">BristolBot AI</div><h3>Ask BristolBot Any Time</h3><p style="margin-bottom:14px">The fastest way to get Bristol CT answers — BristolBot is available 24/7.</p><button class="btn-gold" onclick="document.getElementById(&quot;chat-panel&quot;).classList.add(&quot;open&quot;)">Open BristolBot ↗</button></div>'
  +C('Story Tips','tag-yang','','Share What You Know','Know about a Bristol project, business opening, community event, or civic issue? Use the form or email riveraf30@gmail.com with subject "Story Tip."')
  +C('Partnerships','tag-yin','','Work With BristolTalks','Bristol businesses, nonprofits, and civic organizations — we offer community sponsorships and custom AI integrations.')+C('Services','tag-green','','View Our Packages','Setup package ($150), monthly maintenance ($49/mo), or digital toolkit ($27). <span style="color:var(--gold);cursor:pointer" onclick="go(&quot;services&quot;)">See all plans &rarr;</span>')
  +'</div>'
  +'</div></div></section>';
}

function checkout(priceId){
  var msg=document.getElementById('checkout-msg');
  if(msg){msg.style.display='block';msg.style.background='rgba(245,158,11,0.1)';msg.style.color='var(--gold)';msg.textContent='Redirecting to secure checkout…';}
  fetch('/api/checkout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({priceId:priceId})})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.url){window.location.href=d.url;}
      else if(msg){msg.style.background='rgba(239,68,68,0.1)';msg.style.color='#f87171';msg.textContent=d.error||'Checkout unavailable — please try again.';}
    })
    .catch(function(){if(msg){msg.style.background='rgba(239,68,68,0.1)';msg.style.color='#f87171';msg.textContent='Connection error — please try again.';}});
}
function submitLead(){
  var name=document.getElementById('lead-name');
  var email=document.getElementById('lead-email');
  var phone=document.getElementById('lead-phone');
  var service=document.getElementById('lead-service');
  var message=document.getElementById('lead-message');
  var btn=document.getElementById('lead-submit');
  var msgEl=document.getElementById('lead-msg');
  if(!name||!email||!name.value.trim()||!email.value.trim()){
    if(msgEl){msgEl.style.display='block';msgEl.style.background='rgba(239,68,68,0.1)';msgEl.style.color='#f87171';msgEl.textContent='Name and email are required.';}
    return;
  }
  btn.disabled=true;btn.textContent='Sending…';
  fetch('/api/leads',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({name:name.value.trim(),email:email.value.trim(),phone:phone?phone.value.trim():undefined,service:service?service.value:undefined,message:message?message.value.trim():undefined},_utmParams))})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.ok){
        if(msgEl){msgEl.style.display='block';msgEl.style.background='rgba(34,197,94,0.1)';msgEl.style.color='#4ade80';msgEl.textContent='Message sent! We&#39;ll get back to you soon.';}
        [name,email,phone,service,message].forEach(function(el){if(el)el.value='';});
      } else {
        if(msgEl){msgEl.style.display='block';msgEl.style.background='rgba(239,68,68,0.1)';msgEl.style.color='#f87171';msgEl.textContent=d.error||'Something went wrong. Try emailing riveraf30@gmail.com.';}
      }
      btn.disabled=false;btn.textContent='Send Message →';
    })
    .catch(function(){
      if(msgEl){msgEl.style.display='block';msgEl.style.background='rgba(239,68,68,0.1)';msgEl.style.color='#f87171';msgEl.textContent='Connection error. Try emailing riveraf30@gmail.com.';}
      btn.disabled=false;btn.textContent='Send Message →';
    });
}
function runCounters(){
  document.querySelectorAll('[data-count]').forEach(function(el){
    var t=parseInt(el.getAttribute('data-count'));var s=t/(1200/16);var c=0;
    var tmr=setInterval(function(){c=Math.min(c+s,t);el.textContent=Math.round(c).toLocaleString();if(c>=t)clearInterval(tmr);},16);
  });
}
var _utmParams=(function(){var p=new URLSearchParams(location.search);return{source:p.get('utm_source')||'bristoltalks.com',utm_source:p.get('utm_source')||'bristoltalks.com',utm_campaign:p.get('utm_campaign')||'organic',utm_medium:p.get('utm_medium')||'direct',product:p.get('product'),ref:p.get('ref')};})();
var initPage=location.pathname.replace('/','').split('/').join('')||'home';
go(initPage);
window.onpopstate=function(e){if(e.state&&e.state.p)go(e.state.p);};
document.getElementById('app').addEventListener('click',function(e){
  if(e.target.closest('button,a,.chat-sug'))return;
  var sc=e.target.closest('.sc,.story-featured,.featured-card');if(sc){go('news');return;}
  var vc=e.target.closest('.vc');if(vc){var vt=vc.querySelector('.vc-title');if(vt)chatSend('Tell me about: '+vt.textContent.trim());return;}
  var nbhd=e.target.closest('.nbhd-card');if(nbhd){var nm=nbhd.querySelector('.nbhd-name');if(nm)chatSend('Tell me about the '+nm.textContent.trim()+' neighborhood in Bristol CT');return;}
  var evt=e.target.closest('.evt-card');if(evt){var et=evt.querySelector('.evt-title');if(et)chatSend('Tell me more about: '+et.textContent.trim());return;}
  var card=e.target.closest('.card');if(card){var h=card.querySelector('h3');if(h)chatSend('Tell me more about: '+h.textContent.trim());return;}
});
</script>
</body>
</html>`;

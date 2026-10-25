const CHIPS = [
  "Can you also add a customer loyalty points program? Shouldn't take long, just stamps like the old Magento store.",
  "Finance wants this synced to NetSuite for inventory. Our ops lead said that was implied.",
  "Please add a wholesale login so retailers can see net pricing.",
  "Can we migrate 620 SKUs instead of 400? Catalog grew over summer.",
  "The Add to Cart button doesn't work in Safari on iPhone 12.",
];
const CHIP_LABELS = ["Loyalty points", "NetSuite sync", "Wholesale login", "400 → 620 SKUs", "Safari ATC bug"];
const KINDS = ["deliverable", "exclusion", "assumption", "quantity_limit", "revision_limit", "commercial", "timeline", "other"];

const $ = (id) => document.getElementById(id);
const state = {
  route: { area: "market", page: "product", pid: null },
  user: null,
  authConfig: null,
  projects: [],
  project: null,
  settings: null,
  precedents: [],
};

function money(n) {
  const v = Number(n || 0);
  const cur = (state.settings && state.settings.currency) || "USD";
  const sym = { USD: "$", GBP: "£", EUR: "€", PKR: "Rs ", AED: "AED ", AUD: "A$", CAD: "C$" }[cur] || "$";
  return (v < 0 ? "-" : "") + sym + Math.abs(v).toLocaleString("en-US", { maximumFractionDigits: 0 });
}
function stampClass(c) {
  if (["OUT_OF_SCOPE", "QUANTITY_OVERRUN", "REVISION_OVERRUN", "INTEGRATION_CHANGE", "PLATFORM_CHANGE"].includes(c))
    return "var(--stamp)";
  if (c === "BUG_OR_DEFECT" || c === "IN_SCOPE") return "var(--money)";
  return "var(--warn)";
}
function stampLabel(c) {
  return (c || "REVIEW").replaceAll("_", " ");
}
function escapeHtml(s) {
  return String(s || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
function toast(msg) {
  const el = $("toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.add("hidden"), 2800);
}
function downloadText(filename, text) {
  const blob = new Blob([text], { type: "text/html;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename || "raoguard.html";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 800);
  toast("Downloaded. Open the file — Print → Save as PDF if you need a PDF. Nothing was emailed.");
}
function openSheet(doc) {
  if (!doc) return;
  state.lastDoc = doc;
  $("modal").classList.remove("hidden");
  $("modal").innerHTML = `
    <div class="no-print doc-toolbar">
      <button class="btn" type="button" id="doc-print">Print</button>
      <button class="btn ghost" type="button" id="doc-dl">Download</button>
      <button class="btn ghost" type="button" id="co-close">Close</button>
    </div>
    <article class="co doc-sheet">${doc.html}</article>`;
  $("co-close").onclick = () => $("modal").classList.add("hidden");
  $("doc-print").onclick = () => window.print();
  $("doc-dl").onclick = () => downloadText(doc.filename, doc.document);
}

async function api(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (!opts.body || typeof opts.body === "string") headers["Content-Type"] = headers["Content-Type"] || "application/json";
  const res = await fetch(path, { credentials: "same-origin", ...opts, headers });
  if (res.status === 401) {
    state.user = null;
    if ((location.hash || "").startsWith("#/app")) go("#/login");
    throw new Error("Sign in required");
  }
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const j = await res.json();
      msg = j.detail || JSON.stringify(j);
      if (Array.isArray(msg)) msg = msg.map((x) => x.msg || x).join("; ");
    } catch (e) {}
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  if (res.status === 204) return {};
  return res.json();
}

function parseHash() {
  const h = (location.hash || "#/product").replace(/^#/, "");
  const parts = h.split("/").filter(Boolean);
  if (parts[0] === "app") {
    if (parts[1] === "p" && parts[2]) return { area: "app", page: parts[3] || "overview", pid: parts[2] };
    return { area: "app", page: parts[1] || "dashboard", pid: null };
  }
  return { area: "market", page: parts[0] || "product", pid: null };
}
function go(hash) {
  location.hash = hash.startsWith("#") ? hash : "#/" + hash.replace(/^#?\/?/, "");
}

function renderNav() {
  const r = state.route;
  const top = $("top-nav");
  const signed = !!state.user;
  if (r.area === "market") {
    const items = [
      ["#/product", "Product"],
      ["#/how", "How it works"],
      ["#/analyzer", "Analyzer"],
      ["#/pricing", "Pricing"],
      ["#/about", "About"],
      signed ? ["#/app/dashboard", "Workspace"] : ["#/login", "Sign in"],
    ];
    let html = items
      .map(([href, label]) => {
        const on = href === `#/${r.page}`;
        const cls = label === "Workspace" || label === "Sign in" ? "nav-cta" : on ? "on" : "";
        return `<a href="${href}" class="${cls}">${label}</a>`;
      })
      .join("");
    if (signed) html += `<button type="button" id="logout">Sign out</button>`;
    top.innerHTML = html;
  } else {
    const pid = r.pid || (state.projects[0] && state.projects[0].id);
    const opts = state.projects
      .map((p) => `<option value="${p.id}" ${p.id === pid ? "selected" : ""}>${escapeHtml(p.name)}</option>`)
      .join("");
    top.innerHTML = `
      <select class="switcher" id="proj-switch">${opts || "<option>No projects</option>"}</select>
      <a href="#/app/new">New</a>
      <a href="#/app/settings" class="${r.page === "settings" ? "on" : ""}">Account</a>
      <a href="#/product">Site</a>
      <button type="button" id="logout">Sign out</button>`;
  }
}

function renderSide() {
  const r = state.route;
  if (r.area !== "app") return "";
  const pid = r.pid || (state.projects[0] && state.projects[0].id);
  const items = [
    ["group", "Workspace"],
    ["#/app/dashboard", "Dashboard"],
    ["#/app/projects", "Projects"],
    ["#/app/new", "New project"],
    ["group", "This project"],
    ["overview", "Overview"],
    ["analyzer", "Analyzer"],
    ["scope", "Scope baseline"],
    ["orders", "Change orders"],
    ["report", "Reports"],
    ["history", "History"],
    ["precedents", "Precedents"],
    ["group", "Account"],
    ["#/app/settings", "Settings"],
    ["#/product", "Marketing site"],
  ];
  return `<aside class="sidenav" id="sidenav">${items
    .map((item) => {
      if (item[0] === "group") return `<div class="group">${item[1]}</div>`;
      let href = item[0];
      if (!href.startsWith("#")) href = pid ? `#/app/p/${pid}/${item[0]}` : "#/app/projects";
      const page = href.split("/").pop();
      const on = page === r.page || href === `#/app/${r.page}`;
      return `<a href="${href}" class="${on ? "on" : ""}">${item[1]}</a>`;
    })
    .join("")}</aside>`;
}

function renderFooter() {
  $("site-footer").innerHTML = `
    <span>© 2026 RaoGuard · working name</span>
    <a href="#/how">How it works</a>
    <a href="#/leakage">Leakage</a>
    <a href="#/about">About</a>
    <a href="#/kit">Sales kit</a>
    <a href="#/faq">FAQ</a>
    <a href="#/security">Security</a>
    <a href="#/terms">Terms</a>
    <a href="#/privacy">Privacy</a>
    <a href="#/cookies">Cookies</a>
    <a href="#/contact">Contact</a>
    ${state.user ? `<button type="button" id="logout">Sign out</button>` : `<a href="#/login">Sign in</a>`}`;
}

async function boot() {
  $("burger").onclick = () => {
    $("top-nav").classList.toggle("open");
    const side = $("sidenav");
    if (side) side.classList.toggle("open");
  };
  $("cookie-ok").onclick = () => {
    localStorage.setItem("rg_cookies", "1");
    $("cookie").classList.add("hidden");
  };
  if (!localStorage.getItem("rg_cookies")) $("cookie").classList.remove("hidden");
  window.addEventListener("hashchange", route);
  renderFooter();
  setupChat();
  if (!location.hash) location.hash = "#/product";
  else await route();
}

async function route() {
  state.route = parseHash();
  document.body.classList.toggle("app-mode", state.route.area === "app");
  $("top-nav").classList.remove("open");
  try {
    const me = await api("/api/auth/me");
    state.user = me.user;
    if (!state.authConfig) state.authConfig = await api("/api/auth/config");
    if (!state.plans) {
      try {
        state.plans = await api("/api/plans");
      } catch (e) {
        state.plans = { plans: planList() };
      }
    }
    if (state.user && state.route.area === "market") {
      try {
        state.settings = await api("/api/settings");
      } catch (e) {}
    }
    if (state.route.area === "app") {
      if (!state.user) {
        go("#/login");
        return;
      }
      if (!state.user.terms_accepted) {
        go("#/login");
        return;
      }
      state.settings = await api("/api/settings");
      state.projects = await api("/api/projects");
      if (state.route.pid) state.project = await api(`/api/projects/${state.route.pid}`);
    }
  } catch (e) {
    $("shell").innerHTML = `<div class="page"><p class="err">${escapeHtml(e.message)}</p></div>`;
    renderNav();
    return;
  }
  renderNav();
  renderFooter();
  await render();
}

async function render() {
  const r = state.route;
  const shell = $("shell");
  if (r.area === "market") {
    shell.className = "shell";
    shell.innerHTML = `<div class="page">${marketPage(r.page)}</div>`;
    if (r.page === "analyzer") setupChips("land");
    return;
  }
  shell.className = "app-shell";
  const inner = await appPage(r.page);
  shell.innerHTML = `${renderSide()}<div class="page">${inner}</div>`;
  if (r.page === "analyzer") setupChips("ws");
}

function marketPage(page) {
  const pages = {
    product: pageProduct,
    how: pageHow,
    analyzer: pageAnalyzer,
    leakage: pageLeakage,
    pricing: pagePricing,
    founder: pageFounder,
    kit: pageKit,
    login: pageLogin,
    register: pageRegister,
    terms: pageTerms,
    privacy: pagePrivacy,
    cookies: pageCookies,
    contact: pageContact,
    about: pageAbout,
    faq: pageFaq,
    security: pageSecurity,
  };
  return (pages[page] || pageNotFound)();
}

function pageProduct() {
  const hello = state.user
    ? `<p class="kicker">Signed in · ${escapeHtml(state.user.name)}</p>`
    : `<p class="kicker">Commercial control layer · software agencies</p>`;
  return `
    ${hello}
    <h1 class="hero">Stop doing work you forgot to bill for.</h1>
    <p class="lede">RaoGuard checks a client request against the signed SOW, quotes the clause, estimates the commercial impact, and drafts a change order. Your team decides. Nothing goes to the client until a human says so.</p>
    <div class="flow">
      <span>Signed SOW</span> → <span>Client request</span> → <span>Scope analysis</span> →
      <span>Commercial impact</span> → <span>Human approval</span> → <span>Change order</span>
    </div>
    <div class="row">
      <a class="btn stampc" href="${state.user ? "#/app/dashboard" : "#/login"}">${state.user ? "Open workspace" : "Sign in"}</a>
      <a class="btn ghost" href="#/analyzer">Live analyzer</a>
      <a class="btn ghost" href="#/pricing">Pricing</a>
    </div>
    <div class="stats">
      <div><b>57%</b><span class="muted">Agencies leaking $1–5k / mo</span></div>
      <div><b>1%</b><span class="muted">Bill for every extra request</span></div>
      <div><b>$6,600</b><span class="muted">Loyalty program, if you gift it</span></div>
      <div><b>$0</b><span class="muted">Safari ATC bug — in-scope defect</span></div>
    </div>
    <p class="disclaimer">Working name. Estimates only. Not a legal opinion. Local workspace — see Terms.</p>`;
}

function pageHow() {
  return `
    <p class="kicker">How it works</p>
    <h1 class="page-title">Evidence first. Money in Python. Humans decide.</h1>
    <p class="lede">The product is a pause between “client asked” and “engineer started.” If we cannot quote a stored SOW excerpt, we refuse to pretend.</p>
    <div class="steps">
      <article><div class="mono">01 · Scope</div><h3 class="serif">Fence the SOW</h3><p class="muted">Paste or upload. Deliverables, exclusions, quantity caps, and the change-order rate become a baseline you can edit.</p></article>
      <article><div class="mono">02 · Analyzer</div><h3 class="serif">Drop the request</h3><p class="muted">Slack, Jira, email — paste it. Rules fire before any model. Classifications include bugs, quantity overruns, and needs-human-review.</p></article>
      <article><div class="mono">03 · Change order</div><h3 class="serif">Approve the pause</h3><p class="muted">Hours × rate is calculated in Python. Copy the reply or print the change order. Nothing is sent automatically.</p></article>
    </div>
    <div class="row"><a class="btn" href="#/analyzer">Try the analyzer</a><a class="btn ghost" href="#/login">Sign in</a></div>`;
}

function pageAnalyzer() {
  return `
    <p class="kicker">Analyzer · Northstar Retail demo</p>
    <h1 class="page-title">Check a request against a signed SOW.</h1>
    <p class="lede">This dry-run does not persist and does not require an account. Sign in to approve, edit hours, and print a change order.</p>
    <div class="card" style="max-width:640px;margin-top:1.2rem">
      <div class="pad" style="border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:1rem">
        <div><div class="kicker">Live against a signed SOW</div><div class="serif" style="font-size:1.2rem">Northstar Retail · $48,000</div></div>
        <span class="stamp" style="color:var(--stamp)">Demo</span>
      </div>
      <div class="pad">
        <div class="chips" id="chips"></div>
        <textarea id="land-req"></textarea>
        <button class="btn" style="width:100%;margin-top:.7rem" id="land-run" type="button">Check against the SOW</button>
        <div id="land-out"></div>
      </div>
    </div>`;
}

function pageLeakage() {
  return `
    <p class="kicker">Leakage calculator</p>
    <h1 class="page-title">What is the free work actually costing you?</h1>
    <p class="lede">Unbilled hours × blended rate × 12. A team that gifts 12 hours a month at $150/h leaks $21,600 a year.</p>
    <div class="card" style="max-width:520px;margin-top:1.2rem"><div class="pad">
      <label class="lbl">Hours given away / month</label>
      <input type="range" min="2" max="40" value="12" id="leak-h" />
      <div class="muted" id="leak-h-v">12 hours</div>
      <label class="lbl">Blended rate</label>
      <input type="range" min="50" max="300" step="5" value="150" id="leak-r" />
      <div class="muted" id="leak-r-v">$150/hour</div>
      <div style="margin-top:1.2rem"><div class="kicker">Annual leakage</div><div class="money" id="leak-out">$21,600</div></div>
    </div></div>`;
}

function planList() {
  return (state.plans && state.plans.plans) || [
    { id: "free", name: "Free", price_label: "$0", period: "", badge: "Trial", blurb: "Use the real workflow on one live SOW. Limits included — this is the trial.", features: ["1 live project", "20 SOW checks on this machine", "Full loop: fence → check → draft CO → you decide", "Public analyzer stays unlimited"] },
    { id: "starter", name: "Starter", price_label: "$29", period: "/mo", badge: "", blurb: "Solo PM / 2–6 people.", features: ["3 live projects", "100 SOW checks / month", "3 seats", "Change-order PDF"] },
    { id: "studio", name: "Studio", price_label: "$59", period: "/mo", badge: "Most agencies", blurb: "The one agencies actually buy.", featured: true, features: ["Unlimited projects", "Unlimited SOW checks", "Team workspace", "Recovered-margin dashboard"] },
    { id: "agency", name: "Agency", price_label: "$89", period: "/mo", badge: "", blurb: "Delivery lead + AM.", features: ["Everything in Studio", "White-label change orders", "Precedent memory", "Founder onboarding call"] },
  ];
}

function planBanner(billing) {
  if (!billing || !billing.plan) return "";
  const p = billing.plan;
  const r = billing.remaining || {};
  const bits = [];
  if (r.projects != null) bits.push(r.projects + " project slot" + (r.projects === 1 ? "" : "s") + " left");
  if (r.checks_total != null) bits.push(r.checks_total + " of " + p.max_analyses_total + " checks left");
  if (r.checks_month != null) bits.push(r.checks_month + " checks left this month");
  if (r.seats != null) bits.push(r.seats + " seat" + (r.seats === 1 ? "" : "s") + " left");
  return `<div class="plan-banner">
    <div><span class="kicker">${escapeHtml(p.name)}${p.badge ? " · " + escapeHtml(p.badge) : ""}</span>
    <div class="muted">${bits.join(" · ") || "No caps on this plan."}</div></div>
    <a class="btn small ghost" href="#/pricing">Plans</a>
  </div>`;
}

function pagePricing() {
  const current = state.settings && state.settings.plan;
  return `
    <p class="kicker">Pricing · Pakistan software houses</p>
    <h1 class="page-title">Priced for a Lahore shop, not a US enterprise.</h1>
    <p class="lede">Start on Free — real workflow, real limits, usable as a trial. Then $29 / $59 / $89. USD invoices. PKR by arrangement. This local copy does not collect payment.</p>
    <div class="price-grid four">
      ${planList()
        .map((p) => {
          const on = current === p.id;
          const cta = state.user
            ? `<button class="btn" style="margin-top:auto" type="button" data-plan="${p.id}">${on ? "Current plan" : "Use this plan"}</button>`
            : `<a class="btn" style="margin-top:auto" href="#/${p.id === "free" ? "register" : "login"}">${p.id === "free" ? "Start free trial" : "Get started"}</a>`;
          return `
        <div class="price-card ${p.featured ? "feat" : ""} ${p.id === "free" ? "trial" : ""}">
          <div class="kicker">${escapeHtml(p.badge || p.name)}</div>
          <div class="serif" style="font-size:1.35rem;margin:.35rem 0 0">${escapeHtml(p.name)}</div>
          <div class="serif" style="font-size:2.4rem;margin:.2rem 0">${escapeHtml(p.price_label)}<span style="font-size:1rem">${escapeHtml(p.period || "")}</span></div>
          <p class="muted">${escapeHtml(p.blurb)}</p>
          <ul>${(p.features || []).map((i) => `<li>${escapeHtml(i)}</li>`).join("")}</ul>
          ${cta}
        </div>`;
        })
        .join("")}
    </div>
    <p class="disclaimer">Freemium, not a fake unlimited free. Caps are enforced on this machine. No billing is collected in this copy — picking a paid plan here only lifts the caps so you can evaluate them. A real invoice would be by hand.</p>`;
}

function pageFounder() {
  return pageAbout();
}

function pageKit() {
  return `
    <p class="kicker">Sales kit</p>
    <h1 class="page-title">How you get paid for this.</h1>
    <p class="lede">You are not selling AI. You are selling recovered margin. Open the Northstar analyzer on the call. Let them paste a real Slack message.</p>
    <div class="kit">
      <h2 class="page-title" style="margin-top:2rem">5-minute demo</h2>
      <ol class="muted" style="font-size:15px;line-height:1.6">
        <li>Sign in. Open Dashboard, then Northstar.</li>
        <li>Analyzer → loyalty request. Point at the exclusion and the $6,600 CO.</li>
        <li>Paste their Slack message. Stay quiet.</li>
        <li>Copy the reply. Print the change order.</li>
        <li>Ask how many of these they gifted last month.</li>
      </ol>
    </div>`;
}

function pageLogin() {
  if (state.user) {
    return `
      <p class="kicker">Signed in</p>
      <h1 class="page-title">Welcome back, ${escapeHtml(state.user.name)}.</h1>
      <p class="lede">You are signed in. Open the workspace or stay on the site.</p>
      <div class="row">
        <a class="btn" href="#/product">Home</a>
        <a class="btn ghost" href="#/app/dashboard">Workspace</a>
      </div>`;
  }
  const ver = (state.authConfig && state.authConfig.terms_version) || "2026-09-20";
  return `
    <div class="auth-wrap">
      <p class="kicker">Account</p>
      <h1 class="page-title">Sign in</h1>
      <p class="lede">Use your work email. Accept Terms to continue.</p>
      <div class="card">
        <label class="lbl">Email</label>
        <input id="login-email" type="email" autocomplete="username" placeholder="you@agency.com" />
        <label class="lbl">Password</label>
        <input id="login-pass" type="password" autocomplete="current-password" />
        <label class="check"><input id="login-terms" type="checkbox" /> <span>I have read and accept the <a class="link" href="#/terms">Terms of Use</a> and <a class="link" href="#/privacy">Privacy Policy</a> (v${escapeHtml(ver)}).</span></label>
        <button class="btn" style="width:100%" type="button" id="login-go">Sign in</button>
        <p class="err hidden" id="login-err"></p>
        <p class="muted" style="margin-top:.9rem">New here? <a class="link" href="#/register">Create an account</a></p>
      </div>
    </div>`;
}

function pageRegister() {
  return `
    <div class="auth-wrap">
      <p class="kicker">Workspace</p>
      <h1 class="page-title">Create an account</h1>
      <p class="lede">Free trial is one seat. Extra people need Starter or above. Terms must be accepted.</p>
      <div class="card">
        <label class="lbl">Name</label><input id="reg-name" />
        <label class="lbl">Email</label><input id="reg-email" type="email" />
        <label class="lbl">Password (8+ characters)</label><input id="reg-pass" type="password" />
        <label class="check"><input id="reg-terms" type="checkbox" /> <span>I accept the <a class="link" href="#/terms">Terms of Use</a> and <a class="link" href="#/privacy">Privacy Policy</a>.</span></label>
        <button class="btn" style="width:100%" type="button" id="reg-go">Create account</button>
        <p class="err hidden" id="reg-err"></p>
        <p class="muted" style="margin-top:.9rem">Already have an account? <a class="link" href="#/login">Sign in</a></p>
      </div>
    </div>`;
}

function pageTerms() {
  return `
    <p class="kicker">Legal · v2026-09-20</p>
    <h1 class="page-title">Terms of Use</h1>
    <div class="legal">
      <p>These terms cover this local RaoGuard copy. RaoGuard is a working name, not a filed trademark. This is not a law firm and not legal advice.</p>
      <h2>1. What the product does</h2>
      <p>RaoGuard compares a client request to a stored Statement of Work, quotes an excerpt when it can, estimates hours × rate in Python, and drafts a reply or change order. A human must approve. Nothing is sent to a client automatically.</p>
      <h2>2. What it is not</h2>
      <p>Not a legal opinion. Not a binding quote. Not an e-sign, invoice, or email system. Classifications and dollar figures are estimates. You own every commercial decision.</p>
      <h2>3. Your data</h2>
      <p>On this machine, project data lives in a local SQLite file. If you add a Groq API key, request text and retrieved SOW clauses may be sent to Groq in the US. Rules-only mode sends nothing to Groq.</p>
      <h2>4. Accounts</h2>
      <p>The first owner account is seeded on this machine. You must accept these terms to use the workspace. Change the default password after first sign-in. Do not upload real client SOWs to a public host.</p>
      <h2>5. Liability</h2>
      <p>Use at your own risk. If the tool mis-classifies a request, you are still responsible for what your team builds and bills. No warranty. No SLA on this local copy.</p>
      <h2>6. Contact</h2>
      <p>Muhammad Abdullah, founder. See the Contact page.</p>
    </div>`;
}

function pagePrivacy() {
  return `
    <p class="kicker">Legal · v2026-09-20</p>
    <h1 class="page-title">Privacy Policy</h1>
    <div class="legal">
      <p>This local copy is meant to run on your computer. There is no RaoGuard cloud tenant in this build.</p>
      <h2>What we store here</h2>
      <p>Account email and a password hash; SOW text you paste or upload; requests; analyses; decisions; a session cookie. Original PDFs are not kept after text is extracted.</p>
      <h2>What we do not do</h2>
      <p>No ads. No analytics pixels. No sale of data. We do not train a RaoGuard model on your SOWs.</p>
      <h2>Groq</h2>
      <p>Optional. If you set GROQ_API_KEY, we may send the request and retrieved clauses to Groq. Groq’s own retention policy then applies. Turn it off and the product stays rules-only.</p>
      <h2>Deletion</h2>
      <p>Delete the local database file (<span class="mono">data/raoguard.db</span>) to wipe this copy. There is no backup unless you make one.</p>
    </div>`;
}

function pageCookies() {
  return `
    <p class="kicker">Legal</p>
    <h1 class="page-title">Cookies</h1>
    <div class="legal">
      <p><b>rg_session</b> — HttpOnly session cookie so you stay signed in on this machine. 30 days. Required for the workspace.</p>
      <p><b>rg_cookies</b> — stored in localStorage so we do not keep showing the banner. Not sent to a server.</p>
      <p>No third-party cookies. No advertising IDs.</p>
    </div>`;
}

function pageContact() {
  return `
    <p class="kicker">Contact</p>
    <h1 class="page-title">Talk to the founder</h1>
    <p class="lede">Muhammad Abdullah · Founder, AI Engineer, Data Scientist. Pakistan. This is a working product, not a support desk with an SLA.</p>
    <div class="legal" style="margin-top:1.2rem">
      <p>Email <a class="link" href="mailto:raoengr1080@gmail.com">raoengr1080@gmail.com</a></p>
      <p>LinkedIn <a class="link" href="https://www.linkedin.com/in/raoabdullah1080/" target="_blank" rel="noopener">linkedin.com/in/raoabdullah1080</a></p>
      <p>Do not send live client SOWs to a public URL.</p>
    </div>
    <div class="row"><a class="btn" href="mailto:raoengr1080@gmail.com">Email</a><a class="btn ghost" href="#/about">About</a></div>`;
}

function pageAbout() {
  return `
    <p class="kicker">About</p>
    <h1 class="page-title">RaoGuard</h1>
    <p class="lede">A commercial control layer for software agencies. It pauses the work between “the client asked” and “the engineer started.”</p>
    <div class="legal">
      <h2>The product</h2>
      <p>Paste a signed Statement of Work. Drop a client request from Slack, Jira, or email. RaoGuard quotes a stored clause when it can, classifies the request, and estimates hours × rate in Python. You get a draft reply and a change-order sheet you can print or download. A human approves. Nothing is sent to the client until you send it.</p>
      <p>Rules fire before any model. Money is never invented by an LLM. Estimates are labeled as estimates. This is not legal advice and not an invoice until you issue one.</p>
      <p>Working name only — not a filed trademark. Built as a local $0 MVP: FastAPI, SQLite, optional Groq. Free trial with limits, then Starter $29 / Studio $59 / Agency $89, priced for Pakistan software houses.</p>
      <h2>How it runs</h2>
      <p>Fence the SOW → check the request → commercial impact → human decision → print or download a change order or a project report. The public analyzer is a dry-run against a demo SOW and does not save.</p>
    </div>
    <article class="founder-card" id="founder">
      <p class="kicker">Founder</p>
      <h2 class="page-title" style="margin-top:.25rem">Muhammad Abdullah</h2>
      <p class="lede" style="margin:.35rem 0 1rem">Founder · AI Engineer · Data Scientist</p>
      <p>I’m a founder and AI engineer building at the intersection of <b>artificial intelligence, data, and software engineering</b>.</p>
      <p>I create products and intelligent systems around problems that are often overlooked — turning ideas into working technology through research, experimentation, and engineering.</p>
      <p>My approach to building is deeply technical: understand the problem, investigate the data, prototype quickly, validate with evidence, and engineer the solution into something people can actually use.</p>
      <p>Through my work, I explore <b>machine learning, generative AI, NLP, intelligent automation, data systems, and applied AI</b> — with a particular interest in building practical technology from resource-constrained environments.</p>
      <p>I’m not interested in building AI simply because it is possible.</p>
      <p><b>I want to build technology that solves problems worth solving.</b></p>
      <h3 class="serif" style="margin:1.4rem 0 .4rem">Connect</h3>
      <p>LinkedIn — <a class="link" href="https://www.linkedin.com/in/raoabdullah1080/" target="_blank" rel="noopener">linkedin.com/in/raoabdullah1080</a></p>
      <p>Email — <a class="link" href="mailto:raoengr1080@gmail.com">raoengr1080@gmail.com</a></p>
      <div class="row">
        <a class="btn" href="mailto:raoengr1080@gmail.com">Email</a>
        <a class="btn ghost" href="https://www.linkedin.com/in/raoabdullah1080/" target="_blank" rel="noopener">LinkedIn</a>
      </div>
    </article>`;
}

function pageFaq() {
  return `
    <p class="kicker">FAQ</p>
    <h1 class="page-title">Common questions</h1>
    <div class="legal">
      <h2>Is there a free trial?</h2>
      <p>Yes. Free is the trial: one live project, 20 SOW checks on this machine, full loop (fence → check → draft change order → you approve). The public analyzer stays unlimited. Then Starter $29, Studio $59, Agency $89.</p>
      <h2>How do I sign in?</h2>
      <p>Open Sign in, enter your email and password, accept Terms. After that you land on the homepage as a signed-in user.</p>
      <h2>Does it email my client?</h2>
      <p>No. Copy the reply or print the change order. You send it.</p>
      <h2>Is this legal advice?</h2>
      <p>No. Estimates only. You own the decision.</p>
      <h2>Where is my data?</h2>
      <p>On this computer, in <code>data/raoguard.db</code>. Optional Groq calls send request text and retrieved clauses only if you add a key.</p>
      <h2>Forgot the password?</h2>
      <p>Change it in Settings while signed in. There is no email reset in this local copy.</p>
    </div>`;
}

function pageSecurity() {
  return `
    <p class="kicker">Security</p>
    <h1 class="page-title">How this copy is locked down</h1>
    <div class="legal">
      <p>Passwords are stored as PBKDF2 hashes, not plaintext. Sessions are HttpOnly cookies. Workspace APIs refuse unsigned requests. Terms must be accepted before the workspace opens.</p>
      <p>This is a local tool, not SOC 2. Do not put real client SOWs on a public URL. Change the default password after first sign-in.</p>
      <p>Nothing is auto-sent. Groq is off unless you add a key.</p>
    </div>`;
}

function pageNotFound() {
  return `
    <p class="kicker">404</p>
    <h1 class="page-title">That page is not here.</h1>
    <p class="lede">The URL does not match a RaoGuard screen.</p>
    <div class="row"><a class="btn" href="#/product">Home</a><a class="btn ghost" href="#/login">Sign in</a></div>`;
}

async function appPage(page) {
  const needProject = ["overview", "analyzer", "scope", "orders", "report", "history", "precedents"].includes(page);
  if (needProject && !state.route.pid) {
    const first = state.projects[0];
    if (first) {
      location.hash = `#/app/p/${first.id}/${page}`;
      return `<p class="muted">Opening project…</p>`;
    }
    return `<p class="muted">Create a project first.</p><div class="row"><a class="btn" href="#/app/new">New project</a></div>`;
  }
  const pages = {
    dashboard: pageDashboard,
    projects: pageProjects,
    new: pageNew,
    settings: pageSettings,
    overview: pageOverview,
    analyzer: pageAppAnalyzer,
    scope: pageScope,
    orders: pageOrders,
    report: pageReport,
    history: pageHistory,
    precedents: pagePrecedents,
  };
  return await (pages[page] || pageDashboard)();
}

async function pageDashboard() {
  const d = await api("/api/dashboard");
  const classes = Object.entries(d.by_class || {})
    .map(([k, v]) => `<tr><td>${stampLabel(k)}</td><td class="tabular">${v}</td></tr>`)
    .join("");
  return `
    <p class="kicker">${escapeHtml(d.agency_name)} · ${escapeHtml(state.user.name)}</p>
    <h1 class="page-title">Dashboard</h1>
    <p class="lede">Revenue protection from requests checked against signed scope. Estimates only.</p>
    ${planBanner(d.billing)}
    <div class="stats">
      <div><b class="tabular">${money(d.recovered)}</b><span class="muted">Recovered (approved COs)</span></div>
      <div><b class="tabular">${money(d.at_risk)}</b><span class="muted">At risk (not yet approved)</span></div>
      <div><b>${d.project_count}</b><span class="muted">Projects</span></div>
      <div><b>${d.request_count}</b><span class="muted">Requests checked</span></div>
    </div>
    <h2 class="page-title" style="margin-top:2rem">By classification</h2>
    <div class="table-wrap"><table class="table"><thead><tr><th>Class</th><th>Count</th></tr></thead><tbody>${
      classes || "<tr><td colspan=2>No analyses yet</td></tr>"
    }</tbody></table></div>
    <h2 class="page-title" style="margin-top:2rem">Projects</h2>
    ${projectGrid(d.projects)}
    <p class="disclaimer">${escapeHtml(d.disclaimer)}</p>`;
}

function projectGrid(list) {
  if (!list.length) return `<p class="muted">No projects.</p>`;
  return `<div class="plist">${list
    .map(
      (p) => `
    <a class="pcard" href="#/app/p/${p.id}/overview">
      <div class="kicker">${escapeHtml(p.client_name)}</div>
      <div class="serif" style="font-size:1.4rem;margin:.25rem 0">${escapeHtml(p.name)}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.6rem;margin-top:1rem;font-size:12px">
        <div><div class="muted">SOW</div>${money(p.contract_value)}</div>
        <div><div class="muted">At risk</div><span class="w">${money(p.at_risk)}</span></div>
        <div><div class="muted">Recovered</div><span class="g">${money(p.recovered)}</span></div>
      </div>
    </a>`
    )
    .join("")}</div>`;
}

async function pageProjects() {
  return `
    <div style="display:flex;justify-content:space-between;align-items:end;gap:1rem;flex-wrap:wrap">
      <div><p class="kicker">Workspace</p><h1 class="page-title">Projects</h1>
      <p class="lede">Each project is a signed SOW. Incoming requests get a verdict with a quoted clause.</p></div>
      <a class="btn" href="#/app/new">New project</a>
    </div>
    ${projectGrid(state.projects)}`;
}

async function pageNew() {
  return `
    <p class="kicker">New project</p>
    <h1 class="page-title">Fence a new SOW</h1>
    <p class="lede">Paste the signed statement of work or upload PDF / DOCX / TXT. We split deliverables, exclusions, and commercials.</p>
    ${state.settings && state.settings.billing ? planBanner(state.settings.billing) : ""}
    <label class="lbl">Client</label><input id="new-client" placeholder="Client name" />
    <label class="lbl">Project name (optional)</label><input id="new-name" placeholder="Leave blank to take it from the SOW" />
    <label class="lbl">Statement of work</label>
    <textarea id="new-sow" style="min-height:14rem" placeholder="STATEMENT OF WORK"></textarea>
    <label class="drop" id="new-drop">Drop PDF / DOCX / TXT here or click to choose
      <input type="file" id="new-file" accept=".pdf,.docx,.txt,.md,application/pdf" hidden />
    </label>
    <div class="row"><button class="btn" type="button" id="new-go">Create project</button></div>
    <p class="err hidden" id="new-err"></p>`;
}

async function pageSettings() {
  const s = state.settings || (await api("/api/settings"));
  state.settings = s;
  const u = state.user;
  return `
    <p class="kicker">Account</p>
    <h1 class="page-title">Settings</h1>
    <p class="muted">${escapeHtml(u.email)} · ${escapeHtml(u.role)} · terms ${u.terms_accepted ? "accepted" : "pending"}</p>
    <label class="lbl">Agency</label><input id="s-agency" value="${escapeHtml(s.agency_name)}" />
    <label class="lbl">Owner display name</label><input id="s-owner" value="${escapeHtml(s.owner_name)}" />
    <label class="lbl">Client rate</label><input id="s-cr" type="number" value="${s.client_rate}" />
    <label class="lbl">Internal rate</label><input id="s-ir" type="number" value="${s.internal_rate}" />
    <label class="lbl">Currency</label>
    <select id="s-cur">${["USD", "GBP", "EUR", "AED", "PKR", "AUD", "CAD"].map((c) => `<option ${c === s.currency ? "selected" : ""}>${c}</option>`).join("")}</select>
    <label class="lbl">Reply tone</label>
    <select id="s-tone">${["professional", "friendly", "direct", "warm", "firm", "formal"].map((t) => `<option ${t === s.tone ? "selected" : ""}>${t}</option>`).join("")}</select>
    <p class="muted" style="margin-top:1rem">${escapeHtml(s.data_notice)}</p>
    <p class="muted">Groq key on this machine: ${s.groq_configured ? "yes" : "no — rules-only"}</p>
    <div class="row"><button class="btn" type="button" id="s-save">Save agency</button></div>
    <h2 class="page-title" style="margin-top:2rem">Plan</h2>
    ${planBanner(s.billing)}
    <p class="muted">${escapeHtml((s.billing && s.billing.billing) || "No payment is collected in this copy.")}</p>
    <div class="price-grid four" style="margin-top:1rem">
      ${planList()
        .map((p) => {
          const on = (s.plan || "free") === p.id;
          return `<div class="price-card ${p.featured ? "feat" : ""} ${on ? "on-plan" : ""}">
            <div class="kicker">${escapeHtml(p.name)}${on ? " · current" : ""}</div>
            <div class="serif" style="font-size:1.6rem">${escapeHtml(p.price_label)}<span style="font-size:.9rem">${escapeHtml(p.period || "")}</span></div>
            <p class="muted">${escapeHtml(p.blurb)}</p>
            <button class="btn small" type="button" data-plan="${p.id}" ${on ? "disabled" : ""}>${on ? "Current" : "Use this plan"}</button>
          </div>`;
        })
        .join("")}
    </div>
    <h2 class="page-title" style="margin-top:2rem">Change password</h2>
    <label class="lbl">Current</label><input id="pw-cur" type="password" />
    <label class="lbl">New (8+)</label><input id="pw-new" type="password" />
    <div class="row"><button class="btn ghost" type="button" id="pw-go">Update password</button></div>
    <p class="err hidden" id="s-err"></p>`;
}

function projectHead(extra = "") {
  const p = state.project;
  return `
    <p class="kicker">${escapeHtml(p.client_name)}</p>
    <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;align-items:end">
      <h1 class="page-title" style="margin:0">${escapeHtml(p.name)}</h1>
      <div class="metrics">
        <div>SOW <span class="tabular">${money(p.contract_value)}</span></div>
        <div>At risk <span class="w tabular">${money(p.at_risk)}</span></div>
        <div>Recovered <span class="g tabular">${money(p.recovered)}</span></div>
      </div>
    </div>${extra}`;
}

async function pageOverview() {
  const p = state.project;
  const classes = {};
  (p.analyses || []).forEach((a) => {
    const k = a.result.classification;
    classes[k] = (classes[k] || 0) + 1;
  });
  return `
    ${projectHead(`<p class="lede" style="margin-top:.8rem">Contract, current scope, additional revenue at risk, and approved change orders.</p>`)}
    <div class="stats">
      <div><b>${p.scope_items.length}</b><span class="muted">Scope items</span></div>
      <div><b>${p.requests.length}</b><span class="muted">Requests</span></div>
      <div><b>${(p.analyses || []).filter((a) => a.status === "approved").length}</b><span class="muted">Approved</span></div>
      <div><b class="tabular">${money(p.client_rate)}/h</b><span class="muted">Change-order rate</span></div>
    </div>
    <div class="row">
      <a class="btn" href="#/app/p/${p.id}/analyzer">Open analyzer</a>
      <a class="btn ghost" href="#/app/p/${p.id}/scope">Review scope</a>
      <a class="btn ghost" href="#/app/p/${p.id}/orders">Change orders</a>
      <a class="btn ghost" href="#/app/p/${p.id}/report">Report</a>
    </div>
    <h2 class="page-title" style="margin-top:2rem">Class mix</h2>
    <div class="table-wrap"><table class="table">${
      Object.entries(classes).map(([k, v]) => `<tr><td>${stampLabel(k)}</td><td>${v}</td></tr>`).join("") ||
      "<tr><td>No analyses yet</td></tr>"
    }</table></div>
    <p class="disclaimer">Estimate. Not a legal opinion. Not a binding quote.</p>`;
}

async function pageAppAnalyzer() {
  const p = state.project;
  const analyses = p.analyses || [];
  try {
    state.precedents = (await api(`/api/projects/${p.id}/precedents`)).items || [];
  } catch (e) {
    state.precedents = [];
  }
  return `
    ${projectHead(`<p class="lede" style="margin-top:.8rem">Paste a client request. Rules fire before any model. Nothing is sent to the client until you copy or print.</p>`)}
    <div class="inbox" style="margin-top:1.4rem">
      <div class="composer">
        <div class="kicker">Client request</div>
        <div class="chips" id="chips"></div>
        <textarea id="req-body" placeholder="Slack, Jira, email…"></textarea>
        <button class="btn" style="width:100%;margin-top:.7rem" type="button" id="req-go">Check against SOW</button>
        <p class="muted" style="margin-top:.8rem">Silent observer. Human approval required.</p>
        <p class="err hidden" id="req-err"></p>
      </div>
      <div id="findings">${analyses.map(findingHTML).join("") || '<p class="muted">No checks yet. Use a sample above or paste a real message.</p>'}</div>
    </div>`;
}

function findingHTML(a) {
  const f = a.result || {};
  const ev = f.evidence || [];
  const req = (state.project.requests || []).find((r) => r.id === a.request_id);
  const similar = (state.precedents || [])
    .filter((i) => i.analysis_id !== a.id)
    .slice(0, 3);
  return `
    <article class="finding" id="an-${a.id}">
      <div style="display:flex;justify-content:space-between;gap:1rem;align-items:start">
        <div>
          <div class="serif" style="font-size:1.25rem">${escapeHtml(f.change_order_title)}</div>
          <div class="muted">${Math.round((f.confidence || 0) * 100)}% · ${escapeHtml(a.status)} · ${(f.rules_fired || []).join(", ")}</div>
        </div>
        <span class="stamp" style="color:${stampClass(f.classification)}">${stampLabel(f.classification)}</span>
      </div>
      <p class="quote">“${escapeHtml((req && req.body) || "")}”</p>
      <p class="muted">${escapeHtml(f.reason)}</p>
      ${
        ev.length
          ? ev
              .map(
                (e) =>
                  `<div class="ev"><div class="kind ${e.kind}">${escapeHtml(e.kind)} · ${escapeHtml(e.section_label || "")}</div>${escapeHtml(e.quote)}</div>`
              )
              .join("")
          : `<p class="muted">No stored excerpt could be quoted.</p>`
      }
      ${
        f.client_price > 0
          ? `<div class="serif" style="font-size:2rem;color:#86efac">${money(f.client_price)}</div>`
          : `<div class="muted" style="color:#86efac">No change order · $0</div>`
      }
      <div class="commercial">
        <div><label class="lbl">Hours</label><input id="hrs-${a.id}" type="number" step="0.5" value="${f.estimated_hours || 0}" /></div>
        <div><label class="lbl">Client rate</label><input id="rate-${a.id}" type="number" step="1" value="${f.client_rate || 0}" /></div>
        <div><label class="lbl">Internal rate</label><input id="irate-${a.id}" type="number" step="1" value="${f.internal_rate || 0}" /></div>
        <div><label class="lbl">Timeline days</label><input id="days-${a.id}" type="number" step="0.5" value="${f.timeline_impact_days || 0}" /></div>
      </div>
      <p class="muted" style="border-top:1px solid var(--line-dark);padding-top:.7rem;margin-top:.8rem">${escapeHtml(f.client_reply || "")}</p>
      ${
        similar.length
          ? `<p class="muted">Similar past decisions (history, not a rule): ${similar
              .map((i) => `${stampLabel(i.classification)} ${money(i.price)}`)
              .join(" · ")}</p>`
          : ""
      }
      <label class="lbl">Note</label>
      <input id="note-${a.id}" placeholder="Optional note on this decision" />
      <div class="actions">
        <button class="btn small ghost" type="button" data-copy="${encodeURIComponent(f.client_reply || "")}">Copy reply</button>
        ${f.requires_change_order ? `<button class="btn small ghost" type="button" data-co="${a.id}">Invoice / change order</button>` : ""}
        <button class="btn small ghost" type="button" data-sheet="${a.id}">Print / download</button>
        <button class="btn small ghost" type="button" data-hrs="${a.id}">Recalculate</button>
        ${a.status === "new" || a.status === "clarifying" ? `<button class="btn small" type="button" data-decide="${a.id}" data-act="approve">Approve</button>` : ""}
        ${a.status === "new" ? `<button class="btn small ghost" type="button" data-decide="${a.id}" data-act="clarify">Ask clarification</button>` : ""}
        <button class="btn small ghost" type="button" data-decide="${a.id}" data-act="reject">Reject</button>
      </div>
      <p class="disclaimer">${escapeHtml(f.disclaimer || "Estimate. Not a legal opinion.")}${f.groq_used ? " Groq used for prose." : " Rules-only."}</p>
    </article>`;
}

async function pageScope() {
  const p = state.project;
  const groups = {};
  (p.scope_items || []).forEach((it) => {
    (groups[it.kind] || (groups[it.kind] = [])).push(it);
  });
  const order = ["exclusion", "deliverable", "quantity_limit", "assumption", "commercial", "timeline", "other"];
  const keys = [...order.filter((k) => groups[k]), ...Object.keys(groups).filter((k) => !order.includes(k))];
  return `
    ${projectHead(`<p class="lede" style="margin-top:.8rem">Typed fence from the signed document. Edit a clause if extraction missed. Re-upload to replace the baseline.</p>`)}
    <div class="row">
      <label class="btn ghost" style="cursor:pointer">Upload PDF / DOCX / TXT
        <input type="file" id="sow-file" accept=".pdf,.docx,.txt,.md,application/pdf" hidden />
      </label>
    </div>
    <p class="err hidden" id="sow-err"></p>
    ${keys
      .map(
        (k) => `
      <h2 class="page-title" style="margin-top:1.6rem">${stampLabel(k)}</h2>
      <div class="scope">${groups[k]
        .map(
          (it) => `
        <article>
          <div style="display:flex;justify-content:space-between;gap:.5rem">
            <span class="kind ${it.kind}">${escapeHtml(it.kind)}</span>
            ${it.quantity_value ? `<span class="muted">${it.quantity_value} ${escapeHtml(it.quantity_unit || "")}</span>` : ""}
          </div>
          <p style="margin:.5rem 0 0;font-size:14px;line-height:1.45">${escapeHtml(it.body)}</p>
          <button class="btn small ghost" type="button" data-editscope="${it.id}" style="margin-top:.6rem">Edit</button>
          <div class="scope-edit hidden" id="se-${it.id}">
            <label class="lbl">Kind</label>
            <select id="sk-${it.id}">${KINDS.map((x) => `<option ${x === it.kind ? "selected" : ""}>${x}</option>`).join("")}</select>
            <label class="lbl">Clause</label>
            <textarea id="sb-${it.id}">${escapeHtml(it.body)}</textarea>
            <button class="btn small" type="button" data-savescope="${it.id}">Save clause</button>
          </div>
        </article>`
        )
        .join("")}</div>`
      )
      .join("")}`;
}

async function pageOrders() {
  const p = state.project;
  const rows = (p.analyses || []).filter((a) => a.result && a.result.requires_change_order);
  return `
    ${projectHead(`<p class="lede" style="margin-top:.8rem">Draft change orders. Print or download like an invoice. No e-sign. Nothing is emailed.</p>`)}
    <div style="margin-top:1.2rem">${rows.map(findingHTML).join("") || '<p class="muted">No change orders yet.</p>'}</div>`;
}

async function pageReport() {
  const p = state.project;
  const doc = await api(`/api/projects/${p.id}/report`);
  state.lastReport = doc;
  return `
    ${projectHead(`<p class="lede" style="margin-top:.8rem">A commercial report for this SOW: recovered, at risk, and every request checked. Print it or download it. Nothing is sent to the client.</p>`)}
    <div class="row no-print">
      <button class="btn" type="button" id="report-print">Print report</button>
      <button class="btn ghost" type="button" id="report-dl">Download report</button>
    </div>
    <article class="co doc-sheet">${doc.html}</article>
    <p class="disclaimer">Print uses the system dialog (choose Save as PDF). Download saves an HTML invoice you can reopen later.</p>`;
}

async function pageHistory() {
  const p = state.project;
  const rows = p.analyses || [];
  return `
    ${projectHead(`<p class="lede" style="margin-top:.8rem">Request received → analysis → evidence → human review → final decision.</p>`)}
    <div class="table-wrap" style="margin-top:1.2rem">
    <table class="table">
      <thead><tr><th>Status</th><th>Class</th><th>Title</th><th>Amount</th></tr></thead>
      <tbody>${
        rows
          .map(
            (a) =>
              `<tr><td>${escapeHtml(a.status)}</td><td>${stampLabel(a.result.classification)}</td><td>${escapeHtml(
                a.result.change_order_title
              )}</td><td class="tabular">${money(a.result.client_price)}</td></tr>`
          )
          .join("") || `<tr><td colspan="4">No history yet.</td></tr>`
      }</tbody>
    </table></div>`;
}

async function pagePrecedents() {
  const p = state.project;
  const data = await api(`/api/projects/${p.id}/precedents`);
  return `
    ${projectHead(`<p class="lede" style="margin-top:.8rem">${escapeHtml(data.note)}</p>`)}
    <div class="table-wrap" style="margin-top:1.2rem">
    <table class="table">
      <thead><tr><th>Decision</th><th>Request</th><th>Class</th><th>Price</th></tr></thead>
      <tbody>${
        (data.items || [])
          .map(
            (i) =>
              `<tr><td>${escapeHtml(i.status)}</td><td>${escapeHtml((i.request || "").slice(0, 90))}</td><td>${stampLabel(
                i.classification
              )}</td><td class="tabular">${money(i.price)}</td></tr>`
          )
          .join("") || `<tr><td colspan="4">No precedents yet.</td></tr>`
      }</tbody>
    </table></div>`;
}

function setupChips(mode) {
  const box = $("chips");
  if (!box) return;
  CHIPS.forEach((t, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.dataset.t = t;
    b.textContent = CHIP_LABELS[i] || t.slice(0, 40);
    b.onclick = () => {
      if (mode === "land") runLanding(t);
      else {
        $("req-body").value = t;
        document.querySelectorAll("#chips button").forEach((x) => x.classList.toggle("on", x.dataset.t === t));
      }
    };
    box.appendChild(b);
  });
  if (mode === "land") {
    $("land-req").value = CHIPS[0];
    $("land-run").onclick = () => runLanding();
  }
}

async function runLanding(text) {
  const t = text || $("land-req").value;
  $("land-req").value = t;
  document.querySelectorAll("#chips button").forEach((b) => b.classList.toggle("on", b.dataset.t === t));
  try {
    const r = await api("/api/demo/analyze", { method: "POST", body: JSON.stringify({ body: t }) });
    const f = r.result;
    state.lastDemoBody = t;
    $("land-out").innerHTML = `
      <div class="found">
        <div style="display:flex;justify-content:space-between;gap:1rem;align-items:start">
          <div>
            <div class="serif" style="font-size:1.25rem">${escapeHtml(f.change_order_title)}</div>
            <div class="muted">${Math.round(f.confidence * 100)}% · ${(f.rules_fired || []).join(", ") || "rules"}</div>
          </div>
          <span class="stamp" style="color:${stampClass(f.classification)}">${stampLabel(f.classification)}</span>
        </div>
        <p class="muted" style="margin:.7rem 0 0">${escapeHtml(f.reason)}</p>
        ${f.evidence && f.evidence[0] ? `<p class="muted">“${escapeHtml(f.evidence[0].quote)}”</p>` : ""}
        ${f.client_price > 0 ? `<div class="money">${money(f.client_price)}</div>` : `<div class="muted">$0 · no change order</div>`}
        <div class="row" style="margin-top:.8rem">
          <button class="btn small" type="button" id="land-print">Print</button>
          <button class="btn small ghost" type="button" id="land-dl">Download</button>
        </div>
      </div>`;
  } catch (e) {
    $("land-out").innerHTML = `<p class="err">${escapeHtml(e.message)}</p>`;
  }
}

async function refreshProject() {
  state.project = await api(`/api/projects/${state.project.id}`);
  await render();
}

document.addEventListener("input", (e) => {
  if (e.target.id === "leak-h" || e.target.id === "leak-r") {
    const h = Number(($("leak-h") || {}).value || 12);
    const r = Number(($("leak-r") || {}).value || 150);
    if ($("leak-h-v")) $("leak-h-v").textContent = h + " hours";
    if ($("leak-r-v")) $("leak-r-v").textContent = "$" + r + "/hour";
    if ($("leak-out")) $("leak-out").textContent = money(h * r * 12);
  }
});

document.addEventListener("change", async (e) => {
  if (e.target.id === "proj-switch" && e.target.value) {
    const page = ["overview", "analyzer", "scope", "orders", "history", "precedents"].includes(state.route.page)
      ? state.route.page
      : "overview";
    go(`#/app/p/${e.target.value}/${page}`);
  }
  if (e.target.id === "sow-file" && e.target.files && e.target.files[0] && state.project) {
    const err = $("sow-err");
    const fd = new FormData();
    fd.append("file", e.target.files[0]);
    try {
      await fetch(`/api/projects/${state.project.id}/documents`, { method: "POST", body: fd, credentials: "same-origin" }).then(async (res) => {
        if (!res.ok) {
          const j = await res.json().catch(() => ({}));
          throw new Error(j.detail || res.statusText);
        }
      });
      toast("Scope replaced from the file.");
      await refreshProject();
    } catch (ex) {
      if (err) {
        err.classList.remove("hidden");
        err.textContent = ex.message;
      }
    }
  }
  if (e.target.id === "new-file" && e.target.files && e.target.files[0]) {
    e.target.closest("label").dataset.ready = e.target.files[0].name;
    toast("File ready: " + e.target.files[0].name);
  }
});

document.addEventListener("click", async (e) => {
  const drop = e.target.closest("#new-drop");
  if (drop && e.target.id !== "new-file") $("new-file").click();

  if (e.target.id === "show-pass") {
    const p = $("login-pass");
    if (p) p.type = e.target.checked ? "text" : "password";
    return;
  }
  const planBtn = e.target.closest("[data-plan]");
  if (planBtn && !planBtn.disabled) {
    try {
      state.settings = await api("/api/settings", {
        method: "PUT",
        body: JSON.stringify({ plan: planBtn.dataset.plan }),
      });
      toast("Plan updated on this machine. No payment was taken.");
      await route();
    } catch (ex) {
      toast(ex.message);
    }
    return;
  }
  if (e.target.id === "logout") {
    await api("/api/auth/logout", { method: "POST", body: "{}" });
    state.user = null;
    toast("Signed out.");
    go("#/product");
    return;
  }
  if (e.target.id === "login-go") {
    const err = $("login-err");
    if (!$("login-terms").checked) {
      err.classList.remove("hidden");
      err.textContent = "Accept the Terms of Use and Privacy Policy to sign in.";
      return;
    }
    try {
      const out = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: $("login-email").value,
          password: $("login-pass").value,
          accept_terms: $("login-terms").checked,
        }),
      });
      state.user = out.user;
      toast("Signed in.");
      go("#/product");
    } catch (ex) {
      err.classList.remove("hidden");
      err.textContent = ex.message;
    }
  }
  if (e.target.id === "reg-go") {
    const err = $("reg-err");
    try {
      const out = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          name: $("reg-name").value,
          email: $("reg-email").value,
          password: $("reg-pass").value,
          accept_terms: $("reg-terms").checked,
        }),
      });
      state.user = out.user;
      toast("Account created.");
      go("#/product");
    } catch (ex) {
      err.classList.remove("hidden");
      err.textContent = ex.message;
    }
  }
  if (e.target.id === "req-go") {
    const err = $("req-err");
    try {
      await api(`/api/projects/${state.project.id}/requests`, {
        method: "POST",
        body: JSON.stringify({ body: $("req-body").value, source: "paste" }),
      });
      toast("Checked against the SOW.");
      await refreshProject();
    } catch (ex) {
      err.classList.remove("hidden");
      err.textContent = ex.message;
    }
  }
  if (e.target.id === "new-go") {
    const err = $("new-err");
    try {
      const file = $("new-file") && $("new-file").files && $("new-file").files[0];
      let p;
      if (file) {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("client_name", $("new-client").value);
        fd.append("name", $("new-name").value);
        const res = await fetch("/api/projects/upload", { method: "POST", body: fd, credentials: "same-origin" });
        if (!res.ok) {
          const j = await res.json().catch(() => ({}));
          throw new Error(j.detail || res.statusText);
        }
        p = await res.json();
      } else {
        p = await api("/api/projects", {
          method: "POST",
          body: JSON.stringify({
            sow_text: $("new-sow").value,
            client_name: $("new-client").value,
            name: $("new-name").value,
          }),
        });
      }
      toast("Project created. Review the fence.");
      go(`#/app/p/${p.id}/scope`);
    } catch (ex) {
      err.classList.remove("hidden");
      err.textContent = ex.message;
    }
  }
  if (e.target.id === "s-save") {
    try {
      state.settings = await api("/api/settings", {
        method: "PUT",
        body: JSON.stringify({
          agency_name: $("s-agency").value,
          owner_name: $("s-owner").value,
          client_rate: Number($("s-cr").value),
          internal_rate: Number($("s-ir").value),
          currency: $("s-cur").value,
          tone: $("s-tone").value,
        }),
      });
      toast("Settings saved.");
    } catch (ex) {
      $("s-err").classList.remove("hidden");
      $("s-err").textContent = ex.message;
    }
  }
  if (e.target.id === "report-print") {
    window.print();
    return;
  }
  if (e.target.id === "report-dl" && state.lastReport) {
    downloadText(state.lastReport.filename, state.lastReport.document);
    return;
  }
  if (e.target.id === "land-print" || e.target.id === "land-dl") {
    try {
      const doc = await api("/api/demo/report", {
        method: "POST",
        body: JSON.stringify({ body: state.lastDemoBody || ($("land-req") && $("land-req").value) || "" }),
      });
      if (e.target.id === "land-print") openSheet(doc);
      else downloadText(doc.filename, doc.document);
    } catch (ex) {
      toast(ex.message);
    }
    return;
  }
  if (e.target.id === "pw-go") {
    try {
      await api("/api/auth/password", {
        method: "POST",
        body: JSON.stringify({ current_password: $("pw-cur").value, new_password: $("pw-new").value }),
      });
      toast("Password updated.");
    } catch (ex) {
      $("s-err").classList.remove("hidden");
      $("s-err").textContent = ex.message;
    }
  }
  const t = e.target.closest("[data-copy],[data-co],[data-sheet],[data-decide],[data-hrs],[data-editscope],[data-savescope]");
  if (!t) return;
  if (t.dataset.copy) {
    navigator.clipboard.writeText(decodeURIComponent(t.dataset.copy));
    t.textContent = "Copied";
    toast("Reply copied. It was not sent.");
  }
  if (t.dataset.co) openCO(t.dataset.co);
  if (t.dataset.sheet) openSheet(await api(`/api/analyses/${t.dataset.sheet}/sheet`));
  if (t.dataset.decide) {
    const note = ($("note-" + t.dataset.decide) || {}).value || "";
    await api(`/api/analyses/${t.dataset.decide}/decide`, {
      method: "POST",
      body: JSON.stringify({ action: t.dataset.act, note }),
    });
    toast("Decision saved. Nothing was sent to the client.");
    await refreshProject();
  }
  if (t.dataset.hrs) {
    const id = t.dataset.hrs;
    await api(`/api/analyses/${id}/commercial`, {
      method: "POST",
      body: JSON.stringify({
        estimated_hours: Number($("hrs-" + id).value),
        client_rate: Number($("rate-" + id).value),
        internal_rate: Number($("irate-" + id).value),
        timeline_impact_days: Number($("days-" + id).value),
      }),
    });
    toast("Commercials recalculated in Python.");
    await refreshProject();
  }
  if (t.dataset.editscope) {
    $("se-" + t.dataset.editscope).classList.toggle("hidden");
  }
  if (t.dataset.savescope) {
    const id = t.dataset.savescope;
    await api(`/api/scope-items/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ kind: $("sk-" + id).value, body: $("sb-" + id).value }),
    });
    toast("Clause saved.");
    await refreshProject();
  }
});

async function openCO(id) {
  openSheet(await api(`/api/analyses/${id}/change-order`));
}

function setupChat() {
  const dock = $("chat-dock");
  const panel = $("chat-panel");
  const log = $("chat-log");
  const form = $("chat-form");
  const input = $("chat-input");
  if (!dock || !panel || !form) return;
  const history = [];
  function bubble(role, text) {
    const d = document.createElement("div");
    d.className = "chat-bubble " + (role === "user" ? "user" : "bot");
    d.textContent = text;
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
  }
  function open() {
    panel.classList.remove("hidden");
    dock.classList.add("open");
    if (!log.childElementCount) {
      bubble(
        "bot",
        state.user
          ? "Ask about a live project, recovered fees, or a plan. I only use workspace facts, not full SOW text."
          : "Ask about RaoGuard, the Free trial, pricing ($29 / $59 / $89), or how change orders work. Sign in to ask about your projects."
      );
    }
    input.focus();
  }
  function close() {
    panel.classList.add("hidden");
    dock.classList.remove("open");
  }
  $("chat-fab").onclick = () => (panel.classList.contains("hidden") ? open() : close());
  $("chat-close").onclick = close;
  form.onsubmit = async (ev) => {
    ev.preventDefault();
    const msg = (input.value || "").trim();
    if (msg.length < 2) return;
    input.value = "";
    bubble("user", msg);
    history.push({ role: "user", content: msg });
    try {
      const out = await api("/api/chat", {
        method: "POST",
        body: JSON.stringify({ message: msg, history: history.slice(0, -1) }),
      });
      bubble("bot", out.reply);
      history.push({ role: "assistant", content: out.reply });
    } catch (ex) {
      bubble("bot", ex.message || "Could not reach the assistant.");
    }
  };
}

boot();

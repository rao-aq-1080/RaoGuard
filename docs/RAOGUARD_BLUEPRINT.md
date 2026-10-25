# RaoGuard — Product + Technical Blueprint

**Working name:** RaoGuard  
**Positioning line:** AI Scope & Margin Intelligence  
**Promise:** Know the commercial status of every client request before the team starts building.  
**Document type:** Implementation-ready blueprint for one founder  
**Date:** 19 September 2026  
**Authoring stance:** Senior product/architecture review — not a cheerleading deck  
**Constraint:** $0 development cost, $0 MVP operating cost, Windows 10 / 8 GB RAM, Groq + Python + FastAPI + Supabase + GitHub  

**Status of this document:** Ready to build against. Not a trademark opinion. Not legal advice.

---

## 0. Executive verdict

The problem is real. Agencies leak money because work starts before anyone checks the SOW. Ignition’s 2025 data still holds as the commercial proof: 57% of agencies lose $1–5k/month to unbilled work; only 1% bill for all of it. Average agency net margin is thin (~13%). A tool that sits between “client asked” and “engineer started” is a real product.

**What is not real:**

1. The name **RaoGuard** is a weak commercial brand and has collisions. Treat it as a working title, not a launch brand.
2. The workflow `SOW → paste request → AI verdict → change order` is **already being copied**. ScopeLock AI (Aug 2026), freelancer ScopeGuard clones, agency-ops agents (Enterprise DNA Omni), and PSA tools (Ignition, Productive, Scoro, Accelo) already occupy pieces of this. A generic “AI thinks this is out of scope” product will not get paid.
3. Your proposed 13-phase, 11-screen, precedent-engine, RAG, dashboard, landing-page SaaS is **three products**. The MVP is one screen: evidence-backed classification + editable commercial impact + human approval + a draft change order.
4. **$0 forever production hosting does not exist** in a form agencies will trust with live SOWs. $0 is achievable for *build, test, demo, and first design partners* if you run locally, keep secrets off public GitHub, and use free tiers with their real limits. Always-on, private, SLA-backed hosting is the first honest paid cost — and it should wait until someone pays you.
5. Pricing at $19–29/month is a mistake. You are not selling a toy. You are protecting four-figure monthly leakage. After validation, price against recovered margin, not API cost.

**The only defensible wedge for a solo founder in 2026:**

> Evidence-first commercial control for **software agencies**, with **deterministic rules before the LLM**, **citations that cannot be invented**, **human approval on every commercial act**, and **the agency’s own decision history** as the long-term moat.

If you cannot show a quoted SOW clause next to the client’s sentence, you do not have a product. You have a chatbot.

**Build this, in this order:** Northstar demo that a founder will sit through in 8 minutes → 10 conversations → 3 design partners using their real SOWs → then architecture for memory/precedent. Do not invert that.

---

## 1. Name, domain, GitHub, company, trademark

### 1.1 Findings (web + GitHub, 19 Sep 2026)

| Check | Result | Risk |
|---|---|---|
| Web brand “RaoGuard” as a company/product | No established SaaS, agency, or funded company found under that exact string | Low as a *company* collision |
| GitHub `fahim0-3/RAGuard` | Public repo, last commit 29 Aug 2026. Self-described **citation-verified RAG** for policy/document Q&A. Uses Groq among other providers. 25 commits. | **High phonetic/visual collision.** Same letters, same “RAG + Guard + evidence” story. SEO and GitHub search will mix you up. |
| GitHub topic `roguard` | Unofficial Ragnarok Online Discord bot | Low, different market |
| `RepoGuard` | Educational repo security scanner | Medium suffix crowding (“*Guard” in GitHub) |
| `ScopeGuard` | Multiple landing pages, hackathon agents, idea posts | High category crowding |
| WhoisGuard | Namecheap’s old WHOIS privacy product | Low market overlap, leftover search noise |
| USPTO federal search | **Not completed.** TESS was retired Nov 2023. Live search is [tmsearch.uspto.gov](https://tmsearch.uspto.gov/). This document is **not** clearance. | Unknown until you search |
| Pakistan IPO | Not searched | Unknown if you sell locally under this mark |
| Common-law / App Store / LinkedIn pages | No RaoGuard SaaS found in open web search | Incomplete |

I did **not** obtain a live registrar answer for `raoguard.com` / `.ai` / `.io` in this pass. Check them on the registrar before printing business cards. Do not assume availability.

### 1.2 Brand diagnosis

**RaoGuard** is a founder-name + generic suffix construction.

- “Rao” means nothing to a Brooklyn Shopify agency or a Lahore software house’s US client. It is not descriptive of the job.
- “Guard” is exhausted in software (Cloudflare, Auth0’s Guard naming patterns, Prompt Guard, RepoGuard, ScopeGuard, WhoisGuard).
- Combined with GitHub **RAGuard** (evidence-citing RAG, 2026), you will lose search and look derivative.

USPTO Class 42 (SaaS) and Class 9 (downloadable) are the relevant US classes. “Guard” plus a short prefix is a crowded pattern; examiners look at sight, sound, and commercial impression, not letter-for-letter identity. **RAGuard vs RaoGuard** is exactly the kind of pair that can draw a likelihood-of-confusion argument if that project ever files, and it already pollutes GitHub.

This is **not** a reason to stop building. It is a reason not to tattoo the name on the product.

### 1.3 Recommendation

Keep **RaoGuard as the internal/working name** for the next 90 days. Do not buy five domains, do not file a trademark, do not print it on a pitch deck as if it were cleared.

Before any public launch, run:

1. [tmsearch.uspto.gov](https://tmsearch.uspto.gov/) — word mark, then phonetic, then Class 42/9.
2. GitHub, Product Hunt, LinkedIn company, Google, App Store, Play Store.
3. IPO Pakistan if you will brand in PK.
4. Domain check: `.com` first. `.ai` is a marketing tax, not a strategy.

**Better commercial names to test with 10 agency owners** (do not fall in love yet):

| Candidate | Why it might work | Why it might fail |
|---|---|---|
| **OverScope** | Says the job | Easy to confuse with “over scope” as a phrase, hard to trademark |
| **Billfence** | Money + boundary | Ugly; some will hate it, which can be good |
| **Clause** | Evidence-first | Crowded legal-tech; likely taken |
| **SOWline** | Literal | Ugly, descriptive (harder to register) |
| **Inbounds** | “Is it in bounds?” | Generic |
| **Marginline** | Speaks to the buyer (owner) | Sounds like finance SaaS |

Pick the name **after** five owners say the demo is useful. Names are cheap. Trust is not.

For the rest of this blueprint I will keep saying **RaoGuard** because that is the working title you asked for.

---

## 2. Product strategy

### 2.1 What RaoGuard is

A **commercial control layer** between client requests and engineering work.

It is not a PM tool, CRM, chatbot, invoicing app, or legal AI. It answers one question:

> Before we start working on this request, is it included in what the client paid for?

Then it shows **why**, in the client’s own signed words, and what it would cost to say yes.

### 2.2 Who pays

**Buyer:** agency founder, delivery lead, or account manager.  
**User:** same people, plus a tech lead who pastes tickets.  
**Economic buyer is not the developer.**

**ICP for MVP (narrow on purpose):**

- Software / web / Shopify / custom-dev agencies
- 5–40 people
- Fixed-price or hybrid SOWs (not pure T&M — T&M already bills hours)
- English-language contracts
- Client communication in Slack/email/Jira, but **MVP intake is paste/upload**

**Do not** chase lawyers, construction, marketing retainers, or enterprise Salesforce shops in v1. Different contracts, different buyers, longer sales.

### 2.3 Jobs to be done

1. Stop unpaid work from starting.
2. Make the “this isn’t in the SOW” conversation non-awkward (draft the words).
3. Put a dollar figure on the extra work so the founder can decide.
4. Leave a record of what was decided, in case the client argues later.

Job 4 is how you become sticky. Jobs 1–3 are how you get the first yes.

### 2.4 Anti-positioning (say this out loud)

We are not Asana. We do not replace Jira. We do not send the email. We do not invoice. We do not “autonomously protect your margin.” We produce a **draft commercial decision with evidence**, and a human owns it.

### 2.5 Hero copy (landing)

**Headline:** Stop doing work you forgot to bill for.

**Subhead:** RaoGuard checks a client request against the signed SOW, quotes the clause, estimates the commercial impact, and drafts a change order. Your team decides. Nothing goes to the client until a human says so.

**Workflow strip:** Signed SOW → Client request → Scope analysis → Commercial impact → Human approval → Change order

### 2.6 Founder section (honest)

**Muhammad Abdullah** — Founder & Product Engineer. Software engineering undergraduate. AI/ML builder. Pakistan.

Do not invent customers, revenue, or “trusted by 200 agencies.” The story is:

> Software teams are good at building. They are worse at noticing that a small client request just became unpaid work. RaoGuard is a commercial control point between what was agreed, what was asked, and what actually gets built.

That is enough. Anything more will be smelled immediately.

---

## 3. Competitive analysis

Do not assume uniqueness. The *idea* is circulating in 2026. The *execution quality of evidence* is not.

### 3.1 Competitor map

| Product | Target | What they actually do | SOW intelligence | Request analysis | Evidence/citations | Change orders | Approval | Margin analytics | Integrations | Precedent | Weakness | Your opening |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Ignition** | Agencies, accountants | Proposals, agreements, instant billing | Scope in the *proposal*, not live matching | No live Slack/Jira classifier | Contract text, not AI citations | Instant bill / agreement edit | Client e-sign | Weak as “margin intelligence” | Billing-first | No | Does not watch incoming requests | You sit *after* signature, on the request |
| **Productive, Scoro, Accelo, Kantata** | Agencies / PSA | Projects, time, budget, invoicing | Budget vs plan, not clause-level SOW | Variance alerts, not semantic | No clause quotes | Some CO workflows, heavy | Process-heavy | Strong financials, weak contract NLP | Deep, expensive | No | Slow, expensive, not AI-evidence | You are the wedge they will not build first |
| **Monday / Asana / ClickUp / Jira** | Everyone | Tasks | None | None that knows the SOW | None | None | Workflow | No | Ubiquitous | No | They will not grow SOW-DNA | Never compete at task tracking |
| **ScopeLock AI** (indie, Aug 2026) | Freelancers / small agencies | Parse SOW, flag request, draft CO | Yes (LLM) | Yes | Unclear / likely LLM-only | Yes | Unclear | Thin | Paste | No | Easy to clone; trust unknown | Beat them on **evidence that cannot be invented** + agency workflow |
| **scopeguard.me and clones** | Freelancers | Alerts + response templates | Light | Keyword/LLM | Weak | Templates | Weak | “Revenue protected” vanity | Slack/email claims | No | $19 toys; vapor features | Ignore pricing; take the category upstairs |
| **Enterprise DNA Omni / agency “account health agents”** | Mid agencies | Watch channels, draft COs | Contract ingest | Yes, agentic | Varies | Yes | AM in the loop | Case-study $ | Custom implementation | Informal | Services-shaped, not product | You ship a product a 12-person shop can use this week |
| **PandaDoc / Proposify / Qwilr** | Sales | Proposals | Templates | No live requests | No | Weak | E-sign | No | Sales stack | No | Pre-signature | Different job |
| **Harvey / Spellbook / Kira / Luminance** | Legal | Contract review | Deep | Not agency requests | Strong citations in legal | N/A | Lawyer | N/A | Legal | Matter-based | Wrong buyer, expensive, not change-order native | Steal their **citation discipline**, not their GTM |
| **Harvest / Toggl / Hubstaff** | Time | Time capture | None | None | None | Invoice hours | None | Utilization | Accounting | No | Time ≠ scope | Don’t build timers |

### 3.2 What is already commoditized

- Pasting text into an LLM and asking “is this in scope?”
- Drafting a polite email
- A dashboard with three big numbers
- “AI for agencies” landing pages

If your MVP is those four things, you have no wedge.

### 3.3 What is not commoditized (your actual product)

1. **Structured scope baseline** with typed items (exclusion, quantity cap, revision cap, included module) and **immutable source spans**.
2. **Rules that fire before Groq** (exclusion hit, quantity overrun, revision overrun, missing rate).
3. **Classification richer than in/out** (bug vs feature vs quantity vs platform vs dependency).
4. **Citations that fail closed** — if the model cannot point at a stored span, the system returns `NEEDS_HUMAN_REVIEW`, never a fake §4.2.
5. **Human-required commercial acts.**
6. **Decision history that becomes that agency’s private case law.**

### 3.4 Sources for the market claim

- Ignition / The Drum (May 2025): cash flow, unbilled work, 57% / 30% / 1% figures.
- AAAA agency operations commentary on overservicing.
- Digital Applied (May 2026) SOW framework — the industry is writing playbooks because tools still don’t do this live.

Use these in sales. Do not fake a TAM model beyond “agencies with English SOWs who eat unpaid work.”

---

## 4. Differentiation and the wedge

**Wedge sentence:**

> RaoGuard is the only tool that will refuse to give you an answer if it cannot quote the SOW.

That is sharper than “AI scope creep.”

**Category:** Commercial control software for software agencies.  
**Not:** AI project management.

**90-day wedge feature (only this):**

Upload/paste SOW → review extracted fence → paste request → see classification + quoted evidence + editable hours×rate → approve/edit/reject → download change-order PDF + copy client reply.

Everything else is a sequel.

---

## 5. Critical review (read this before writing code)

### 5.1 What is genuinely valuable

The **pause**. The product’s job is to insert a 30-second commercial checkpoint. If you do that with evidence, agencies will pay. If you do that with vibes, they will try it once and mute you.

### 5.2 What is already commoditized

LLM summarization of a PDF. Polite email drafts. “Confidence: 96%.” Fake enterprise sidebars.

### 5.3 What competitors already do

Ignition already bills extra work — after a human notices. PSA tools already show budget overrun — after hours are logged. Indie tools already paste-and-classify. You are not first to the sentence. You can still be first to **trusted evidence + agency workflow + memory**.

### 5.4 What is easy to copy

Your prompts. Your Streamlit screens. Your Northstar demo. Assume a competent intern can clone the happy path in a weekend. **Do not** rest the company on the happy path.

### 5.5 What is hard

- Parsing real SOWs (scanned PDFs, tables, “see Exhibit B”, contradictory annexes).
- Bug vs feature without being a lawyer.
- Not hallucinating clause numbers.
- Getting a PM to paste requests *before* assigning the ticket.
- Multi-tenant isolation that an agency’s lawyer will accept.

### 5.6 Legal / liability risk (serious)

If RaoGuard says **IN_SCOPE** and the team works for free, you contributed to the loss.  
If it says **OUT_OF_SCOPE** wrongly, the AM looks adversarial and you contributed to a lost client.  
If it **invents a clause**, you are in defamation-of-contract territory in spirit even if not in court.

**Mitigations that are product, not legalese:**

- Every screen: “Estimate. Not a legal opinion. Not a binding quote.”
- Human must click Approve before anything is treated as a decision.
- No auto-send. Ever, in v1–v3.
- Evidence spans must exist in `scope_items.source_text` or the analysis is invalid.
- Log model, prompt version, retrieved item IDs.
- Offer deletion.
- Do not claim SOC2 until you have it.

You are not a law firm. Do not analyze employment contracts, NDAs as a service, or “is this illegal.” SOW commercial scope only.

### 5.7 What would make agencies refuse

- Sending their SOW to a US LLM with no explanation.
- Public Streamlit URLs with client names.
- Auto-emailing the client.
- Being wrong twice in week one.
- Asking them to replace Jira.

**Groq data flow must be explicit in Settings and in the analysis footer:**

> We send the request text and the retrieved SOW *clauses* (not necessarily the full PDF) to Groq (US). We do not send your API keys. We do not use your data to train a RaoGuard model. Groq’s own retention policy applies. You can run rules-only mode.

Offer **Rules-only mode** (no Groq). It will be dumber and it will close the most paranoid shops.

### 5.8 What would make them pay

One recovered change order larger than a year of subscription. Show that in the demo with *their* Slack message.

Your $19–29 idea underprices the job and attracts freelancers who churn. After validation, think **$79–149** only if you stay tiny; **$199–499** if you sell to 8–40 person software houses. Research at pricing time; do not lock numbers in the MVP.

### 5.9 Strongest long-term moat

Not the model. Not the UI.

```
that agency’s SOWs
+ their requests
+ their human overrides
+ what they actually billed
+ what the project actually cost
```

That is **company commercial memory**. It is not “training the AI.” It is a private database of how *this* firm interprets scope. Switching cost becomes real around month 4, not day 1.

### 5.10 Unnecessary in v1 (cut without guilt)

Gmail/Slack monitors, auto-send, e-sign, QuickBooks, SSO, mobile app, RBAC beyond owner/member, autonomous agents, scraping, custom model training, pgvector, embeddings, multi-currency FX engine, white-label, public marketing site with fake metrics, microservice mesh, Docker, Kubernetes, Colab GPUs.

Colab is useful for *experiments*, not for the product runtime. Your 8 GB machine can run FastAPI + Streamlit + Postgres-over-network just fine. You do not need a GPU.

---

## 6. MVP definition

A user can, without paying anyone:

1. Create an organization + project (Northstar seeded).
2. Upload PDF / DOCX / TXT or paste an SOW.
3. Review and edit the extracted scope baseline.
4. Submit a client request (paste).
5. Get a classification with **quoted evidence**, confidence, and reason.
6. See commercial impact (hours × client rate, internal cost, gross profit, timeline) labeled as estimates.
7. Edit hours, rate, price, timeline.
8. Approve / edit / reject / ask for clarification.
9. Copy a client-ready reply (tone selectable).
10. Generate a change-order document (HTML/PDF).
11. See the decision in history.

If any of those eleven require a paid API, you failed the constraint.

**Out of MVP:** live Slack, Gmail, Jira OAuth, e-sign, invoicing, dashboards with 20 charts, precedent UI as a separate product area (a “similar past decisions” box on the analysis screen is enough).

### 6.1 Success criteria (measurable)

- Northstar’s five requests classify as specified in §21, with evidence spans, without Groq being allowed to invent clauses.
- A stranger can complete the eleven steps in <15 minutes on your machine.
- 5 agency conversations in 30 days; 2 of them paste a real SOW.
- Zero paid invoices from vendors.

Kill criteria: if 10 owners say “we’d just ask ChatGPT,” your evidence UX is not strong enough. Fix citations, don’t add features.

---

## 7. User journeys

### 7.1 First-run (founder, 8 minutes)

Opens app → Northstar project already there → opens request “loyalty points” → sees OUT_OF_SCOPE, quoted exclusion, $6,600, Approve + Change order → downloads PDF.  
That is the sales demo. Script it. Do not ad-lib.

### 7.2 Real project

Creates project → uploads SOW → waits 15–60s → corrects 3 wrong extractions (this *will* happen) → confirms baseline → pastes Slack screenshot-as-text → reviews analysis → edits hours 40→32 → approves → copies reply → stores CO.

### 7.3 Bug path

Pastes “ATC broken on Safari” → BUG_OR_DEFECT → $0 → reply “we’ll fix in current sprint” → no CO.

### 7.4 Ambiguity path

Conflicting clauses or no evidence → NEEDS_HUMAN_REVIEW → no price pretended as fact → user must pick.

### 7.5 Failure path

Scanned PDF with no text → error “This PDF has no extractable text. Paste the scope section or export to Word.” Do not silently send garbage to Groq.

---

## 8. Architecture

### 8.1 Principle

```
Document parser (Python)
    → Structured scope (Postgres)
    → Retrieve relevant items (SQL, not “the whole PDF”)
    → Deterministic rules
    → Groq (optional, JSON only, retrieved items only)
    → Evidence validator (must match stored spans)
    → Commercial calculator (Python only)
    → Human review
    → Change order / reply drafts
    → Audit row
```

**Forbidden:**

```
SOW + request → Groq → everything
```

### 8.2 Runtime (one developer, 8 GB RAM)

```
Windows 10
  Streamlit UI  (localhost:8501)
       │  HTTP
  FastAPI       (localhost:8000)
       │
  Supabase Postgres + Auth   (cloud free)
       │
  Groq API                   (cloud free tier)
```

No Docker. No local LLM. No local embedding model (they blow RAM). No Redis. No Celery. No Kafka. Analysis is synchronous; a single SOW extract is the slow call (one Groq request).

SQLite is an acceptable **offline fallback** if Supabase is paused. Default to Supabase so Auth/RLS is real. Provide `DATABASE_URL` switching.

### 8.3 Why not pgvector in MVP

A typical SOW is 5–40 pages. After extraction you have 20–80 scope items. Keyword + Postgres `ILIKE` / `tsvector` plus type filters (exclusion vs deliverable) will retrieve the right rows. Embeddings add: another model, RAM, token cost, failure modes. Add pgvector **after** you have SOWs where FTS misses semantically (“loyalty” vs “rewards programme”).

### 8.4 Why Streamlit first

You asked for $0 and Python. Streamlit is the honest UI for that. It is **not** a product you sell to a 40-person agency as “our platform.” When you have three paying teams, replace Streamlit with a simple server-rendered or HTMX/FastAPI UI, or a small React app. Do not start there.

### 8.5 Process model

One Uvicorn process. One Streamlit process. That’s it.

---

## 9. Database schema (Supabase Postgres)

Keep it smaller than the wishlist. Client is a field on `projects` until you have repeat clients.

```sql
-- Enable if you use FTS
create extension if not exists pg_trgm;

create table organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique not null,
  default_client_rate numeric(12,2) not null default 150,
  default_internal_rate numeric(12,2) not null default 80,
  currency char(3) not null default 'USD',
  groq_enabled boolean not null default true,
  created_at timestamptz not null default now()
);

create table org_members (
  org_id uuid not null references organizations(id) on delete cascade,
  user_id uuid not null, -- supabase auth.users
  role text not null check (role in ('owner','member')),
  created_at timestamptz not null default now(),
  primary key (org_id, user_id)
);

create table projects (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  name text not null,
  client_name text not null,
  contract_value numeric(14,2),
  currency char(3) not null default 'USD',
  timeline_weeks numeric(6,1),
  client_rate numeric(12,2),
  internal_rate numeric(12,2),
  status text not null default 'active' check (status in ('active','closed')),
  created_at timestamptz not null default now()
);
create index on projects (org_id);

create table scope_documents (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  filename text,
  mime_type text,
  raw_text text not null,          -- extracted plaintext; the source of truth
  page_count int,
  sha256 text,
  created_at timestamptz not null default now()
);

-- Typed fence. source_text MUST be a substring of scope_documents.raw_text
create table scope_items (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references scope_documents(id) on delete cascade,
  project_id uuid not null references projects(id) on delete cascade,
  kind text not null check (kind in (
    'deliverable','exclusion','assumption','quantity_limit',
    'revision_limit','commercial','dependency','timeline','other'
  )),
  title text not null,
  body text not null,
  quantity_value numeric(12,2),
  quantity_unit text,              -- skus, pages, revisions, hours, users
  section_label text,              -- "§4.2" if present in source; nullable
  page_hint int,
  source_text text not null,       -- exact excerpt
  source_start int,                -- char offset into raw_text
  source_end int,
  created_at timestamptz not null default now()
);
create index on scope_items (project_id, kind);
create index on scope_items using gin (body gin_trgm_ops);

create table requests (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  source text not null default 'paste' check (source in ('paste','email','slack','jira','meeting','other')),
  body text not null,
  created_by uuid,
  created_at timestamptz not null default now()
);
create index on requests (project_id, created_at desc);

create table analyses (
  id uuid primary key default gen_random_uuid(),
  request_id uuid not null references requests(id) on delete cascade,
  project_id uuid not null references projects(id) on delete cascade,
  classification text not null check (classification in (
    'IN_SCOPE','OUT_OF_SCOPE','BUG_OR_DEFECT','QUANTITY_OVERRUN',
    'REVISION_OVERRUN','REQUIREMENT_CHANGE','INTEGRATION_CHANGE',
    'PLATFORM_CHANGE','TIMELINE_CHANGE','CLIENT_DEPENDENCY',
    'AMBIGUOUS','NEEDS_HUMAN_REVIEW'
  )),
  confidence numeric(4,3) not null check (confidence >= 0 and confidence <= 1),
  reason text not null,
  estimated_hours numeric(8,2),
  timeline_impact_days numeric(6,1),
  requires_change_order boolean not null default false,
  requires_human_review boolean not null default true,
  rules_fired jsonb not null default '[]',
  groq_used boolean not null default false,
  groq_model text,
  prompt_version text,
  raw_model_json jsonb,
  created_at timestamptz not null default now()
);

create table analysis_evidence (
  id uuid primary key default gen_random_uuid(),
  analysis_id uuid not null references analyses(id) on delete cascade,
  scope_item_id uuid not null references scope_items(id),
  role text not null check (role in ('supports','conflicts')),
  quote text not null                 -- must equal scope_items.source_text or a subset
);

create table commercial_snapshots (
  id uuid primary key default gen_random_uuid(),
  analysis_id uuid not null references analyses(id) on delete cascade,
  estimated_hours numeric(8,2) not null,
  client_rate numeric(12,2) not null,
  internal_rate numeric(12,2) not null,
  client_price numeric(14,2) not null,     -- hours * client_rate  (Python)
  internal_cost numeric(14,2) not null,    -- hours * internal_rate
  gross_profit numeric(14,2) not null,
  timeline_impact_days numeric(6,1),
  is_estimate boolean not null default true,
  edited_by_human boolean not null default false,
  created_at timestamptz not null default now()
);

create table decisions (
  id uuid primary key default gen_random_uuid(),
  analysis_id uuid not null references analyses(id) on delete cascade,
  actor uuid,
  action text not null check (action in ('approve','reject','edit','clarify')),
  note text,
  final_classification text,
  created_at timestamptz not null default now()
);

create table change_orders (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  analysis_id uuid not null references analyses(id),
  title text not null,
  body_markdown text not null,
  hours numeric(8,2) not null,
  price numeric(14,2) not null,
  status text not null default 'draft' check (status in ('draft','sent','approved','declined')),
  created_at timestamptz not null default now()
);

create table audit_events (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  project_id uuid,
  actor uuid,
  event_type text not null,
  payload jsonb not null default '{}',
  created_at timestamptz not null default now()
);
create index on audit_events (org_id, created_at desc);
```

**Precedents:** do not create a table. Query past `analyses` joined to `requests` and `decisions` where `action = 'approve'` and trigram-similar request bodies. That *is* the precedent engine in v1.

### 9.1 RLS sketch

```sql
alter table organizations enable row level security;
-- Repeat for every table.

-- Helper: current user's org ids
-- org_members.user_id = auth.uid()

create policy "member_read_org"
  on projects for select
  using (org_id in (select org_id from org_members where user_id = auth.uid()));
```

Write analogous policies for all tables via `project_id → projects.org_id → org_members`. Service role key is **backend only**. Streamlit never sees the service role.

Supabase Auth: email magic link is enough. No SSO.

### 9.2 Indexes / storage discipline (stay inside 500 MB)

- Store `raw_text`, not original PDFs, unless the user needs download. Original files: optional, compress, or skip in MVP (1 GB file cap is the other wall).
- Don’t store Groq full traces forever; keep `raw_model_json` for 30 days then null it, or store only on `NEEDS_HUMAN_REVIEW`.
- Northstar seed is tiny.

---

## 10. API (FastAPI)

Thin, boring, one file group.

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/session` | verify supabase JWT (or skip if Streamlit uses supabase client directly) |
| GET | `/projects` | list |
| POST | `/projects` | create |
| GET | `/projects/{id}` | overview |
| POST | `/projects/{id}/documents` | upload; extract text; persist |
| POST | `/projects/{id}/scope/extract` | parse + Groq structure + save items |
| PATCH | `/scope-items/{id}` | human correction of the fence |
| GET | `/projects/{id}/scope` | list items |
| POST | `/projects/{id}/requests` | create request |
| POST | `/requests/{id}/analyze` | rules + groq + validate + calc |
| GET | `/requests/{id}` | request + latest analysis |
| POST | `/analyses/{id}/commercial` | human edit hours/rate |
| POST | `/analyses/{id}/decide` | approve/reject/edit/clarify |
| POST | `/analyses/{id}/change-order` | generate draft |
| GET | `/change-orders/{id}` | body |
| GET | `/projects/{id}/history` | decisions |
| GET | `/projects/{id}/precedents?q=` | similar approved decisions |
| GET | `/projects/{id}/dashboard` | aggregates |

Do not build a public unauthenticated analyze endpoint. That is how your Groq quota dies.

---

## 11. AI architecture, rules, RAG, confidence

### 11.1 Document pipeline

| Input | Library | Cost |
|---|---|---|
| PDF | `pymupdf` (fitz) | Open source |
| DOCX | `python-docx` | Open source |
| TXT / paste | stdlib | Open source |
| Scanned PDF | Detect empty text; **do not** call a paid OCR. Tell the user to paste. Optional later: local Tesseract if they install it. | Tesseract is OSS but extra install — not required |

Extract plaintext with page breaks as `\n\n[[page=N]]\n\n` so `page_hint` is real.

### 11.2 Scope extraction

1. Regex/section split (deterministic): headings like “Out of scope”, “Exclusions”, “Deliverables”, “Assumptions”, “Change orders”, “Fees”.
2. Bullet split.
3. Quantity regex: `(\d[\d,]*)\s*(SKUs?|pages?|screens?|templates?|revisions?|hours?|users?)`.
4. Money / rate / weeks regex.
5. **Then** Groq `sow_extract` prompt with the section text (chunked ≤ 4k tokens), schema-constrained JSON.
6. For each returned item, **re-find** `source_text` in `raw_text` with exact match or fuzzy (rapidfuzz, OSS). If not found → drop the item or mark `needs_review`. **Never keep a Groq clause you cannot locate in the file.**

### 11.3 Retrieval (not RAG theatre)

Given a request:

```python
# 1. token overlap / trigram against scope_items.body
# 2. always include all kind='exclusion'
# 3. always include quantity_limit and revision_limit
# 4. cap at ~12 items
# 5. pass those 12 to rules + Groq
```

That is retrieval. No vectors.

### 11.4 Deterministic rule engine (runs first)

File: `backend/rules/engine.py`

| Rule | If | Classification | CO? |
|---|---|---|---|
| `EXPLICIT_EXCLUSION` | exclusion item fuzzy/keyword match above threshold | OUT_OF_SCOPE | yes |
| `QUANTITY_OVERRUN` | request quantity > item.quantity_value same unit | QUANTITY_OVERRUN | yes |
| `REVISION_OVERRUN` | revision count exceeded (needs a counter on project; v1: if request says “another round” and revision_limit = 1) | REVISION_OVERRUN | yes |
| `INCLUDED_BROKEN` | bug lexicon (broken, doesn’t work, safari, overlap, 500, ticket) AND overlapping deliverable | BUG_OR_DEFECT | no |
| `NO_SCOPE` | zero scope_items | NEEDS_HUMAN_REVIEW | no |
| `NO_RATE` | out-of-scope-ish but client_rate missing | NEEDS_HUMAN_REVIEW (still classify, don’t invent $) | maybe |
| `CONFLICT` | one exclusion and one deliverable both high-score | NEEDS_HUMAN_REVIEW | no |

Rules attach `rules_fired` and candidate evidence IDs. Groq may **confirm or downgrade to NEEDS_HUMAN_REVIEW**. Groq may **not** invent a higher-confidence OUT_OF_SCOPE without evidence IDs that exist.

### 11.5 Groq layer

**Use Groq for:** structuring SOW chunks, semantic comparison, explanation, client reply, change-order prose.

**Never use Groq for:** multiplication, money totals, “is 620 > 400”, JSON schema enforcement (validate in Pydantic), legal conclusions as fact.

**Model policy (verify in your console — limits are org-specific):**

- Default reasoning: `llama-3.3-70b-versatile` **if** it is on your free limits page.
- Fallback / high-volume: `llama-3.1-8b-instant` (secondary sources report much higher daily request caps).
- JSON mode: Groq chat `response_format={"type": "json_object"}` where supported; still Pydantic-validate.

**Official Groq docs (fetched 19 Sep 2026):** rate limits are org-level; exact numbers live at [console.groq.com/settings/limits](https://console.groq.com/settings/limits), not as a single frozen public table for every model. The public rate-limit page lists some models (e.g. `openai/gpt-oss-20b` 30 RPM / 1K RPD / 8K TPM / 200K TPD on the table we fetched) and tells you to check your Limits page. **Do not hard-code blog numbers into production.** Read response headers `x-ratelimit-*` and back off on 429.

Secondary sources (Mar–Aug 2026, not a contract) commonly report free-tier ballparks of ~30 RPM and ~1,000 RPD on 70B-class chat models, with 8B-instant much higher RPD. Treat that as planning folklore. Confirm on your key.

**Token hygiene:**

- Never send the full SOW on each request.
- Cache extract results.
- One Groq call per analyze (comparison+classification+reason in one JSON). Separate calls for reply and CO **only after** human clicks those buttons.
- Prompt version string in DB.

### 11.6 Evidence validator (non-negotiable)

```python
def validate_evidence(quote: str, item: ScopeItem) -> bool:
    q = normalize(quote)
    return q and (q in normalize(item.source_text) or q in normalize(item.body))
```

If Groq returns evidence that fails: drop it. If zero evidence remain and classification is not BUG/IN_SCOPE-with-deliverable: force `NEEDS_HUMAN_REVIEW`, confidence ≤ 0.4.

### 11.7 Confidence

Start from rules:

- Explicit exclusion exact-ish match: 0.90–0.96
- Quantity overrun deterministic: 0.85–0.92
- Bug lexicon + deliverable: 0.80–0.90
- Groq-only semantic: cap at 0.75
- Any failed evidence: cap at 0.40 and human review

Do not display 96% unless a rule fired. Fake precision destroys trust.

### 11.8 Output schema (Pydantic)

```json
{
  "classification": "OUT_OF_SCOPE",
  "confidence": 0.94,
  "reason": "…",
  "evidence_item_ids": ["uuid", "uuid"],
  "quotes": ["exact excerpt"],
  "estimated_hours": 40,
  "timeline_impact_days": 5,
  "requires_change_order": true,
  "requires_human_review": false,
  "feature_title": "Custom loyalty / points program"
}
```

Hours are **suggestions**. Python computes money.

---

## 12. Prompt architecture

Store under `prompts/` as versioned text files. `PROMPT_VERSION=2026-09-19.1`

Nine prompts, all: role, JSON-only, “use only provided excerpts”, “if unsure NEEDS_HUMAN_REVIEW”.

1. `01_sow_extract.md` — given a chunk, return items `{kind,title,body,quantity_value,quantity_unit,section_label,source_text}`. source_text must be copied verbatim.
2. `02_normalize.md` — merge duplicates after extract (optional v1; can skip).
3. `03_request_clean.md` — optional; usually skip. Use the paste as-is.
4. `04_compare.md` — **the money prompt**. Inputs: request, retrieved items with ids. Output: schema above. Forbidden: ids not in the list.
5. `05_classify.md` — merged into 04 for quota reasons.
6. `06_explain.md` — merged into 04 `reason` field.
7. `07_client_reply.md` — after decision. Tones: professional, friendly, direct, relationship-friendly. No new facts.
8. `08_change_order.md` — prose sections only; numbers passed in from Python.
9. `09_precedent.md` — summarize similar past decisions; do not override current evidence.

Full prompt texts: `prompts/` in this repo (see companion files). Keep them short. Long prompts burn Groq TPM.

---

## 13. Commercial calculations (Python only)

```python
from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")

def money(hours: Decimal, rate: Decimal) -> Decimal:
    return (hours * rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

client_price = money(hours, client_rate)
internal_cost = money(hours, internal_rate)
gross_profit = client_price - internal_cost
```

UI must show:

```
Estimated effort: 40 hours   [edit]
Client rate: $165            [edit]
Internal cost rate: $80      [edit]

Client price (estimate): 40 × $165 = $6,600
Internal cost (estimate): 40 × $80 = $3,200
Potential gross profit: $3,400
Timeline (estimate): +4–6 working days   [edit]

These figures are estimates, not a guaranteed engineering quote.
```

If classification is BUG_OR_DEFECT or IN_SCOPE: hours may be 0; do not manufacture a CO.

Quantity overrun hours: start with a boring function, e.g. extra SKUs `max(4, round(extra/50)*4)` — overridable.

---

## 14. Change orders, replies, audit, precedents

**Client reply:** generated on demand, tone enum, copy button. Never auto-send.

**Change order HTML/PDF:** `weasyprint` can be painful on Windows. Prefer:

- Render HTML in Streamlit and **Print to PDF** (zero extra deps), or
- `fpdf2` (pure Python, OSS) for a simple one-pager.

Sections: project, client, date, original SOW value, requested change, quoted evidence, reason, new deliverables, hours, price, timeline, assumptions, exclusions, signature lines (wet ink). No e-sign.

**Audit events:** `document_uploaded`, `scope_extracted`, `scope_item_edited`, `request_created`, `analyzed`, `evidence_dropped`, `groq_failed`, `commercial_edited`, `decided`, `change_order_created`. Payload = ids, not full SOW (keep audit small).

**Precedent box:** top 3 past approved requests by trigram similarity, same org, showing classification + price. Display “this is history, not a rule.”

---

## 15. UI/UX

Professional B2B. Paper/ink, not purple AI. No emoji. No animated gradients. No fake “neural” backgrounds.

**MVP screens (8, not 11):**

1. Sign in
2. Projects list (Northstar at top)
3. Project overview (value, rate, counts)
4. Scope baseline (grouped by kind, inline edit)
5. Request analyzer (paste + result on one page — **the product**)
6. Change order preview
7. History
8. Settings (rates, currency, tone, Groq on/off, “what we send to Groq”)

Dashboard is a few numbers on project overview. Do not build a separate vanity dashboard in v1.

**Analyzer layout (this is the product):**

```
[CLASSIFICATION STAMP]    confidence 94%   rules: EXPLICIT_EXCLUSION

WHY
  SOW §2  EXCLUSION
  "Custom loyalty or points programs"
  — quoted from the signed document, item #12

CLIENT REQUEST
  "Can you also add loyalty points?"

COMMERCIAL IMPACT (estimate)
  40h × $165 = $6,600 client
  40h × $80  = $3,200 cost
  profit     = $3,400
  timeline   +5 days
  [edit hours] [edit rates]

SIMILAR PAST DECISIONS (if any)
  Northstar / loyalty / OUT_OF_SCOPE / $6,600 approved

[Approve] [Edit] [Reject] [Ask for clarification]
[Copy client reply] [Generate change order]

Footer: Groq llama-3.3-70b used. 2 clauses sent. Prompt 2026-09-19.1
```

Landing page can wait until you have a URL you are willing to show. Copy is in §2.5. Do not spend a week on marketing CSS.

---

## 16. Security

| Control | MVP how |
|---|---|
| Auth | Supabase Auth, email |
| Tenant isolation | RLS + backend org checks |
| Secrets | `.env` locally; Streamlit secrets in cloud; **never** `GROQ_API_KEY` in frontend |
| Transport | HTTPS on hosted; localhost on demo |
| Least Groq data | retrieved clauses + request only |
| Keys | rotate if leaked; GitHub secret scanning on |
| Deletion | Settings → delete project (cascade) |
| Audit | `audit_events` |
| Encryption at rest | whatever Supabase free gives; do not claim more |
| Files | prefer not storing original PDF |
| No public demo with real client data | Northstar only on any public host |

Windows `.env` via `python-dotenv`. Commit `.env.example` only.

---

## 17. Testing

`pytest` + golden Northstar cases. No paid CI beyond GitHub Free (2,000 Actions minutes/month — enough).

Must-pass:

| Case | Expected |
|---|---|
| Loyalty points | OUT_OF_SCOPE, exclusion quote, 40h, $6,600 at $165 |
| NetSuite sync | OUT_OF_SCOPE, ERP exclusion, 64h, $10,560 |
| Wholesale login | OUT_OF_SCOPE, 80h, $13,200 |
| 400 → 620 SKUs | QUANTITY_OVERRUN, $2,970 |
| Safari ATC | BUG_OR_DEFECT, $0 |
| Conflicting clauses | NEEDS_HUMAN_REVIEW |
| Empty PDF text | error, no Groq |
| Groq 429 | degrade to rules-only, surface warning |
| Groq invented quote | dropped, NEEDS_HUMAN_REVIEW |
| 40 * 165 | exactly 6600.00 in Decimal |
| Human edits hours to 10 | price 1650.00 |

Do not mock away the validator. That’s the product.

---

## 18. Folder structure (one-developer)

```
raoguard/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # env
│   ├── db.py                   # supabase client
│   ├── api/
│   │   ├── projects.py
│   │   ├── documents.py
│   │   ├── scope.py
│   │   ├── requests.py
│   │   └── change_orders.py
│   ├── documents/
│   │   └── extract.py          # pymupdf, python-docx
│   ├── rules/
│   │   └── engine.py
│   ├── ai/
│   │   ├── groq_client.py      # retries, 429, JSON
│   │   └── validate.py
│   ├── calc/
│   │   └── commercial.py
│   ├── services/
│   │   ├── analyze.py          # orchestration
│   │   └── change_order.py
│   └── schemas.py              # pydantic
├── frontend/
│   └── app.py                  # Streamlit
├── prompts/
├── tests/
│   ├── test_rules.py
│   ├── test_calc.py
│   ├── test_validate.py
│   └── test_northstar.py
├── docs/
│   └── RAOGUARD_BLUEPRINT.md
├── seeds/
│   └── northstar_sow.txt
├── .env.example
├── requirements.txt
└── README.md
```

No `rag/` package until you need it.

### requirements.txt (all OSS / free clients)

```
fastapi
uvicorn[standard]
httpx
pydantic
python-dotenv
pymupdf
python-docx
rapidfuzz
supabase
groq
streamlit
fpdf2
pytest
```

No pandas unless you actually need it. You don’t. No scikit-learn. No langchain. No llama-index. No openai SDK required (`groq` package).

---

## 19. Cost table (verified vs unverified)

Legend: **Official** = fetched from vendor page 19 Sep 2026. **Secondary** = blogs/docs aggregators, confirm yourself. **OSS** = no license fee.

| Component | Technology | MVP $ | Limit nature | Purpose | Source / caveat |
|---|---|---|---|---|---|
| LLM | Groq API | $0 on Free | **Free tier with rate limits, no SLA.** Org-level RPM/RPD/TPM/TPD. Exact numbers: your Limits page. 429 when exceeded. Not unlimited. | Reasoning | Official: [console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits). Check [settings/limits](https://console.groq.com/settings/limits). |
| Database + Auth | Supabase Free | $0 | 500 MB DB, 50k MAU, 5 GB egress, 1 GB files, **2 active projects**, **pause after 1 week inactivity**, shared CPU ~500 MB RAM, unlimited API requests, community support, **commercial use allowed**, no PITR/SLA/SOC2 | Data, auth, RLS | Official: [supabase.com/pricing](https://supabase.com/pricing) |
| Vector | pgvector | $0 if enabled | Same DB size. **Do not use in MVP.** | — | Skip |
| Backend | FastAPI + Uvicorn | $0 | Local process | API | OSS |
| Frontend | Streamlit OSS | $0 | Local | UI | OSS |
| Hosted UI (optional demo) | Streamlit Community Cloud | $0 | Free hosting; public apps from GitHub; resource/sleep limits apply and **are not a written SLA**. Community Cloud page: “Totally free.” Third parties report ~1 GB RAM class, sleep after idle hours, 1 private app. Confirm current docs before relying. | Public Northstar demo only | Official marketing: [streamlit.io/cloud](https://streamlit.io/cloud). Quotas change. |
| Alt demo host | Hugging Face Spaces CPU | $0 | Free CPU Space; sleeps after idle (third parties: ~48h); public by default; private Spaces typically Pro | Demo | Third-party 2026 writeups; confirm HF pricing page |
| Alt API host | Render Free web service | $0 | Sleeps after **15 min** idle; cold start; 750 hrs/mo class; **free Postgres expires ~30 days** — do not put the DB here | Temporary API demo | Third-party 2026 Render writeups; confirm render.com/docs/free |
| Git | GitHub Free | $0 | Unlimited public/private repos; **2,000 Actions min/month**; 500 MB Packages. Fine for one founder. | VCS, light CI | Widely documented GitHub Free; confirm github.com/pricing |
| Docs parse | PyMuPDF, python-docx | $0 | OSS licenses (PyMuPDF has AGPL/commercial nuance — **read the license**. If AGPL is a problem for closed SaaS, use `pypdf` instead.) | Parsing | License check required |
| Fuzzy match | rapidfuzz | $0 | OSS | Evidence locate | OSS |
| PDF CO | fpdf2 or browser print | $0 | OSS | Change orders | OSS |
| HTTP | httpx | $0 | OSS | Groq calls | OSS |
| Colab | Google Colab Free | $0 | Dynamic GPU/RAM; sessions die; **not for serving the app** | Experiments only | Google does not publish a stable quota |
| Email / monitoring / analytics | none | $0 | Log to stdout + audit table | — | — |
| OCR / scraping / paid automation | none | $0 | Out of scope | — | — |

**PyMuPDF license is the one OSS foot-gun.** If you will not open-source RaoGuard, prefer `pypdf` (BSD) even if it is worse at layout.

### 19.1 How to stay at $0 in practice

- Develop on localhost. Ping Supabase weekly or accept pause (unpause in dashboard).
- Never upload 50 MB PDFs.
- One Groq call per analysis; replies only on click.
- Public cloud demo = Northstar sample, not customer SOWs.
- Do not enable Supabase Pro “just in case.”
- Do not put a credit card on Groq “just in case” unless you also set a $0 spend cap — Groq spend limits are a **paid-plan** feature per their spend-limits doc.

**Honest sentence for the README:**

> You can build, demo, and run design-partner sessions at $0. You cannot honestly promise an always-on, private, non-pausing production tenant at $0. When a customer pays, the first real cost is likely Supabase Pro ($25/mo) or a $7–$10 host — still less than one recovered change order.

---

## 20. Zero-cost implementation plan

### Local (default)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# fill SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE, GROQ_API_KEY
uvicorn backend.main:app --reload --port 8000
streamlit run frontend/app.py
```

Windows 10, 8 GB: this fits. Close Chrome tabs. Do not run Docker Desktop.

### Groq usage budget (planning, not a quota)

Until you read your Limits page, assume you must be stingy:

- Extract: 1–3 calls per SOW (chunked), once.
- Analyze: 1 call.
- Reply: 1 call on button.
- CO prose: 1 call on button.

A demo day of 20 analyzes ≈ 20–40 Groq calls. Fine on any published free ballpark. A badly written loop that re-extracts the SOW every keystroke will 429. Cache.

### Cloud MVP without spend

1. Keep using Supabase Free (unpause when needed).
2. Put **only** Northstar + dummy org on Streamlit Cloud from a **public** repo that contains **no customer data and no keys**.
3. Real customer work: your laptop, screen-share, or a private repo Streamlit app (Community Cloud: one private app — third-party claim, verify).
4. Do not use Render free Postgres for anything you care about (30-day expiry in 2026 writeups).

### Colab

Use only to try a prompt or a parser notebook. Do not deploy RaoGuard on Colab.

### Monitoring

`print` + `audit_events`. No Sentry (paid after quota). No Mixpanel.

---

## 21. Development roadmap (staged, compressed)

Do not treat 13 phases as 13 weeks. Phases 1–9 are **one** vertical slice.

| Phase | Deliver | Done when |
|---|---|---|
| 1 | Repo, env, FastAPI health, Supabase tables, RLS | `GET /health` + can insert a project as a user |
| 2 | PDF/DOCX/TXT extract | Northstar PDF/text round-trips |
| 3–4 | Scope extract + edit UI | You can fix a wrong exclusion by hand |
| 5–8 | Analyze: rules + Groq + validator + money | Five Northstar tests green |
| 9 | Reply + change-order HTML/PDF | Printable CO |
| 10 | Audit + history | Approve shows in history |
| 11 | Precedent query box | Similar request lists Northstar loyalty |
| 12 | Project overview numbers | At-risk / recovered from approved COs |
| 13 | Optional Streamlit Cloud Northstar demo | Public URL, sample data only |

**Stop after the vertical slice and talk to humans.** Integrations are a different quarter.

---

## 22. Demo data (Northstar)

Use the existing Northstar SOW (Shopify Plus, $48,000, $165/h blended, 10 weeks). Seed it.

| # | Request | Expected class | Hours | Price @ $165 |
|---|---|---|---|---|
| 1 | “Can you also add loyalty points?” | OUT_OF_SCOPE | 40 | $6,600 |
| 2 | “Can you sync orders to NetSuite?” | OUT_OF_SCOPE | 64 | $10,560 |
| 3 | “Can you add wholesale login?” | OUT_OF_SCOPE | 80 | $13,200 |
| 4 | “We originally agreed on 400 SKUs but now need 620.” | QUANTITY_OVERRUN | (engine) | $2,970 |
| 5 | “The Add to Cart button doesn't work in Safari.” | BUG_OR_DEFECT | 0 | $0 |

If Groq disagrees with a rule that has hard evidence, **the rule wins**, Groq’s text can still explain.

---

## 23. Failure handling

| Failure | Behavior |
|---|---|
| Unreadable / scanned PDF | Stop. Ask paste. No Groq. |
| Incomplete SOW | Extract what exists; flag missing rate/exclusions. |
| Conflicting clauses | NEEDS_HUMAN_REVIEW |
| Ambiguous request | AMBIGUOUS or NEEDS_HUMAN_REVIEW |
| Missing rate | Classify; block dollar figure |
| Missing hours from model | Use rule default or force human |
| Groq 5xx / timeout | Rules-only + banner |
| Groq 429 | Exponential backoff once, then rules-only |
| Malformed JSON | Retry once with repair prompt; then fail visible |
| Hallucinated evidence | Drop; maybe force review |
| DB down / paused | Clear error: “Database paused — open Supabase and restore” |
| Duplicate paste | Show previous analysis, don’t rebill Groq |
| Unsupported type | `.xlsx` etc. rejected |

Never silent fail. Never show a dollar amount from the model’s mouth.

---

## 24. Future roadmap (after the wedge works)

1. Slack paste helper (still human-initiated).
2. Jira/Linear issue paste via URL if free APIs allow — not OAuth theatre.
3. pgvector if FTS misses real customer language.
4. Gmail/Slack monitors — only with explicit OAuth and a lawyer-friendly data note.
5. QuickBooks/Xero **after** people ask to invoice from a CO.
6. E-sign — last. PDF + email is enough for a long time.
7. Enterprise SSO, SOC2 — when a deal requires it, not before.

---

## 25. Monetization (later)

Do not implement billing in the MVP.

When you have evidence of value:

- Do not start at $19 unless you only want freelancers.
- Anchor to recovered CO value.
- Re-read competitor prices the week you charge (Ignition, Productive, indie ScopeLock).
- Pakistan-origin, USD invoices via Stripe/Paddle/Lemon Squeezy when you leave $0 — that is post-validation.

Suggested research band, not a decision: **$99–$499/mo** for software houses. Your $19–29 band is a different product.

---

## 26. Product moat

Day 0: none. Be faster and more honest than the clones.  
Day 30: a library of that agency’s corrected scope items.  
Day 90: approved decisions + actual CO prices.  
Day 365: commercial memory no general LLM has.

Protect it with RLS, exports (so they don’t fear lock-in), and not training a public model on their SOWs.

---

## 27. Launch checklist (first 30 days)

- [ ] Read Groq Limits page for **your** org; screenshot it into `docs/limits.md`
- [ ] Create Supabase free project; apply SQL; enable RLS
- [ ] Confirm PyMuPDF vs pypdf license choice
- [ ] Northstar tests green without network (rules + calc)
- [ ] Northstar tests green with Groq
- [ ] Evidence validator tested with a fake clause
- [ ] Settings page explains Groq data flow
- [ ] No customer SOW in a public repo
- [ ] 10 conversations, 5-minute demo script
- [ ] Working name only; no trademark filing yet
- [ ] Search tmsearch.uspto.gov before any public brand spend
- [ ] Kill/continue: 2 real SOWs ingested or stop decorating the UI

---

## 28. Final product judgment

**Build it.** The job is real. The stack you have is enough. The $0 constraint is compatible with an honest MVP if you stay local-first and Groq-stingy.

**Do not build the science-fair version.** No vectors, no agents, no Slack firehose, no fake SOC2, no $19 price, no RaoGuard trademark spend.

**Do build the boring version that quotes the SOW and refuses to lie.** That is the whole company.

If you only remember four rules:

1. Rules before Groq.  
2. No citation, no claim.  
3. Python owns the money.  
4. Humans own the decision.

---

*End of blueprint. Companion files: `prompts/`, `.env.example`, `requirements.txt`, `seeds/northstar_sow.txt`.*

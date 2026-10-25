# RaoGuard (working name)

Commercial control layer for software agencies. Paste a signed SOW, drop a client request, get a quoted clause and an estimated change order. **Python owns hours × rate. You approve. Nothing is emailed or invoiced automatically.**

This zip is a local $0 copy: FastAPI + SQLite + a full website. Groq is optional.

## What you need

- Windows 10 (8 GB RAM is enough)
- Python **3.12** or newer — https://www.python.org/downloads/
  - During install, tick **Add python.exe to PATH**
- A browser (Chrome, Edge, Firefox)
- No Docker, no GPU, no paid APIs

## Start it (easiest)

1. Unzip `RaoGuard.zip` to a folder you can find, e.g. `C:\RaoGuard`.
2. Double-click **`run.bat`**.
3. Wait until the window says `Uvicorn running on http://127.0.0.1:8000`.
4. Open **http://127.0.0.1:8000** in your browser.
5. Leave the black window open while you use the site. Close it to stop.

If Windows SmartScreen warns on `run.bat`, choose **More info → Run anyway**. This file only starts Python on your PC.

## Start it by hand (if `run.bat` is blocked)

Open **Command Prompt** in the unzipped folder:

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
set PYTHONPATH=%cd%
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000

## First sign-in

On first start the app creates a local owner on **this machine** (not shown on the public pages):

| | |
|---|---|
| Email | `founder@raoguard.local` |
| Password | `RaoGuard2026` |

1. Open **Sign in**.
2. Enter that email and password.
3. Tick **Terms of Use** and **Privacy Policy**.
4. You land on the **homepage as a signed-in user**.
5. Change the password under **Workspace → Account**.

Northstar Retail (a demo SOW) is already loaded so the analyzer has something real to check.

## What to click after it is running

| Page | What it does |
|---|---|
| **Analyzer** (top nav) | Public dry-run vs the Northstar SOW. Try “Loyalty points”. Then **Print** / **Download**. Does not save. Does not use your Free quota. |
| **About** | Product intro, then founder (Muhammad Abdullah) with LinkedIn and email. |
| **Pricing** | Free trial (limits) then $29 / $59 / $89. This copy does **not** collect payment. |
| **Workspace** | Dashboard: recovered $6,600, at-risk extras, Northstar project. |
| **Analyzer** (inside a project) | Paste a real request. Approve / reject. **Invoice / change order** and **Print / download**. |
| **Reports** (project sidebar) | Commercial report. Print or download. |
| **Change orders** | Draft COs. Print / download like an invoice. Nothing is sent. |
| Corner **R** | Small assistant. Hover to expand. Signed-in it can talk about this workspace’s facts, not full SOW text. |

## Plans (enforced on this machine)

- **Free (trial)** — 1 live project, 20 SOW checks, 1 seat. Full loop still works.
- **Starter $29** — 3 projects, 100 checks/month, 3 seats.
- **Studio $59** — unlimited.
- **Agency $89** — unlimited + white-label change orders.

No Stripe. Picking a paid plan in Settings only lifts the caps so you can evaluate them. A real invoice would be by hand.

## Optional: Groq (chat + prose)

The product works **without** a key (rules-only). To turn Groq on later:

1. Create a free key at https://console.groq.com
2. Open the `.env` file in this folder
3. Set `GROQ_API_KEY=your_key_here`
4. Restart `run.bat`

Do not paste a fake key. Limits are on your Groq account’s Limits page.

## Stop / start again

- Stop: close the `run.bat` window or Ctrl+C.
- Start again: double-click `run.bat`. Your SQLite file `data\raoguard.db` is kept.

## Checks you can run

```
.venv\Scripts\activate
set PYTHONPATH=%cd%
python -m pytest tests -q
```

Expect **19 passed**.

## Honest limits of this copy

- Not legal advice. Estimates only.
- Not e-sign, not email, not accounting, not SSO.
- Nothing is auto-sent to a client.
- Working name, not a filed trademark. GitHub already has `fahim0-3/RAGuard` (unrelated RAG project).
- Do not upload real client SOWs to a public URL.

## Contact

Muhammad Abdullah — Founder · AI Engineer · Data Scientist  
Email: raoengr1080@gmail.com  
LinkedIn: https://www.linkedin.com/in/raoabdullah1080/

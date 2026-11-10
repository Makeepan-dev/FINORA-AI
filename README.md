# FINORA — AI-Powered Everyday Money-Saving Assistant
**Financial Intelligence Network for Optimization, Reasoning & Automation**  
*PayPal AI Hackathon 2026 Submission*

---

## 1. Product Identity & Central Promise

**FINORA** is an AI-powered personal financial intelligence assistant designed to help individuals understand where their money goes, detect unnecessary expenditure, discover cheaper local alternatives, and make smarter everyday financial decisions.

> **Central Promise:** *"FINORA helps people understand where their money goes, identify unnecessary expenditure, discover cheaper alternatives and make smarter everyday financial decisions."*

Unlike disconnected chatbots or static budgeting apps, FINORA connects **persisted transaction records**, **deterministic Decimal financial math**, **subscription utilization telemetry**, **permission-based GPS local discovery**, and **user-approved PayPal Sandbox actions** into a unified money-saving workflow.

---

## 2. Five Core Hackathon MVP Capabilities Implemented

### Feature 1 — Smart Personal Finance Tracker (`/api/v1/transactions`)
- **SQLite-Persisted Ledger:** Stores income, expenses, transfers, and refunds in SQLite (`transactions` table).
- **CSV Import & Validation Pipeline:** Upload or paste bank CSV statements, preview parsed rows, validate dates and amounts, reject invalid entries, and automatically skip duplicate imports.
- **Manual Entry Fallback:** Log cash or ad-hoc transactions directly from the UI.
- **Strict Accounting Rules:**
  - Internal account transfers (`type = transfer`) are strictly excluded from income and expense totals.
  - All financial calculations use Python `Decimal` precision to eliminate binary floating-point drift.
  - **Remaining Available Money** is explicitly defined and displayed as `Total Income ($) - Total Expenses ($)`.

### Feature 2 — Knowledge-First AI Financial Advisor (`/api/v1/guardian`)
- **7-Stage Intelligence Pipeline:** Processes user questions through Intent Recognition → Internal Knowledge Base Retrieval (16 rules) → Deterministic Formula Execution (44 formulas) → Sufficiency Scoring → Google Gemini Escalation (only when needed) → Numerical Grounding Verification.
- **Grounded in Actual Records:** Answers key everyday questions using the user's persisted ledger:
  - *"Help me save $100 this month"*
  - *"How much did I spend this month and where is most of my money going?"*
  - *"Can I afford to buy a $1200 laptop?"*
  - *"Perform a complete subscription audit"*
- **Deterministic Fallback:** If external AI APIs are offline or rate-limited, FINORA falls back transparently to its deterministic calculation engine without fabricating responses.

### Feature 3 — GPS & Nearby Places Money-Saving Intelligence (`/api/v1/location`)
- **Permission-First Geolocation:** Supports one-time browser GPS (`navigator.geolocation.getCurrentPosition`), manual city/coordinate selection, and 1-click permission revocation. Never performs continuous background tracking.
- **Transport-Adjusted Price Comparison:** Evaluates local alternatives for Gyms, Supermarkets, and Fuel Stations by subtracting estimated round-trip transport cost (`distance_miles * 2 * trips * $0.67/mile`) from gross savings.
- **Live OpenStreetMap Overpass Discovery:** Queries real-world supermarkets, gyms, and fuel stations near permitted coordinates via OpenStreetMap Overpass API, explicitly labelling price status as `"Unavailable (Live OSM Listing)"` rather than fabricating prices.

### Feature 4 — Subscription & Financial Waste Detector (`/api/v1/optimization`, `/api/v1/location/gym-scenario`)
- **Recurring Expense Detection:** Identifies recurring commitments, monthly/annual cost equivalents, and dormancy periods.
- **Cross-Module Gym Demonstration Scenario:**
  - Detects a **$45.00/month** gym membership with **6 consecutive monthly payments** ($270 total) and **0 recorded visits in the last 45 days**.
  - Discovers a nearby alternative (**Planet Fitness Classic**, 0.8 miles away) at **$20.00/month** ($25/month or $300/year gross difference; +$20.71/month net after transport).
  - **Honest Uncertainty Disclosure:** Explicitly explains what location data was available, notes that visits while GPS was off or to partner branches are not captured, and asks: *"Your gym membership may be underutilized based on the available records. A nearby alternative appears to cost less. Would you like to compare the options?"*
- **User Permission Gate:** Never automatically cancels or modifies any subscription.

### Feature 5 — Daily Money-Saving Intelligence (`/api/v1/savings`)
- **Multi-Factor Opportunity Ranking:** Ranks recommendations using a composite score combining **Financial Impact (35%)**, **Evidence Quality (30%)**, **Confidence (20%)**, and **Low Effort (15%)** — never ranking by theoretical maximum savings alone.
- **Potential vs. Realized Savings Distinction:** Strictly separates **Potential Savings** (estimates awaiting review), **Accepted Actions** (user-approved, pending next billing cycle), and **Verified Realized Savings** (confirmed by actual ledger refunds or lower bills).

---

## 3. PayPal Developer Platform Integration (`/api/v1/payments`)

- **Official PayPal Sandbox OAuth 2.0 & Orders v2 API:** Authenticates with PayPal Sandbox (`/v1/oauth2/token`) and creates server-validated orders (`/v2/checkout/orders`).
- **User-Approved Money-Saving Switch Demonstration:** When a user accepts a money-saving switch recommendation (e.g., switching to the $20/mo Planet Fitness pass or $4.99/mo StrataVault 200GB plan), they can execute an isolated, explicitly user-approved PayPal Sandbox checkout and capture flow.
- **Security Controls:**
  - Server-side price lookup from authoritative catalog (`SAVINGS_SWITCH_CATALOG` & product catalog); never trusts client-submitted amounts.
  - Per-order `asyncio.Lock` + SQLite `CapturedPayment` check prevents concurrent duplicate captures.
  - Client secrets and Bearer tokens are stored exclusively in backend `.env` and never exposed to the frontend.

---

## 4. Explicit Distinction: Live Data vs. Demo Data

| Data / Integration Layer | Live / Persisted Capability | Demo / Benchmark Capability |
| :--- | :--- | :--- |
| **Transactions & CSV Import** | **Live SQLite Persistence**: User CSV imports and manual entries persist across restarts and immediately update summaries. | Initial seeded records are marked with `is_demo: true` (`Demo Mode Data` badge in UI). |
| **AI Financial Advisor** | **Live Deterministic Engine + Google Gemini API**: Real calculations and live Gemini API synthesis when configured. | Transparent fallback to `deterministic_financial_engine` if API key is absent or quota-limited. |
| **Geolocation & Places** | **Live Browser Geolocation + Live OpenStreetMap Overpass API** for nearby place discovery. | Curated benchmark rate cards are explicitly badged as `Verified Demo Rate Card` or `Estimated Basket Price`. |
| **PayPal Integration** | **Live PayPal Sandbox API** (`/v1/oauth2/token`, `/v2/checkout/orders`, `/capture`). | Sandbox-only; zero real-money transactions. |

---

## 5. Setup & Running Instructions

### Prerequisites
- **Python 3.11+** (Backend virtual environment in `backend/.venv`)
- **Node.js 18+** (Frontend in `frontend/`)

### Environment Variables (`.env`)
Copy `.env.example` to `.env` (and `backend/.env`) and configure:
```env
AI_PRIMARY_PROVIDER=gemini
AI_MODEL=gemini-flash-lite-latest
GEMINI_API_KEY=your_gemini_api_key_here

PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_paypal_sandbox_client_secret
PAYPAL_API_BASE=https://api.sandbox.paypal.com

DATABASE_URL=sqlite:///./finora.db
```

### 1. Start the Backend Server
```powershell
cd D:\FINORA
$env:PYTHONPATH="D:\FINORA\backend"
.\backend\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

### 2. Start the Frontend Application
```powershell
cd D:\FINORA\frontend
npm install
npm run dev
```

### 3. Run the Automated Test Suite (124 Passing Tests)
```powershell
cd D:\FINORA
$env:PYTHONPATH="D:\FINORA\backend"
.\backend\.venv\Scripts\python.exe -m pytest backend/tests -q
```

---

## 6. Hackathon Demonstration Walkthrough ("Help me save $100 this month")

1. **Open Overview & Transactions (`Transactions & CSV` tab):**
   - Click **"Import CSV Transactions"** → Click **"1. Preview & Validate Records"** to see valid rows, duplicate detection, and transfer exclusion → Click **"2. Confirm Import"**.
   - Observe the updated **Remaining Available Money** (`Income − Expenses`).
2. **Ask the AI Advisor (`AI Advisor & Subscriptions` tab):**
   - Click the quick prompt **"Help me save $100 this month"**.
   - Review the grounded breakdown showing **$115.77+/month** in actionable savings across the Gym membership ($25/mo), Food Delivery 20% reduction ($40.77/mo), and dormant SaaS downgrades ($50/mo).
3. **Inspect GPS & Gym Scenario (`Nearby Savings (GPS)` tab):**
   - Click **"Use Browser GPS (One-Time)"** or set manual coordinates.
   - Review the **Cross-Module Gym Scenario** ($45/mo → $20/mo Planet Fitness Classic, 0.8 mi away) with full evidence caveats and transport-cost calculations.
4. **Accept Recommendations & Execute PayPal Sandbox Action (`Money-Saving Insights` tab):**
   - Review the **Potential vs. Verified Realized Savings** banner.
   - Click **"Accept Recommendation"** on top ranked opportunities, then click **"Execute Switch in PayPal Sandbox"** to create and capture the server-verified Sandbox order.

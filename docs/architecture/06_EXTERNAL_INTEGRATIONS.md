# FINORA — External Integrations & Third-Party Services
## Document 06: Third-Party APIs, Authentication & Integration Status

---

## 1. External Integration Overview

FINORA interfaces with external services primarily for **live AI reasoning** and **financial checkout payments**, while providing robust simulation fallbacks when external credentials are absent or network connectivity is degraded:

```
+---------------------------------------------------------------------------------------------------------+
|                                    FINORA EXTERNAL INTEGRATIONS MAP                                     |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
            +--------------------+-------------------+--------------------+--------------------+
            |                    |                                        |                    |
            v                    v                                        v                    v
+-----------------------+ +-----------------------------+ +---------------------------+ +-----------------+
|     GOOGLE GEMINI     | |      PAYPAL REST API        | |  GROQ & OPENROUTER STUBS  | |  OPEN BANKING   |
| - Generative Language | | - Sandbox Environment       | | - Alternative LLM stubs   | | - Plaid Core    |
| - v1beta API          | | - OAuth 2.0 Client Creds    | | - Configurable in .env    | | - TrueLayer UK  |
| - Model: Flash-Lite   | | - Orders v2 & Capture       | | - Revert to deterministic | | - In-Memory Sim |
| - STATUS: LIVE        | | - STATUS: LIVE / SIMULATED  | | - STATUS: STUBS           | | - STATUS: MOCK  |
+-----------------------+ +-----------------------------+ +---------------------------+ +-----------------+
```

---

## 2. Integration 1: Google Gemini Generative Language API

- **Provider:** Google DeepMind / Google Cloud AI.
- **Purpose:** Conversational reasoning for complex, open-ended personal finance queries, trade-off evaluations, and circumstances changes.
- **Codebase Location:** [`backend/app/services/ai_service.py`](file:///d:/FINORA/backend/app/services/ai_service.py) (`_call_gemini_free()`).
- **Base Endpoint:** `https://generativelanguage.googleapis.com/v1beta`
- **Authentication:** Query parameter API key (`?key=${GEMINI_API_KEY}`). Key is kept strictly on the backend and never exposed to the frontend.
- **Endpoints Interfaced:**
  - `POST /v1beta/models/{model_name}:generateContent`
  - Candidate models tried in sequence: `gemini-flash-lite-latest`, `gemini-flash-latest`.
- **Payload & Data Exchanged:**
  - Inbound payload: Injected user prompt, user financial profile (income, expenses, cash flow), and verified active subscription list.
  - Outbound response: Structured JSON conforming to `GuardianStructuredResponse` (`factual_analysis`, `classifications`, `estimates`, `recommendations`, `unknowns`).
- **Error Handling & Resilience:**
  - **HTTP 503 Spikes:** Automatically pauses 0.5s and retries once on high-demand spikes.
  - **HTTP 429 Quota Exhaustion:** Transparently catches quota limits and falls back to `rule_based_conversational_v2`.
  - **Timeout:** 15.0-second timeout limit via HTTPX. On timeout, sets `is_fallback: True` and reverts to deterministic reasoning.
- **Current Status:** **LIVE & VERIFIED (HTTP 200)**.

---

## 3. Integration 2: PayPal REST Sandbox Payment Network

- **Provider:** PayPal Developer Platform.
- **Purpose:** Secure personal checkout, merchant landed cost authorization, buyer approval workflow, and server-side payment capture.
- **Codebase Location:** [`backend/app/services/paypal_service.py`](file:///d:/FINORA/backend/app/services/paypal_service.py) and [`backend/app/api/payments.py`](file:///d:/FINORA/backend/app/api/payments.py).
- **Base Endpoint:** `https://api-m.sandbox.paypal.com`
- **Authentication:** OAuth 2.0 Client Credentials Grant (`Basic base64(client_id:client_secret)`).
- **Endpoints Interfaced:**
  - `POST /v1/oauth2/token` — Obtains and caches short-lived Bearer access tokens (`expires_in: 3600`).
  - `POST /v2/checkout/orders` — Creates order with backend-calculated landed total (`intent: "CAPTURE"`).
  - `POST /v2/checkout/orders/{order_id}/capture` — Captures funds server-side.
  - Callback Webhooks/Redirects: `/api/payments/return` and `/api/payments/cancel`.
- **Payload & Data Exchanged:**
  - Order Creation: Item name, quantity, unit price, shipping price, currency (`USD`), and application context (`return_url`, `cancel_url`).
  - Order Capture: Order ID, idempotency key to prevent double-capture.
- **Error Handling & Dual Mode:**
  - **Live Sandbox Mode:** Active when `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` are configured in `.env`.
  - **Integrated Simulation Mode:** When credentials are empty, PayPal service runs seamlessly in simulation mode, generating deterministic synthetic order IDs (`ORD-YYYYMMDD-XXXX`), approval URLs (`https://www.sandbox.paypal.com/checkoutnow?token=...`), and recording captures in SQLite.
- **Current Status:** **DUAL ARCHITECTURE (LIVE SANDBOX READY + VERIFIED SIMULATION)**.

---

## 4. Integration 3 & 4: Groq & OpenRouter Free-Tier Stubs

- **Providers:** Groq Cloud Inc. / OpenRouter Inc.
- **Purpose:** Optional backup free-tier AI providers.
- **Codebase Location:** [`backend/app/services/ai_service.py`](file:///d:/FINORA/backend/app/services/ai_service.py) (`_call_groq_free()`, `_call_openrouter_free()`).
- **Base Endpoints:**
  - Groq: `https://api.groq.com/openai/v1/chat/completions` (Model: `llama-3.3-70b-versatile`).
  - OpenRouter: `https://openrouter.ai/api/v1/chat/completions` (Model: `meta-llama/llama-3.3-70b-instruct:free`).
- **Authentication:** HTTP Bearer token (`Authorization: Bearer <API_KEY>`).
- **Current Status:** **CONFIGURED STUBS**. If credentials are empty or API calls fail, the system falls back to the deterministic engine.

---

## 5. Integration 5: Open Banking & Institution Sync (Plaid / TrueLayer)

- **Providers:** Plaid Technologies Inc. / TrueLayer Ltd.
- **Purpose:** Open Banking connectivity for personal checking, savings, and credit card accounts.
- **Codebase Location:** [`backend/app/services/sync_service.py`](file:///d:/FINORA/backend/app/services/sync_service.py) and [`backend/app/api/connections.py`](file:///d:/FINORA/backend/app/api/connections.py).
- **Authentication:** Simulated OAuth 2.0 token grant.
- **Supported Institutions in Directory:**
  1. `inst_paypal`: PayPal Commerce & Wallet (PayPal Direct).
  2. `inst_chase`: Chase Bank (JPMorgan Chase via Plaid).
  3. `inst_boa`: Bank of America (via Plaid).
  4. `inst_fidelity`: Fidelity Investments (via Plaid).
  5. `inst_barclays`: Barclays UK Open Banking (via TrueLayer UK).
- **Current Status:** **MOCK / SIMULATED**. The integration simulates realistic multi-institution bank streaming, connection health monitoring, manual sync triggers, and permission revocation, writing state changes to `connected_accounts` and `sync_logs` in SQLite.

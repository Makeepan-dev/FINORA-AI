# FINORA — Backend Architecture Mapping
## Document 03: Server Initialization, API Routers, Services & Request Lifecycle

---

## 1. Backend Architecture Topology

FINORA's backend is implemented in **Python 3.12** using the asynchronous **FastAPI** web framework. It follows a layered service-oriented architecture:

```
+---------------------------------------------------------------------------------------------------+
|                                      CLIENT HTTP REQUEST                                          |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 FASTAPI APPLICATION (app/main.py)                                 |
|  - CORSMiddleware (allow_origins=["*"], credentials=True)                                         |
|  - Root Health & Status Handlers: GET /, GET /health                                              |
|  - Database Schema Auto-Initialization: Base.metadata.create_all(bind=engine)                     |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 API CONTROLLERS & ROUTERS (app/api/)                              |
|  - demo_data.py    - analytics.py    - guardian.py     - shopping.py     - payments.py            |
|  - settings.py     - income.py       - connections.py  - knowledge.py    - optimization.py        |
|  - location.py     - automation.py                                                                |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                    SERVICE & AGENT LAYER                                          |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
|  |       AI AGENTS           |  |      BUSINESS SERVICES    |  |     KNOWLEDGE ORCHESTRATOR    |  |
|  | - FinancialGuardianAgent  |  | - AnalyticsService        |  | - 7-Stage Pipeline            |  |
|  | - ShoppingAgent           |  | - IncomeIntelligenceSvc   |  | - Intent Classification       |  |
|  |                           |  | - FinancialSyncService    |  | - Sufficiency Assessment      |  |
|  |                           |  | - PayPalService           |  | - Selective Escalation        |  |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
|  |       DETERMINISTIC ALGORITHMS (Decimal)         |          INTERNAL KNOWLEDGE BASE            |
|  | - Loan amortization, break-even, margins, TCO    | - 5 structured personal/business domains    |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                         v                                                 v
+-------------------------------------------------+     +-------------------------------------------+
|          IN-MEMORY DATA BANK (app/demo_data/)   |     |       RELATIONAL DB (app/database/)       |
|  - DatasetManager (seed=42)                     |     |  - SQLite (finora.db via SQLAlchemy)      |
|  - 3 Personas, 13 Accounts, 347 Transactions    |     |  - captured_payments, paypal_orders       |
|  - 36 Merchants, 105 Products, 12 Subscriptions |     |  - connected_accounts, sync_logs          |
|  - 20 Test Scenarios, Referential Integrity     |     |  - user_preferences                       |
+-------------------------------------------------+     +-------------------------------------------+
```

---

## 2. Server Initialization & Configuration

### 2.1 Entry Point Execution
1. Uvicorn runs `app.main:app` from the `backend/` working directory.
2. `backend/app/main.py` executes:
   - Imports `settings` from `app.core.config`.
   - Executes `Base.metadata.create_all(bind=engine)` via SQLAlchemy to ensure tables exist in `finora.db`.
   - Creates the `FastAPI` instance.
   - Registers CORS middleware.
   - Registers all 12 routers with prefix `/api`.
   - Defines root `/` and `/health` endpoints.

### 2.2 Environment & Settings Resolution (`app/core/config.py`)
- Employs Pydantic `BaseSettings` (`SettingsConfigDict`).
- Candidate `.env` resolution paths:
  1. `backend/.env`
  2. `FINORA/.env`
  3. Current directory `.env`
- Exposes `reload_settings()` allowing runtime refresh without server restarts.
- Enforces strict zero-paid guardrails: `ALLOW_PAID_MODELS=False`, `MAX_API_SPEND_USD=0.0`.

---

## 3. Complete API Router Inventory

| Router Prefix | Source File | Endpoints | Responsibilities |
| :--- | :--- | :--- | :--- |
| `/api/analytics` | `api/analytics.py` | `GET /dashboard` | Returns aggregated portfolio telemetry: cash balances, cash flow, category budgets, monthly trends. |
| `/api/guardian` | `api/guardian.py` | `POST /chat`, `GET /audit-subscriptions` | Primary conversational AI interface; returns factual analysis, recommendations, and subscription audits. |
| `/api/shopping` | `api/shopping.py` | `GET /products`, `POST /evaluate-budget`, `POST /compare` | Searches catalog, calculates landed costs, checks remaining monthly category budgets, evaluates 3-year TCO. |
| `/api/payments` | `api/payments.py` | `POST /create-order`, `POST /capture-order`, `POST /test-connection`, `GET /history`, `GET /config-status`, `GET /return`, `GET /cancel` | PayPal Sandbox order creation, buyer approval URL generation, capture, anti-duplicate checks, and connection tests. |
| `/api/income` | `api/income.py` | `GET /intelligence` | Ingests cleared income transactions, classifies income streams, calculates volatility, and models expected payments. |
| `/api/connections` | `api/connections.py`| `GET /`, `GET /institutions`, `POST /connect`, `POST /{id}/sync`, `POST /{id}/revoke`, `GET /history` | Manages Open Banking and PayPal connections, triggers transaction syncs, logs sync history. |
| `/api/demo-data` | `api/demo_data.py` | `GET /status`, `GET /users`, `GET /accounts`, `GET /transactions`, `GET /subscriptions`, `GET /products`, `GET /scenarios`, `POST /generate`, `POST /reset`, `POST /load-scenario`, `POST /validate`, `GET /export/json`, `GET /export/csv` | Controls the deterministic synthetic financial data bank, scenario activation, mathematical validation, and serialization. |
| `/api/settings` | `api/settings.py` | `GET /status` | Reports active AI provider, model, key presence, PayPal status, and persona profiles. |
| `/api/knowledge` | `api/knowledge.py` | `GET /inventory`, `GET /search`, `GET /{topic}` | Structured financial knowledge inspection across 5 domains. |
| `/api/optimization`| `api/optimization.py`| `GET /audit`, `POST /compare` | Executes the 14-step autonomous expense optimization workflow; compares recurring alternatives. |
| `/api/location` | `api/location.py` | `GET /status`, `POST /permission`, `GET /nearby` | Permission-based geolocation service and Haversine business discovery. |
| `/api/automation` | `api/automation.py` | `GET /rules`, `GET /history`, `POST /rules/{id}/toggle` | Event-driven and scheduled financial automation triggers and execution logs. |

---

## 4. Service & Agent Layer Breakdown

### 4.1 AnalyticsService (`app/services/analytics_service.py`)
- **Core Function:** Aggregates portfolio figures from `DatasetManager`.
- **Calculations:**
  - `total_balance`: Sum of checking, savings, and digital wallet balances.
  - `monthly_income` & `monthly_expenses`: Reconciled totals for target month (`2026-10`).
  - `monthly_trends`: 6-month historical cash flow array (`2026-05` to `2026-10`).
  - `budget_progress`: Computes percentage used per category and status (`normal`, `warning`, `exceeded`).
  - `get_subscription_audit_facts`: Audits all active subscriptions, calculates cost-per-use, evaluates utilization telemetry, and identifies potential savings cushions.

### 4.2 IncomeIntelligenceService (`app/services/income_service.py`)
- **Core Function:** Ingests cleared income deposits and structures multi-stream analytics.
- **Invariant Rule:** Contractual expected income (e.g. pending client invoices) is strictly separated from cash on hand.
- **Metrics:** Stream classification (Salary, Freelance, Dividends), historical monthly totals, and irregularity standard deviation.

### 4.3 FinancialSyncService (`app/services/sync_service.py`)
- **Core Function:** Simulates Open Banking (Plaid, TrueLayer) and PayPal Direct connections.
- **Persistence:** Writes to SQLite tables `connected_accounts` and `sync_logs`.
- **Operations:** Connects new institutions, triggers simulated record synchronization, and handles permission revocation.

### 4.4 PayPalService (`app/services/paypal_service.py`)
- **Core Function:** Orchestrates PayPal payments in both live Sandbox mode and integrated simulation mode.
- **Security:** Computes order totals on backend; caches OAuth 2.0 access tokens; checks duplicate captures using idempotency keys.
- **Endpoints Interfaced:**
  - `POST /v1/oauth2/token`
  - `POST /v2/checkout/orders`
  - `POST /v2/checkout/orders/{id}/capture`

### 4.5 KnowledgeOrchestrator (`app/services/knowledge_orchestrator.py`)
- **Core Function:** 7-stage query processing pipeline.
- **Execution:**
  1. Classifies intent (`SUBSCRIPTION_TOTALS`, `LOAN_AMORTIZATION`, `BREAK_EVEN`, `PROFIT_MARGINS`, `COMMERCE_TCO`, `GYM_OPTIMIZATION`, `KNOWLEDGE_LOOKUP`, or `GENERAL_OR_AI_ESCALATION`).
  2. Ingests structured domain knowledge from `KnowledgeRepository`.
  3. Executes deterministic calculations using `app/algorithms/`.
  4. Determines sufficiency. If sufficient, answers immediately with 0 AI API calls.
  5. If insufficient or open-ended, escalates to `AIService` with ground-truth telemetry injected.

### 4.6 FinancialGuardianAgent (`app/agents/financial_guardian.py`)
- **Core Function:** Primary user-facing agent. Combines real-time analytics snapshot with `KnowledgeOrchestrator.process_question()`.

### 4.7 ShoppingAgent (`app/agents/shopping_agent.py`)
- **Core Function:** Evaluates product purchases against monthly category budgets, computes 3-year TCO, and ranks products by value score.

---

## 5. Complete Request Lifecycle Walkthrough

```
[User Browser]
       │
       ▼  HTTP POST /api/guardian/chat { prompt: "What is my total subscription spending?", user_id: "usr_alex_chen" }
[FastAPI CORSMiddleware]
       │ (Validates CORS headers)
       ▼
[app/api/guardian.py: chat_with_guardian()]
       │
       ▼
[app/agents/financial_guardian.py: FinancialGuardianAgent.chat()]
       │
       ├─► Calls AnalyticsService.get_user_dashboard_metrics("usr_alex_chen")
       │     └─ Queries DatasetManager for accounts, transactions, budgets
       │
       ├─► Calls AnalyticsService.get_subscription_audit_facts("usr_alex_chen")
       │     └─ Queries DatasetManager for subscriptions, telemetry, potential savings
       │
       ▼
[app/services/knowledge_orchestrator.py: KnowledgeOrchestrator.process_question()]
       │
       ├─► Stage 1: Classifies Intent -> "SUBSCRIPTION_TOTALS"
       ├─► Stage 2: Queries KnowledgeRepository for matching entries
       ├─► Stage 3: Evaluates facts (total_mo: $291.97, total_yr: $3,503.64, 7 commitments)
       ├─► Stage 4: Evaluates Knowledge Sufficiency -> SUFFICIENT
       │
       ▼  (Decision: No AI escalation needed)
[Formulates Verified Response]
       │ - provider: "deterministic_financial_engine"
       │ - model: "internal_knowledge_pipeline_v1"
       │ - escalated_to_ai: False
       │ - knowledge_sufficiency: "SUFFICIENT"
       │ - factual_analysis: "You have 7 active recurring commitments totaling $291.97/mo..."
       │
       ▼
[HTTP 200 Response to Client]
```

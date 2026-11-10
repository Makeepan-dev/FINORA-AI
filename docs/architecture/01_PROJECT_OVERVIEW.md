# FINORA — Architectural Reconnaissance & System Overview
## Document 01: Project Overview & Scope

---

## 1. System Identity & Mission

**FINORA** stands for **Financial Intelligence Network for Optimization, Reasoning & Automation**.

Built initially as a prototype for the **PayPal AI Hackathon 2026**, FINORA is an **AI-powered personal financial and commerce intelligence assistant**. Its fundamental mission is to move AI beyond answering generic financial questions toward helping individual users make informed personal financial decisions, optimize recurring commitments, make value-grounded purchases, and execute user-approved payments via PayPal.

### Scope & Boundaries
- **Core Domain:** Personal finance and consumer commerce for individual users, households, and independent freelancers.
- **Key Capabilities:**
  - Personal multi-account banking and wallet tracking (checking, savings, credit cards, digital wallets).
  - Income and expense analysis with multi-stream classification and volatility detection.
  - Granular transaction history with deterministic category allocation.
  - Monthly category budgeting, savings goals, and overrun alerting.
  - Recurring subscription auditing, utilization telemetry analysis, and fee optimization.
  - Commerce intelligence: Total Cost of Ownership (TCO), cost-per-use, and quality/warranty value scoring.
  - Autonomous expense optimization with permission-based local business discovery.
  - User-authorized payments and order lifecycle management via the official PayPal Sandbox REST API.
  - Knowledge-first AI reasoning combining internal structured finance knowledge with zero-cost Google Gemini escalation.
- **Explicit Anti-Scope:**
  - FINORA is **not** an enterprise ERP, corporate CFO platform, business payroll processor, corporate double-entry accounting software, or multi-tenant B2B platform.
  - While legacy synthetic data generators contain two sample businesses and invoices for edge testing, the application's runtime product experience is strictly tailored to personal and freelance individuals.

---

## 2. Technology Stack & Runtime Environment

| Tier / Subsystem | Technology | Version | Purpose & Architecture |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | React | `18.3.1` | Component-based UI with hooks and functional components |
| **Language (Frontend)** | TypeScript | `~5.6.2` | Strong static typing for financial models, API contracts, and UI state |
| **Build Tool & Bundler**| Vite | `5.4.10` | Fast development server and production Rollup-based asset compilation |
| **Styling & CSS** | Tailwind CSS | `3.4.15` | Modern dark-fintech utility styling (`#0B0F19` slate-blue foundation) |
| **Data Visualization** | Recharts | `2.13.3` | SVG-based responsive bar charts, pie charts, and monthly trend visualizations |
| **Iconography** | Lucide React | `0.460.0` | Clean, accessible vector icons for fintech navigation and indicators |
| **Backend Framework** | FastAPI | `0.115.0+` | High-performance asynchronous Python web API with automatic OpenAPI docs |
| **Language (Backend)** | Python | `3.12.7` | Backend services, agents, mathematical algorithms, and data structures |
| **Monetary Math** | Python `Decimal` | Standard Lib | Arbitrary-precision decimal arithmetic; zero IEEE-754 float drift |
| **ORM & DB Access** | SQLAlchemy | `2.0+` | Relational persistence for stateful orders, payments, accounts, sync logs |
| **Local Database** | SQLite | `3.x` | Embedded relational store (`finora.db`) for orders, payments, sync history |
| **Data Validation** | Pydantic v2 | `2.x` | Declarative schemas, type validation, and serialization (`model_dump()`) |
| **HTTP Client** | HTTPX | `0.27+` | Asynchronous HTTP requests for PayPal Sandbox and Google Gemini REST APIs |
| **AI Integration** | Google Gemini REST | Free Tier | Context-grounded conversational reasoning via `gemini-flash-lite-latest` |
| **Payment Network** | PayPal REST API | v1/v2 Sandbox | OAuth 2.0 client credentials, `/v2/checkout/orders` create and capture |
| **Testing Framework** | Pytest & pytest-asyncio | `9.2.0` | Asynchronous test execution across 55 comprehensive test cases |

---

## 3. High-Level Repository Structure

The FINORA repository is organized into a clean root-level separation between the frontend client, the backend server, and system documentation:

```
D:\FINORA\
├── .env                         # Root environment configuration (API keys, ports)
├── .env.example                 # Documented template for configuration variables
├── README.md                    # Primary repository overview and startup guide
├── LICENSE                      # MIT License declaration
├── backend\                     # Python FastAPI application root
│   ├── .env                     # Backend local environment overrides
│   ├── finora.db                # SQLite database file (payments, orders, connections)
│   ├── requirements.txt         # Python package dependencies
│   ├── app\                     # Core application source package
│   │   ├── main.py              # Application entry point, CORS, and route registration
│   │   ├── core\                # Application settings and environment resolution
│   │   ├── database\            # SQLAlchemy engine, session factory, and get_db()
│   │   ├── models\              # SQLAlchemy declarative ORM models
│   │   ├── schemas\             # Pydantic request/response validation schemas
│   │   ├── api\                 # API route handlers across 12 feature domains
│   │   ├── services\            # Business logic (AI, analytics, income, sync, PayPal)
│   │   ├── agents\              # Specialized agents (Financial Guardian, Shopping)
│   │   ├── algorithms\          # Deterministic Decimal math, loan, margins, TCO
│   │   ├── knowledge\           # Structured knowledge base across 5 financial domains
│   │   ├── location\            # Geolocation permission and business discovery
│   │   ├── optimization\        # 14-step autonomous expense optimization engine
│   │   ├── automation\          # Event-driven and scheduled automation engine
│   │   └── demo_data\           # Deterministic synthetic financial data bank
│   └── tests\                   # Pytest automated test suite (55 test cases)
├── frontend\                    # React TypeScript client application
│   ├── index.html               # Single-page application HTML entry shell
│   ├── package.json             # NPM package manifest and scripts
│   ├── tsconfig.json            # TypeScript compiler configuration
│   ├── vite.config.ts           # Vite bundler configuration with /api proxy
│   ├── tailwind.config.js       # Tailwind CSS theme extension
│   └── src\                     # Client application source code
│       ├── main.tsx             # React DOM root entry point
│       ├── App.tsx              # Root component, state coordination, and tab routing
│       ├── types\               # TypeScript interface and type declarations
│       ├── services\            # Frontend API client library (`api.ts`)
│       ├── components\          # Reusable UI components (Navbar, Sidebar)
│       ├── pages\               # 8 Core application views
│       └── styles\              # Global CSS and Tailwind directives
└── docs\                        # Comprehensive architectural documentation
    ├── AI_PROVIDER_SETUP.md     # Free-tier AI provider guide
    ├── ARCHITECTURE.md          # Architectural pillars and system summary
    ├── DEMO_DATA_BANK.md        # Synthetic data bank design and entity relationships
    ├── PAYPAL_SETUP.md          # PayPal Sandbox configuration and workflow
    ├── TEST_REPORT.md           # Automated verification test results
    └── architecture\            # Comprehensive 11-document architecture audit
```

---

## 4. Application Entry Points

### 4.1 Backend Entry Point
- **File:** [`backend/app/main.py`](file:///d:/FINORA/backend/app/main.py)
- **Lifecycle:**
  1. Executes `Base.metadata.create_all(bind=engine)` to ensure all 5 SQLite tables exist.
  2. Instantiates `FastAPI(title="FINORA", version="1.0.0")`.
  3. Configures `CORSMiddleware` with `allow_origins=["*"]` for local development.
  4. Registers 12 domain routers under prefix `/api`:
     - `demo_data.py`: `/api/demo-data/*`
     - `analytics.py`: `/api/analytics/*`
     - `guardian.py`: `/api/guardian/*`
     - `shopping.py`: `/api/shopping/*`
     - `payments.py`: `/api/payments/*`
     - `settings.py`: `/api/settings/*`
     - `income.py`: `/api/income/*`
     - `connections.py`: `/api/connections/*`
     - `knowledge.py`: `/api/knowledge/*`
     - `optimization.py`: `/api/optimization/*`
     - `location.py`: `/api/location/*`
     - `automation.py`: `/api/automation/*`
  5. Exposes root health endpoints: `GET /` and `GET /health`.
- **Command:** `uvicorn app.main:app --port 8000 --reload` (executed from `backend/`).

### 4.2 Frontend Entry Point
- **Files:** [`frontend/index.html`](file:///d:/FINORA/frontend/index.html) $\rightarrow$ [`frontend/src/main.tsx`](file:///d:/FINORA/frontend/src/main.tsx) $\rightarrow$ [`frontend/src/App.tsx`](file:///d:/FINORA/frontend/src/App.tsx)
- **Lifecycle:**
  1. Browser loads `index.html` referencing `<script type="module" src="/src/main.tsx">`.
  2. `main.tsx` mounts `<App />` into `document.getElementById('root')`.
  3. `App.tsx` initializes state:
     - `currentTab = 'overview'`
     - `activeUserId = 'usr_alex_chen'`
     - `activeScenarioId = 'scen_01_normal_spending'`
  4. `useEffect` triggers `loadDashboard('usr_alex_chen')`, querying `GET /api/analytics/dashboard`.
  5. Renders persistent `<Navbar />` and `<Sidebar />`, conditionally rendering the active view container.
- **Command:** `npm run dev` (running on `http://localhost:5173` with proxy to `http://localhost:8000`).

---

## 5. Major Architectural Decisions

### 5.1 Hybrid Storage Architecture: In-Memory Data Bank + SQLite Persistence
- **Decision:** Separate the foundational financial profile data from stateful payment/connection mutations.
- **Implementation:**
  - **In-Memory Synthetic Data Bank (`DatasetManager`):** Holds 3 personas, 13 accounts, 347 reconciled transactions, 36 merchants, 105 products, 12 subscriptions, 2 businesses, and 20 test scenarios. Computed deterministically on startup using a fixed seed (`seed=42`).
  - **SQLite Database (`finora.db`):** Stores mutations that occur during live runtime: PayPal orders created (`paypal_orders`), PayPal payments captured (`captured_payments`), Open Banking connected institutions (`connected_accounts`), synchronization logs (`sync_logs`), and user preference overrides (`user_preferences`).

### 5.2 Knowledge-First Question Processing Pipeline
- **Decision:** Do not rely on external LLM inference for routine financial arithmetic, loan calculations, break-even math, or knowledge definitions.
- **Implementation:** FINORA runs a 7-stage orchestrator:
  1. *Intent Understanding:* Identifies whether the user is asking for arithmetic, loan repayment, break-even volume, subscriptions, accounting rules, or an open-ended strategic question.
  2. *Internal Knowledge Retrieval:* Searches internal domain entries across 5 structured domains.
  3. *Deterministic Algorithm Execution:* Executes arbitrary-precision Python `Decimal` algorithms.
  4. *Sufficiency Assessment:* Flags query as `SUFFICIENT`, `PARTIAL`, or `REQUIRES_EXTERNAL_DATA`.
  5. *Escalation Decision:* If `SUFFICIENT`, answers directly with 0 external API calls ($0.00 spend).
  6. *Selective AI Escalation:* If complex circumstantial trade-offs exist (e.g. 50k tokens daily Cognition Engine query), escalates to Google Gemini Free Tier (`gemini-flash-lite-latest`) with verified facts pre-injected into the prompt.
  7. *Validation & Governance:* Ensures the output does not contradict database telemetry and enforces the Step 14 user approval gate.

### 5.3 Authoritative Backend Order Pricing
- **Decision:** Never trust product prices submitted from the client browser.
- **Implementation:** When `/api/payments/create-order` is called with `product_id`, the backend retrieves the product from `DatasetManager.products`, computes the authoritative total price ($P_{\text{base}} + \text{Shipping}$), creates the PayPal order with that exact sum, and stores the record in SQLite before returning the approval link.

### 5.4 Strict Zero-Paid AI Guardrails
- **Decision:** Ensure FINORA can never run up unexpected commercial AI API bills.
- **Implementation:** `ALLOW_PAID_MODELS=false`, `ALLOW_AUTO_RECHARGE=false`, and `MAX_API_SPEND_USD=0.0`. If external AI APIs fail, time out, or exhaust free quotas, FINORA falls back gracefully to its built-in deterministic conversational engine.

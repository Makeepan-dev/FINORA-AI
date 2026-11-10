# FINORA — Master Codebase Index & Architectural Sitemap
## Document 11: Central Navigation Document & File Inventory

---

## 1. Architectural Documentation Suite Sitemap

| Document | Title | Primary Focus & Contents |
| :--- | :--- | :--- |
| [`01_PROJECT_OVERVIEW.md`](file:///d:/FINORA/docs/architecture/01_PROJECT_OVERVIEW.md) | **Project Overview & Scope** | System mission, personal finance boundaries, tech stack, entry points, major architectural decisions. |
| [`02_FRONTEND_ARCHITECTURE.md`](file:///d:/FINORA/docs/architecture/02_FRONTEND_ARCHITECTURE.md) | **Frontend Architecture** | React SPA, 8 core pages, tab-based state routing, UI styling, Recharts, cross-view interactions. |
| [`03_BACKEND_ARCHITECTURE.md`](file:///d:/FINORA/docs/architecture/03_BACKEND_ARCHITECTURE.md) | **Backend Architecture** | FastAPI setup, 12 API routers, services, agents, complete request lifecycle. |
| [`04_DATABASE_ARCHITECTURE.md`](file:///d:/FINORA/docs/architecture/04_DATABASE_ARCHITECTURE.md) | **Database Architecture** | Hybrid data model: SQLite `finora.db` (5 tables) vs. in-memory synthetic data bank (Pydantic v2). |
| [`05_AI_ARCHITECTURE.md`](file:///d:/FINORA/docs/architecture/05_AI_ARCHITECTURE.md) | **AI & Intelligence** | 7-stage Knowledge-First orchestrator, Gemini free-tier, deterministic math, zero-spend guardrails. |
| [`06_EXTERNAL_INTEGRATIONS.md`](file:///d:/FINORA/docs/architecture/06_EXTERNAL_INTEGRATIONS.md) | **External Integrations** | Google Gemini REST, PayPal Sandbox REST, Groq/OpenRouter stubs, Open Banking simulator. |
| [`07_FEATURE_IMPLEMENTATION_MATRIX.md`](file:///d:/FINORA/docs/architecture/07_FEATURE_IMPLEMENTATION_MATRIX.md) | **Implementation Matrix** | Comprehensive reality audit: Fully Implemented, Partially Implemented, Simulated, Broken. |
| [`08_SECURITY_AND_RISK_AUDIT.md`](file:///d:/FINORA/docs/architecture/08_SECURITY_AND_RISK_AUDIT.md) | **Security & Risk Audit** | Authentication gaps, CORS review, secrets management, Decimal precision, defense-in-depth. |
| [`09_TECHNICAL_DEBT.md`](file:///d:/FINORA/docs/architecture/09_TECHNICAL_DEBT.md) | **Technical Debt Register** | Frontend chunk size, tab routing vs URL routes, dual data store, deprecations, stateless chat. |
| [`10_SYSTEM_DEPENDENCY_MAP.md`](file:///d:/FINORA/docs/architecture/10_SYSTEM_DEPENDENCY_MAP.md) | **System Dependency Map** | Mermaid architectural diagrams, backend dependencies, AI decision flow, PayPal payment flow. |
| [`11_MASTER_CODEBASE_INDEX.md`](file:///d:/FINORA/docs/architecture/11_MASTER_CODEBASE_INDEX.md) | **Master Codebase Index** | This document: full directory tree, file inventory, module responsibilities. |

---

## 2. Complete Application File & Module Inventory

### 2.1 Backend Modules (`backend/app/`)

| File Path | Lines | Responsibilities | Key Symbols / Exports |
| :--- | :--- | :--- | :--- |
| [`backend/app/main.py`](file:///d:/FINORA/backend/app/main.py) | 58 | Server entry point; DB schema initialization; CORS middleware; registers 12 API routers. | `app`, `root()`, `health_check()` |
| [`backend/app/core/config.py`](file:///d:/FINORA/backend/app/core/config.py) | 52 | Pydantic `BaseSettings` resolving candidate `.env` files; zero-spend configuration. | `Settings`, `settings`, `reload_settings()` |
| [`backend/app/database/session.py`](file:///d:/FINORA/backend/app/database/session.py) | 17 | SQLAlchemy engine, session maker (`SessionLocal`), and `get_db()` dependency generator. | `engine`, `SessionLocal`, `Base`, `get_db()` |
| [`backend/app/models/db_models.py`](file:///d:/FINORA/backend/app/models/db_models.py) | 76 | Declarative ORM models for SQLite persistence (`captured_payments`, `paypal_orders`, etc.). | `CapturedPayment`, `PayPalOrderRecord`, `ConnectedAccount`, `SyncLog`, `UserPreference` |
| [`backend/app/schemas/guardian.py`](file:///d:/FINORA/backend/app/schemas/guardian.py) | 33 | Pydantic validation models for structured Guardian responses and subscription audits. | `SubscriptionAuditClassification`, `GuardianStructuredResponse` |

#### API Controllers (`backend/app/api/`)
| File Path | Lines | Route Prefix | Responsibilities |
| :--- | :--- | :--- | :--- |
| [`backend/app/api/analytics.py`](file:///d:/FINORA/backend/app/api/analytics.py) | 8 | `/api/analytics` | `GET /dashboard` — Aggregated dashboard metrics. |
| [`backend/app/api/guardian.py`](file:///d:/FINORA/backend/app/api/guardian.py) | 16 | `/api/guardian` | `POST /chat`, `GET /audit-subscriptions` — Guardian conversational interface. |
| [`backend/app/api/shopping.py`](file:///d:/FINORA/backend/app/api/shopping.py) | 30 | `/api/shopping` | `GET /products`, `POST /evaluate-budget`, `POST /compare`. |
| [`backend/app/api/payments.py`](file:///d:/FINORA/backend/app/api/payments.py) | 64 | `/api/payments` | PayPal order creation, server-side capture, connection testing, history. |
| [`backend/app/api/income.py`](file:///d:/FINORA/backend/app/api/income.py) | 8 | `/api/income` | `GET /intelligence` — Ingests cleared income and analyzes streams. |
| [`backend/app/api/connections.py`](file:///d:/FINORA/backend/app/api/connections.py) | 45 | `/api/connections`| Open Banking and PayPal account connections, sync, and revocation. |
| [`backend/app/api/demo_data.py`](file:///d:/FINORA/backend/app/api/demo_data.py) | 117 | `/api/demo-data` | Synthetic data bank endpoints, scenario activation, validation, and export. |
| [`backend/app/api/settings.py`](file:///d:/FINORA/backend/app/api/settings.py) | 30 | `/api/settings` | `GET /status` — Application and AI provider runtime status. |
| [`backend/app/api/knowledge.py`](file:///d:/FINORA/backend/app/api/knowledge.py) | 24 | `/api/knowledge` | Knowledge base inventory, search, and topic lookups. |
| [`backend/app/api/optimization.py`](file:///d:/FINORA/backend/app/api/optimization.py) | 31 | `/api/optimization` | 14-step expense optimization audit and commitment comparison. |
| [`backend/app/api/location.py`](file:///d:/FINORA/backend/app/api/location.py) | 43 | `/api/location` | Location permission management and Haversine nearby discovery. |
| [`backend/app/api/automation.py`](file:///d:/FINORA/backend/app/api/automation.py) | 21 | `/api/automation` | Event-driven automation rules, execution history, rule toggling. |

#### Services & Agents (`backend/app/services/` & `app/agents/`)
| File Path | Lines | Responsibilities | Key Exports |
| :--- | :--- | :--- | :--- |
| [`backend/app/services/ai_service.py`](file:///d:/FINORA/backend/app/services/ai_service.py) | 548 | Zero-cost multi-provider AI engine; calls Gemini Free-Tier; fallback engine. | `AIService`, `global_ai_service` |
| [`backend/app/services/knowledge_orchestrator.py`](file:///d:/FINORA/backend/app/services/knowledge_orchestrator.py) | 484 | 7-stage query processing pipeline coordinating intent, knowledge, and algorithms. | `KnowledgeOrchestrator`, `global_knowledge_orchestrator` |
| [`backend/app/services/analytics_service.py`](file:///d:/FINORA/backend/app/services/analytics_service.py) | 392 | Computes authoritative cash balances, spending breakdown, budget progress. | `AnalyticsService`, `global_analytics_service` |
| [`backend/app/services/paypal_service.py`](file:///d:/FINORA/backend/app/services/paypal_service.py) | 432 | Orchestrates PayPal Sandbox order creation, capture, and simulation fallback. | `PayPalService`, `global_paypal_service` |
| [`backend/app/services/income_service.py`](file:///d:/FINORA/backend/app/services/income_service.py) | 207 | Multi-stream income classification, volatility metrics, expected cash flows. | `IncomeIntelligenceService`, `global_income_service` |
| [`backend/app/services/sync_service.py`](file:///d:/FINORA/backend/app/services/sync_service.py) | 271 | Simulates Open Banking institution syncing, health status, and logging. | `FinancialSyncService`, `global_sync_service` |
| [`backend/app/agents/financial_guardian.py`](file:///d:/FINORA/backend/app/agents/financial_guardian.py) | 53 | Primary user-facing agent interfacing with `KnowledgeOrchestrator`. | `FinancialGuardianAgent`, `global_financial_guardian` |
| [`backend/app/agents/shopping_agent.py`](file:///d:/FINORA/backend/app/agents/shopping_agent.py) | 164 | Product catalog search, budget pre-evaluation, 3-year TCO, value scoring. | `ShoppingAgent`, `global_shopping_agent` |

#### Algorithms & Knowledge (`backend/app/algorithms/` & `app/knowledge/`)
| File Path | Lines | Responsibilities | Key Exports |
| :--- | :--- | :--- | :--- |
| [`backend/app/algorithms/decimal_math.py`](file:///d:/FINORA/backend/app/algorithms/decimal_math.py) | 48 | Banker's rounding (`ROUND_HALF_UP`), safe division, float sanitization. | `to_decimal`, `round_currency`, `safe_divide` |
| [`backend/app/algorithms/financial_calculations.py`](file:///d:/FINORA/backend/app/algorithms/financial_calculations.py) | 207 | Loan amortization, break-even point ($Q=FC/(P-VC)$), profit margins, depreciation. | `calculate_loan_amortization`, `calculate_break_even` |
| [`backend/app/algorithms/financial_intelligence.py`](file:///d:/FINORA/backend/app/algorithms/financial_intelligence.py) | 177 | Duplicate detection with license whitelisting, spending spikes, cash runway. | `detect_duplicate_transactions`, `calculate_cash_flow_runway` |
| [`backend/app/algorithms/commerce_intelligence.py`](file:///d:/FINORA/backend/app/algorithms/commerce_intelligence.py) | 115 | 1/3/5-year TCO, cost-per-use, quality and warranty-adjusted value scoring. | `calculate_total_cost_of_ownership`, `calculate_value_adjusted_score` |
| [`backend/app/knowledge/repository.py`](file:///d:/FINORA/backend/app/knowledge/repository.py) | 84 | In-memory search index for 5 structured knowledge domains. | `KnowledgeRepository`, `global_knowledge_repository` |
| [`backend/app/location/discovery.py`](file:///d:/FINORA/backend/app/location/discovery.py) | 144 | Haversine distance calculator and directory of verified local alternatives. | `BusinessDiscoveryEngine`, `haversine_distance_miles` |
| [`backend/app/optimization/expense_optimizer.py`](file:///d:/FINORA/backend/app/optimization/expense_optimizer.py) | 139 | 14-step autonomous expense optimization pipeline with Step 14 user gate. | `AutonomousExpenseOptimizer`, `global_expense_optimizer` |
| [`backend/app/automation/engine.py`](file:///d:/FINORA/backend/app/automation/engine.py) | 108 | Event-driven and scheduled automation rules and execution logs. | `AutomationEngine`, `global_automation_engine` |

---

### 2.2 Frontend Modules (`frontend/src/`)

| File Path | Lines | Responsibilities | Key Components / Exports |
| :--- | :--- | :--- | :--- |
| [`frontend/src/main.tsx`](file:///d:/FINORA/frontend/src/main.tsx) | 10 | React DOM root mounting `<App />` into `#root`. | Root render |
| [`frontend/src/App.tsx`](file:///d:/FINORA/frontend/src/App.tsx) | 145 | Central state coordinator, layout shell, and tab-based router. | `App` |
| [`frontend/src/services/api.ts`](file:///d:/FINORA/frontend/src/services/api.ts) | 203 | Client-side API client wrapping `fetch()` with TypeScript types. | `api` |
| [`frontend/src/types/index.ts`](file:///d:/FINORA/frontend/src/types/index.ts) | 196 | TypeScript interfaces for dashboard data, products, AI response, scenarios. | `DashboardData`, `AIResponse`, `ProductItem` |
| [`frontend/src/components/Navbar.tsx`](file:///d:/FINORA/frontend/src/components/Navbar.tsx) | 59 | Sticky header with branding, persona dropdown, scenario badge. | `Navbar` |
| [`frontend/src/components/Sidebar.tsx`](file:///d:/FINORA/frontend/src/components/Sidebar.tsx) | 92 | Left navigation sidebar with 8 tabs and savings counter badge. | `Sidebar` |

#### Page Views (`frontend/src/pages/`)
| File Path | Lines | Tab Name | Responsibilities |
| :--- | :--- | :--- | :--- |
| [`frontend/src/pages/Overview.tsx`](file:///d:/FINORA/frontend/src/pages/Overview.tsx) | 306 | `overview` | High-level KPI summary, spending pie chart, 6-month trends, budget progress. |
| [`frontend/src/pages/Transactions.tsx`](file:///d:/FINORA/frontend/src/pages/Transactions.tsx) | 212 | `transactions`| Multi-account financial ledger with search, category filter, and anomaly badges. |
| [`frontend/src/pages/Income.tsx`](file:///d:/FINORA/frontend/src/pages/Income.tsx) | 286 | `income` | Multi-stream income breakdown, volatility gauge, expected cash flows. |
| [`frontend/src/pages/Guardian.tsx`](file:///d:/FINORA/frontend/src/pages/Guardian.tsx) | 395 | `guardian` | Conversational financial AI interface, sufficiency badges, subscription audits. |
| [`frontend/src/pages/Shopping.tsx`](file:///d:/FINORA/frontend/src/pages/Shopping.tsx) | 404 | `shopping` | 105-product catalog, budget pre-evaluation modal, side-by-side comparison. |
| [`frontend/src/pages/Payments.tsx`](file:///d:/FINORA/frontend/src/pages/Payments.tsx) | 432 | `payments` | PayPal Sandbox order creation, buyer approval simulation, capture, history. |
| [`frontend/src/pages/Connections.tsx`](file:///d:/FINORA/frontend/src/pages/Connections.tsx) | 313 | `connections` | Open Banking / Plaid institutions list, connection modal, sync audit logs. |
| [`frontend/src/pages/Settings.tsx`](file:///d:/FINORA/frontend/src/pages/Settings.tsx) | 350 | `settings` | 20 test scenario switcher, data bank integrity validator, system diagnostics. |

---

### 2.3 Automated Test Suite (`backend/tests/`)

| Test File | Tests | Focus Area | Status |
| :--- | :--- | :--- | :--- |
| [`backend/tests/test_api_and_services.py`](file:///d:/FINORA/backend/tests/test_api_and_services.py) | 6 | API health, dashboard analytics, shopping agent, PayPal order lifecycle. | **6 PASSED** |
| [`backend/tests/test_conversational_reasoning.py`](file:///d:/FINORA/backend/tests/test_conversational_reasoning.py) | 12 | Contextual circumstance shifts, missing telemetry, fallback honesty. | **12 PASSED** |
| [`backend/tests/test_demo_data_integrity.py`](file:///d:/FINORA/backend/tests/test_demo_data_integrity.py) | 7 | Deterministic generation, balance reconciliation, synthetic safety markers. | **7 PASSED** |
| [`backend/tests/test_guardian_reasoning.py`](file:///d:/FINORA/backend/tests/test_guardian_reasoning.py) | 8 | All 7 subscriptions audited, zero-cost guardrails, expensive utilities. | **8 PASSED** |
| [`backend/tests/test_income_and_connections.py`](file:///d:/FINORA/backend/tests/test_income_and_connections.py) | 4 | Invariant: Expected income not counted as cash; connected account lifecycle. | **4 PASSED** |
| [`backend/tests/test_knowledge_engine_and_zero_ai.py`](file:///d:/FINORA/backend/tests/test_knowledge_engine_and_zero_ai.py) | 18 | Decimal math, break-even, loan amortization, TCO, Zero-AI acceptance tests. | **18 PASSED** |
| **Total Automated Tests** | **55** | **Comprehensive Full System Verification** | **55 PASSED (100%)** |

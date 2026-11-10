# FINORA — Frontend Architecture Mapping
## Document 02: Client-Side Modules, Pages, Routing & State Management

---

## 1. Frontend System Topology & Architecture

FINORA's frontend is a modern, single-page application (SPA) built with **React 18**, **TypeScript**, **Vite**, and **Tailwind CSS**. It follows a dark fintech aesthetic styled around a deep `#0B0F19` foundation palette with cyan, emerald, purple, and amber accents.

```
+---------------------------------------------------------------------------------------------------------+
|                                           HTML SHELL (index.html)                                       |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                       REACT ENTRY POINT (src/main.tsx)                                  |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                          ROOT COMPONENT (src/App.tsx)                                   |
|   - Central State: activeUserId, currentTab, dashboardData, activeScenarioId, selectedProduct, loading  |
|   - Global Layout: <Navbar /> (Sticky Top) + <Sidebar /> (Fixed Left) + <main /> (Dynamic View)         |
+------------------+-------------------------------------------------------------------+------------------+
                   |                                                                   |
                   v                                                                   v
+--------------------------------------+           +------------------------------------------------------+
|          NAVIGATION SHELL            |           |                     CORE PAGES (src/pages/)          |
|  - <Navbar />:                       |           |  1. <Overview />: High-level KPI summary, charts     |
|    - App branding & hackathon tag    |           |  2. <Transactions />: Full ledger table & search     |
|    - Synthetic data status badge     |           |  3. <Income />: Multi-stream income intelligence     |
|    - Active scenario indicator       |           |  4. <Guardian />: Financial conversational AI agent   |
|    - Persona selector dropdown       |           |  5. <Shopping />: Catalog search, TCO, budget checks |
|  - <Sidebar />:                      |           |  6. <Payments />: PayPal checkout, order capture     |
|    - 8 primary navigation tabs       |           |  7. <Connections />: Open Banking / Plaid connectors |
|    - Dynamic savings badge counter   |           |  8. <SettingsPage />: Scenarios & DB integrity checks|
+--------------------------------------+           +---------------------------+--------------------------+
                                                                               |
                                                                               v
+---------------------------------------------------------------------------------------------------------+
|                                        API SERVICE LAYER (src/services/api.ts)                          |
|  - Typed async functions communicating with backend FastAPI endpoints via fetch()                       |
|  - Types & Contracts defined in src/types/index.ts                                                      |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Navigation & Routing Architecture

### 2.1 Tab-Based State Routing
Unlike traditional web applications that employ browser URL routing via `react-router-dom`, FINORA uses a **centralized state-driven tab router** inside [`App.tsx`](file:///d:/FINORA/frontend/src/App.tsx):

- **State Variable:** `currentTab: string` (defaults to `'overview'`).
- **Mechanics:** Clicking a tab in the `<Sidebar />` triggers `onSelectTab(tabId)`, updating `currentTab` in `App.tsx`.
- **Conditional Rendering:** A single `<main>` container mounts the corresponding view:
  ```tsx
  {currentTab === 'overview' && <Overview data={dashboardData} ... />}
  {currentTab === 'transactions' && <Transactions transactions={dashboardData.recent_transactions} />}
  {currentTab === 'income' && <Income activeUserId={activeUserId} />}
  {currentTab === 'guardian' && <Guardian dashboardData={dashboardData} activeUserId={activeUserId} />}
  {currentTab === 'shopping' && <Shopping onSelectForCheckout={handleSelectProductForCheckout} ... />}
  {currentTab === 'payments' && <Payments selectedProduct={selectedProduct} activeUserId={activeUserId} ... />}
  {currentTab === 'connections' && <Connections activeUserId={activeUserId} />}
  {currentTab === 'settings' && <SettingsPage activeUserId={activeUserId} ... />}
  ```
- **Cross-View Deep Navigation:**
  - Clicking *"Ask Guardian"* on the Overview page calls `onNavigateToGuardian()`, switching `currentTab` to `'guardian'`.
  - Clicking *"Buy with PayPal"* on a product card in Shopping calls `handleSelectProductForCheckout(product)`, sets `selectedProduct`, and switches `currentTab` to `'payments'` with the product pre-loaded for checkout.

---

## 3. Global State Coordination & Context

FINORA currently manages global state at the top-level `<App />` component using native React `useState` and `useEffect` hooks:

| State Field | Type | Default Value | Purpose |
| :--- | :--- | :--- | :--- |
| `activeUserId` | `string` | `'usr_alex_chen'` | Active user profile driving all portfolio telemetry, income, and budgets |
| `currentTab` | `string` | `'overview'` | Currently active screen rendered in the main viewport |
| `dashboardData` | `DashboardData \| null` | `null` | Authoritative aggregated portfolio telemetry ingested from `/api/analytics/dashboard` |
| `activeScenarioId`| `string` | `'scen_01_normal_spending'` | Currently active synthetic test scenario ID |
| `selectedProduct` | `ProductItem \| null` | `null` | Product selected in Shopping and forwarded to Payments for PayPal order creation |
| `loading` | `boolean` | `true` | Global initial loader gate preventing render until dashboard data resolves |

### Data Synchronization Flow
1. On initial load or whenever `activeUserId` changes, `loadDashboard(activeUserId)` executes.
2. It calls `api.getDashboard(userId)` (`GET /api/analytics/dashboard?user_id=...`).
3. Returned metrics populate `dashboardData`.
4. If a scenario is activated from Settings, `handleScenarioActivated(scenarioId)` updates `activeScenarioId` and reloads the dashboard.

---

## 4. Detailed Page & Screen Inventory

### 4.1 Overview Screen (`src/pages/Overview.tsx`)
- **Purpose:** Central command center summarizing cash balances, discretionary cash flow, category budgets, monthly spending trends, and active financial alerts.
- **Main Components:**
  - KPI Stat Cards: Liquid Cash Balance, Monthly Inflows, Monthly Outflows, Discretionary Surplus.
  - Spending Breakdown: Recharts `<PieChart>` visualizing category allocations with percentage distribution.
  - 6-Month Income vs. Expense Trend: Recharts `<BarChart>` showing historical cash flow stability.
  - Budget Progress Bars: Visual progress bars with status thresholds (`normal`, `warning`, `exceeded`).
  - Active Insights & Alerts: Actionable warnings (e.g. gym pass low usage, category budget overrun).
- **Data Source:** Props passed from `dashboardData` in `App.tsx`.
- **API Dependencies:** Ingested via `api.getDashboard(userId)`.
- **Implementation Status:** **FULLY IMPLEMENTED**.

---

### 4.2 Transactions Screen (`src/pages/Transactions.tsx`)
- **Purpose:** Full historical financial ledger displaying reconciled multi-account debits, credits, refunds, and transfers.
- **Main Components:**
  - Search Input: Filter by transaction ID, merchant name, or description.
  - Category Dropdown: Filter by category (e.g., `groceries`, `software`, `utilities`, `fitness`).
  - Transaction Table: Columns for Date, Description, Category, Payment Method, Account ID, and Amount.
  - Anomaly Flag Indicators: Visual badges identifying transactions flagged for investigation (e.g., duplicate charges, spending spikes).
  - Transaction Detail Slide-Out / Modal: Deep inspection of transaction metadata, related transaction IDs, and carrier confirmation notes.
- **Data Source:** `dashboardData.recent_transactions` or `api.getTransactions()`.
- **Implementation Status:** **FULLY IMPLEMENTED**.

---

### 4.3 Income Intelligence Screen (`src/pages/Income.tsx`)
- **Purpose:** Personal income tracking, stream classification, volatility measurement, and cash flow forecasting.
- **Main Components:**
  - Received vs. Expected Income KPI Cards: Invariant enforcement: Contractual expected income is never counted as cash on hand.
  - Stream Classification Breakdown: Donut chart displaying Salary, Freelance & Contract, Dividends, and Business Income.
  - Freelance Irregularity & Volatility Gauge: Standard deviation and coefficient of variation for variable income.
  - Scheduled Inflows Timeline: List of expected upcoming payments with contract reference and confidence rating.
- **Data Source:** `api.getIncomeIntelligence(activeUserId)`.
- **API Dependency:** `GET /api/income/intelligence?user_id=...`.
- **Implementation Status:** **FULLY IMPLEMENTED**.

---

### 4.4 Financial Guardian Screen (`src/pages/Guardian.tsx`)
- **Purpose:** Conversational AI financial assistant providing fact-grounded portfolio advice, subscription audits, debt amortization, and expense optimization.
- **Main Components:**
  - Provider Status Badge: Dynamically reports `Internal Knowledge & Algorithms (Zero AI)`, `Google Gemini Free Tier`, or `Deterministic Fallback`.
  - Knowledge Sufficiency Pills: Displays `SUFFICIENT`, `PARTIAL`, or `REQUIRES_EXTERNAL_DATA`.
  - Applied Knowledge Tags: Clickable tags displaying applied internal knowledge IDs (e.g. `kn_pf_001_cash_flow`).
  - Suggested Prompts: Fast 1-click test prompts for internal arithmetic vs. complex circumstantial AI queries.
  - Chat Stream: Markdown-rendered conversational bubble with verified factual analysis, recommendation cards, and potential savings cushion indicators.
  - Subscription Audit Cards: Interactive audit list categorizing commitments into `KEEP`, `REDUCE`, `REPLACE`, `ELIMINATE`, and `INVESTIGATE`.
- **Data Source:** `api.chatWithGuardian(prompt, activeUserId)`.
- **API Dependency:** `POST /api/guardian/chat`.
- **Implementation Status:** **FULLY IMPLEMENTED**.

---

### 4.5 Shopping Agent Screen (`src/pages/Shopping.tsx`)
- **Purpose:** Autonomous shopping assistant that searches the 105-product catalog, calculates landed costs, evaluates remaining monthly budgets, computes 3-year TCO, and ranks products by value score.
- **Main Components:**
  - Product Catalog Grid: Searchable, category-filtered cards with base price, shipping cost, rating, warranty, and value score.
  - Budget Pre-Evaluation Modal: Inspects remaining category budget before checkout, displaying budget variance and approval recommendations.
  - Side-by-Side Product Comparison Matrix: Compares specs, TCO, and value-adjusted scores across up to 3 products.
  - *"Buy with PayPal"* Action Button: Forwards selected product to Payments page.
- **Data Source:** `api.searchProducts()`, `api.evaluateBudget()`, `api.compareProducts()`.
- **API Dependencies:** `GET /api/shopping/products`, `POST /api/shopping/evaluate-budget`, `POST /api/shopping/compare`.
- **Implementation Status:** **FULLY IMPLEMENTED**.

---

### 4.6 Payments & PayPal Checkout Screen (`src/pages/Payments.tsx`)
- **Purpose:** User-supervised payment execution interface facilitating PayPal order creation, buyer approval simulation, order capture, and payment history audit.
- **Main Components:**
  - Order Initiation Card: Shows item price, shipping cost, landed total, and PayPal Sandbox mode indicator.
  - PayPal Connection Diagnostic Panel: Tests OAuth 2.0 handshake with `https://api-m.sandbox.paypal.com`.
  - Buyer Approval Gate: Displays PayPal approval URL and handles simulated buyer approval.
  - Order Capture Button: Executes server-side capture and anti-duplicate payment check.
  - Captured Payments Ledger: Table of historical captures with PayPal Order ID, Capture ID, amount, and status.
- **Data Source:** `api.createPayPalOrder()`, `api.capturePayPalOrder()`, `api.testPayPalConnection()`, `api.getPaymentHistory()`.
- **API Dependencies:** `/api/payments/*`.
- **Implementation Status:** **FULLY IMPLEMENTED**.

---

### 4.7 Connected Accounts Screen (`src/pages/Connections.tsx`)
- **Purpose:** Manages financial institution connections (Plaid Open Banking, PayPal Direct, TrueLayer UK) with permission toggling, manual synchronization, and audit logging.
- **Main Components:**
  - Institution Connection Cards: Visual list of connected banks with health status (`healthy`, `syncing`, `degraded`).
  - Connect Institution Modal: Lets user select institution and account type to establish a new connection.
  - Manual Sync Trigger: Dispatches synchronization job and shows count of ingested records.
  - Revoke Permission Action: Revokes access permissions without deleting historical ledgers.
  - Synchronization Audit Log: History table showing sync timestamps, duration (ms), records ingested, and status.
- **Data Source:** `api.getConnectedAccounts()`, `api.getSupportedInstitutions()`, `api.getSyncHistory()`.
- **API Dependencies:** `/api/connections/*`.
- **Implementation Status:** **FULLY IMPLEMENTED**.

---

### 4.8 Settings & Data Bank Screen (`src/pages/Settings.tsx`)
- **Purpose:** Demonstration control panel for switching test personas, activating any of the 20 test scenarios, validating financial data bank integrity, and inspecting AI/PayPal system settings.
- **Main Components:**
  - Scenario Selector: Grid of 20 test scenarios with descriptions, target users, and expected calculation outcomes.
  - Data Bank Validation Dashboard: 1-click execution of the mathematical integrity validator (referential integrity, balance reconciliation, synthetic safety markers).
  - Data Bank Reset & Regeneration: Resets data bank to initial seed state or regenerates with custom seed.
  - System Diagnostics Panel: Displays active AI provider, model, zero-spend enforcement, and PayPal credentials preview.
- **Data Source:** `api.getScenarios()`, `api.validateDataBank()`, `api.getSystemSettings()`.
- **API Dependencies:** `/api/demo-data/*`, `/api/settings/*`.
- **Implementation Status:** **FULLY IMPLEMENTED**.

---

## 5. UI Layout, Theming & Responsiveness

### 5.1 Dark Fintech Aesthetic
- Foundation color: `#0B0F19` (rich slate-midnight blue).
- Card containers: `bg-slate-900/95 border border-slate-800 rounded-2xl`.
- Accent colors:
  - Cyan (`text-cyan-400`, `bg-cyan-500`): Primary actions, branding, highlights.
  - Emerald (`text-emerald-400`): Income, positive cash flow, verified data markers.
  - Amber (`text-amber-400`): Warnings, optimization opportunities, fallback indicators.
  - Rose (`text-rose-400`): Budget overruns, critical anomalies, cancellation actions.

### 5.2 Responsive Layout
- Sticky Navbar (`h-16 sticky top-0 z-40`) across all screen widths.
- Desktop Sidebar (`w-64 min-h-[calc(100vh-4rem)]`) fixed to the left.
- Mobile compatibility: Navigation elements gracefully hide text labels on smaller viewports (`hidden sm:block`, `hidden md:flex`).
- Scrollable main viewport: `flex-1 overflow-y-auto max-w-7xl mx-auto p-6 lg:p-8`.

# FINORA — Technical Debt & Architectural Risk Register
## Document 09: Technical Debt Analysis & Code Quality Findings

---

## 1. Technical Debt Overview

The technical debt in FINORA reflects its rapid evolution from an in-memory synthetic data bank prototype into a knowledge-first personal financial assistant. The existing code is clean, well-tested, and mathematically rigorous, but several architectural shortcuts exist that should be addressed in subsequent development cycles.

```
+---------------------------------------------------------------------------------------------------------+
|                                        TECHNICAL DEBT CLUSTERS                                          |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                         +---------------------------+---------------------------+
                         |                                                       |
                         v                                                       v
+----------------------------------------------------+  +-------------------------------------------------+
|               FRONTEND TECHNICAL DEBT              |  |               BACKEND TECHNICAL DEBT            |
|  - Monolithic JS chunk (671 kB > 500 kB warning)   |  |  - Dual Data Store (In-Memory + SQLite)         |
|  - Tab-based state routing (no URL deep linking)   |  |  - Stateless /guardian/chat (No multi-turn ctx) |
|  - Prop drilling of activeUserId across components |  |  - Python 3.12 datetime.utcnow() deprecations   |
|  - No UI for backend automation rules engine       |  |  - Legacy B2B business entities in data bank    |
+----------------------------------------------------+  +-------------------------------------------------+
```

---

## 2. Technical Debt Register

### Debt Item 1: Dual Data Store Divergence (In-Memory vs. SQLite) [SEVERITY: HIGH]
- **Category:** Data Architecture & State Consistency.
- **Affected Modules:** [`backend/app/demo_data/dataset_manager.py`](file:///d:/FINORA/backend/app/demo_data/dataset_manager.py), [`backend/app/models/db_models.py`](file:///d:/FINORA/backend/app/models/db_models.py).
- **Description:**
  - Synthetic accounts, transactions, users, and subscriptions reside exclusively in memory inside `DatasetManager`.
  - Captured payments and connected account records reside on disk in `finora.db`.
- **Impact:**
  - Calling `POST /api/demo-data/reset` regenerates the in-memory accounts and balances to baseline, but does **not** truncate or rollback `captured_payments` or `connected_accounts` in SQLite.
  - This can create orphaned orders where a payment in SQLite refers to a transaction that no longer exists in memory.
- **Recommended Resolution:**
  - Unify persistence by migrating the synthetic data bank models into SQLite tables with seed migrations via Alembic.

---

### Debt Item 2: Frontend Bundle Size & Monolithic Chunking [SEVERITY: MEDIUM]
- **Category:** Frontend Performance & Asset Optimization.
- **Affected Modules:** [`frontend/vite.config.ts`](file:///d:/FINORA/frontend/vite.config.ts), `frontend/dist/assets/index-C1Bs6wAR.js`.
- **Description:**
  - Production build output:
    `dist/assets/index-C1Bs6wAR.js  671.21 kB │ gzip: 180.58 kB`
  - Vite emits: `(!) Some chunks are larger than 500 kB after minification.`
  - Large dependencies (Recharts, Lucide React, Tailwind merge) are bundled into a single JavaScript file.
- **Impact:** Slower initial page load and parse time on low-bandwidth mobile connections.
- **Recommended Resolution:**
  - Configure `rollupOptions.output.manualChunks` in `vite.config.ts` to code-split vendor bundles:
    ```typescript
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor-recharts': ['recharts'],
            'vendor-lucide': ['lucide-react'],
            'vendor-react': ['react', 'react-dom']
          }
        }
      }
    }
    ```
  - Implement React `lazy()` and `<Suspense>` for secondary pages (`Settings`, `Connections`).

---

### Debt Item 3: Single-Page Tab Routing without URL Deep Linking [SEVERITY: MEDIUM]
- **Category:** User Experience & Navigation.
- **Affected Modules:** [`frontend/src/App.tsx`](file:///d:/FINORA/frontend/src/App.tsx), [`frontend/src/components/Sidebar.tsx`](file:///d:/FINORA/frontend/src/components/Sidebar.tsx).
- **Description:**
  - Navigation between views is managed entirely by a React `useState('overview')` state variable.
  - Browser URL remains static at `http://localhost:5173/`.
- **Impact:**
  - Users cannot bookmark specific tabs (e.g. `/guardian` or `/shopping`).
  - Browser Back and Forward buttons do not navigate through screen history.
  - Refreshing the browser resets the view back to Overview.
- **Recommended Resolution:**
  - Adopt `react-router-dom` to map tabs to clean URL routes (`/overview`, `/transactions`, `/guardian`, `/shopping`, `/payments`, `/connections`, `/settings`).

---

### Debt Item 4: Stateless Financial Guardian Chat Endpoint [SEVERITY: MEDIUM]
- **Category:** AI Agent Capabilities.
- **Affected Modules:** `app/api/guardian.py`, `app/agents/financial_guardian.py`, `Guardian.tsx`.
- **Description:**
  - `POST /api/guardian/chat` accepts only `{ prompt: str, user_id: str }`.
  - While `Guardian.tsx` accumulates visual message bubbles in local React state, previous messages in the conversation are not transmitted back to the backend.
- **Impact:**
  - The Guardian cannot resolve follow-up pronouns or conversational references (e.g., *"Why did you suggest that?"* or *"What was the second option again?"*). Every user query is evaluated as an isolated turn.
- **Recommended Resolution:**
  - Update `POST /api/guardian/chat` to accept an optional `conversation_history: List[ChatMessage]` array, passing previous turn pairs into the Gemini prompt payload.

---

### Debt Item 5: Legacy B2B Entities in Personal Finance Scope [SEVERITY: LOW]
- **Category:** Domain Boundary & Conceptual Alignment.
- **Affected Modules:** `demo_data/generators/businesses.py`, `demo_data/generators/invoices.py`, scenarios `scen_14` to `scen_17`.
- **Description:**
  - The synthetic data bank contains 2 business entities (Apex Horizon Software, BlueSky Creative) and 10 B2B supplier/customer invoices.
- **Impact:**
  - Clutters the data model with corporate accounting artifacts when FINORA's primary mission is personal consumer/freelancer financial intelligence.
- **Recommended Resolution:**
  - Demote or isolate B2B invoice fixtures into a dedicated test folder, refocusing user data schemas purely on personal bank accounts, salaries, freelancer client retainers, and household utilities.

---

### Debt Item 6: Python 3.12 Deprecation Warnings [SEVERITY: LOW]
- **Category:** Code Hygiene & Future Upgrades.
- **Affected Modules:** `app/models/db_models.py`, `app/services/sync_service.py`, `app/automation/engine.py`.
- **Description:**
  - Generates 17 `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version.`
- **Impact:** Harmless in Python 3.12, but will cause errors when upgrading to Python 3.13 or 3.14.
- **Recommended Resolution:**
  - Replace all occurrences of `datetime.utcnow()` with `datetime.now(datetime.timezone.utc)`.

---

### Debt Item 7: Backend Automation Engine Missing Frontend UI [SEVERITY: LOW]
- **Category:** Feature Completeness.
- **Affected Modules:** `app/automation/engine.py`, `app/api/automation.py`.
- **Description:**
  - The backend has a fully functional rules engine (`rule_renewal_monitor`, `rule_low_usage_optimizer`, `rule_budget_threshold`) and execution history endpoint.
  - However, there is no UI component in the frontend to visualize or toggle these rules.
- **Impact:** Users can only inspect automation rules via API documentation (`/docs`).
- **Recommended Resolution:**
  - Add an "Automations" tab or widget in the Settings / Guardian interface.

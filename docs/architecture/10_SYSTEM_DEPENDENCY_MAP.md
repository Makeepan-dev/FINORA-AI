# FINORA — System Dependency & Process Flow Maps
## Document 10: Architectural Dependencies, Diagrams & Critical Flows

---

## 1. Overall System Architecture Diagram

```mermaid
graph TD
    subgraph Client ["Frontend Client (React + TS + Vite)"]
        UI["React UI (Overview, Transactions, Guardian, Shopping, Payments)"]
        APIClient["API Service Layer (api.ts)"]
        UI --> APIClient
    end

    subgraph Server ["Backend Core (FastAPI)"]
        CORS["CORS Middleware"]
        Router["API Routers (/api/*)"]
        APIClient -->|HTTP REST| CORS
        CORS --> Router

        subgraph CoreAgents ["Specialized Intelligence"]
            Guardian["Financial Guardian Agent"]
            Shopping["Shopping Agent"]
            Orchestrator["7-Stage Knowledge Orchestrator"]
        end

        subgraph Algorithms ["Deterministic Engine (Decimal)"]
            Math["Loan Amortization & Break-Even"]
            TCO["Total Cost of Ownership & Value Scoring"]
            Intel["Duplicate & Anomaly Detection"]
        end

        subgraph KnowledgeBase ["Structured Knowledge"]
            Repo["Knowledge Repository (5 Domains)"]
        end

        subgraph BusinessServices ["Services Layer"]
            Analytics["AnalyticsService"]
            Income["IncomeIntelligenceService"]
            Sync["FinancialSyncService"]
            PayPalSvc["PayPalService"]
            AISvc["AIService"]
        end

        Router --> Guardian
        Router --> Shopping
        Router --> Analytics
        Router --> Income
        Router --> Sync
        Router --> PayPalSvc

        Guardian --> Orchestrator
        Orchestrator --> Repo
        Orchestrator --> Algorithms
        Orchestrator --> AISvc
        Shopping --> Algorithms
    end

    subgraph DataLayer ["Data Storage"]
        DatasetMgr["In-Memory DatasetManager (seed=42)"]
        SQLiteDB[("SQLite Database (finora.db)")]
        Analytics --> DatasetMgr
        Income --> DatasetMgr
        Shopping --> DatasetMgr
        Sync --> SQLiteDB
        PayPalSvc --> SQLiteDB
    end

    subgraph External ["External Third-Party APIs"]
        Gemini["Google Gemini Free Tier (REST)"]
        PayPal["PayPal Sandbox REST API"]
        AISvc -.->|v1beta generateContent| Gemini
        PayPalSvc -.->|v1/v2 REST| PayPal
    end
```

---

## 2. Frontend Component Dependency Diagram

```mermaid
graph TD
    App["App.tsx (Root State: activeUserId, currentTab, dashboardData)"]
    Navbar["Navbar.tsx (Persona Selector, Scenario Badge)"]
    Sidebar["Sidebar.tsx (Tab Navigation, Savings Counter)"]
    API["services/api.ts (Type-safe fetch wrappers)"]
    Types["types/index.ts (TypeScript Interfaces)"]

    App --> Navbar
    App --> Sidebar
    App --> API
    API --> Types

    subgraph Pages ["View Containers (src/pages/)"]
        Overview["Overview.tsx"]
        Transactions["Transactions.tsx"]
        Income["Income.tsx"]
        Guardian["Guardian.tsx"]
        Shopping["Shopping.tsx"]
        Payments["Payments.tsx"]
        Connections["Connections.tsx"]
        Settings["Settings.tsx"]
    end

    App --> Overview
    App --> Transactions
    App --> Income
    App --> Guardian
    App --> Shopping
    App --> Payments
    App --> Connections
    App --> Settings

    Overview --> API
    Transactions --> API
    Income --> API
    Guardian --> API
    Shopping --> API
    Payments --> API
    Connections --> API
    Settings --> API
```

---

## 3. Backend Module Dependency Diagram

```mermaid
graph TD
    Main["app/main.py"] --> Routers["app/api/*.py"]
    Main --> DB["app/database/session.py"]
    Main --> Config["app/core/config.py"]

    subgraph RoutersGroup ["API Routers"]
        R_Guardian["guardian.py"]
        R_Shopping["shopping.py"]
        R_Payments["payments.py"]
        R_Analytics["analytics.py"]
        R_Income["income.py"]
        R_Conn["connections.py"]
        R_Demo["demo_data.py"]
    end

    Routers --> R_Guardian
    Routers --> R_Shopping
    Routers --> R_Payments
    Routers --> R_Analytics
    Routers --> R_Income
    Routers --> R_Conn
    Routers --> R_Demo

    R_Guardian --> GuardianAgent["agents/financial_guardian.py"]
    GuardianAgent --> Orchestrator["services/knowledge_orchestrator.py"]
    Orchestrator --> KnowledgeRepo["knowledge/repository.py"]
    Orchestrator --> FinancialCalc["algorithms/financial_calculations.py"]
    Orchestrator --> AIService["services/ai_service.py"]

    R_Shopping --> ShoppingAgent["agents/shopping_agent.py"]
    ShoppingAgent --> CommerceIntel["algorithms/commerce_intelligence.py"]

    R_Payments --> PayPalService["services/paypal_service.py"]
    PayPalService --> DBModels["models/db_models.py"]

    R_Analytics --> AnalyticsService["services/analytics_service.py"]
    AnalyticsService --> DatasetMgr["demo_data/dataset_manager.py"]

    R_Income --> IncomeService["services/income_service.py"]
    IncomeService --> DatasetMgr

    R_Conn --> SyncService["services/sync_service.py"]
    SyncService --> DBModels
```

---

## 4. AI Request & Decision Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant API as /api/guardian/chat
    participant Guardian as FinancialGuardianAgent
    participant Orchestrator as KnowledgeOrchestrator
    participant Knowledge as KnowledgeRepository
    participant Alg as Decimal Algorithms
    participant AI as AIService (Gemini)
    participant Engine as Deterministic Fallback

    User->>API: POST { prompt, user_id }
    API->>Guardian: chat(prompt, user_id)
    Guardian->>Guardian: Retrieve portfolio facts from AnalyticsService
    Guardian->>Orchestrator: process_question(prompt, metrics, scenario)
    
    Orchestrator->>Orchestrator: Stage 1: Classify Intent
    Orchestrator->>Knowledge: Stage 2: Search structured knowledge
    Knowledge-->>Orchestrator: Matched entries (5 domains)
    
    alt Arithmetic / Loan / Break-even / Direct Knowledge
        Orchestrator->>Alg: Stage 3: Execute Decimal calculation
        Alg-->>Orchestrator: Exact mathematical result
        Orchestrator->>Orchestrator: Stage 4: Sufficiency = SUFFICIENT
        Orchestrator-->>Guardian: Return verified deterministic response (0 AI calls)
    else Complex Circumstance Shift / Strategic Trade-Off
        Orchestrator->>Orchestrator: Stage 4: Sufficiency = REQUIRES_EXTERNAL_DATA
        Orchestrator->>AI: Stage 6: generate_financial_response(prompt, ground_truth_facts)
        alt Gemini Free Tier Success
            AI-->>Orchestrator: JSON with factual_analysis & reasoning
        else API Failure / Timeout / Quota Exhaustion
            AI->>Engine: Revert to rule_based_conversational_v2
            Engine-->>Orchestrator: Deterministic fallback with honest notice
        end
        Orchestrator->>Orchestrator: Stage 7: Validate bounds & check Step 14 gate
        Orchestrator-->>Guardian: Return response with provider badge
    end

    Guardian-->>API: Response payload
    API-->>User: HTTP 200 JSON { ai_response, metrics_snapshot }
```

---

## 5. PayPal Payment Execution Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Buyer
    participant Client as Frontend (Payments.tsx)
    participant API as /api/payments/*
    participant PayPalSvc as PayPalService
    participant Catalog as DatasetManager.products
    participant DB as SQLite (finora.db)
    participant PayPalAPI as PayPal Sandbox REST API

    User->>Client: Clicks "Buy with PayPal" on Product Card
    Client->>Client: Switches to Payments tab, sets selectedProduct
    User->>Client: Confirms and clicks "Create PayPal Order"
    
    Client->>API: POST /api/payments/create-order { product_id, user_id }
    API->>PayPalSvc: create_order(product_id, user_id)
    PayPalSvc->>Catalog: Fetch authoritative product price & shipping
    Catalog-->>PayPalSvc: Exact landed cost (e.g. $420.00)
    
    alt Live Sandbox Configured
        PayPalSvc->>PayPalAPI: POST /v2/checkout/orders
        PayPalAPI-->>PayPalSvc: { id: "ORD-XXX", links: [{ rel: "approve", href: approval_url }] }
    else Simulation Mode
        PayPalSvc->>PayPalSvc: Generate synthetic order & approval link
    end

    PayPalSvc->>DB: INSERT into paypal_orders (order_id, user_id, amount, status: "CREATED")
    PayPalSvc-->>API: Order record with approval_url
    API-->>Client: HTTP 200 Order payload

    User->>Client: Reviews and clicks "Simulate Buyer Approval" (or visits PayPal link)
    Client->>API: POST /api/payments/capture-order { order_id }
    API->>PayPalSvc: capture_order(order_id)
    
    PayPalSvc->>DB: Check if order_id already captured (Anti-duplicate prevention)
    
    alt Live Sandbox Configured
        PayPalSvc->>PayPalAPI: POST /v2/checkout/orders/{id}/capture
        PayPalAPI-->>PayPalSvc: { id: "CAP-XXX", status: "COMPLETED" }
    else Simulation Mode
        PayPalSvc->>PayPalSvc: Generate synthetic capture record
    end

    PayPalSvc->>DB: UPDATE paypal_orders SET status = "CAPTURED"
    PayPalSvc->>DB: INSERT into captured_payments (id, paypal_order_id, amount, status: "COMPLETED")
    PayPalSvc-->>API: Capture confirmation
    API-->>Client: HTTP 200 Capture payload
    Client->>Client: Displays success checkmark and updates payment history
```

---

## 6. Coupling & Dependency Analysis

1. **Clean Separation of Concerns:**
   - Algorithms in `app/algorithms/` have **zero** dependencies on external libraries or databases. They depend only on Python's built-in `decimal` and `math` modules.
   - Knowledge entries in `app/knowledge/` are pure data structures with zero framework dependencies.
2. **Circular Dependencies:**
   - **None.** Codebase imports follow a strict downward hierarchy: API $\rightarrow$ Agents $\rightarrow$ Services $\rightarrow$ Algorithms / Models.
3. **Single Points of Failure:**
   - `DatasetManager` instance is a process-global singleton (`global_dataset_manager`). In-memory mutations persist for the server process lifetime. Restarting the server resets in-memory data to seed state.
   - SQLite file `finora.db` operates in single-file mode. Concurrent write operations are locked by SQLite, which is suitable for prototype development but would require PostgreSQL for multi-user production.

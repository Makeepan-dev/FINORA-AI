# FINORA System Architecture

## Overview
**FINORA** (*Financial Intelligence Network for Optimization, Reasoning & Automation*) is an AI-powered financial intelligence and autonomous transaction-management platform built for the **PayPal AI Hackathon 2026**.

The platform is designed around three primary foundational pillars:
1. **Interconnected Synthetic Financial Data Bank (`demo_data`)**: A deterministic, multi-entity, 12+ month financial simulator featuring exact Python `Decimal` reconciliation, 20 reusable test scenarios, activity evidence graphs, and anti-fraud anomaly test cases.
2. **Deterministic Intelligence & Zero-Cost AI Core**: An AI provider abstraction strictly adhering to zero API spend (`MAX_API_SPEND_USD=0`) and backed by a deterministic financial calculation engine.
3. **Official PayPal Sandbox Payment Network**: Server-side OAuth 2.0 authentication, authoritative backend order price calculation, user-supervised authorization policies, and anti-duplicate capture prevention.

---

## High-Level Component Topology

```
+-------------------------------------------------------------------------+
|                          REACT + TS FRONTEND                            |
|  - Modern Dark Fintech UI (#0B0F19 foundation, Tailwind, Recharts)     |
|  - 6 Core Views: Overview, Transactions, Guardian, Shopping,            |
|                  Payments, Settings & Data Bank                         |
+------------------------------------+------------------------------------+
                                     |
                                     | HTTP REST (/api/*)
                                     v
+-------------------------------------------------------------------------+
|                         FASTAPI BACKEND CORE                            |
|                                                                         |
|  +------------------------+  +---------------------------------------+  |
|  |     AI SERVICE         |  |          PAYPAL REST SERVICE          |  |
|  | - Zero-Cost Guardrails |  | - OAuth 2.0 Access Token Caching      |  |
|  | - Gemini / Groq /      |  | - /v2/checkout/orders                 |  |
|  |   OpenRouter (Free)    |  | - /v2/checkout/orders/{id}/capture    |  |
|  | - Deterministic Engine |  | - Anti-duplicate Idempotency Cache   |  |
|  +------------------------+  +---------------------------------------+  |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |                   SPECIALIZED MVP AI AGENTS                       |  |
|  | - Financial Guardian Agent (income, expenses, budgets, savings)   |  |
|  | - Autonomous Shopping Agent (105-item catalog, budget checks)     |  |
|  +-------------------------------------------------------------------+  |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |            SYNTHETIC FINANCIAL DATA BANK (backend/demo_data)      |  |
|  | - 3 Persona Profiles (Chen, Jenkins, Vance)                       |  |
|  | - 13 Reconciled Accounts (Checking, Savings, CC, PayPal Wallets)   |  |
|  | - 347 Reconciled Historical Transactions (Decimal Arithmetic)     |  |
|  | - 36 Merchants across 14 categories                               |  |
|  | - 105 Products with Landed Costs & Specifications                 |  |
|  | - 12 Recurring Commitments with Activity Telemetry Links           |  |
|  | - 2 Businesses (SaaS Startup & Consulting Agency) + Invoices       |  |
|  | - 20 Reusable Test Scenarios with Grounded Expectations           |  |
|  | - Automated Integrity & Reconciliation Validator (100% PASS)      |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

---

## Core Security & Reliability Principles

1. **Monetary Precision with Python `Decimal`**:
   All monetary amounts, account balances, subscription renewals, invoice totals, and product calculations use Python's arbitrary-precision `Decimal`. Floating-point arithmetic is prohibited for monetary storage.

2. **Authoritative Backend Order Amounts**:
   Under no circumstances does the backend trust prices submitted from the frontend. When `/api/payments/create-order` is invoked, the backend independently queries the authoritative product catalog, calculates the exact item price and shipping cost, and generates the PayPal order.

3. **Missing Evidence vs. Inactivity**:
   Missing telemetry (e.g. absent turnstile badge swipes) is explicitly treated as `MISSING` data, **never** as proof of user inactivity or zero attendance.

4. **Zero-Cost AI Safety**:
   The application cannot incur surprise API bills. If no free-tier API key is configured or quotas are exhausted, the built-in deterministic financial engine handles all queries seamlessly.

---

## Knowledge-First Intelligence Engine

FINORA implements a **Knowledge-First Financial & Commerce Architecture**:
```
User Question -> Intent Understanding -> Internal Knowledge Retrieval -> Deterministic Algorithms -> Knowledge Sufficiency Assessment -> AI API Escalation Only When Necessary -> Verified Response
```

### 1. Structured Knowledge Base (`app/knowledge/`)
1. **Personal Finance**: Cash flow margins, debt amortization, savings rate, emergency runway, net worth.
2. **Business Finance**: Break-even volume ($Q = FC/(P-VC)$), gross/operating/net margins, working capital.
3. **Accounting**: Double-entry fundamental equation ($Assets = Liabilities + Equity$), debits/credits, accrual vs cash, straight-line depreciation.
4. **Payments & Commerce**: Four-party card model, interchange and card-not-present fees (2.9% + $0.30), dispute lifecycle and chargeback rules.
5. **Consumer Commerce**: Total Cost of Ownership (TCO), cost-per-use, multi-factor value scoring.

### 2. Deterministic Financial & Commerce Algorithms (`app/algorithms/`)
- `decimal_math.py`: Arbitrary-precision math, Banker's rounding (`ROUND_HALF_UP`), zero binary float drift.
- `financial_calculations.py`: Loan amortization schedules, break-even analysis, multi-tier margins, straight-line depreciation.
- `financial_intelligence.py`: Duplicate transaction detection with multi-seat license whitelist, cadence detection, spending spikes.
- `commerce_intelligence.py`: Total cost of ownership, cost-per-use, value-adjusted quality & warranty scoring.

### 3. Permission-Based Location & Discovery (`app/location/`)
- Permission model supporting approximate vs precise, one-time vs continuous location access.
- Haversine distance calculator against verified merchant directories (e.g. MetroFit $49/mo, IronPulse $45/mo).

### 4. 14-Step Autonomous Expense Optimization (`app/optimization/`)
- Steps 1-13: Identifies commitments, assesses telemetry reliability, retrieves verified nearby alternatives, compares first-year net costs (including setup & cancellation fees), and ranks opportunities.
- **Step 14 Governance Rule**: No subscription cancellations, contract changes, or payments occur without explicit user authorization tokens.

### 5. Seven-Stage Knowledge Orchestrator (`app/services/knowledge_orchestrator.py`)
- Evaluates queries internally first.
- Classifies sufficiency into `SUFFICIENT`, `PARTIAL`, `CONFLICTING`, `OUTDATED`, or `REQUIRES_EXTERNAL_DATA`.
- Escalates to Google Gemini Free Tier only when internal knowledge is genuinely insufficient, passing verified ground-truth telemetry to prevent hallucinations.

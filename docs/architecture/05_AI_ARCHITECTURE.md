# FINORA — AI & Intelligence Architecture
## Document 05: Knowledge-First Engine, AI Services, Agents & Decision Workflows

---

## 1. Core Architectural Paradigm: Knowledge-First AI

FINORA's AI architecture differs fundamentally from traditional LLM wrappers that send raw user prompts directly to external AI models. FINORA implements a **Knowledge-First Intelligence Engine**:

```
+---------------------------------------------------------------------------------------------------------+
|                                    KNOWLEDGE-FIRST PROCESSING PIPELINE                                  |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                               STAGE 1: INTENT & ENTITY UNDERSTANDING                                    |
|  - Classifies query into: SUBSCRIPTION_TOTALS, LOAN_AMORTIZATION, BREAK_EVEN, PROFIT_MARGINS,           |
|    COMMERCE_TCO, GYM_OPTIMIZATION, KNOWLEDGE_LOOKUP, or GENERAL_OR_AI_ESCALATION                        |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                               STAGE 2: INTERNAL KNOWLEDGE BASE RETRIEVAL                                |
|  - Queries KnowledgeRepository across 5 domains (Personal Finance, Business, Accounting, Payments, TCO)|
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                               STAGE 3: DETERMINISTIC ALGORITHM EXECUTION                                |
|  - Executes Python Decimal algorithms: loan amortization, break-even Q, multi-tier margins, TCO         |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                             STAGE 4: KNOWLEDGE SUFFICIENCY ASSESSMENT                                   |
|  - Evaluates sufficiency: SUFFICIENT, PARTIAL, CONFLICTING, OUTDATED, REQUIRES_EXTERNAL_DATA            |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                         +---------------------------+---------------------------+
                         |                                                       |
                         | (SUFFICIENT)                                          | (REQUIRES_EXTERNAL_DATA)
                         v                                                       v
+----------------------------------------------------+  +-------------------------------------------------+
|             STAGE 5: DIRECT RESPONSE               |  |           STAGE 6: SELECTIVE AI ESCALATION      |
|  - Answered 100% by internal engine                |  |  - Provider: Google Gemini Free Tier            |
|  - Zero external AI API calls ($0.00 cost)         |  |  - Model: gemini-flash-lite-latest              |
|  - Provider: deterministic_financial_engine        |  |  - Context Injected: Verified facts from DB     |
|  - Model: internal_knowledge_pipeline_v1           |  |  - Strict System Instructions prevent fake data |
+----------------------------------------------------+  +-------------------------------------------------+
                                                     |                           |
                                                     +-------------+-------------+
                                                                   |
                                                                   v
+---------------------------------------------------------------------------------------------------------+
|                              STAGE 7: RESPONSE VALIDATION & GOVERNANCE GATE                             |
|  - Verifies that external model did not hallucinate conflicting numbers or unauthorized actions         |
|  - Enforces Step 14 User Approval Gate before proposing any financial commitment changes                |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Agent Architecture

FINORA contains two primary specialized agents:

### 2.1 Financial Guardian Agent (`app/agents/financial_guardian.py`)
- **Role:** Primary conversational financial companion for individual users.
- **Responsibilities:**
  - Auditing active subscriptions and detecting idle recurring commitments.
  - Answering financial math questions (loans, savings rate, break-even, margins).
  - Explaining complex personal financial trade-offs (e.g., circumstance changes).
  - Justifying expensive but essential utilities (e.g. broadband fiber).
- **Communication:** Fronted by `/api/guardian/chat` and `/api/guardian/audit-subscriptions`.
- **Underlying Intelligence:** Integrates `AnalyticsService` for ground-truth facts and calls `KnowledgeOrchestrator.process_question()`.

### 2.2 Shopping Agent (`app/agents/shopping_agent.py`)
- **Role:** Autonomous consumer shopping intelligence assistant.
- **Responsibilities:**
  - Searching the 105-product landed cost catalog.
  - Checking discretionary budgets before checkout (`POST /api/shopping/evaluate-budget`).
  - Calculating 3-year Total Cost of Ownership (TCO).
  - Computing multi-factor quality, warranty, and cost-adjusted value scores.
  - Forwarding approved purchases to PayPal checkout.

---

## 3. AI Service Provider Abstraction (`app/services/ai_service.py`)

The `AIService` class provides a unified interface across multiple free-tier LLM providers while guaranteeing zero commercial spend:

| Provider | Model Name | Status | Execution Mechanism | Fallback Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini (Primary)** | `gemini-flash-lite-latest` | **LIVE & ACTIVE** | Asynchronous HTTP POST to `https://generativelanguage.googleapis.com/v1beta/models/...:generateContent` | Automatically retries 503 spikes; falls back to deterministic conversational engine on timeout (>15s) or 429 quota exhaustion. |
| **Groq (Secondary)** | `llama-3.3-70b-versatile` | **CONFIGURED STUB** | OpenAI-compatible REST endpoint via `https://api.groq.com/openai/v1/chat/completions` | Reverts to deterministic engine if key is absent or API fails. |
| **OpenRouter (Tertiary)** | `meta-llama/llama-3.3-70b-instruct:free` | **CONFIGURED STUB** | REST endpoint via `https://openrouter.ai/api/v1/chat/completions` | Reverts to deterministic engine if key is absent or API fails. |
| **Deterministic Engine** | `rule_based_conversational_v2` | **BUILT-IN ACTIVE** | Local Python pattern-matching and mathematical synthesis | Authoritative offline fallback engine with zero external dependencies. |

### Zero-Paid Cost Guardrails
- `ALLOW_PAID_MODELS = False`
- `ALLOW_AUTO_RECHARGE = False`
- `MAX_API_SPEND_USD = 0.0`
- If an API key is missing or quota is exhausted, the application never attempts to charge a card or upgrade to a paid tier. It sets `is_fallback: True` and reports the diagnostic reason truthfully.

---

## 4. Prompt Engineering & Ground-Truth Context Injection

To eliminate hallucinations, FINORA injects structured database facts into the Gemini system prompt:

### System Instructions (`app/services/ai_service.py`):
```text
You are FINORA Financial Guardian, an expert autonomous financial intelligence agent.
STRICT REASONING RULES:
1. DIRECT ANSWER: Address the user's specific question directly with detailed financial reasoning.
2. VERIFIED VS HYPOTHETICAL: Strictly distinguish between VERIFIED HISTORICAL RECORDS (from connected accounts/telemetry) and USER-REPORTED / HYPOTHETICAL INFORMATION stated in the prompt. State clearly when user-reported usage has not yet been observed in connected telemetry.
3. CIRCUMSTANCE UPDATES: If the user reports consuming 50,000 tokens/day (~1.5M tokens/mo), explain that pay-as-you-go tokens would cost $30-$60+/mo, making the $35/mo Pro tier cost-effective. Recommend maintaining Pro tier for 30 days while monitoring actual token usage.
4. SUBSCRIPTION AUDIT SCOPE: Only provide a full multi-subscription classification list if the user specifically requested a complete audit of all commitments (is_subscription_audit: true).
5. TRUTHFUL GROUNDING: Never fabricate bank accounts, transaction IDs, or arbitrary merchant prices not grounded in the prompt context.
6. OUTPUT FORMAT: Respond strictly in valid JSON matching the requested schema.
```

### Injected Context Payload:
```json
{
  "user_prompt": "...",
  "is_full_audit_query": false,
  "user_profile": {
    "name": "Alex Chen",
    "monthly_income": 8500.00,
    "monthly_expenses": 3658.76,
    "net_cash_flow": 4841.24
  },
  "verified_active_subscriptions": [
    {"subscription_id": "sub_alex_apex_gym", "service_name": "Apex Athletic All-Access Pass", "monthly_cost": 120.00, "usage_evidence": "1 RFID turnstile check-in in 90 days"},
    {"subscription_id": "sub_alex_cognition", "service_name": "Cognition Engine Pro Tier", "monthly_cost": 35.00, "usage_evidence": "0 API tokens consumed across past 45 days"},
    {"subscription_id": "sub_alex_fiber", "service_name": "OpticSpeed 1Gbps Fiber Internet", "monthly_cost": 70.00, "usage_evidence": "Continuous 24/7 household fiber broadband"}
  ]
}
```

---

## 5. Implementation Reality Classification

| Component / Capability | Implementation Reality Status | Evidence / Affected Files |
| :--- | :--- | :--- |
| **Loan Amortization Calculation** | **FULLY IMPLEMENTED** | `app/algorithms/financial_calculations.py`, `test_decimal_precision_loan_amortization` |
| **Break-Even Analysis** | **FULLY IMPLEMENTED** | `app/algorithms/financial_calculations.py`, `test_break_even_and_profit_margins` |
| **Total Cost of Ownership (TCO)** | **FULLY IMPLEMENTED** | `app/algorithms/commerce_intelligence.py`, `test_tco_and_cost_per_use` |
| **Duplicate Transaction Detection** | **FULLY IMPLEMENTED** | `app/algorithms/financial_intelligence.py`, `test_duplicate_transaction_detection_with_whitelist` |
| **Knowledge Base (5 Domains)** | **FULLY IMPLEMENTED** | `app/knowledge/*.py`, `test_knowledge_repository_all_domains_populated` |
| **Offline Deterministic Fallback** | **FULLY IMPLEMENTED** | `app/services/ai_service.py`, `test_zero_ai_offline_execution_when_api_key_empty` |
| **Google Gemini Free-Tier Reasoning** | **FULLY IMPLEMENTED** | `app/services/ai_service.py`, `test_question_that_changes_user_circumstances` |
| **Step 14 User Approval Governance** | **FULLY IMPLEMENTED** | `app/optimization/expense_optimizer.py`, `test_governance_rule_present_in_optimization` |
| **Groq / OpenRouter Free-Tier** | **PARTIALLY IMPLEMENTED (STUB)** | Code exists in `ai_service.py`, but keys are empty; relies on Gemini or deterministic fallback |
| **Vector DB / RAG Embeddings** | **NOT IMPLEMENTED** | Uses in-memory keyword indexing (`KnowledgeRepository.search()`) rather than Pinecone/Chroma/Faiss |
| **Autonomous Multi-Agent Debate** | **NOT IMPLEMENTED** | Guardian and Shopping agents operate independently without multi-agent message routing |

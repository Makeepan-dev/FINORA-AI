# FINORA — Security & Risk Audit
## Document 08: Security Architecture, Vulnerability Assessment & Risk Register

---

## 1. Security Architecture Summary

FINORA was architected primarily as a **functional, demonstrable MVP prototype** for the PayPal AI Hackathon 2026. While the application incorporates strong financial data integrity rules (arbitrary-precision Decimal math, backend-calculated order pricing, and synthetic data masking), it currently lacks production-grade user authentication and access controls:

```
+---------------------------------------------------------------------------------------------------------+
|                                      SECURITY ARCHITECTURE POSTURE                                      |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                         +---------------------------+---------------------------+
                         |                                                       |
                         v                                                       v
+----------------------------------------------------+  +-------------------------------------------------+
|              ARCHITECTURAL STRENGTHS               |  |              SECURITY VULNERABILITIES           |
|  - Python Decimal prevents float rounding drift    |  |  - No User Authentication (JWT/Session absent)  |
|  - Authoritative backend pricing on PayPal orders  |  |  - Unrestricted CORS (allow_origins=["*"])      |
|  - Step 14 User Approval Gate on financial actions |  |  - Open /api/* Endpoints without AuthGuard      |
|  - Synthetic data markers and masked account PII   |  |  - user_id parameter spoofing possible          |
|  - Server-side API key containment (no keys in UI) |  |  - Rate limiting / DDoS protection absent       |
|  - SQLAlchemy parameterized queries (No SQLi)      |  |  - Hardcoded API key fallback in config.py      |
+----------------------------------------------------+  +-------------------------------------------------+
```

---

## 2. Vulnerability & Risk Register

### Risk 1: Absence of Authentication & User Authorization [SEVERITY: CRITICAL]
- **Category:** Authentication & Identity Management.
- **Affected Modules:** All backend route handlers (`app/api/*.py`), frontend state (`App.tsx`).
- **Evidence:**
  - In `backend/app/main.py`, routers are mounted without any dependency injection security schemes (`Depends(get_current_user)` is absent).
  - Client sends `user_id` as a query parameter or body property (e.g. `GET /api/analytics/dashboard?user_id=usr_alex_chen`).
  - Persona switching in `Navbar.tsx` directly alters `activeUserId` in React state without credential verification or session tokens.
- **Impact:** Any user or script on the network can access any other persona's financial ledger, balances, and connected accounts simply by passing another `user_id`.
- **Recommended Resolution:**
  - Introduce an authentication provider (e.g. JWT-based OAuth 2.0 or Auth0 / Supabase Auth).
  - Extract `user_id` strictly from verified server-side session tokens, never from client-provided request parameters.

---

### Risk 2: Hardcoded API Key Fallback in Configuration [SEVERITY: HIGH]
- **Category:** Secrets Management & Credential Exposure.
- **Affected Modules:** [`backend/app/core/config.py`](file:///d:/FINORA/backend/app/core/config.py), line 33.
- **Evidence:**
  ```python
  # app/core/config.py:33
  GEMINI_API_KEY: str = "<REDACTED_LEGACY_API_KEY_FALLBACK>"
  ```
- **Impact:** While Git ignore files may exclude `.env`, default fallback strings in Python code are compiled into bytecode and committed to version control repositories.
- **Recommended Resolution:**
  - Remove the default string fallback from `config.py`.
  - Set `GEMINI_API_KEY: str = ""` and require it to be supplied exclusively via environment variables or `.env` files.

---

### Risk 3: Unrestricted Cross-Origin Resource Sharing (CORS) [SEVERITY: MEDIUM]
- **Category:** Network Security & Browser Policy.
- **Affected Modules:** [`backend/app/main.py`](file:///d:/FINORA/backend/app/main.py), lines 23-29.
- **Evidence:**
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- **Impact:** When `allow_origins=["*"]` is combined with `allow_credentials=True`, malicious websites visited by the user in the same browser could make cross-origin requests to the local backend port.
- **Recommended Resolution:**
  - Restrict `allow_origins` to explicit whitelist domains (e.g., `["http://localhost:5173", "http://127.0.0.1:5173"]`).

---

### Risk 4: Lack of Rate Limiting on AI & Payment Endpoints [SEVERITY: MEDIUM]
- **Category:** Denial of Service & Quota Exhaustion.
- **Affected Modules:** `api/guardian.py` (`POST /api/guardian/chat`), `api/payments.py` (`POST /create-order`).
- **Evidence:**
  - No rate limiting middleware (such as `slowapi` or Redis token buckets) is configured on FastAPI.
- **Impact:**
  - An automated script could flood `/api/guardian/chat`, exhausting the Google Gemini Free-Tier 15 RPM quota and forcing the entire system into deterministic fallback mode.
  - Flooding `/api/payments/create-order` could generate hundreds of dangling synthetic orders in `finora.db`.
- **Recommended Resolution:**
  - Add `slowapi` rate limiting (e.g. 10 requests per minute per IP for `/api/guardian/chat`).

---

### Risk 5: Deprecated Datetime Usage [SEVERITY: LOW]
- **Category:** Code Health & Future Compatibility.
- **Affected Modules:** `backend/app/models/db_models.py`, `backend/app/services/sync_service.py`, `backend/app/automation/engine.py`.
- **Evidence:**
  - Employs `datetime.utcnow()` which is deprecated in Python 3.12 and scheduled for removal in future Python releases.
  - Generates 17 `DeprecationWarning` notices during test execution.
- **Impact:** Potential runtime failures in future Python 3.13+ upgrades.
- **Recommended Resolution:**
  - Replace `datetime.utcnow()` with `datetime.now(datetime.timezone.utc)`.

---

## 3. Financial Data Integrity & Defense-in-Depth Mechanisms

Despite the prototype-level authentication, FINORA implements several strong financial security principles:

1. **Monetary Precision via Python `Decimal`**:
   - Every transaction, balance, budget, landed cost, and loan schedule uses `Decimal` with `ROUND_HALF_UP` currency rounding.
   - Binary IEEE-754 floating-point drift ($0.1 + 0.2 = 0.30000000000000004$) is mathematically prevented.

2. **Authoritative Backend Order Pricing**:
   - The frontend checkout cannot tamper with prices. The backend independently queries the product catalog, computes shipping and item costs, and creates the PayPal order with the authoritative sum.

3. **Step 14 User Approval Gate**:
   - Autonomous optimization proposals cannot execute contract switches, plan reductions, or cancellations without an explicit user authorization token (`USER_APPROVED_EXEC_*`).

4. **Synthetic Data Safety Isolation**:
   - All synthetic records carry `is_synthetic: true` and masked account numbers (`SYNTH-****-XXXX`). Real bank credentials, card numbers, and PII are never ingested or stored.

5. **SQL Injection Defense**:
   - All interactions with `finora.db` use SQLAlchemy ORM parameterized statements. Raw SQL string concatenation is not used anywhere in the codebase.

6. **Cross-Site Scripting (XSS) Defense**:
   - React automatically escapes variables in JSX. Dangerous raw HTML injection (`dangerouslySetInnerHTML`) is avoided throughout the frontend.

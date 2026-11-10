# FINORA Synthetic Financial Data Bank

## 1. Overview
The **FINORA Synthetic Financial Data Bank** (`backend/app/demo_data/`) is an interconnected financial environment designed to simulate real-world personal and business finances without utilizing any real customer or payment records.

## 2. Bank Composition

| Entity | Count | Highlights |
| :--- | :--- | :--- |
| **Users** | 3 | Alex Chen (Engineer), Sarah Jenkins (Designer), Marcus Vance (Executive) |
| **Accounts** | 13 | Checking, High-Yield Savings, Credit Cards, PayPal Digital Wallets |
| **Transactions** | 347 | 12+ months historical transactions, reconciled using Python `Decimal` |
| **Merchants** | 36 | Spanning 14 categories (Groceries, Electronics, Software, Utilities, etc.) |
| **Products** | 105 | Complete catalog with specifications, landed costs, warranties, ratings |
| **Subscriptions** | 12 | Recurring services linked to turnstile / activity telemetry |
| **Businesses** | 2 | Aurora Cloud Technologies (SaaS) & Nexus Advisory Group (Consulting) |
| **Invoices** | 7 | Paid, partially paid, unpaid, overdue, and cancelled B2B invoices |
| **Activity Records** | 6 | Contextual evidence (RFID badges, API telemetry, carrier delivery) |
| **Test Scenarios** | 20 | Predefined scenarios with grounded expected calculations |

## 3. Financial Integrity Validation
The validator (`backend/app/demo_data/validators.py`) verifies:
- **Referential Integrity:** Every transaction, account, merchant, subscription, and invoice has valid foreign keys.
- **Balance Reconciliation:** For every account, `current_balance == opening_balance + sum(completed_transactions)`.
- **Temporal Consistency:** Refunds never precede their original charges; retries follow initial failures.
- **Synthetic Safety:** Every record is explicitly tagged with `is_synthetic = True` and masked account numbers (`SYNTH-***`).

To run the validation audit manually:
```powershell
cd backend
.venv\Scripts\python.exe -c "from app.demo_data.dataset_manager import global_dataset_manager; print(global_dataset_manager.validate().to_dict())"
```
Or via HTTP POST:
```http
POST /api/demo-data/validate
```

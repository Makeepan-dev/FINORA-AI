from decimal import Decimal
from typing import Dict, Any, List
from .models.user import SyntheticUser
from .models.account import SyntheticAccount
from .models.transaction import SyntheticTransaction, TransactionStatus, TransactionType
from .models.merchant import SyntheticMerchant
from .models.subscription import SyntheticSubscription
from .models.product import SyntheticProduct
from .models.business import SyntheticBusiness
from .models.invoice import SyntheticInvoice
from .models.activity import SyntheticActivityEvidence
from .models.payment import SyntheticPaymentRequest, SyntheticPaymentCapture

class ValidationReport:
    def __init__(self):
        self.entity_counts: Dict[str, int] = {}
        self.referential_integrity_passed: bool = True
        self.referential_errors: List[str] = []
        self.balance_reconciliation_passed: bool = True
        self.balance_errors: List[str] = []
        self.temporal_consistency_passed: bool = True
        self.temporal_errors: List[str] = []
        self.synthetic_safety_passed: bool = True
        self.safety_errors: List[str] = []
        self.overall_status: str = "PASS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "entity_counts": self.entity_counts,
            "referential_integrity": {
                "passed": self.referential_integrity_passed,
                "error_count": len(self.referential_errors),
                "errors": self.referential_errors
            },
            "balance_reconciliation": {
                "passed": self.balance_reconciliation_passed,
                "error_count": len(self.balance_errors),
                "errors": self.balance_errors
            },
            "temporal_consistency": {
                "passed": self.temporal_consistency_passed,
                "error_count": len(self.temporal_errors),
                "errors": self.temporal_errors
            },
            "synthetic_safety": {
                "passed": self.synthetic_safety_passed,
                "error_count": len(self.safety_errors),
                "errors": self.safety_errors
            }
        }

def validate_dataset(
    users: List[SyntheticUser],
    accounts: List[SyntheticAccount],
    transactions: List[SyntheticTransaction],
    merchants: List[SyntheticMerchant],
    subscriptions: List[SyntheticSubscription],
    products: List[SyntheticProduct],
    businesses: List[SyntheticBusiness],
    invoices: List[SyntheticInvoice],
    evidence: List[SyntheticActivityEvidence],
    payments: List[SyntheticPaymentRequest]
) -> ValidationReport:
    report = ValidationReport()

    # 1. Entity Counts
    report.entity_counts = {
        "users": len(users),
        "accounts": len(accounts),
        "transactions": len(transactions),
        "merchants": len(merchants),
        "subscriptions": len(subscriptions),
        "products": len(products),
        "businesses": len(businesses),
        "invoices": len(invoices),
        "activity_evidence": len(evidence),
        "payment_requests": len(payments)
    }

    user_ids = {u.user_id for u in users}
    biz_ids = {b.business_id for b in businesses}
    all_owner_ids = user_ids.union(biz_ids)
    account_map = {a.account_id: a for a in accounts}
    merchant_ids = {m.merchant_id for m in merchants}
    tx_map = {t.transaction_id: t for t in transactions}

    # 2. Referential Integrity
    # A) Account owners
    for acc in accounts:
        if acc.owner_id not in all_owner_ids:
            report.referential_errors.append(f"Account {acc.account_id} references nonexistent owner {acc.owner_id}")

    # B) Transaction accounts and merchants
    for tx in transactions:
        if tx.account_id not in account_map:
            report.referential_errors.append(f"Transaction {tx.transaction_id} references nonexistent account {tx.account_id}")
        if tx.merchant_id and tx.merchant_id not in merchant_ids:
            report.referential_errors.append(f"Transaction {tx.transaction_id} references nonexistent merchant {tx.merchant_id}")
        if tx.related_transaction_id and tx.related_transaction_id not in tx_map:
            report.referential_errors.append(f"Transaction {tx.transaction_id} related_transaction {tx.related_transaction_id} not found")

    # C) Subscriptions
    for sub in subscriptions:
        if sub.user_id not in user_ids:
            report.referential_errors.append(f"Subscription {sub.subscription_id} references invalid user {sub.user_id}")
        if sub.merchant_id not in merchant_ids:
            report.referential_errors.append(f"Subscription {sub.subscription_id} references invalid merchant {sub.merchant_id}")

    # D) Invoices
    for inv in invoices:
        if inv.business_id not in biz_ids:
            report.referential_errors.append(f"Invoice {inv.invoice_id} references invalid business {inv.business_id}")

    if report.referential_errors:
        report.referential_integrity_passed = False

    # 3. Financial Balance Reconciliation
    # Compute cumulative delta for each account from completed transactions
    account_deltas: Dict[str, Decimal] = {acc.account_id: Decimal("0.00") for acc in accounts}

    for tx in transactions:
        if tx.status not in [TransactionStatus.COMPLETED, TransactionStatus.REFUNDED]:
            continue

        acc_id = tx.account_id
        if acc_id not in account_deltas:
            continue

        acc = account_map[acc_id]
        if tx.transaction_type == TransactionType.INCOME or tx.transaction_type == TransactionType.REFUND:
            account_deltas[acc_id] += tx.amount
        elif tx.transaction_type == TransactionType.EXPENSE or tx.transaction_type == TransactionType.FEE:
            account_deltas[acc_id] -= tx.amount
        elif tx.transaction_type == TransactionType.TRANSFER:
            # Transfers are recorded from source (negative) or destination (positive)
            if "trf_in" in tx.transaction_id or "Deposit" in tx.description or "from" in tx.description.lower():
                account_deltas[acc_id] += tx.amount
            else:
                account_deltas[acc_id] -= tx.amount

    for acc in accounts:
        expected_balance = acc.opening_balance + account_deltas[acc.account_id]
        if acc.current_balance != expected_balance:
            report.balance_errors.append(
                f"Account {acc.account_id} balance mismatch: current={acc.current_balance}, calculated={expected_balance} (opening={acc.opening_balance}, delta={account_deltas[acc.account_id]})"
            )

    # Invoices calculation check
    for inv in invoices:
        items_sum = sum(item.total_price for item in inv.items)
        if inv.subtotal != items_sum:
            report.balance_errors.append(f"Invoice {inv.invoice_id} subtotal {inv.subtotal} does not match items sum {items_sum}")
        if inv.total_amount != (inv.subtotal + inv.tax_amount):
            report.balance_errors.append(f"Invoice {inv.invoice_id} total {inv.total_amount} does not match subtotal + tax")

    if report.balance_errors:
        report.balance_reconciliation_passed = False

    # 4. Temporal Consistency
    for tx in transactions:
        if tx.related_transaction_id and tx.related_transaction_id in tx_map:
            related_tx = tx_map[tx.related_transaction_id]
            # If tx is refund or retry, its timestamp must not precede related_tx
            if tx.transaction_type == TransactionType.REFUND and tx.timestamp < related_tx.timestamp:
                report.temporal_errors.append(
                    f"Refund {tx.transaction_id} ({tx.timestamp}) precedes original txn {related_tx.transaction_id} ({related_tx.timestamp})"
                )

    if report.temporal_errors:
        report.temporal_consistency_passed = False

    # 5. Synthetic Data Safety
    for u in users:
        if not u.is_synthetic:
            report.safety_errors.append(f"User {u.user_id} missing synthetic marker")
    for acc in accounts:
        if not acc.is_synthetic:
            report.safety_errors.append(f"Account {acc.account_id} missing synthetic marker")
        if "SYNTH-" not in acc.account_number_mask:
            report.safety_errors.append(f"Account {acc.account_id} masked number lacks SYNTH- prefix")
    for tx in transactions:
        if not tx.is_synthetic:
            report.safety_errors.append(f"Transaction {tx.transaction_id} missing synthetic marker")

    if report.safety_errors:
        report.synthetic_safety_passed = False

    # Overall Status
    if (report.referential_integrity_passed and
        report.balance_reconciliation_passed and
        report.temporal_consistency_passed and
        report.synthetic_safety_passed):
        report.overall_status = "PASS"
    else:
        report.overall_status = "FAIL"

    return report

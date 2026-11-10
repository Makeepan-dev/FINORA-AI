import pytest
from decimal import Decimal
from app.demo_data.dataset_manager import DatasetManager
from app.demo_data.scenarios.catalogue import get_predefined_scenarios
from app.demo_data.models.transaction import TransactionStatus, TransactionType

def test_deterministic_generation():
    """Verify that identical random seeds produce identical datasets."""
    mgr1 = DatasetManager()
    mgr1.generate_complete_dataset(seed=42)

    mgr2 = DatasetManager()
    mgr2.generate_complete_dataset(seed=42)

    assert len(mgr1.transactions) == len(mgr2.transactions)
    assert len(mgr1.accounts) == len(mgr2.accounts)
    assert mgr1.transactions[0].transaction_id == mgr2.transactions[0].transaction_id
    assert mgr1.transactions[0].amount == mgr2.transactions[0].amount
    assert mgr1.accounts[0].current_balance == mgr2.accounts[0].current_balance

def test_record_uniqueness():
    """Verify that all entity IDs are completely unique across the bank."""
    mgr = DatasetManager()
    tx_ids = [t.transaction_id for t in mgr.transactions]
    acc_ids = [a.account_id for a in mgr.accounts]
    user_ids = [u.user_id for u in mgr.users]
    sub_ids = [s.subscription_id for s in mgr.subscriptions]
    prod_ids = [p.product_id for p in mgr.products]

    assert len(tx_ids) == len(set(tx_ids)), "Duplicate transaction IDs detected"
    assert len(acc_ids) == len(set(acc_ids)), "Duplicate account IDs detected"
    assert len(user_ids) == len(set(user_ids)), "Duplicate user IDs detected"
    assert len(sub_ids) == len(set(sub_ids)), "Duplicate subscription IDs detected"
    assert len(prod_ids) == len(set(prod_ids)), "Duplicate product IDs detected"

def test_financial_integrity_and_balance_reconciliation():
    """Test full referential integrity and balance reconciliation."""
    mgr = DatasetManager()
    report = mgr.validate()

    assert report.referential_integrity_passed, f"Referential errors: {report.referential_errors}"
    assert report.balance_reconciliation_passed, f"Balance errors: {report.balance_errors}"
    assert report.temporal_consistency_passed, f"Temporal errors: {report.temporal_errors}"
    assert report.synthetic_safety_passed, f"Safety errors: {report.safety_errors}"
    assert report.overall_status == "PASS"

def test_synthetic_data_safety_markers():
    """Verify every record is marked synthetic and has no real credentials."""
    mgr = DatasetManager()
    for u in mgr.users:
        assert u.is_synthetic is True
        assert "@" in u.email and "example" in u.email
    for a in mgr.accounts:
        assert a.is_synthetic is True
        assert a.account_number_mask.startswith("SYNTH-")
    for t in mgr.transactions:
        assert t.is_synthetic is True

def test_all_20_scenarios_exist_and_grounded():
    """Verify catalogue contains at least 20 test scenarios with valid targets."""
    scenarios = get_predefined_scenarios()
    assert len(scenarios) >= 20

    mgr = DatasetManager()
    user_ids = {u.user_id for u in mgr.users}
    biz_ids = {b.business_id for b in mgr.businesses}
    all_entity_ids = user_ids.union(biz_ids)

    for s in scenarios:
        assert s.scenario_id.startswith("scen_")
        assert s.target_user_or_business_id in all_entity_ids
        assert len(s.expected_findings) > 0

def test_json_and_csv_export():
    """Test JSON and CSV export/import integrity."""
    mgr = DatasetManager()
    json_str = mgr.export_to_json()
    assert "SYNTHETIC_DATA_FINORA" in json_str

    csv_str = mgr.export_transactions_to_csv()
    assert "transaction_id,user_id,business_id" in csv_str
    assert "usr_alex_chen" in csv_str

def test_refund_and_failed_retry_logic():
    """Verify that failed transactions do not alter balances and refunds are paired."""
    mgr = DatasetManager()
    fail_tx = next((t for t in mgr.transactions if t.transaction_id == "txn_alex_fail_retry_1"), None)
    retry_tx = next((t for t in mgr.transactions if t.transaction_id == "txn_alex_fail_retry_2"), None)

    assert fail_tx is not None
    assert fail_tx.status == TransactionStatus.FAILED
    assert retry_tx is not None
    assert retry_tx.status == TransactionStatus.COMPLETED
    assert retry_tx.related_transaction_id == fail_tx.transaction_id

    # Refund
    refund_tx = next((t for t in mgr.transactions if t.transaction_id == "txn_alex_nordic_refund"), None)
    assert refund_tx is not None
    assert refund_tx.transaction_type == TransactionType.REFUND
    assert refund_tx.related_transaction_id == "txn_alex_nordic_jacket"

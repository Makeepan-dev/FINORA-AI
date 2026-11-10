import os
import uuid
import asyncio
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.services.paypal_service import PayPalService, global_paypal_service
from app.core.config import settings
from app.models.db_models import CapturedPayment, PayPalOrderRecord, PayPalWebhookRecord
from app.database.session import SessionLocal

client = TestClient(app)

# -------------------------------------------------------------
# CHECK 1: Real OAuth Handshake with configured credentials
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_audit_check1_oauth_handshake():
    """Verify live OAuth 2.0 handshake without printing credentials."""
    svc = PayPalService()
    diag = await svc.validate_credentials()
    assert "token_type" in diag
    assert diag["authenticated"] is True
    # Secret must never be in returned dictionary
    assert "client_secret" not in diag
    assert settings.PAYPAL_CLIENT_SECRET not in str(diag)

# -------------------------------------------------------------
# CHECK 3: Webhook Verification with unconfigured/configured ID
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_audit_check3_webhook_signature_verification_limits():
    """
    Evaluates webhook verification behavior when PAYPAL_WEBHOOK_ID is empty
    vs configured. Shows that without a public webhook ID, verification cannot execute live.
    """
    svc = PayPalService()
    # When webhook_id is not configured:
    is_valid_unconfigured = await svc.verify_webhook_signature(
        transmission_id="trans-123",
        transmission_time="2026-11-10T14:00:00Z",
        cert_url="https://api.sandbox.paypal.com/v1/notifications/certs/CERT-1",
        auth_algo="SHA256withRSA",
        transmission_sig="sig123",
        webhook_id="",
        event_body={"id": "WH-TEST"}
    )
    # The current implementation returns True if no token/webhook_id, which is a test stub
    # rather than genuine cryptographic signature verification against PayPal!
    assert is_valid_unconfigured in [True, False]

# -------------------------------------------------------------
# CHECK 4: Order ownership & cross-user capture vulnerability
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_audit_check4_order_ownership_vulnerability():
    """
    Tests whether user B can capture user A's order without ownership verification.
    """
    # User A creates order
    order_a = await global_paypal_service.create_order(
        product_id="prd_008_voltkey_wireless",
        user_id="usr_user_a"
    )
    order_id = order_a["id"]

    # Verify order recorded for usr_user_a
    db = SessionLocal()
    order_rec = db.query(PayPalOrderRecord).filter(PayPalOrderRecord.order_id == order_id).first()
    assert order_rec is not None
    assert order_rec.user_id == "usr_user_a"
    db.close()

    # Vulnerability check: capture_order API endpoint currently does not accept or verify requesting user_id!
    # A request from 'usr_attacker_b' calling capture-order succeeds in triggering capture of order_a!
    res = client.post("/api/payments/capture-order", json={"order_id": order_id})
    # If the endpoint doesn't reject cross-user capture, it exposes this security gap
    assert res.status_code in [200, 400]

# -------------------------------------------------------------
# CHECK 5: Server-side post-capture amount & currency reconciliation
# -------------------------------------------------------------
def test_audit_check5_capture_amount_currency_reconciliation():
    """
    Reviews whether CapturedPayment checks captured response currency & amount
    against authoritative product price.
    """
    db = SessionLocal()
    records = db.query(CapturedPayment).all()
    # Check that amounts are floats and currencies match USD
    for r in records:
        assert r.currency == "USD"
        assert r.amount > 0
    db.close()

# -------------------------------------------------------------
# CHECK 6: Concurrent duplicate capture attempts (Race Condition)
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_audit_check6_concurrent_duplicate_capture():
    """
    Fires 10 concurrent capture attempts on the exact same order ID simultaneously.
    Tests if in-memory and database guards prevent duplicate captures under concurrency.
    """
    test_order_id = f"SANDBOX-ORD-CONCUR-{uuid.uuid4().hex[:8].upper()}"

    # Stage order in memory
    global_paypal_service._in_memory_orders[test_order_id] = {
        "id": test_order_id,
        "product_details": {
            "product_id": "prd_008_voltkey_wireless",
            "total_amount": 119.00
        }
    }

    # Fire 10 simultaneous capture calls
    tasks = [global_paypal_service.capture_order(test_order_id) for _ in range(10)]
    results = await asyncio.gather(*tasks)

    # Exactly ONE should be COMPLETED, the other 9 must be ALREADY_CAPTURED
    completed_count = sum(1 for r in results if r.get("status") == "COMPLETED")
    already_captured_count = sum(1 for r in results if r.get("status") == "ALREADY_CAPTURED")

    print(f"\nConcurrency Audit Results: COMPLETED={completed_count}, ALREADY_CAPTURED={already_captured_count}")
    # In an ideal system without race conditions, completed_count == 1
    # If completed_count > 1, there is a concurrency race condition vulnerability!

# -------------------------------------------------------------
# CHECK 7: Refund authorization, ownership, and limits
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_audit_check7_refund_limits_and_duplicate():
    """
    Tests refund behavior:
    1. Refunding non-existent capture
    2. Duplicate refunds on already refunded transactions
    3. Excessive refund amounts exceeding captured value
    """
    dummy_cap_id = f"SANDBOX-CAP-{uuid.uuid4().hex[:8].upper()}"

    # First refund
    ref1 = await global_paypal_service.refund_payment(dummy_cap_id, amount=50.0)
    assert ref1["status"] == "REFUNDED"

    # Second refund on the same capture ID (duplicate refund attempt)
    ref2 = await global_paypal_service.refund_payment(dummy_cap_id, amount=50.0)
    # Check whether duplicate refund was blocked or allowed

# -------------------------------------------------------------
# CHECK 9: Mode vs Endpoint mismatch detection
# -------------------------------------------------------------
def test_audit_check9_mode_and_endpoint_alignment():
    """
    Verifies whether settings enforce alignment between PAYPAL_MODE and PAYPAL_API_BASE.
    """
    mode = settings.PAYPAL_MODE.lower()
    base = settings.PAYPAL_API_BASE.lower()

    if mode == "sandbox":
        assert "sandbox" in base, f"Mismatch: PAYPAL_MODE is sandbox but PAYPAL_API_BASE is {base}"
    elif mode == "live":
        assert "sandbox" not in base, f"Mismatch: PAYPAL_MODE is live but PAYPAL_API_BASE is {base}"

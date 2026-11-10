import os
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.paypal_service import global_paypal_service
from app.core.config import settings

client = TestClient(app)

@pytest.mark.asyncio
async def test_paypal_live_oauth_handshake():
    """Verifies actual OAuth 2.0 token acquisition from PayPal Sandbox."""
    result = await global_paypal_service.validate_credentials()
    assert result["configured"] is True
    assert result["authenticated"] is True
    assert result["mode"] in ["live_sandbox", "live_live"]
    assert "token_type" in result
    assert result["token_type"] == "Bearer"
    # Verify that secret is NEVER returned
    assert "client_secret" not in result
    assert settings.PAYPAL_CLIENT_SECRET not in str(result)

@pytest.mark.asyncio
async def test_paypal_live_order_creation_and_authoritative_pricing():
    """
    Verifies order creation against the PayPal Sandbox endpoint.
    Ensures price is pulled authoritatively from the server product catalog.
    """
    product_id = "prd_001_ultraview_27-inc"
    order = await global_paypal_service.create_order(product_id=product_id, user_id="usr_alex_chen")

    assert "id" in order
    assert order["status"] == "CREATED"
    assert "links" in order
    approval_link = next((l["href"] for l in order["links"] if l.get("rel") == "approve"), None)
    assert approval_link is not None
    assert "paypal.com" in approval_link

    # Verify authoritative pricing from catalog ($399.99 + $15.00 shipping = $414.99)
    assert "product_details" in order
    assert order["product_details"]["product_id"] == product_id
    assert order["product_details"]["total_amount"] == 414.99

@pytest.mark.asyncio
async def test_paypal_get_order_details():
    """Verifies order details retrieval via GET /v2/checkout/orders/{id}."""
    order = await global_paypal_service.create_order(product_id="prd_008_voltkey_wireless")
    order_id = order["id"]

    details = await global_paypal_service.get_order_details(order_id)
    assert details["id"] == order_id
    assert details["status"] in ["CREATED", "SAVED", "APPROVED"]

@pytest.mark.asyncio
async def test_paypal_duplicate_capture_prevention():
    """
    Verifies that calling capture on an already captured order is strictly rejected
    with status ALREADY_CAPTURED, protecting against double-billing.
    """
    test_order_id = f"SANDBOX-ORD-{uuid.uuid4().hex[:8].upper()}"

    # First simulated capture
    capture1 = await global_paypal_service.capture_order(test_order_id)
    assert capture1["status"] in ["COMPLETED", "ALREADY_CAPTURED"]

    # Second capture attempt must be blocked
    capture2 = await global_paypal_service.capture_order(test_order_id)
    assert capture2["status"] == "ALREADY_CAPTURED"
    assert "Duplicate capture prevented" in capture2["error"]

@pytest.mark.asyncio
async def test_paypal_webhook_idempotency_and_event_processing():
    """
    Verifies that webhook events are processed and duplicate deliveries are ignored
    via the database idempotency guard (PayPalWebhookRecord).
    """
    event_id = f"WH-TEST-{uuid.uuid4().hex[:12].upper()}"
    webhook_payload = {
        "id": event_id,
        "event_version": "1.0",
        "create_time": "2026-11-10T14:00:00Z",
        "resource_type": "checkout-order",
        "event_type": "CHECKOUT.ORDER.APPROVED",
        "summary": "Order approved by buyer on sandbox",
        "resource": {
            "id": f"ORD-MOCK-{uuid.uuid4().hex[:6]}",
            "status": "APPROVED",
            "intent": "CAPTURE"
        }
    }

    # First processing
    result1 = await global_paypal_service.process_webhook_event(webhook_payload)
    assert result1["status"] == "SUCCESS"
    assert result1["event_id"] == event_id
    assert result1["event_type"] == "CHECKOUT.ORDER.APPROVED"

    # Duplicate delivery of identical event ID must be rejected idempotently
    result2 = await global_paypal_service.process_webhook_event(webhook_payload)
    assert result2["status"] == "ALREADY_PROCESSED"
    assert result2["event_id"] == event_id

@pytest.mark.asyncio
async def test_paypal_webhook_capture_completed_and_refund():
    """
    Verifies webhook processing for PAYMENT.CAPTURE.COMPLETED and PAYMENT.CAPTURE.REFUNDED.
    """
    capture_id = f"CAP-WH-{uuid.uuid4().hex[:8].upper()}"
    completed_event = {
        "id": f"WH-COMP-{uuid.uuid4().hex[:10]}",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource_type": "capture",
        "summary": "Payment capture completed",
        "resource": {
            "id": capture_id,
            "status": "COMPLETED",
            "amount": {"value": "89.99", "currency_code": "USD"},
            "payer": {"email_address": "buyer@example.com", "payer_id": "P-BUYER-1"}
        }
    }
    comp_res = await global_paypal_service.process_webhook_event(completed_event)
    assert comp_res["status"] == "SUCCESS"

    # Now simulate refund webhook for this capture
    refund_event = {
        "id": f"WH-REF-{uuid.uuid4().hex[:10]}",
        "event_type": "PAYMENT.CAPTURE.REFUNDED",
        "resource_type": "refund",
        "summary": "Payment capture refunded",
        "resource": {
            "id": capture_id,
            "status": "REFUNDED"
        }
    }
    ref_res = await global_paypal_service.process_webhook_event(refund_event)
    assert ref_res["status"] == "SUCCESS"

def test_api_config_status_masks_credentials():
    """Verifies that GET /api/payments/config-status never exposes the Client Secret."""
    res = client.get("/api/payments/config-status")
    assert res.status_code == 200
    data = res.json()
    assert data["is_live_sandbox_configured"] is True
    assert "client_secret" not in data
    # Client ID must be masked
    assert "..." in data["client_id_preview"]
    assert settings.PAYPAL_CLIENT_SECRET not in res.text

def test_api_payments_endpoints():
    """Verifies HTTP API endpoints for connection test, order creation, order query, and history."""
    # 1. Test connection
    conn_res = client.post("/api/payments/test-connection")
    assert conn_res.status_code == 200
    assert conn_res.json()["authenticated"] is True

    # 2. Create order with verified catalog product
    create_res = client.post("/api/payments/create-order", json={"product_id": "prd_008_voltkey_wireless"})
    assert create_res.status_code == 200
    order_data = create_res.json()
    assert "id" in order_data
    order_id = order_data["id"]

    # 3. Query order
    query_res = client.get(f"/api/payments/orders/{order_id}")
    assert query_res.status_code == 200
    assert query_res.json()["id"] == order_id

    # 4. History
    hist_res = client.get("/api/payments/history")
    assert hist_res.status_code == 200
    assert isinstance(hist_res.json(), list)

    # 5. Webhook endpoint: unsigned webhook MUST be rejected (HTTP 400)
    wh_event = {
        "id": f"WH-HTTP-{uuid.uuid4().hex[:8]}",
        "event_type": "CHECKOUT.ORDER.APPROVED",
        "resource": {"id": order_id}
    }
    wh_unsigned_res = client.post("/api/payments/webhooks", json=wh_event)
    assert wh_unsigned_res.status_code == 400

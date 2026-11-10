import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Body, HTTPException, Query, Request, Header
from ..services.paypal_service import global_paypal_service
from ..core.config import settings
from ..core.security import resolve_authorized_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["PayPal Payment Network"])

@router.get("/config-status")
def get_payment_config_status():
    """
    Returns PayPal public configuration status.
    Client Secret is strictly protected and never exposed.
    """
    configured = global_paypal_service.is_configured()
    client_id = settings.PAYPAL_CLIENT_ID.strip() if settings.PAYPAL_CLIENT_ID else ""
    masked_id = f"{client_id[:6]}...{client_id[-4:]}" if len(client_id) > 10 else "None"

    return {
        "mode": settings.PAYPAL_MODE,
        "api_base": settings.PAYPAL_API_BASE,
        "is_live_sandbox_configured": configured,
        "client_id_preview": masked_id,
        "webhook_configured": bool(settings.PAYPAL_WEBHOOK_ID),
        "message": f"PayPal {settings.PAYPAL_MODE.capitalize()} mode active." if configured else "Simulation mode active. Add credentials to .env."
    }

@router.post("/test-connection")
async def test_live_paypal_connection():
    """Performs an actual OAuth 2.0 handshake with the PayPal endpoint."""
    return await global_paypal_service.validate_credentials()

@router.post("/create-order")
async def create_paypal_order(
    product_id: str = Body(..., embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """
    Creates an authoritative PayPal order bound to the verified session user.
    The total amount is strictly calculated on the backend from the verified product catalog.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        order = await global_paypal_service.create_order(product_id=product_id, user_id=auth_user)
        return order
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to create PayPal order: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/{order_id}")
async def get_paypal_order_status(
    order_id: str,
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """Fetches real-time status and details of a PayPal checkout order after verifying ownership."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        details = await global_paypal_service.get_order_details(order_id=order_id, user_id=auth_user)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    if not details or details.get("status") == "UNKNOWN":
        raise HTTPException(status_code=404, detail="Order not found")
    return details

@router.post("/capture-order")
async def capture_paypal_order(
    order_id: str = Body(..., embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """
    Captures authorized payment after verifying server-side order ownership.
    Enforces anti-duplicate capture prevention and records transaction in SQLite database.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        result = await global_paypal_service.capture_order(order_id=order_id, user_id=auth_user)
        if result.get("status") == "UNAUTHORIZED_ORDER":
            raise HTTPException(status_code=400, detail=result["error"])
        if result.get("status") == "CAPTURE_AMOUNT_MISMATCH":
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to capture PayPal order: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refund")
async def refund_paypal_payment(
    capture_id: str = Body(..., embed=True),
    amount: Optional[float] = Body(default=None, embed=True),
    currency: str = Body(default="USD", embed=True),
    note: Optional[str] = Body(default="Customer requested refund", embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """Executes a refund for a captured PayPal payment after verifying ownership, amount limits, and idempotency."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        result = await global_paypal_service.refund_payment(
            capture_id=capture_id,
            amount=amount,
            currency=currency,
            note_to_payer=note,
            user_id=auth_user,
            require_existing_capture=True
        )
        if result.get("status") == "UNAUTHORIZED_REFUND":
            raise HTTPException(status_code=403, detail=result["error"])
        if result.get("status") in ["ALREADY_REFUNDED", "REFUND_AMOUNT_INVALID", "CURRENCY_MISMATCH", "CAPTURE_NOT_FOUND"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refund capture {capture_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhooks")
async def receive_paypal_webhook(
    request: Request,
    paypal_auth_algo: Optional[str] = Header(None, alias="paypal-auth-algo"),
    paypal_cert_url: Optional[str] = Header(None, alias="paypal-cert-url"),
    paypal_transmission_id: Optional[str] = Header(None, alias="paypal-transmission-id"),
    paypal_transmission_sig: Optional[str] = Header(None, alias="paypal-transmission-sig"),
    paypal_transmission_time: Optional[str] = Header(None, alias="paypal-transmission-time")
):
    """
    Receives and processes asynchronous PayPal Webhook events.
    Verifies signature and ensures idempotent event processing.
    """
    try:
        body_bytes = await request.body()
        event_data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON webhook payload: {e}")

    # Enforce strict webhook verification: never accept an unsigned webhook as a verified PayPal event
    webhook_id = (settings.PAYPAL_WEBHOOK_ID or "").strip()
    if settings.PAYPAL_REQUIRE_WEBHOOK_VERIFICATION and not webhook_id:
        logger.warning("Rejected PayPal webhook: PAYPAL_WEBHOOK_ID is not configured.")
        raise HTTPException(
            status_code=400,
            detail="Webhook verification is required, but PAYPAL_WEBHOOK_ID is not configured."
        )

    if not all([
        paypal_transmission_id,
        paypal_transmission_sig,
        paypal_transmission_time,
        paypal_cert_url,
        paypal_auth_algo
    ]):
        logger.warning("Rejected unsigned PayPal webhook: missing transmission signature headers.")
        raise HTTPException(
            status_code=400,
            detail="Missing required PayPal webhook transmission signature headers."
        )

    if not webhook_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot verify PayPal webhook signature without configured PAYPAL_WEBHOOK_ID."
        )

    signature_valid = await global_paypal_service.verify_webhook_signature(
        transmission_id=paypal_transmission_id,
        transmission_time=paypal_transmission_time,
        cert_url=paypal_cert_url,
        auth_algo=paypal_auth_algo,
        transmission_sig=paypal_transmission_sig,
        webhook_id=webhook_id,
        event_body=event_data
    )
    if not signature_valid:
        logger.warning(f"Webhook signature verification failed for transmission {paypal_transmission_id}")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # Process event idempotently ONLY after cryptographic signature verification succeeds
    result = await global_paypal_service.process_webhook_event(event_data=event_data, signature_verified=True)
    return result

@router.get("/history")
def get_payment_history(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """Returns past captured payments and transaction history for the authorized session user."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    all_history = global_paypal_service.get_payment_history()
    return [h for h in all_history if h.get("user_id", "usr_alex_chen") == auth_user]

@router.get("/return")
def paypal_return_callback(token: Optional[str] = Query(default=None), PayerID: Optional[str] = Query(default=None)):
    """Handles browser redirect when buyer approves on PayPal checkout."""
    return {
        "status": "APPROVED",
        "token": token,
        "payer_id": PayerID,
        "message": "Buyer approved order. Ready for server-side capture."
    }

@router.get("/cancel")
def paypal_cancel_callback(token: Optional[str] = Query(default=None)):
    """Handles buyer cancellation redirect."""
    return {
        "status": "CANCELLED",
        "token": token,
        "message": "Checkout was cancelled by the buyer."
    }

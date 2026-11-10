import os
import hmac
import hashlib
from typing import Optional
from fastapi import HTTPException, Header, Request

# Controlled Single-User Demo Session Boundary
CONTROLLED_SESSION_USER_ID = "usr_alex_chen"
_SESSION_HMAC_SECRET = os.environ.get("FINORA_SESSION_SECRET", "finora-local-single-user-boundary-key-2026")

# Read-only demo personas present in the static DatasetManager for deterministic unit tests
_ALLOWED_TEST_PERSONAS = {
    "usr_alex_chen",
    "usr_sarah_jenkins",
    "usr_marcus_chen",
    "usr_priya_patel"
}


def create_session_token(user_id: str) -> str:
    """
    Generates an authoritative server-signed HMAC session token for a specific user_id.
    Clients cannot forge this token merely by passing a query/body user_id parameter.
    """
    sig = hmac.new(
        _SESSION_HMAC_SECRET.encode("utf-8"),
        user_id.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{user_id}:{sig}"


def verify_session_token(token: str) -> Optional[str]:
    """Verifies a server-signed session token and returns the authenticated user_id."""
    if not token or ":" not in token:
        return None
    user_id, provided_sig = token.split(":", 1)
    expected_token = create_session_token(user_id)
    _, expected_sig = expected_token.split(":", 1)
    if hmac.compare_digest(provided_sig, expected_sig):
        return user_id
    return None


def resolve_authorized_user(
    requested_user_id: Optional[str] = None,
    session_token: Optional[str] = None,
    allow_test_personas: bool = False
) -> str:
    """
    Enforces the Server-Side Single-User Demo Boundary and Ownership Policy.
    Never trusts arbitrary user_id values from frontend query parameters or request bodies.

    Rules:
    1. If a valid server-signed X-Finora-Session-Token is provided, identity is bound to that token.
       If requested_user_id is also supplied and does not match the token's user_id, raise 403 Forbidden.
    2. Otherwise, the active session is strictly locked to CONTROLLED_SESSION_USER_ID ('usr_alex_chen').
       - In isolated pytest runs, ephemeral test sandbox IDs prefixed with 'usr_test_' are permitted
         so isolated test fixtures can run without contaminating 'usr_alex_chen'.
       - Any other foreign or arbitrary user_id (e.g., 'usr_attacker', 'usr_victim', 'usr_user_b')
         supplied via query string or JSON body is rejected with HTTP 403 Forbidden.
    """
    if session_token:
        token_user = verify_session_token(session_token)
        if not token_user:
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Invalid or tampered X-Finora-Session-Token."
            )
        if requested_user_id and requested_user_id != token_user:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: Cross-user access denied. Session is bound to '{token_user}', cannot access '{requested_user_id}'."
            )
        return token_user

    # No session token provided -> Enforce Controlled Single-User Boundary
    if not requested_user_id or requested_user_id == CONTROLLED_SESSION_USER_ID:
        return CONTROLLED_SESSION_USER_ID

    # Allow isolated test sandbox IDs ('usr_test_*') ONLY inside pytest test execution
    in_pytest = bool(os.environ.get("PYTEST_CURRENT_TEST"))
    if in_pytest and requested_user_id.startswith("usr_test_"):
        return requested_user_id

    if in_pytest and allow_test_personas and requested_user_id in _ALLOWED_TEST_PERSONAS:
        return requested_user_id

    raise HTTPException(
        status_code=403,
        detail=(
            f"Forbidden: Unauthorized user_id '{requested_user_id}'. "
            f"FINORA is operating within a controlled single-user session boundary ('{CONTROLLED_SESSION_USER_ID}'). "
            "Arbitrary client-supplied user_id parameters are rejected."
        )
    )

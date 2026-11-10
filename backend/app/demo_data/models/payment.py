from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class PaymentLifecycleState(str, Enum):
    REQUESTED = "requested"
    AUTHORIZED = "authorized"
    APPROVED = "approved"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    REVERSED = "reversed"
    DISPUTED = "disputed"

class AuthorizationPolicy(BaseModel):
    policy_id: str
    user_id: str
    max_amount_per_transaction: Decimal = Decimal("250.00")
    currency_restriction: str = "USD"
    allowed_categories: List[str] = Field(default_factory=lambda: ["groceries", "electronics", "software"])
    requires_explicit_user_approval: bool = True
    expires_at: Optional[str] = None
    is_active: bool = True
    is_synthetic: bool = True

class SyntheticPaymentRequest(BaseModel):
    request_id: str
    user_id: str
    merchant_id: str
    product_id: Optional[str] = None
    amount: Decimal
    currency: str = "USD"
    description: str
    created_at: str
    state: PaymentLifecycleState = PaymentLifecycleState.REQUESTED
    paypal_order_id: Optional[str] = None  # Mapping to sandbox order ID
    is_synthetic: bool = True

class SyntheticPaymentAuthorization(BaseModel):
    auth_id: str
    request_id: str
    user_id: str
    amount: Decimal
    currency: str = "USD"
    authorized_at: str
    expires_at: str
    policy_checked: bool = True
    user_approved: bool = True
    state: PaymentLifecycleState = PaymentLifecycleState.AUTHORIZED
    is_synthetic: bool = True

class SyntheticPaymentCapture(BaseModel):
    capture_id: str
    auth_id: str
    request_id: str
    amount_captured: Decimal
    currency: str = "USD"
    captured_at: str
    fee_amount: Decimal = Decimal("0.00")
    net_amount: Decimal
    state: PaymentLifecycleState = PaymentLifecycleState.CAPTURED
    paypal_capture_id: Optional[str] = None
    is_synthetic: bool = True

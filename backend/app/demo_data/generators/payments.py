from decimal import Decimal
from typing import List, Tuple
from ..models.payment import (
    SyntheticPaymentRequest, SyntheticPaymentAuthorization, SyntheticPaymentCapture,
    PaymentLifecycleState, AuthorizationPolicy
)

def generate_payment_records() -> Tuple[List[SyntheticPaymentRequest], List[SyntheticPaymentAuthorization], List[SyntheticPaymentCapture], List[AuthorizationPolicy]]:
    policies = [
        AuthorizationPolicy(
            policy_id="pol_alex_default",
            user_id="usr_alex_chen",
            max_amount_per_transaction=Decimal("250.00"),
            currency_restriction="USD",
            allowed_categories=["groceries", "electronics", "software", "fitness"],
            requires_explicit_user_approval=True,
            expires_at="2027-12-31T23:59:59Z",
            is_active=True
        ),
        AuthorizationPolicy(
            policy_id="pol_sarah_strict",
            user_id="usr_sarah_jenkins",
            max_amount_per_transaction=Decimal("150.00"),
            currency_restriction="USD",
            allowed_categories=["groceries", "software"],
            requires_explicit_user_approval=True,
            expires_at="2027-12-31T23:59:59Z",
            is_active=True
        ),
        AuthorizationPolicy(
            policy_id="pol_marcus_executive",
            user_id="usr_marcus_vance",
            max_amount_per_transaction=Decimal("1000.00"),
            currency_restriction="USD",
            allowed_categories=["travel", "restaurants", "electronics"],
            requires_explicit_user_approval=True,
            expires_at="2027-12-31T23:59:59Z",
            is_active=True
        ),
    ]

    requests = [
        # Normal completed PayPal purchase for Alex Chen
        SyntheticPaymentRequest(
            request_id="payreq_alex_keyboard",
            user_id="usr_alex_chen",
            merchant_id="mer_volt_circuits",
            product_id="prd_008_voltkey_wireless",
            amount=Decimal("119.00"),
            currency="USD",
            description="Synthetic Demo: VoltKey Dual-Mode Mechanical Keyboard",
            created_at="2026-10-18T14:30:00Z",
            state=PaymentLifecycleState.CAPTURED,
            paypal_order_id="SYNTH-ORDER-88210-ALEX"
        ),
        # Payment exceeding policy limit ($399.99 > $250.00 limit) requiring user elevated approval
        SyntheticPaymentRequest(
            request_id="payreq_alex_monitor_limit_exceeded",
            user_id="usr_alex_chen",
            merchant_id="mer_volt_circuits",
            product_id="prd_001_ultraview_27-in",
            amount=Decimal("414.99"),  # $399.99 + $15.00 shipping
            currency="USD",
            description="Synthetic Demo: UltraView 27-inch 4K Studio Monitor (Exceeds $250 policy limit)",
            created_at="2026-11-02T10:15:00Z",
            state=PaymentLifecycleState.REQUESTED,
            paypal_order_id=None
        ),
    ]

    auths = [
        SyntheticPaymentAuthorization(
            auth_id="payauth_alex_keyboard",
            request_id="payreq_alex_keyboard",
            user_id="usr_alex_chen",
            amount=Decimal("119.00"),
            currency="USD",
            authorized_at="2026-10-18T14:32:00Z",
            expires_at="2026-10-21T14:32:00Z",
            policy_checked=True,
            user_approved=True,
            state=PaymentLifecycleState.AUTHORIZED
        )
    ]

    captures = [
        SyntheticPaymentCapture(
            capture_id="paycap_alex_keyboard",
            auth_id="payauth_alex_keyboard",
            request_id="payreq_alex_keyboard",
            amount_captured=Decimal("119.00"),
            currency="USD",
            captured_at="2026-10-18T14:33:00Z",
            fee_amount=Decimal("3.75"),
            net_amount=Decimal("115.25"),
            state=PaymentLifecycleState.CAPTURED,
            paypal_capture_id="SYNTH-CAP-9914-ALEX"
        )
    ]

    return requests, auths, captures, policies

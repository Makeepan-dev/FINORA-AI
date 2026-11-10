from decimal import Decimal
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class BillingFrequency(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"
    WEEKLY = "weekly"
    QUARTERLY = "quarterly"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class EvidenceAvailability(str, Enum):
    CONFIRMED_ACTIVE = "confirmed_active"
    CONFIRMED_LOW_USAGE = "confirmed_low_usage"
    UNVERIFIED_MISSING = "unverified_missing"
    CONTRADICTORY = "contradictory"

class SyntheticSubscription(BaseModel):
    subscription_id: str
    user_id: str
    merchant_id: str
    service_name: str
    category: str
    amount: Decimal
    currency: str = "USD"
    billing_frequency: BillingFrequency = BillingFrequency.MONTHLY
    next_billing_date: str
    start_date: str
    cancellation_date: Optional[str] = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    evidence_availability: EvidenceAvailability = EvidenceAvailability.UNVERIFIED_MISSING
    payment_method_id: Optional[str] = None
    historical_payment_ids: List[str] = Field(default_factory=list)
    suggested_action: Optional[str] = None
    potential_monthly_savings: Decimal = Decimal("0.00")
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

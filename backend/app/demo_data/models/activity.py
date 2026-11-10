from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class EvidenceState(str, Enum):
    CONFIRMED = "confirmed"
    PARTIALLY_VERIFIED = "partially_verified"
    USER_REPORTED = "user_reported"
    UNVERIFIED = "unverified"
    MISSING = "missing"
    CONTRADICTORY = "contradictory"

class EvidenceType(str, Enum):
    GYM_VISIT = "gym_visit"
    SUBSCRIPTION_USAGE = "subscription_usage"
    PRODUCT_USAGE = "product_usage"
    PURCHASE_CONFIRMATION = "purchase_confirmation"
    DELIVERY_CONFIRMATION = "delivery_confirmation"
    BOOKING_ATTENDANCE = "booking_attendance"
    TRAVEL_ACTIVITY = "travel_activity"
    USER_CONFIRMED_CANCELLATION = "user_confirmed_cancellation"
    USER_CONFIRMED_DISSATISFACTION = "user_confirmed_dissatisfaction"

class SyntheticActivityEvidence(BaseModel):
    evidence_id: str
    user_id: str
    evidence_type: EvidenceType
    related_merchant_id: Optional[str] = None
    related_subscription_id: Optional[str] = None
    related_transaction_ids: List[str] = Field(default_factory=list)
    event_timestamp: Optional[str] = None
    evidence_source: str  # e.g., "gym_turnstile_scan", "app_login_telemetry", "email_receipt", "user_prompt"
    confidence_level: float = 1.0  # 0.0 to 1.0
    evidence_state: EvidenceState = EvidenceState.CONFIRMED
    notes: str = ""
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class InvestigationStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED_LEGITIMATE = "resolved_legitimate"
    RESOLVED_UNAUTHORIZED = "resolved_unauthorized"
    RESOLVED_DISPUTED = "resolved_disputed"
    CLOSED = "closed"

class AnomalyClassification(str, Enum):
    GENUINE_FRAUD_OR_UNAUTHORIZED = "genuine_fraud_or_unauthorized"
    LEGITIMATE_REPEATED_CHARGE = "legitimate_repeated_charge"
    FAILED_RETRY = "failed_retry"
    SEASONAL_OR_PLANNED_SPIKE = "seasonal_or_planned_spike"
    DELAYED_REFUND = "delayed_refund"
    MERCHANT_NAME_DISCREPANCY = "merchant_name_discrepancy"
    FALSE_POSITIVE = "false_positive"

class RecommendedAction(str, Enum):
    NO_ACTION_REQUIRED = "no_action_required"
    PROMPT_USER_VERIFICATION = "prompt_user_verification"
    INITIATE_PAYPAL_DISPUTE = "initiate_paypal_dispute"
    CANCEL_SUBSCRIPTION = "cancel_subscription"
    CONTACT_MERCHANT_SUPPORT = "contact_merchant_support"
    FREEZE_PAYMENT_METHOD = "freeze_payment_method"

class SyntheticInvestigationCase(BaseModel):
    case_id: str
    user_id: Optional[str] = None
    business_id: Optional[str] = None
    related_transaction_ids: List[str] = Field(default_factory=list)
    related_evidence_ids: List[str] = Field(default_factory=list)
    status: InvestigationStatus = InvestigationStatus.OPEN
    ground_truth_classification: AnomalyClassification
    expected_findings: str
    alternative_explanations: List[str] = Field(default_factory=list)
    confidence_score: float = 0.85
    recommended_action: RecommendedAction
    notes: Optional[str] = None
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

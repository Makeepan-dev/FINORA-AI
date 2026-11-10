from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SubscriptionAuditClassification(BaseModel):
    subscription_id: str
    subscription_name: str
    merchant: str
    monthly_cost: float
    annual_cost: float
    classification: str = Field(..., description="One of: KEEP, REDUCE, REPLACE, ELIMINATE, INVESTIGATE")
    usage_evidence: str
    value_assessment: str
    recommendation: str
    explanation: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    potential_savings: float
    unknown_information: str
    user_confirmation_needed: bool

class GuardianStructuredResponse(BaseModel):
    provider: str
    model: str
    status: str
    is_fallback: bool = False
    fallback_reason: Optional[str] = None
    factual_analysis: str
    classifications: List[SubscriptionAuditClassification] = []
    estimates: List[Dict[str, str]] = []
    recommendations: List[str] = []
    prioritized_actions: List[str] = []
    unknowns: str
    potential_monthly_savings: float = 0.0
    potential_annual_savings: float = 0.0

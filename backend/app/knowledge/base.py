from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class KnowledgeDomain(str, Enum):
    PERSONAL_FINANCE = "PersonalFinanceKnowledge"
    BUSINESS_FINANCE = "BusinessFinanceKnowledge"
    ACCOUNTING = "AccountingKnowledge"
    PAYMENTS_COMMERCE = "PaymentsCommerceKnowledge"
    CONSUMER_COMMERCE = "ConsumerCommerceKnowledge"
    SUBSCRIPTIONS = "SubscriptionKnowledge"
    FINANCIAL_RISK = "FinancialRiskKnowledge"
    TAX = "TaxKnowledge"
    CURRENCY = "CurrencyKnowledge"
    FINANCIAL_OPTIMIZATION = "FinancialOptimizationKnowledge"

class VerificationStatus(str, Enum):
    VERIFIED_CANONICAL = "verified_canonical"
    REGULATORY_STANDARD = "regulatory_standard"
    EMPIRICAL_RULE = "empirical_rule"
    HEURISTIC = "heuristic"

class KnowledgeSufficiency(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    CONFLICTING = "CONFLICTING"
    OUTDATED = "OUTDATED"
    REQUIRES_EXTERNAL_DATA = "REQUIRES_EXTERNAL_DATA"

class KnowledgeEntry(BaseModel):
    knowledge_id: str
    domain: KnowledgeDomain
    topic: str
    title: str
    definition: str
    rules: List[str] = Field(default_factory=list)
    required_inputs: List[str] = Field(default_factory=list)
    formula: Optional[str] = None
    calculation_procedure: Optional[str] = None
    output_fields: List[str] = Field(default_factory=list)
    authority_source: str
    verification_status: VerificationStatus = VerificationStatus.VERIFIED_CANONICAL
    confidence_score: float = 1.0
    limitations: str = ""
    last_reviewed: str = "2026-11-10"

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class MerchantCategory(str, Enum):
    GROCERIES = "groceries"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    RESTAURANTS = "restaurants"
    ENTERTAINMENT = "entertainment"
    TRANSPORTATION = "transportation"
    DIGITAL_SERVICES = "digital_services"
    EDUCATION = "education"
    FITNESS = "fitness"
    TRAVEL = "travel"
    HOME_IMPROVEMENT = "home_improvement"
    SOFTWARE = "software"
    HEALTHCARE = "healthcare"
    UTILITIES = "utilities"

class SyntheticMerchant(BaseModel):
    merchant_id: str
    name: str
    category: MerchantCategory
    sub_category: Optional[str] = None
    website: str
    country: str = "US"
    currency: str = "USD"
    supports_paypal: bool = True
    trusted_score: float = 0.95
    tags: List[str] = Field(default_factory=list)
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

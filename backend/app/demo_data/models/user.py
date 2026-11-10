from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class RiskPreference(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    GROWTH = "growth"
    AGGRESSIVE = "aggressive"

class FinancialGoal(BaseModel):
    goal_id: str
    name: str
    target_amount: Decimal
    current_amount: Decimal = Decimal("0.00")
    target_date: str
    category: str
    is_synthetic: bool = True

class BudgetLimit(BaseModel):
    category: str
    monthly_limit: Decimal
    alert_threshold_percent: int = 85
    is_synthetic: bool = True

class SyntheticUser(BaseModel):
    user_id: str
    full_name: str
    email: str
    country: str
    currency: str = "USD"
    employment_status: str
    employer_name: Optional[str] = None
    monthly_income: Decimal
    income_frequency: str = "monthly"  # monthly, bi-weekly
    financial_goals: List[FinancialGoal] = Field(default_factory=list)
    monthly_budgets: List[BudgetLimit] = Field(default_factory=list)
    risk_preference: RiskPreference = RiskPreference.MODERATE
    financial_obligations: List[Dict[str, str]] = Field(default_factory=list)
    notes: Optional[str] = None
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

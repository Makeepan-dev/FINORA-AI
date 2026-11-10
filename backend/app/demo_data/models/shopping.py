from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

class ShoppingComparison(BaseModel):
    comparison_id: str
    user_id: str
    product_ids: List[str]
    target_budget: Decimal
    recommended_product_id: Optional[str] = None
    reasoning: str
    price_difference: Decimal = Decimal("0.00")
    shipping_compared: bool = True
    warranty_compared: bool = True
    is_synthetic: bool = True

class PurchaseIntention(BaseModel):
    intent_id: str
    user_id: str
    product_id: str
    merchant_id: str
    calculated_amount: Decimal
    shipping_amount: Decimal = Decimal("0.00")
    total_amount: Decimal
    currency: str = "USD"
    budget_limit: Decimal
    is_within_budget: bool
    status: str = "draft"  # draft, ready_for_approval, checkout_initiated, completed, cancelled
    is_synthetic: bool = True

class ShoppingHistoryItem(BaseModel):
    history_id: str
    user_id: str
    product_id: str
    purchased_at: str
    amount_paid: Decimal
    transaction_id: str
    is_synthetic: bool = True

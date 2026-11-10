from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field

class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    OFFICE = "office"
    PRODUCTIVITY = "productivity"
    FITNESS = "fitness"
    HOME = "home"
    AUDIO = "audio"
    SOFTWARE = "software"

class SyntheticProduct(BaseModel):
    product_id: str
    merchant_id: str
    product_name: str
    description: str
    category: ProductCategory
    price: Decimal
    currency: str = "USD"
    availability: bool = True
    stock_count: int = 50
    shipping_cost: Decimal = Decimal("0.00")
    estimated_delivery_days: int = 3
    return_policy_days: int = 30
    warranty_months: int = 12
    specifications: Dict[str, str] = Field(default_factory=dict)
    rating: float = 4.7
    review_count: int = 128
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

    @property
    def total_cost(self) -> Decimal:
        return self.price + self.shipping_cost

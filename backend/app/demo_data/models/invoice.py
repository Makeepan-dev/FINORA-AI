from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class InvoiceStatus(str, Enum):
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    UNPAID = "unpaid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class InvoiceItem(BaseModel):
    item_id: str
    description: str
    quantity: int = 1
    unit_price: Decimal
    total_price: Decimal
    is_synthetic: bool = True

class SyntheticInvoice(BaseModel):
    invoice_id: str
    business_id: str
    customer_or_vendor_id: str
    customer_or_vendor_name: str
    direction: str = "receivable"  # "receivable" (we bill customer) or "payable" (supplier bills us)
    issue_date: str
    due_date: str
    paid_date: Optional[str] = None
    subtotal: Decimal
    tax_amount: Decimal = Decimal("0.00")
    total_amount: Decimal
    amount_paid: Decimal = Decimal("0.00")
    status: InvoiceStatus = InvoiceStatus.UNPAID
    items: List[InvoiceItem] = Field(default_factory=list)
    related_transaction_id: Optional[str] = None
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

    @property
    def balance_due(self) -> Decimal:
        return self.total_amount - self.amount_paid

from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    REFUND = "refund"
    FEE = "fee"
    REVERSAL = "reversal"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    REVERSED = "reversed"
    DISPUTED = "disputed"

class PaymentMethod(str, Enum):
    PAYPAL = "paypal"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"

class SyntheticTransaction(BaseModel):
    transaction_id: str
    user_id: Optional[str] = None
    business_id: Optional[str] = None
    account_id: str
    merchant_id: Optional[str] = None
    amount: Decimal  # Always positive magnitude
    currency: str = "USD"
    transaction_type: TransactionType
    category: str
    timestamp: str  # ISO 8601
    description: str
    status: TransactionStatus = TransactionStatus.COMPLETED
    payment_method: PaymentMethod = PaymentMethod.PAYPAL
    related_transaction_id: Optional[str] = None  # Original txn for refunds/reversals/transfers
    is_recurring: bool = False
    anomaly_flag: bool = False
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

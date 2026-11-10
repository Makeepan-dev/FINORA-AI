from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    DIGITAL_WALLET = "digital_wallet"
    PAYPAL_WALLET = "paypal_wallet"

class AccountStatus(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"

class SyntheticAccount(BaseModel):
    account_id: str
    owner_id: str  # user_id or business_id
    owner_type: str = "user"  # "user" or "business"
    account_name: str
    account_type: AccountType
    currency: str = "USD"
    opening_balance: Decimal
    current_balance: Decimal
    credit_limit: Optional[Decimal] = None
    account_status: AccountStatus = AccountStatus.ACTIVE
    creation_date: str
    account_number_mask: str  # e.g. "SYNTH-****-4921"
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

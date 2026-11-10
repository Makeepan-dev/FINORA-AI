from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class BusinessType(str, Enum):
    SAAS_STARTUP = "saas_startup"
    CONSULTING_AGENCY = "consulting_agency"
    RETAIL_BOUTIQUE = "retail_boutique"

class EmployeeRecord(BaseModel):
    employee_id: str
    full_name: str
    role: str
    monthly_salary: Decimal
    is_synthetic: bool = True

class SyntheticBusiness(BaseModel):
    business_id: str
    business_name: str
    business_type: BusinessType
    country: str = "US"
    currency: str = "USD"
    monthly_recurring_revenue: Decimal
    cash_balance: Decimal
    monthly_payroll: Decimal
    operating_expenses_target: Decimal
    suppliers: List[Dict[str, str]] = Field(default_factory=list)
    customers: List[Dict[str, str]] = Field(default_factory=list)
    employees: List[EmployeeRecord] = Field(default_factory=list)
    tax_id_mask: str = "SYNTH-TAX-***-991"
    is_synthetic: bool = True
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

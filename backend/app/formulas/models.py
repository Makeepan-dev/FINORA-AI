from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class FormulaDomain(str, Enum):
    CORE_MATH = "A_Core_Financial_Math"
    INCOME_EXPENSE = "B_Personal_Income_Expenses"
    SAVINGS_GOALS = "C_Savings_Financial_Goals"
    BANKING_DEPOSITS = "D_Banking_Deposits"
    LOANS_DEBT = "E_Loans_And_Debt"
    CREDIT_CARDS = "F_Credit_Cards"
    INVESTMENTS_WEALTH = "G_Investments_And_Wealth"
    TAXATION = "H_Taxation"
    INSURANCE_PROTECTION = "I_Insurance_Protection"
    FX_TRANSFERS = "J_Foreign_Exchange_Transfers"
    SHOPPING_COMMERCE = "K_Shopping_Commerce"
    PROPERTY_VEHICLE = "L_Property_And_Vehicles"
    FREELANCE_SELF_EMPLOYED = "M_Freelance_Self_Employment"
    FORECASTING_STATISTICS = "N_Forecasting_Statistics"
    ADVANCED_MODELS = "O_Advanced_Financial_Models"
    DECISION_METRICS = "P_Financial_Decision_Metrics"

class FormulaStatus(str, Enum):
    EXECUTABLE_TESTED = "EXECUTABLE_TESTED"
    EXECUTABLE_UNTESTED = "EXECUTABLE_UNTESTED"
    REFERENCE_ONLY = "REFERENCE_ONLY"
    REQUIRES_EXTERNAL_DATA = "REQUIRES_EXTERNAL_DATA"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

class InputVariableSpec(BaseModel):
    name: str
    type: str  # "Decimal", "int", "float", "str", "List[Decimal]"
    unit: str  # "USD", "%", "months", "years", "ratio", "units", "count"
    description: str
    default: Optional[Any] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

class FormulaEntry(BaseModel):
    unique_id: str
    name: str
    domain: FormulaDomain
    description: str
    equation_or_def: str
    required_inputs: List[InputVariableSpec]
    optional_inputs: List[InputVariableSpec] = Field(default_factory=list)
    expected_output: str
    currency_requirements: str = "Normalized to user base currency (USD default)"
    time_period_requirements: str = "Monthly or Annual where specified"
    preconditions: List[str] = Field(default_factory=list)
    validation_rules: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    jurisdiction: str = "GLOBAL"  # "GLOBAL", "US", "UK", "IN"
    status: FormulaStatus = FormulaStatus.EXECUTABLE_TESTED
    test_coverage_status: str = "TESTED"
    knowledge_source: str
    related_formulas: List[str] = Field(default_factory=list)

class CalculationResult(BaseModel):
    formula_id: str
    formula_name: str
    result: Any
    result_formatted: str
    output_units: str
    inputs: Dict[str, Any]
    explanation: str
    assumptions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    missing_information: Optional[str] = None
    data_source: str = "user_input"
    confidence_score: float = 1.0
    is_exact: bool = True  # True if exact mathematical calculation, False if estimate/illustrative

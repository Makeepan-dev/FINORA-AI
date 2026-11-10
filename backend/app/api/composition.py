from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from ..formulas.composition import CompositionWorkflowResult, global_composition_engine

router = APIRouter(prefix="/composition", tags=["Multi-Formula Decision Composition Engine"])

@router.get("/recipes")
def list_available_recipes() -> List[Dict[str, Any]]:
    """Returns the inventory of available multi-formula decision workflows."""
    return [
        {
            "recipe_id": "recipe_subscription_optimization",
            "name": "Subscription Retention & Optimization Workflow",
            "description": "Multi-formula decision algorithm (Cost Per Use + Alternative TCO + Net First-Year Savings) outputting KEEP, REDUCE, REPLACE, ELIMINATE, or INVESTIGATE.",
            "domains": ["SHOPPING_COMMERCE", "PERSONAL_INCOME_EXPENSES"]
        },
        {
            "recipe_id": "recipe_loan_early_payoff",
            "name": "Loan Early Repayment & Liquidity Assessment",
            "description": "Combines amortization schedule, extra payment interest saved, and 3-month emergency reserve cushion checks.",
            "domains": ["LOANS_DEBT", "SAVINGS_FINANCIAL_GOALS"]
        },
        {
            "recipe_id": "recipe_purchase_affordability",
            "name": "Purchase Affordability & Budget Impact Workflow",
            "description": "Evaluates discretionary purchases against liquid cash, upcoming commitments, and 10-year opportunity cost.",
            "domains": ["SHOPPING_COMMERCE", "DECISION_METRICS"]
        },
        {
            "recipe_id": "recipe_deposit_comparison",
            "name": "Deposit Yield & After-Tax Comparison",
            "description": "Compares fixed deposit maturity values, APY, compounding frequencies, and after-tax take-home returns.",
            "domains": ["BANKING_DEPOSITS", "TAXATION"]
        },
        {
            "recipe_id": "recipe_vehicle_tco_affordability",
            "name": "Vehicle True Cost of Ownership & Affordability",
            "description": "Combines financing loan installment, monthly fuel/insurance/maintenance, and 5-year depreciation.",
            "domains": ["PROPERTY_VEHICLE", "LOANS_DEBT"]
        }
    ]

@router.post("/subscription-decision", response_model=CompositionWorkflowResult)
def evaluate_subscription(
    subscription_name: str = Body(..., embed=True),
    monthly_cost: float = Body(..., embed=True),
    recorded_uses_90_days: Optional[int] = Body(None, embed=True),
    user_confirmed_active: Optional[bool] = Body(None, embed=True),
    alternative_monthly_price: Optional[float] = Body(None, embed=True),
    alternative_name: Optional[str] = Body(None, embed=True),
    cancellation_notice_days: int = Body(30, embed=True)
) -> CompositionWorkflowResult:
    """Executes the multi-step subscription evaluation decision workflow."""
    return global_composition_engine.evaluate_subscription_decision(
        subscription_name=subscription_name,
        monthly_cost=monthly_cost,
        recorded_uses_90_days=recorded_uses_90_days,
        user_confirmed_active=user_confirmed_active,
        alternative_monthly_price=alternative_monthly_price,
        alternative_name=alternative_name,
        cancellation_notice_days=cancellation_notice_days
    )

@router.post("/loan-early-payoff", response_model=CompositionWorkflowResult)
def evaluate_loan_payoff(
    loan_principal: float = Body(..., embed=True),
    annual_interest_rate_pct: float = Body(..., embed=True),
    remaining_months: int = Body(..., embed=True),
    extra_monthly_repayment: float = Body(..., embed=True),
    liquid_cash_reserves: float = Body(..., embed=True),
    monthly_essential_expenses: float = Body(..., embed=True)
) -> CompositionWorkflowResult:
    """Evaluates whether to accelerate loan payoff considering interest saved and emergency cash reserves."""
    return global_composition_engine.evaluate_loan_early_repayment(
        loan_principal=loan_principal,
        annual_interest_rate_pct=annual_interest_rate_pct,
        remaining_months=remaining_months,
        extra_monthly_repayment=extra_monthly_repayment,
        liquid_cash_reserves=liquid_cash_reserves,
        monthly_essential_expenses=monthly_essential_expenses
    )

@router.post("/purchase-affordability", response_model=CompositionWorkflowResult)
def evaluate_affordability(
    item_name: str = Body(..., embed=True),
    price: float = Body(..., embed=True),
    shipping: float = Body(0.0, embed=True),
    tax_pct: float = Body(0.0, embed=True),
    available_liquid_cash: float = Body(..., embed=True),
    monthly_income: float = Body(..., embed=True),
    monthly_expenses: float = Body(..., embed=True),
    essential_expenses: float = Body(..., embed=True)
) -> CompositionWorkflowResult:
    """Evaluates discretionary purchase affordability, safety cushion, and opportunity cost."""
    return global_composition_engine.evaluate_purchase_affordability(
        item_name=item_name,
        price=price,
        shipping=shipping,
        tax_pct=tax_pct,
        available_liquid_cash=available_liquid_cash,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        essential_expenses=essential_expenses
    )

@router.post("/deposit-comparison", response_model=CompositionWorkflowResult)
def compare_deposits(
    principal: float = Body(..., embed=True),
    tenure_months: int = Body(..., embed=True),
    option_a_name: str = Body(..., embed=True),
    option_a_rate_pct: float = Body(..., embed=True),
    option_a_compound_freq: int = Body(4, embed=True),
    option_b_name: str = Body(..., embed=True),
    option_b_rate_pct: float = Body(..., embed=True),
    option_b_compound_freq: int = Body(1, embed=True),
    marginal_tax_rate_pct: float = Body(22.0, embed=True)
) -> CompositionWorkflowResult:
    """Compares maturity value and after-tax yield between two term deposit options."""
    return global_composition_engine.compare_deposit_options(
        principal=principal,
        tenure_months=tenure_months,
        option_a_name=option_a_name,
        option_a_rate_pct=option_a_rate_pct,
        option_a_compound_freq=option_a_compound_freq,
        option_b_name=option_b_name,
        option_b_rate_pct=option_b_rate_pct,
        option_b_compound_freq=option_b_compound_freq,
        marginal_tax_rate_pct=marginal_tax_rate_pct
    )

@router.post("/vehicle-tco", response_model=CompositionWorkflowResult)
def evaluate_vehicle_tco(
    vehicle_model: str = Body(..., embed=True),
    purchase_price: float = Body(..., embed=True),
    down_payment: float = Body(..., embed=True),
    loan_rate_pct: float = Body(..., embed=True),
    loan_months: int = Body(..., embed=True),
    fuel_monthly: float = Body(..., embed=True),
    insurance_monthly: float = Body(..., embed=True),
    maintenance_monthly: float = Body(..., embed=True),
    monthly_income: float = Body(..., embed=True),
    monthly_existing_expenses: float = Body(..., embed=True)
) -> CompositionWorkflowResult:
    """Evaluates comprehensive vehicle ownership cost, monthly commitment, and income affordability."""
    return global_composition_engine.evaluate_vehicle_ownership_affordability(
        vehicle_model=vehicle_model,
        purchase_price=purchase_price,
        down_payment=down_payment,
        loan_rate_pct=loan_rate_pct,
        loan_months=loan_months,
        fuel_monthly=fuel_monthly,
        insurance_monthly=insurance_monthly,
        maintenance_monthly=maintenance_monthly,
        monthly_income=monthly_income,
        monthly_existing_expenses=monthly_existing_expenses
    )

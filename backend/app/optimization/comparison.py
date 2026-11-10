from decimal import Decimal
from typing import Dict, Any, Optional
from ..algorithms.decimal_math import to_decimal, round_currency, safe_divide

def compare_recurring_alternatives(
    current_monthly_cost: Decimal,
    alternative_monthly_cost: Decimal,
    alternative_setup_fee: Decimal = Decimal("0.00"),
    current_cancellation_fee: Decimal = Decimal("0.00"),
    contract_duration_months: int = 12
) -> Dict[str, Any]:
    """
    Compares recurring commitments on first-year total cost,
    accounting for setup fees, cancellation penalties, and net savings.
    """
    c_mo = to_decimal(current_monthly_cost)
    a_mo = to_decimal(alternative_monthly_cost)
    setup = to_decimal(alternative_setup_fee)
    cancel_fee = to_decimal(current_cancellation_fee)
    duration = max(1, int(contract_duration_months))

    # Current costs
    current_run_rate_annual = round_currency(c_mo * Decimal("12"))
    current_duration_cost = round_currency(c_mo * Decimal(duration))

    # Alternative costs
    alt_duration_cost = round_currency(a_mo * Decimal(duration) + setup)
    alt_annual_run_rate = round_currency(a_mo * Decimal("12"))

    # Savings
    monthly_run_rate_savings = round_currency(c_mo - a_mo)
    annual_gross_savings = round_currency(current_run_rate_annual - alt_annual_run_rate)

    # Net first-year savings (accounting for switching costs & cancel fee)
    first_year_net_savings = round_currency(
        (c_mo * Decimal("12")) - (alt_annual_run_rate + setup + cancel_fee)
    )

    # Break-even period in months
    switching_cost = setup + cancel_fee
    if monthly_run_rate_savings > Decimal("0.00") and switching_cost > Decimal("0.00"):
        break_even_months = float(safe_divide(switching_cost, monthly_run_rate_savings))
    elif monthly_run_rate_savings > Decimal("0.00"):
        break_even_months = 0.0
    else:
        break_even_months = None

    return {
        "current_monthly_cost": float(c_mo),
        "current_annual_cost": float(current_run_rate_annual),
        "alternative_monthly_cost": float(a_mo),
        "alternative_setup_fee": float(setup),
        "cancellation_fee": float(cancel_fee),
        "monthly_run_rate_savings": float(monthly_run_rate_savings),
        "annual_gross_savings": float(annual_gross_savings),
        "first_year_net_savings": float(first_year_net_savings),
        "break_even_months": round(break_even_months, 1) if break_even_months is not None else None,
        "is_economically_viable": first_year_net_savings > Decimal("0.00")
    }

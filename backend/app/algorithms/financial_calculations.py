from decimal import Decimal
from typing import Dict, Any, List
from .decimal_math import to_decimal, round_currency, round_rate, safe_divide

def calculate_loan_amortization(
    principal: Decimal,
    annual_interest_rate_percent: Decimal,
    tenure_months: int
) -> Dict[str, Any]:
    """
    Computes precise loan amortization schedule using standard financial formula:
    PMT = P * [r(1 + r)^n] / [(1 + r)^n - 1]
    where r = annual_rate / 12 / 100
    """
    p = to_decimal(principal)
    r_pct = to_decimal(annual_interest_rate_percent)
    n = int(tenure_months)

    if n <= 0 or p <= Decimal("0"):
        return {
            "principal": float(p),
            "monthly_payment": 0.0,
            "total_interest": 0.0,
            "total_payment": 0.0,
            "schedule": []
        }

    monthly_rate = (r_pct / Decimal("100")) / Decimal("12")

    if monthly_rate == Decimal("0"):
        monthly_pmt = round_currency(p / Decimal(n))
        total_payment = round_currency(p)
        total_interest = Decimal("0.00")
    else:
        # PMT = p * (r * (1 + r)^n) / ((1 + r)^n - 1)
        factor = (Decimal("1") + monthly_rate) ** n
        monthly_pmt = round_currency(p * (monthly_rate * factor) / (factor - Decimal("1")))
        total_payment = round_currency(monthly_pmt * Decimal(n))
        total_interest = round_currency(total_payment - p)

    schedule = []
    balance = p
    for m in range(1, min(n + 1, 13)):  # First 12 months in detail
        interest_for_month = round_currency(balance * monthly_rate)
        principal_for_month = round_currency(monthly_pmt - interest_for_month)
        balance = max(Decimal("0.00"), round_currency(balance - principal_for_month))
        schedule.append({
            "month": m,
            "payment": float(monthly_pmt),
            "principal_paid": float(principal_for_month),
            "interest_paid": float(interest_for_month),
            "remaining_balance": float(balance)
        })

    return {
        "principal": float(p),
        "annual_interest_rate": float(r_pct),
        "tenure_months": n,
        "monthly_payment": float(monthly_pmt),
        "total_payment": float(total_payment),
        "total_interest": float(total_interest),
        "interest_to_principal_ratio": float(round_rate(safe_divide(total_interest, p))),
        "sample_schedule": schedule
    }

def calculate_break_even(
    fixed_costs: Decimal,
    unit_price: Decimal,
    unit_variable_cost: Decimal
) -> Dict[str, Any]:
    """
    Computes break-even quantity and break-even revenue:
    Q = FC / (P - VC)
    Contribution Margin = P - VC
    """
    fc = to_decimal(fixed_costs)
    p = to_decimal(unit_price)
    vc = to_decimal(unit_variable_cost)

    unit_cm = p - vc
    if unit_cm <= Decimal("0"):
        return {
            "status": "UNVIABLE",
            "message": "Variable cost exceeds or equals unit price. Product cannot break even.",
            "contribution_margin_per_unit": float(unit_cm),
            "contribution_margin_ratio": 0.0,
            "break_even_units": None,
            "break_even_revenue": None
        }

    cm_ratio = round_rate(safe_divide(unit_cm, p))
    break_even_units = round_currency(safe_divide(fc, unit_cm), Decimal("1"))
    break_even_revenue = round_currency(break_even_units * p)

    return {
        "status": "VIABLE",
        "fixed_costs": float(fc),
        "unit_price": float(p),
        "unit_variable_cost": float(vc),
        "contribution_margin_per_unit": float(unit_cm),
        "contribution_margin_ratio": float(cm_ratio),
        "break_even_units": int(break_even_units),
        "break_even_revenue": float(break_even_revenue)
    }

def calculate_profit_margins(
    revenue: Decimal,
    cogs: Decimal,
    operating_expenses: Decimal,
    tax_rate: Decimal = Decimal("0.20")
) -> Dict[str, Any]:
    """
    Computes Gross Profit, Gross Margin %, Operating Profit, Net Profit, and Net Margin %.
    """
    rev = to_decimal(revenue)
    cg = to_decimal(cogs)
    opex = to_decimal(operating_expenses)
    tax_r = to_decimal(tax_rate)

    gross_profit = rev - cg
    gross_margin_pct = round_currency(safe_divide(gross_profit * Decimal("100"), rev))

    operating_profit = gross_profit - opex
    operating_margin_pct = round_currency(safe_divide(operating_profit * Decimal("100"), rev))

    taxes = max(Decimal("0.00"), round_currency(operating_profit * tax_r)) if operating_profit > Decimal("0") else Decimal("0.00")
    net_profit = operating_profit - taxes
    net_margin_pct = round_currency(safe_divide(net_profit * Decimal("100"), rev))

    return {
        "revenue": float(rev),
        "cogs": float(cg),
        "gross_profit": float(gross_profit),
        "gross_margin_percent": float(gross_margin_pct),
        "operating_expenses": float(opex),
        "operating_profit": float(operating_profit),
        "operating_margin_percent": float(operating_margin_pct),
        "taxes": float(taxes),
        "net_profit": float(net_profit),
        "net_margin_percent": float(net_margin_pct)
    }

def calculate_roi(gain_from_investment: Decimal, cost_of_investment: Decimal) -> Dict[str, Any]:
    """Computes Return on Investment: ROI = (Gain - Cost) / Cost * 100."""
    gain = to_decimal(gain_from_investment)
    cost = to_decimal(cost_of_investment)

    net_return = gain - cost
    roi_pct = round_currency(safe_divide(net_return * Decimal("100"), cost))

    return {
        "cost_of_investment": float(cost),
        "gain_from_investment": float(gain),
        "net_return": float(net_return),
        "roi_percent": float(roi_pct)
    }

def calculate_savings_rate(total_income: Decimal, total_expenses: Decimal) -> Dict[str, Any]:
    """Computes monthly savings rate percentage."""
    inc = to_decimal(total_income)
    exp = to_decimal(total_expenses)
    savings = inc - exp
    rate_pct = round_currency(safe_divide(savings * Decimal("100"), inc))

    return {
        "total_income": float(inc),
        "total_expenses": float(exp),
        "net_savings": float(savings),
        "savings_rate_percent": float(rate_pct)
    }

def calculate_depreciation_straight_line(
    asset_cost: Decimal,
    salvage_value: Decimal,
    useful_life_years: int
) -> Dict[str, Any]:
    """
    Computes straight-line depreciation:
    Annual = (Cost - Salvage) / UsefulLife
    """
    cost = to_decimal(asset_cost)
    salvage = to_decimal(salvage_value)
    life = max(1, int(useful_life_years))

    depreciable_base = max(Decimal("0.00"), cost - salvage)
    annual_depreciation = round_currency(depreciable_base / Decimal(life))
    monthly_depreciation = round_currency(annual_depreciation / Decimal("12"))

    schedule = []
    book_value = cost
    for yr in range(1, life + 1):
        book_value = max(salvage, round_currency(book_value - annual_depreciation))
        schedule.append({
            "year": yr,
            "depreciation_expense": float(annual_depreciation),
            "ending_book_value": float(book_value)
        })

    return {
        "asset_cost": float(cost),
        "salvage_value": float(salvage),
        "useful_life_years": life,
        "depreciable_base": float(depreciable_base),
        "annual_depreciation": float(annual_depreciation),
        "monthly_depreciation": float(monthly_depreciation),
        "schedule": schedule
    }

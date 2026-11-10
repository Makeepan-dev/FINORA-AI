from decimal import Decimal
from typing import Dict, Any, Optional
from .decimal_math import to_decimal, round_currency, safe_divide

def calculate_total_cost_of_ownership(
    base_price: Decimal,
    shipping_cost: Decimal = Decimal("0.00"),
    tax_rate_percent: Decimal = Decimal("0.00"),
    setup_fee: Decimal = Decimal("0.00"),
    annual_maintenance: Decimal = Decimal("0.00"),
    recurring_monthly_fee: Decimal = Decimal("0.00"),
    lifespan_years: int = 3
) -> Dict[str, Any]:
    """
    Computes comprehensive Total Cost of Ownership (TCO) across product lifespan:
    TCO = (Base + Shipping + Taxes + Setup) + (Monthly * 12 * Years) + (Maintenance * Years)
    """
    p = to_decimal(base_price)
    shp = to_decimal(shipping_cost)
    tax_pct = to_decimal(tax_rate_percent)
    setup = to_decimal(setup_fee)
    maint_yr = to_decimal(annual_maintenance)
    rec_mo = to_decimal(recurring_monthly_fee)
    years = max(1, int(lifespan_years))

    tax_amount = round_currency(p * (tax_pct / Decimal("100")))
    initial_acquisition = round_currency(p + shp + tax_amount + setup)

    total_recurring = round_currency(rec_mo * Decimal("12") * Decimal(years))
    total_maintenance = round_currency(maint_yr * Decimal(years))

    total_tco = round_currency(initial_acquisition + total_recurring + total_maintenance)
    annualized_tco = round_currency(total_tco / Decimal(years))
    monthly_tco = round_currency(annualized_tco / Decimal("12"))

    return {
        "base_price": float(p),
        "shipping_cost": float(shp),
        "tax_amount": float(tax_amount),
        "setup_fee": float(setup),
        "initial_acquisition_cost": float(initial_acquisition),
        "lifespan_years": years,
        "total_recurring_fees": float(total_recurring),
        "total_maintenance_costs": float(total_maintenance),
        "total_cost_of_ownership": float(total_tco),
        "annualized_tco": float(annualized_tco),
        "monthly_tco": float(monthly_tco)
    }

def calculate_cost_per_use(
    total_cost: Decimal,
    total_uses: int
) -> Dict[str, Any]:
    """
    Computes cost per utilization instance.
    """
    cost = to_decimal(total_cost)
    uses = max(0, int(total_uses))

    if uses == 0:
        return {
            "total_cost": float(cost),
            "total_uses": 0,
            "cost_per_use": None,
            "interpretation": "Undefined (Zero usage instances recorded — complete idle waste)"
        }

    cpu = round_currency(cost / Decimal(uses))
    return {
        "total_cost": float(cost),
        "total_uses": uses,
        "cost_per_use": float(cpu),
        "interpretation": f"${float(cpu):.2f} per utilization event"
    }

def calculate_value_adjusted_score(
    price: Decimal,
    quality_rating: float,
    warranty_months: int,
    expected_lifespan_years: int
) -> Dict[str, Any]:
    """
    Multi-factor consumer commerce score evaluating quality, durability, warranty,
    and initial cost. Explicitly prevents cheapest product from automatically winning.
    """
    p = to_decimal(price)
    qr = max(1.0, min(5.0, float(quality_rating)))
    w_mo = max(0, int(warranty_months))
    life_yr = max(1, int(expected_lifespan_years))

    # Annualized acquisition cost
    annual_cost = float(safe_divide(p, Decimal(life_yr)))

    # Quality factor (normalized 0.2 to 1.0)
    q_factor = qr / 5.0

    # Warranty security factor (12 mo = 1.0, 24 mo = 1.2, 0 mo = 0.8)
    w_factor = 0.8 + min(0.4, (w_mo / 60.0))

    # Value score: Higher quality & warranty per dollar of annual cost
    if annual_cost > 0:
        raw_score = (q_factor * w_factor * 1000.0) / annual_cost
        normalized_score = round(min(100.0, raw_score), 1)
    else:
        normalized_score = 0.0

    return {
        "price": float(p),
        "quality_rating": qr,
        "warranty_months": w_mo,
        "expected_lifespan_years": life_yr,
        "annualized_acquisition_cost": round(annual_cost, 2),
        "value_score": normalized_score,
        "evaluation_rule": "Quality, expected lifespan, and warranty duration are weighted against annualized cost."
    }

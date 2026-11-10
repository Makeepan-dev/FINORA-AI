from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Union, Optional

CENT = Decimal("0.01")
PERCENT = Decimal("0.0001")

def to_decimal(val: Union[float, int, str, Decimal, None], default: str = "0.00") -> Decimal:
    """Safely converts any numeric input to Decimal without binary floating-point drift."""
    if val is None:
        return Decimal(default)
    if isinstance(val, Decimal):
        return val
    try:
        # If float, convert to string first to avoid precision artifacts
        if isinstance(val, float):
            return Decimal(f"{val:.6f}")
        return Decimal(str(val).strip())
    except (InvalidOperation, ValueError):
        return Decimal(default)

def round_currency(val: Union[Decimal, float, int, str], precision: Decimal = CENT) -> Decimal:
    """Rounds an authoritative monetary amount using banker-safe HALF_UP rounding."""
    d = to_decimal(val)
    return d.quantize(precision, rounding=ROUND_HALF_UP)

def round_rate(val: Union[Decimal, float, int, str], precision: Decimal = PERCENT) -> Decimal:
    """Rounds interest rates or ratios with 4-decimal precision."""
    d = to_decimal(val)
    return d.quantize(precision, rounding=ROUND_HALF_UP)

def safe_divide(numerator: Decimal, denominator: Decimal, default: Decimal = Decimal("0.00")) -> Decimal:
    """Performs safe Decimal division, returning default if denominator is zero."""
    if denominator == Decimal("0") or denominator == Decimal("0.00"):
        return default
    return numerator / denominator

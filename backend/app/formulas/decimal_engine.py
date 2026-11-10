import math
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, Any, List, Optional, Tuple, Union
from .models import CalculationResult

CENT = Decimal("0.01")
PERCENT = Decimal("0.0001")
RATIO = Decimal("0.000001")

def to_d(val: Union[float, int, str, Decimal, None], default: str = "0.00") -> Decimal:
    """Safely converts any numeric input to Decimal with zero floating-point leakage."""
    if val is None:
        return Decimal(default)
    if isinstance(val, Decimal):
        return val
    try:
        if isinstance(val, float):
            return Decimal(f"{val:.8f}")
        return Decimal(str(val).strip())
    except (InvalidOperation, ValueError):
        return Decimal(default)

def q_curr(val: Union[Decimal, float, int, str]) -> Decimal:
    """Quantizes to standard currency precision (2 decimals, banker's HALF_UP)."""
    return to_d(val).quantize(CENT, rounding=ROUND_HALF_UP)

def q_pct(val: Union[Decimal, float, int, str]) -> Decimal:
    """Quantizes to percentage precision (2 decimals)."""
    return to_d(val).quantize(CENT, rounding=ROUND_HALF_UP)

def q_rate(val: Union[Decimal, float, int, str]) -> Decimal:
    """Quantizes to rate precision (4 decimals)."""
    return to_d(val).quantize(PERCENT, rounding=ROUND_HALF_UP)

def s_div(num: Decimal, den: Decimal, default: Decimal = Decimal("0.00")) -> Decimal:
    """Safely divides decimals, preventing division by zero."""
    if den == Decimal("0") or den == Decimal("0.00"):
        return default
    return num / den

# =========================================================================
# DOMAIN A: CORE FINANCIAL MATHEMATICS
# =========================================================================

def calc_percentage_change(old_val: Any, new_val: Any) -> CalculationResult:
    o, n = to_d(old_val), to_d(new_val)
    if o == Decimal("0"):
        pct_change = Decimal("0.00")
        warn = ["Baseline old_value is zero; percentage change is undefined."]
    else:
        pct_change = q_pct(((n - o) / abs(o)) * Decimal("100"))
        warn = []
    return CalculationResult(
        formula_id="form_a_pct_change",
        formula_name="Percentage Change",
        result=float(pct_change),
        result_formatted=f"{'+' if pct_change > 0 else ''}{pct_change}%",
        output_units="%",
        inputs={"old_value": float(o), "new_value": float(n)},
        explanation=f"Calculated percentage change from {o} to {n} as ((New - Old) / |Old|) * 100 = {pct_change}%.",
        warnings=warn,
        is_exact=True
    )

def calc_simple_interest(principal: Any, annual_rate_pct: Any, time_years: Any) -> CalculationResult:
    p, r_pct, t = to_d(principal), to_d(annual_rate_pct), to_d(time_years)
    r = r_pct / Decimal("100")
    interest = q_curr(p * r * t)
    total_accrued = q_curr(p + interest)
    return CalculationResult(
        formula_id="form_a_simple_interest",
        formula_name="Simple Interest",
        result={"interest_amount": float(interest), "total_accrued_amount": float(total_accrued)},
        result_formatted=f"Interest: ${interest:,.2f}, Total: ${total_accrued:,.2f}",
        output_units="USD",
        inputs={"principal": float(p), "annual_rate_pct": float(r_pct), "time_years": float(t)},
        explanation=f"Simple interest I = P * r * t = ${p} * {r} * {t} = ${interest:,.2f}.",
        is_exact=True
    )

def calc_compound_interest(
    principal: Any,
    annual_rate_pct: Any,
    time_years: Any,
    compound_freq: int = 12
) -> CalculationResult:
    p = to_d(principal)
    r_pct = to_d(annual_rate_pct)
    t = to_d(time_years)
    n = max(1, int(compound_freq))
    r = r_pct / Decimal("100")
    
    # A = P * (1 + r/n)^(n*t)
    # Using Decimal math with safe float conversion for power if fractional
    rate_per_period = r / Decimal(n)
    total_periods = float(t * Decimal(n))
    base = float(Decimal("1") + rate_per_period)
    compounded_factor = to_d(math.pow(base, total_periods))
    future_val = q_curr(p * compounded_factor)
    interest_earned = q_curr(future_val - p)

    return CalculationResult(
        formula_id="form_a_compound_interest",
        formula_name="Compound Interest",
        result={"future_value": float(future_val), "interest_earned": float(interest_earned)},
        result_formatted=f"Future Value: ${future_val:,.2f} (Interest Earned: ${interest_earned:,.2f})",
        output_units="USD",
        inputs={"principal": float(p), "annual_rate_pct": float(r_pct), "time_years": float(t), "compounding_frequency": n},
        explanation=f"Compounded {n} times/year at {r_pct}% over {t} years yields ${future_val:,.2f}.",
        is_exact=True
    )

def calc_present_value(future_value: Any, annual_rate_pct: Any, time_years: Any) -> CalculationResult:
    fv, r_pct, t = to_d(future_value), to_d(annual_rate_pct), to_d(time_years)
    r = r_pct / Decimal("100")
    discount_factor = to_d(math.pow(float(Decimal("1") + r), float(t)))
    pv = q_curr(s_div(fv, discount_factor))
    return CalculationResult(
        formula_id="form_a_present_value",
        formula_name="Present Value (Discounting)",
        result=float(pv),
        result_formatted=f"${pv:,.2f}",
        output_units="USD",
        inputs={"future_value": float(fv), "annual_rate_pct": float(r_pct), "time_years": float(t)},
        explanation=f"Discounting future ${fv:,.2f} at {r_pct}% across {t} years gives present value of ${pv:,.2f}.",
        is_exact=True
    )

def calc_effective_annual_rate(nominal_rate_pct: Any, compounding_frequency: int = 12) -> CalculationResult:
    nom_pct = to_d(nominal_rate_pct)
    n = max(1, int(compounding_frequency))
    r = nom_pct / Decimal("100")
    rate_per_period = float(r / Decimal(n))
    ear = q_rate(Decimal(math.pow(1.0 + rate_per_period, n) - 1.0) * Decimal("100"))
    return CalculationResult(
        formula_id="form_a_effective_annual_rate",
        formula_name="Effective Annual Rate (EAR / APY)",
        result=float(ear),
        result_formatted=f"{ear}%",
        output_units="%",
        inputs={"nominal_rate_pct": float(nom_pct), "compounding_frequency": n},
        explanation=f"Nominal {nom_pct}% compounded {n} times per year equates to an effective annual rate of {ear}%.",
        is_exact=True
    )

def calc_rule_of_72(annual_rate_pct: Any) -> CalculationResult:
    r = to_d(annual_rate_pct)
    if r <= Decimal("0"):
        return CalculationResult(
            formula_id="form_a_rule_of_72",
            formula_name="Rule of 72 (Doubling Time)",
            result=None,
            result_formatted="Undefined (Zero or Negative Rate)",
            output_units="years",
            inputs={"annual_rate_pct": float(r)},
            explanation="Interest rate must be strictly positive to estimate doubling time.",
            warnings=["Rate <= 0 cannot double capital."],
            is_exact=False
        )
    doubling_years = q_pct(Decimal("72") / r)
    return CalculationResult(
        formula_id="form_a_rule_of_72",
        formula_name="Rule of 72 (Doubling Time)",
        result=float(doubling_years),
        result_formatted=f"{doubling_years} years",
        output_units="years",
        inputs={"annual_rate_pct": float(r)},
        explanation=f"At an annual return of {r}%, capital will double in approximately {doubling_years} years (72 / {r}).",
        is_exact=False
    )

def calc_inflation_adjusted_value(amount: Any, inflation_rate_pct: Any, years: Any) -> CalculationResult:
    amt, infl, yrs = to_d(amount), to_d(inflation_rate_pct), to_d(years)
    r = infl / Decimal("100")
    factor = to_d(math.pow(float(Decimal("1") + r), float(yrs)))
    purchasing_power = q_curr(s_div(amt, factor))
    future_nominal_needed = q_curr(amt * factor)
    return CalculationResult(
        formula_id="form_a_inflation_adjustment",
        formula_name="Inflation Adjusted Purchasing Power",
        result={"purchasing_power_in_todays_dollars": float(purchasing_power), "future_amount_needed": float(future_nominal_needed)},
        result_formatted=f"Real Value: ${purchasing_power:,.2f} (Need ${future_nominal_needed:,.2f} to match)",
        output_units="USD",
        inputs={"amount": float(amt), "inflation_rate_pct": float(infl), "years": float(yrs)},
        explanation=f"With {infl}% annual inflation over {yrs} years, ${amt:,.2f} will have the real purchasing power of ${purchasing_power:,.2f}.",
        is_exact=True
    )

# =========================================================================
# DOMAIN B: PERSONAL INCOME AND EXPENSES
# =========================================================================

def calc_disposable_income(gross_income: Any, total_taxes: Any, mandatory_deductions: Any = 0) -> CalculationResult:
    g = to_d(gross_income)
    t = to_d(total_taxes)
    d = to_d(mandatory_deductions)
    disposable = q_curr(g - t - d)
    effective_take_home_pct = q_pct(s_div(disposable * Decimal("100"), g))
    return CalculationResult(
        formula_id="form_b_disposable_income",
        formula_name="Disposable (Net) Income",
        result={"disposable_income": float(disposable), "take_home_ratio_pct": float(effective_take_home_pct)},
        result_formatted=f"${disposable:,.2f}/mo ({effective_take_home_pct}% of gross)",
        output_units="USD",
        inputs={"gross_income": float(g), "total_taxes": float(t), "mandatory_deductions": float(d)},
        explanation=f"Gross income ${g:,.2f} minus taxes (${t:,.2f}) and deductions (${d:,.2f}) leaves ${disposable:,.2f} disposable cash.",
        is_exact=True
    )

def calc_monthly_cash_flow(monthly_income: Any, monthly_expenses: Any) -> CalculationResult:
    inc, exp = to_d(monthly_income), to_d(monthly_expenses)
    net_flow = q_curr(inc - exp)
    ratio = q_pct(s_div(exp * Decimal("100"), inc))
    status = "SURPLUS" if net_flow > 0 else ("BALANCED" if net_flow == 0 else "DEFICIT")
    return CalculationResult(
        formula_id="form_b_cash_flow",
        formula_name="Monthly Cash Flow & Surplus/Deficit",
        result={"net_cash_flow": float(net_flow), "expense_to_income_pct": float(ratio), "status": status},
        result_formatted=f"{'+' if net_flow >= 0 else ''}${net_flow:,.2f}/mo ({status})",
        output_units="USD",
        inputs={"monthly_income": float(inc), "monthly_expenses": float(exp)},
        explanation=f"Net monthly cash flow is ${inc:,.2f} - ${exp:,.2f} = ${net_flow:,.2f} ({ratio}% spent).",
        warnings=["Cash flow is negative; reserves are depleting."] if net_flow < 0 else [],
        is_exact=True
    )

def calc_savings_rate(monthly_income: Any, monthly_savings: Any) -> CalculationResult:
    inc, sav = to_d(monthly_income), to_d(monthly_savings)
    rate = q_pct(s_div(sav * Decimal("100"), inc))
    return CalculationResult(
        formula_id="form_b_savings_rate",
        formula_name="Personal Savings Rate",
        result=float(rate),
        result_formatted=f"{rate}%",
        output_units="%",
        inputs={"monthly_income": float(inc), "monthly_savings": float(sav)},
        explanation=f"Saving ${sav:,.2f} out of ${inc:,.2f} monthly represents a personal savings rate of {rate}%.",
        assumptions=["Standard benchmark for financial independence is 20%+."],
        is_exact=True
    )

def calc_expense_ratios(total_expenses: Any, fixed_expenses: Any, essential_expenses: Any) -> CalculationResult:
    tot, fix, ess = to_d(total_expenses), to_d(fixed_expenses), to_d(essential_expenses)
    fix_pct = q_pct(s_div(fix * Decimal("100"), tot))
    var_pct = q_pct(Decimal("100.00") - fix_pct)
    ess_pct = q_pct(s_div(ess * Decimal("100"), tot))
    disc_pct = q_pct(Decimal("100.00") - ess_pct)
    return CalculationResult(
        formula_id="form_b_expense_ratios",
        formula_name="Expense Composition Ratios",
        result={
            "fixed_expense_pct": float(fix_pct),
            "variable_expense_pct": float(var_pct),
            "essential_expense_pct": float(ess_pct),
            "discretionary_expense_pct": float(disc_pct)
        },
        result_formatted=f"Fixed: {fix_pct}%, Variable: {var_pct}%, Essential: {ess_pct}%, Discretionary: {disc_pct}%",
        output_units="%",
        inputs={"total_expenses": float(tot), "fixed_expenses": float(fix), "essential_expenses": float(ess)},
        explanation=f"Analyzed ${tot:,.2f} monthly spend: {fix_pct}% fixed commitments and {ess_pct}% essential needs.",
        is_exact=True
    )

def calc_income_volatility(monthly_incomes: List[Any]) -> CalculationResult:
    if not monthly_incomes or len(monthly_incomes) < 2:
        return CalculationResult(
            formula_id="form_b_income_volatility",
            formula_name="Income Volatility Index",
            result=0.0,
            result_formatted="0.0% (Insufficient Data)",
            output_units="%",
            inputs={"sample_count": len(monthly_incomes or [])},
            explanation="At least 2 monthly income records are required to calculate volatility.",
            warnings=["Need multiple months of income telemetry."],
            is_exact=False
        )
    incomes = [to_d(x) for x in monthly_incomes]
    n = len(incomes)
    mean = sum(incomes) / Decimal(n)
    variance = sum((x - mean) ** 2 for x in incomes) / Decimal(n - 1)
    std_dev = to_d(math.sqrt(float(variance)))
    cov = q_pct(s_div(std_dev * Decimal("100"), mean))
    return CalculationResult(
        formula_id="form_b_income_volatility",
        formula_name="Income Volatility Index (Coefficient of Variation)",
        result={"mean_monthly_income": float(q_curr(mean)), "standard_deviation": float(q_curr(std_dev)), "volatility_index_pct": float(cov)},
        result_formatted=f"{cov}% (Mean: ${mean:,.2f})",
        output_units="%",
        inputs={"monthly_incomes": [float(x) for x in incomes]},
        explanation=f"Calculated standard deviation (${std_dev:,.2f}) relative to mean income (${mean:,.2f}) gives {cov}% volatility.",
        assumptions=["Scores above 25% indicate variable freelance/commission income requiring larger cash buffers."],
        is_exact=True
    )

# =========================================================================
# DOMAIN C: SAVINGS AND FINANCIAL GOALS
# =========================================================================

def calc_required_monthly_savings(
    target_amount: Any,
    current_savings: Any,
    annual_return_pct: Any,
    target_months: int
) -> CalculationResult:
    tgt, cur = to_d(target_amount), to_d(current_savings)
    r_pct = to_d(annual_return_pct)
    n = max(1, int(target_months))
    
    shortfall = max(Decimal("0.00"), tgt - cur)
    if shortfall == Decimal("0.00"):
        return CalculationResult(
            formula_id="form_c_required_monthly_savings",
            formula_name="Required Monthly Savings for Goal",
            result=0.0,
            result_formatted="$0.00/mo (Goal Already Achieved)",
            output_units="USD",
            inputs={"target_amount": float(tgt), "current_savings": float(cur), "target_months": n},
            explanation="Current accumulated savings already equal or exceed the goal target.",
            is_exact=True
        )

    r_monthly = (r_pct / Decimal("100")) / Decimal("12")
    if r_monthly == Decimal("0"):
        monthly_contrib = q_curr(shortfall / Decimal(n))
    else:
        # FV of current savings after n months
        cur_fv = cur * to_d(math.pow(float(Decimal("1") + r_monthly), n))
        rem_needed = max(Decimal("0.00"), tgt - cur_fv)
        # Sinking fund formula: PMT = rem * r / ((1+r)^n - 1)
        factor = to_d(math.pow(float(Decimal("1") + r_monthly), n)) - Decimal("1")
        monthly_contrib = q_curr(s_div(rem_needed * r_monthly, factor))

    return CalculationResult(
        formula_id="form_c_required_monthly_savings",
        formula_name="Required Monthly Savings for Goal",
        result=float(monthly_contrib),
        result_formatted=f"${monthly_contrib:,.2f}/mo",
        output_units="USD",
        inputs={"target_amount": float(tgt), "current_savings": float(cur), "annual_return_pct": float(r_pct), "target_months": n},
        explanation=f"To reach ${tgt:,.2f} in {n} months starting from ${cur:,.2f} at {r_pct}% return, save ${monthly_contrib:,.2f}/mo.",
        is_exact=True
    )

def calc_emergency_fund_target(monthly_essential_expenses: Any, months_coverage: int = 6) -> CalculationResult:
    ess = to_d(monthly_essential_expenses)
    m = max(1, int(months_coverage))
    target = q_curr(ess * Decimal(m))
    return CalculationResult(
        formula_id="form_c_emergency_fund_target",
        formula_name="Emergency Fund Target",
        result=float(target),
        result_formatted=f"${target:,.2f} ({m} Months)",
        output_units="USD",
        inputs={"monthly_essential_expenses": float(ess), "months_coverage": m},
        explanation=f"{m} months of essential expenses (${ess:,.2f}/mo) requires a reserve target of ${target:,.2f}.",
        assumptions=["Covers non-negotiable living expenses (rent, food, insurance, debt minimums)."],
        is_exact=True
    )

def calc_emergency_fund_coverage(current_liquid_savings: Any, monthly_essential_expenses: Any) -> CalculationResult:
    cur = to_d(current_liquid_savings)
    ess = to_d(monthly_essential_expenses)
    coverage = q_pct(s_div(cur, ess))
    status = "OPTIMAL" if coverage >= Decimal("6.0") else ("ADEQUATE" if coverage >= Decimal("3.0") else "VULNERABLE")
    return CalculationResult(
        formula_id="form_c_emergency_fund_coverage",
        formula_name="Emergency Reserve Runway Coverage",
        result={"coverage_months": float(coverage), "status": status},
        result_formatted=f"{coverage} Months ({status})",
        output_units="months",
        inputs={"current_liquid_savings": float(cur), "monthly_essential_expenses": float(ess)},
        explanation=f"${cur:,.2f} in liquid savings provides {coverage} months of basic survival runway at ${ess:,.2f}/mo.",
        warnings=["Coverage is under 3 months; prioritize building emergency cash."] if coverage < Decimal("3.0") else [],
        is_exact=True
    )

# =========================================================================
# DOMAIN D: BANKING AND DEPOSITS
# =========================================================================

def calc_fixed_deposit_maturity(
    principal: Any,
    annual_rate_pct: Any,
    tenure_months: int,
    compound_freq: int = 4
) -> CalculationResult:
    p = to_d(principal)
    r_pct = to_d(annual_rate_pct)
    m = max(1, int(tenure_months))
    n = max(1, int(compound_freq))
    t_years = Decimal(m) / Decimal("12")
    r = r_pct / Decimal("100")

    rate_per_period = float(r / Decimal(n))
    periods = float(t_years * Decimal(n))
    maturity = q_curr(p * to_d(math.pow(1.0 + rate_per_period, periods)))
    interest = q_curr(maturity - p)

    return CalculationResult(
        formula_id="form_d_fd_maturity",
        formula_name="Fixed Deposit (Certificate of Deposit) Maturity",
        result={"maturity_amount": float(maturity), "total_interest": float(interest)},
        result_formatted=f"Maturity: ${maturity:,.2f} (Interest: ${interest:,.2f})",
        output_units="USD",
        inputs={"principal": float(p), "annual_rate_pct": float(r_pct), "tenure_months": m, "compound_frequency": n},
        explanation=f"Fixed deposit of ${p:,.2f} at {r_pct}% compounded {n} times/yr yields ${maturity:,.2f} after {m} months.",
        is_exact=True
    )

def calc_after_tax_deposit_yield(nominal_yield_pct: Any, marginal_tax_rate_pct: Any) -> CalculationResult:
    nom = to_d(nominal_yield_pct)
    tax = to_d(marginal_tax_rate_pct)
    after_tax = q_pct(nom * (Decimal("1.00") - (tax / Decimal("100"))))
    return CalculationResult(
        formula_id="form_d_after_tax_yield",
        formula_name="After-Tax Deposit Yield",
        result=float(after_tax),
        result_formatted=f"{after_tax}% net",
        output_units="%",
        inputs={"nominal_yield_pct": float(nom), "marginal_tax_rate_pct": float(tax)},
        explanation=f"Nominal yield {nom}% taxed at {tax}% marginal rate leaves an effective return of {after_tax}%.",
        is_exact=True
    )

# =========================================================================
# DOMAIN E: LOANS AND DEBT
# =========================================================================

def calc_loan_amortization_schedule(
    principal: Any,
    annual_interest_rate_pct: Any,
    tenure_months: int
) -> CalculationResult:
    p = to_d(principal)
    r_pct = to_d(annual_interest_rate_pct)
    n = max(1, int(tenure_months))

    if p <= Decimal("0"):
        return CalculationResult(
            formula_id="form_e_loan_amortization",
            formula_name="Loan Amortization & Installment",
            result={"monthly_payment": 0.0, "total_interest": 0.0, "total_payment": 0.0},
            result_formatted="$0.00/mo",
            output_units="USD",
            inputs={"principal": float(p), "annual_rate_pct": float(r_pct), "tenure_months": n},
            explanation="Principal is zero; no loan obligation.",
            is_exact=True
        )

    r_mo = (r_pct / Decimal("100")) / Decimal("12")
    if r_mo == Decimal("0"):
        pmt = q_curr(p / Decimal(n))
        tot_pay = q_curr(p)
        tot_int = Decimal("0.00")
    else:
        factor = to_d(math.pow(float(Decimal("1") + r_mo), n))
        pmt = q_curr(p * (r_mo * factor) / (factor - Decimal("1")))
        tot_pay = q_curr(pmt * Decimal(n))
        tot_int = q_curr(tot_pay - p)

    ratio = q_pct(s_div(tot_int * Decimal("100"), p))
    return CalculationResult(
        formula_id="form_e_loan_amortization",
        formula_name="Loan Amortization & Installment",
        result={
            "monthly_payment": float(pmt),
            "total_payment": float(tot_pay),
            "total_interest": float(tot_int),
            "interest_to_principal_ratio_pct": float(ratio)
        },
        result_formatted=f"${pmt:,.2f}/mo (Total Interest: ${tot_int:,.2f})",
        output_units="USD",
        inputs={"principal": float(p), "annual_interest_rate_pct": float(r_pct), "tenure_months": n},
        explanation=f"Financing ${p:,.2f} at {r_pct}% across {n} months costs ${pmt:,.2f}/mo. Total interest paid is ${tot_int:,.2f}.",
        is_exact=True
    )

def calc_loan_early_repayment_savings(
    principal: Any,
    annual_rate_pct: Any,
    tenure_months: int,
    extra_monthly_payment: Any
) -> CalculationResult:
    p, r_pct = to_d(principal), to_d(annual_rate_pct)
    n = max(1, int(tenure_months))
    extra = to_d(extra_monthly_payment)

    standard = calc_loan_amortization_schedule(p, r_pct, n)
    base_pmt = to_d(standard.result["monthly_payment"])
    total_new_pmt = base_pmt + extra

    r_mo = (r_pct / Decimal("100")) / Decimal("12")
    balance = p
    months_taken = 0
    total_interest_paid = Decimal("0.00")

    while balance > Decimal("0.01") and months_taken < 1200:
        months_taken += 1
        interest_charge = q_curr(balance * r_mo)
        principal_paid = min(balance, total_new_pmt - interest_charge)
        total_interest_paid += interest_charge
        balance = q_curr(balance - principal_paid)

    interest_saved = q_curr(to_d(standard.result["total_interest"]) - total_interest_paid)
    months_saved = n - months_taken

    return CalculationResult(
        formula_id="form_e_early_repayment",
        formula_name="Loan Early Repayment Savings",
        result={
            "interest_saved": float(interest_saved),
            "months_saved": months_saved,
            "new_tenure_months": months_taken,
            "new_total_interest": float(total_interest_paid)
        },
        result_formatted=f"Save ${interest_saved:,.2f} and pay off {months_saved} months early",
        output_units="USD",
        inputs={"principal": float(p), "rate_pct": float(r_pct), "tenure_months": n, "extra_monthly_payment": float(extra)},
        explanation=f"Adding ${extra:,.2f}/mo reduces repayment term by {months_saved} months and saves ${interest_saved:,.2f} in interest.",
        is_exact=True
    )

def calc_debt_to_income_ratio(monthly_debt_payments: Any, monthly_gross_income: Any) -> CalculationResult:
    debt, inc = to_d(monthly_debt_payments), to_d(monthly_gross_income)
    dti = q_pct(s_div(debt * Decimal("100"), inc))
    status = "HEALTHY" if dti <= Decimal("36.0") else ("MODERATE" if dti <= Decimal("43.0") else "HIGH_RISK")
    return CalculationResult(
        formula_id="form_e_dti_ratio",
        formula_name="Debt-to-Income (DTI) Ratio",
        result={"dti_percent": float(dti), "risk_tier": status},
        result_formatted=f"{dti}% ({status})",
        output_units="%",
        inputs={"monthly_debt_payments": float(debt), "monthly_gross_income": float(inc)},
        explanation=f"Monthly debt commitments of ${debt:,.2f} on ${inc:,.2f} gross income gives a DTI ratio of {dti}%.",
        assumptions=["Standard mortgage lending limit is 43% DTI."],
        warnings=["DTI exceeds 43%; debt consolidation or reduction strongly recommended."] if dti > Decimal("43.0") else [],
        is_exact=True
    )

def calc_loan_to_value_ratio(loan_amount: Any, asset_value: Any) -> CalculationResult:
    loan, val = to_d(loan_amount), to_d(asset_value)
    ltv = q_pct(s_div(loan * Decimal("100"), val))
    return CalculationResult(
        formula_id="form_e_ltv_ratio",
        formula_name="Loan-to-Value (LTV) Ratio",
        result=float(ltv),
        result_formatted=f"{ltv}%",
        output_units="%",
        inputs={"loan_amount": float(loan), "asset_value": float(val)},
        explanation=f"Financing ${loan:,.2f} against asset value ${val:,.2f} results in an LTV ratio of {ltv}%.",
        assumptions=["LTV over 80% on property typically requires Private Mortgage Insurance (PMI)."],
        is_exact=True
    )

# =========================================================================
# DOMAIN F: CREDIT CARDS
# =========================================================================

def calc_credit_utilization(total_credit_used: Any, total_credit_limit: Any) -> CalculationResult:
    used, limit = to_d(total_credit_used), to_d(total_credit_limit)
    util = q_pct(s_div(used * Decimal("100"), limit))
    status = "OPTIMAL" if util <= Decimal("10.0") else ("GOOD" if util <= Decimal("30.0") else "HIGH_UTILIZATION")
    return CalculationResult(
        formula_id="form_f_credit_utilization",
        formula_name="Revolving Credit Utilization Ratio",
        result={"utilization_pct": float(util), "status": status},
        result_formatted=f"{util}% ({status})",
        output_units="%",
        inputs={"total_credit_used": float(used), "total_credit_limit": float(limit)},
        explanation=f"Carrying ${used:,.2f} balance across ${limit:,.2f} total credit limit represents {util}% utilization.",
        warnings=["Utilization above 30% negatively impacts FICO credit scores."] if util > Decimal("30.0") else [],
        is_exact=True
    )

def calc_credit_card_interest_charge(average_daily_balance: Any, apr_pct: Any, billing_days: int = 30) -> CalculationResult:
    adb, apr = to_d(average_daily_balance), to_d(apr_pct)
    days = max(1, int(billing_days))
    daily_rate = (apr / Decimal("100")) / Decimal("365")
    charge = q_curr(adb * daily_rate * Decimal(days))
    return CalculationResult(
        formula_id="form_f_cc_interest",
        formula_name="Credit Card Monthly Finance Charge",
        result=float(charge),
        result_formatted=f"${charge:,.2f}",
        output_units="USD",
        inputs={"average_daily_balance": float(adb), "apr_pct": float(apr), "billing_days": days},
        explanation=f"Average daily balance of ${adb:,.2f} at {apr}% APR incurs ${charge:,.2f} in interest across {days} days.",
        is_exact=True
    )

# =========================================================================
# DOMAIN G: INVESTMENTS AND WEALTH
# =========================================================================

def calc_net_worth(total_assets: Any, total_liabilities: Any) -> CalculationResult:
    ast, lia = to_d(total_assets), to_d(total_liabilities)
    nw = q_curr(ast - lia)
    ratio = q_pct(s_div(lia * Decimal("100"), ast))
    return CalculationResult(
        formula_id="form_g_net_worth",
        formula_name="Personal Net Worth",
        result={"net_worth": float(nw), "debt_to_asset_pct": float(ratio)},
        result_formatted=f"${nw:,.2f} (Assets: ${ast:,.2f}, Liabilities: ${lia:,.2f})",
        output_units="USD",
        inputs={"total_assets": float(ast), "total_liabilities": float(lia)},
        explanation=f"Total assets (${ast:,.2f}) minus total liabilities (${lia:,.2f}) equals personal net worth of ${nw:,.2f}.",
        is_exact=True
    )

def calc_cagr(beginning_value: Any, ending_value: Any, years: Any) -> CalculationResult:
    bv, ev, yrs = to_d(beginning_value), to_d(ending_value), to_d(years)
    if bv <= Decimal("0") or yrs <= Decimal("0"):
        return CalculationResult(
            formula_id="form_g_cagr",
            formula_name="Compound Annual Growth Rate (CAGR)",
            result=0.0,
            result_formatted="0.0%",
            output_units="%",
            inputs={"beginning_value": float(bv), "ending_value": float(ev), "years": float(yrs)},
            explanation="Beginning value and years must be strictly positive.",
            warnings=["Invalid bounds for CAGR calculation."],
            is_exact=False
        )
    ratio = float(ev / bv)
    cagr = q_pct(Decimal(math.pow(ratio, 1.0 / float(yrs)) - 1.0) * Decimal("100"))
    return CalculationResult(
        formula_id="form_g_cagr",
        formula_name="Compound Annual Growth Rate (CAGR)",
        result=float(cagr),
        result_formatted=f"{cagr}%/yr",
        output_units="%",
        inputs={"beginning_value": float(bv), "ending_value": float(ev), "years": float(yrs)},
        explanation=f"Growing from ${bv:,.2f} to ${ev:,.2f} across {yrs} years represents a CAGR of {cagr}%.",
        is_exact=True
    )

def calc_roi(gain_or_current_value: Any, initial_cost: Any) -> CalculationResult:
    gain, cost = to_d(gain_or_current_value), to_d(initial_cost)
    net_return = q_curr(gain - cost)
    roi_pct = q_pct(s_div(net_return * Decimal("100"), cost))
    return CalculationResult(
        formula_id="form_g_roi",
        formula_name="Return on Investment (ROI)",
        result={"net_return": float(net_return), "roi_percent": float(roi_pct)},
        result_formatted=f"{roi_pct}% (Net: ${net_return:,.2f})",
        output_units="%",
        inputs={"gain_or_current_value": float(gain), "initial_cost": float(cost)},
        explanation=f"Return of ${net_return:,.2f} on initial investment of ${cost:,.2f} gives an ROI of {roi_pct}%.",
        is_exact=True
    )

# =========================================================================
# DOMAIN H: TAXATION (JURISDICTION AWARE)
# =========================================================================

def calc_progressive_income_tax(taxable_income: Any, jurisdiction: str = "US_SINGLE_2024") -> CalculationResult:
    inc = to_d(taxable_income)
    
    # Standard verified tax brackets (US Federal 2024/2026 Single Filer reference)
    brackets_us_single = [
        (Decimal("11600"), Decimal("0.10")),
        (Decimal("47150"), Decimal("0.12")),
        (Decimal("100525"), Decimal("0.22")),
        (Decimal("191950"), Decimal("0.24")),
        (Decimal("243725"), Decimal("0.32")),
        (Decimal("609350"), Decimal("0.35")),
        (Decimal("999999999"), Decimal("0.37")),
    ]
    # UK 2024/2026 Income Tax Brackets (Standard Personal Allowance £12,570)
    brackets_uk = [
        (Decimal("12570"), Decimal("0.00")),
        (Decimal("50270"), Decimal("0.20")),
        (Decimal("125140"), Decimal("0.40")),
        (Decimal("999999999"), Decimal("0.45")),
    ]
    
    selected_brackets = brackets_uk if "UK" in jurisdiction.upper() else brackets_us_single
    
    tax_due = Decimal("0.00")
    prev_limit = Decimal("0.00")
    marginal_rate = Decimal("0.00")
    
    for limit, rate in selected_brackets:
        if inc > prev_limit:
            taxable_in_bracket = min(inc - prev_limit, limit - prev_limit)
            tax_due += taxable_in_bracket * rate
            marginal_rate = rate * Decimal("100")
            prev_limit = limit
        else:
            break

    tax_due = q_curr(tax_due)
    effective_rate = q_pct(s_div(tax_due * Decimal("100"), inc))
    after_tax = q_curr(inc - tax_due)

    return CalculationResult(
        formula_id="form_h_progressive_tax",
        formula_name=f"Progressive Income Tax ({jurisdiction})",
        result={
            "tax_liability": float(tax_due),
            "effective_tax_rate_pct": float(effective_rate),
            "marginal_tax_rate_pct": float(marginal_rate),
            "after_tax_income": float(after_tax)
        },
        result_formatted=f"Tax: ${tax_due:,.2f} (Effective: {effective_rate}%, Marginal: {marginal_rate}%)",
        output_units="USD",
        inputs={"taxable_income": float(inc), "jurisdiction": jurisdiction},
        explanation=f"On taxable income of ${inc:,.2f}, calculated tax liability is ${tax_due:,.2f} ({effective_rate}% effective).",
        assumptions=[f"Computed using authoritative {jurisdiction} statutory progressive brackets."],
        is_exact=True
    )

# =========================================================================
# DOMAIN I: INSURANCE AND PROTECTION
# =========================================================================

def calc_insurance_claim_payout(
    loss_amount: Any,
    deductible: Any,
    coinsurance_pct: Any = 20,
    policy_limit: Any = 1000000
) -> CalculationResult:
    loss, ded = to_d(loss_amount), to_d(deductible)
    co_pct, lim = to_d(coinsurance_pct), to_d(policy_limit)

    if loss <= ded:
        return CalculationResult(
            formula_id="form_i_insurance_payout",
            formula_name="Insurance Claim Net Payout",
            result={"net_payout": 0.0, "out_of_pocket": float(loss)},
            result_formatted="$0.00 Payout (Loss <= Deductible)",
            output_units="USD",
            inputs={"loss_amount": float(loss), "deductible": float(ded)},
            explanation=f"Loss ${loss:,.2f} is within deductible (${ded:,.2f}). Insurer pays $0.00.",
            is_exact=True
        )

    covered_above_ded = loss - ded
    insurer_share_pct = Decimal("1.00") - (co_pct / Decimal("100"))
    payout = min(lim, q_curr(covered_above_ded * insurer_share_pct))
    out_of_pocket = q_curr(loss - payout)

    return CalculationResult(
        formula_id="form_i_insurance_payout",
        formula_name="Insurance Claim Net Payout",
        result={"net_payout": float(payout), "out_of_pocket_expense": float(out_of_pocket)},
        result_formatted=f"Payout: ${payout:,.2f} (Out of Pocket: ${out_of_pocket:,.2f})",
        output_units="USD",
        inputs={"loss_amount": float(loss), "deductible": float(ded), "coinsurance_pct": float(co_pct), "policy_limit": float(lim)},
        explanation=f"Insurer covers ${payout:,.2f} after deductible (${ded:,.2f}) and {co_pct}% coinsurance.",
        is_exact=True
    )

# =========================================================================
# DOMAIN J: FOREIGN EXCHANGE AND TRANSFERS
# =========================================================================

def calc_fx_conversion(
    source_amount: Any,
    mid_market_exchange_rate: Any,
    spread_markup_pct: Any = 1.5,
    fixed_transfer_fee: Any = 0.0
) -> CalculationResult:
    src = to_d(source_amount)
    rate = to_d(mid_market_exchange_rate)
    spr_pct = to_d(spread_markup_pct)
    fee = to_d(fixed_transfer_fee)

    net_src = max(Decimal("0.00"), src - fee)
    effective_rate = rate * (Decimal("1.00") - (spr_pct / Decimal("100")))
    target_amount = q_curr(net_src * effective_rate)
    total_hidden_and_explicit_fees = q_curr(fee + (src * (spr_pct / Decimal("100"))))

    return CalculationResult(
        formula_id="form_j_fx_conversion",
        formula_name="Foreign Currency Transfer & Spread Cost",
        result={
            "target_received_amount": float(target_amount),
            "effective_exchange_rate": float(q_rate(effective_rate)),
            "total_fees_and_spread": float(total_hidden_and_explicit_fees)
        },
        result_formatted=f"Receives {target_amount:,.2f} (Total FX Cost: ${total_hidden_and_explicit_fees:,.2f})",
        output_units="TARGET_CURRENCY",
        inputs={"source_amount": float(src), "exchange_rate": float(rate), "spread_pct": float(spr_pct), "fixed_fee": float(fee)},
        explanation=f"Converting ${src:,.2f} at rate {rate} with {spr_pct}% spread and ${fee:,.2f} fee yields {target_amount:,.2f}.",
        is_exact=True
    )

# =========================================================================
# DOMAIN K: SHOPPING AND COMMERCE
# =========================================================================

def calc_commerce_tco(
    base_price: Any,
    shipping_cost: Any = 0.0,
    tax_rate_pct: Any = 0.0,
    setup_fee: Any = 0.0,
    annual_maintenance: Any = 0.0,
    recurring_monthly_fee: Any = 0.0,
    lifespan_years: int = 3
) -> CalculationResult:
    p, shp, tax_pct = to_d(base_price), to_d(shipping_cost), to_d(tax_rate_pct)
    setup, maint, rec = to_d(setup_fee), to_d(annual_maintenance), to_d(recurring_monthly_fee)
    yrs = max(1, int(lifespan_years))

    tax_amt = q_curr(p * (tax_pct / Decimal("100")))
    upfront = q_curr(p + shp + tax_amt + setup)
    recurring_total = q_curr(rec * Decimal(12 * yrs))
    maint_total = q_curr(maint * Decimal(yrs))
    total_tco = q_curr(upfront + recurring_total + maint_total)
    annualized = q_curr(total_tco / Decimal(yrs))
    monthly = q_curr(annualized / Decimal("12"))

    return CalculationResult(
        formula_id="form_k_tco",
        formula_name="Commerce Total Cost of Ownership (TCO)",
        result={
            "total_tco": float(total_tco),
            "initial_acquisition_cost": float(upfront),
            "annualized_tco": float(annualized),
            "monthly_equivalent_tco": float(monthly)
        },
        result_formatted=f"TCO: ${total_tco:,.2f} (${monthly:,.2f}/mo across {yrs} yrs)",
        output_units="USD",
        inputs={"base_price": float(p), "shipping": float(shp), "tax_pct": float(tax_pct), "lifespan_years": yrs},
        explanation=f"Acquisition of ${upfront:,.2f} plus {yrs} yrs recurring/maintenance totals ${total_tco:,.2f} TCO.",
        is_exact=True
    )

def calc_cost_per_use(total_cost: Any, total_uses: int) -> CalculationResult:
    cost = to_d(total_cost)
    uses = max(0, int(total_uses))
    if uses == 0:
        return CalculationResult(
            formula_id="form_k_cost_per_use",
            formula_name="Cost Per Use (Utilization Metric)",
            result=None,
            result_formatted="Undefined (Zero Uses — 100% Idle Waste)",
            output_units="USD/use",
            inputs={"total_cost": float(cost), "total_uses": 0},
            explanation="Cost per use is undefined when zero utilization events have occurred.",
            warnings=["Zero usage represents complete capital waste."],
            is_exact=False
        )
    cpu = q_curr(cost / Decimal(uses))
    return CalculationResult(
        formula_id="form_k_cost_per_use",
        formula_name="Cost Per Use (Utilization Metric)",
        result=float(cpu),
        result_formatted=f"${cpu:,.2f}/use",
        output_units="USD/use",
        inputs={"total_cost": float(cost), "total_uses": uses},
        explanation=f"${cost:,.2f} spent over {uses} sessions equals ${cpu:,.2f} per utilization event.",
        is_exact=True
    )

def calc_unit_price(package_price: Any, quantity: Any, unit_name: str = "units") -> CalculationResult:
    p, q = to_d(package_price), to_d(quantity)
    unit_price = q_curr(s_div(p, q))
    return CalculationResult(
        formula_id="form_k_unit_price",
        formula_name="Normalized Unit Price",
        result=float(unit_price),
        result_formatted=f"${unit_price:,.2f} per {unit_name}",
        output_units=f"USD/{unit_name}",
        inputs={"package_price": float(p), "quantity": float(q), "unit_name": unit_name},
        explanation=f"${p:,.2f} for {q} {unit_name} equates to ${unit_price:,.2f} per unit.",
        is_exact=True
    )

def calc_buy_vs_subscribe_break_even(purchase_price: Any, monthly_subscription_price: Any) -> CalculationResult:
    buy, sub = to_d(purchase_price), to_d(monthly_subscription_price)
    months = q_pct(s_div(buy, sub))
    years = q_pct(s_div(months, Decimal("12")))
    return CalculationResult(
        formula_id="form_k_buy_vs_subscribe",
        formula_name="Buy vs. Subscribe Break-Even Analysis",
        result={"break_even_months": float(months), "break_even_years": float(years)},
        result_formatted=f"{months} Months ({years} Years)",
        output_units="months",
        inputs={"purchase_price": float(buy), "monthly_subscription_price": float(sub)},
        explanation=f"Purchasing for ${buy:,.2f} breaks even against ${sub:,.2f}/mo subscription after {months} months.",
        assumptions=["Assumes equal functionality and no unexpected repair expenses."],
        is_exact=True
    )

# =========================================================================
# DOMAIN L: PROPERTY AND VEHICLES
# =========================================================================

def calc_straight_line_depreciation(asset_cost: Any, salvage_value: Any, useful_life_years: int) -> CalculationResult:
    cost, salvage = to_d(asset_cost), to_d(salvage_value)
    life = max(1, int(useful_life_years))
    depreciable_base = max(Decimal("0.00"), cost - salvage)
    annual = q_curr(depreciable_base / Decimal(life))
    monthly = q_curr(annual / Decimal("12"))
    return CalculationResult(
        formula_id="form_l_depreciation",
        formula_name="Straight-Line Depreciation",
        result={"annual_depreciation": float(annual), "monthly_depreciation": float(monthly), "depreciable_base": float(depreciable_base)},
        result_formatted=f"${annual:,.2f}/yr (${monthly:,.2f}/mo)",
        output_units="USD",
        inputs={"asset_cost": float(cost), "salvage_value": float(salvage), "useful_life_years": life},
        explanation=f"Depreciable base ${depreciable_base:,.2f} over {life} years depreciates at ${annual:,.2f}/yr.",
        is_exact=True
    )

def calc_rental_yield(annual_rental_income: Any, property_price: Any, annual_operating_costs: Any = 0.0) -> CalculationResult:
    inc, price, opex = to_d(annual_rental_income), to_d(property_price), to_d(annual_operating_costs)
    gross_yield = q_pct(s_div(inc * Decimal("100"), price))
    net_inc = inc - opex
    net_yield = q_pct(s_div(net_inc * Decimal("100"), price))
    return CalculationResult(
        formula_id="form_l_rental_yield",
        formula_name="Property Gross & Net Rental Yield",
        result={"gross_yield_pct": float(gross_yield), "net_yield_pct": float(net_yield), "net_annual_income": float(net_inc)},
        result_formatted=f"Gross: {gross_yield}%, Net: {net_yield}%",
        output_units="%",
        inputs={"annual_rental_income": float(inc), "property_price": float(price), "annual_operating_costs": float(opex)},
        explanation=f"Annual rent ${inc:,.2f} on ${price:,.2f} property gives {gross_yield}% gross yield ({net_yield}% net).",
        is_exact=True
    )

# =========================================================================
# DOMAIN M: FREELANCE AND SELF-EMPLOYMENT
# =========================================================================

def calc_effective_hourly_rate(
    billable_rate: Any,
    billable_hours_per_week: Any,
    unpaid_admin_hours_per_week: Any
) -> CalculationResult:
    rate = to_d(billable_rate)
    b_hrs = to_d(billable_hours_per_week)
    u_hrs = to_d(unpaid_admin_hours_per_week)
    total_hrs = b_hrs + u_hrs
    weekly_gross = rate * b_hrs
    eff_rate = q_curr(s_div(weekly_gross, total_hrs))
    discount_pct = q_pct(s_div((rate - eff_rate) * Decimal("100"), rate))
    return CalculationResult(
        formula_id="form_m_effective_hourly_rate",
        formula_name="Freelance Effective Real Hourly Rate",
        result={"effective_hourly_rate": float(eff_rate), "nominal_billable_rate": float(rate), "dilution_pct": float(discount_pct)},
        result_formatted=f"${eff_rate:,.2f}/hr (Nominal: ${rate:,.2f}/hr)",
        output_units="USD/hr",
        inputs={"billable_rate": float(rate), "billable_hours": float(b_hrs), "unpaid_admin_hours": float(u_hrs)},
        explanation=f"Billing ${rate:,.2f}/hr for {b_hrs} hrs with {u_hrs} unpaid hrs dilutes effective real earnings to ${eff_rate:,.2f}/hr.",
        is_exact=True
    )

# =========================================================================
# DOMAIN N: FORECASTING AND STATISTICS
# =========================================================================

def calc_simple_moving_average(series: List[Any], window: int = 3) -> CalculationResult:
    w = max(1, int(window))
    if not series or len(series) < w:
        return CalculationResult(
            formula_id="form_n_sma",
            formula_name="Simple Moving Average (SMA)",
            result=0.0,
            result_formatted="0.0 (Insufficient Data)",
            output_units="USD",
            inputs={"series_length": len(series or []), "window": w},
            explanation="Series length must be at least equal to window.",
            is_exact=False
        )
    sub = [to_d(x) for x in series[-w:]]
    sma = q_curr(sum(sub) / Decimal(w))
    return CalculationResult(
        formula_id="form_n_sma",
        formula_name="Simple Moving Average (SMA)",
        result=float(sma),
        result_formatted=f"${sma:,.2f} ({w}-period SMA)",
        output_units="USD",
        inputs={"window": w, "recent_points": [float(x) for x in sub]},
        explanation=f"Average of the last {w} periods is ${sma:,.2f}.",
        is_exact=True
    )

# =========================================================================
# DOMAIN O: ADVANCED FINANCIAL MODELS
# =========================================================================

def calc_bond_price(
    face_value: Any,
    coupon_rate_pct: Any,
    years_to_maturity: Any,
    market_yield_pct: Any,
    coupon_freq: int = 2
) -> CalculationResult:
    fv = to_d(face_value)
    cr_pct = to_d(coupon_rate_pct)
    yrs = to_d(years_to_maturity)
    y_pct = to_d(market_yield_pct)
    freq = max(1, int(coupon_freq))

    n_periods = int(yrs * Decimal(freq))
    coupon_pmt = (fv * (cr_pct / Decimal("100"))) / Decimal(freq)
    y_per_period = float((y_pct / Decimal("100")) / Decimal(freq))

    # PV of coupons + PV of par
    pv_coupons = Decimal("0.00")
    for t in range(1, n_periods + 1):
        disc = to_d(math.pow(1.0 + y_per_period, t))
        pv_coupons += s_div(coupon_pmt, disc)
    
    pv_par = s_div(fv, to_d(math.pow(1.0 + y_per_period, n_periods)))
    bond_price = q_curr(pv_coupons + pv_par)
    status = "PREMIUM" if bond_price > fv else ("DISCOUNT" if bond_price < fv else "PAR")

    return CalculationResult(
        formula_id="form_o_bond_pricing",
        formula_name="Bond Pricing (Discounted Cash Flow)",
        result={"bond_price": float(bond_price), "pricing_status": status, "coupon_payment": float(q_curr(coupon_pmt))},
        result_formatted=f"${bond_price:,.2f} ({status})",
        output_units="USD",
        inputs={"face_value": float(fv), "coupon_rate_pct": float(cr_pct), "years": float(yrs), "market_yield_pct": float(y_pct)},
        explanation=f"Bond with {cr_pct}% coupon priced at {y_pct}% market yield trades at ${bond_price:,.2f} ({status}).",
        assumptions=["Assumes fixed flat yield curve and timely coupon payment."],
        is_exact=True
    )

def _norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def calc_black_scholes(
    spot_price: Any,
    strike_price: Any,
    time_years: Any,
    risk_free_rate_pct: Any,
    volatility_pct: Any
) -> CalculationResult:
    s = float(to_d(spot_price))
    k = float(to_d(strike_price))
    t = float(to_d(time_years))
    r = float(to_d(risk_free_rate_pct) / Decimal("100"))
    v = float(to_d(volatility_pct) / Decimal("100"))

    if s <= 0 or k <= 0 or t <= 0 or v <= 0:
        return CalculationResult(
            formula_id="form_o_black_scholes",
            formula_name="Black-Scholes European Option Pricing",
            result=None,
            result_formatted="Undefined Parameters",
            output_units="USD",
            inputs={"spot": s, "strike": k, "time_years": t, "volatility": v},
            explanation="Spot, strike, time, and volatility must be strictly positive.",
            warnings=["Invalid parameters."],
            is_exact=False
        )

    d1 = (math.log(s / k) + (r + 0.5 * v * v) * t) / (v * math.sqrt(t))
    d2 = d1 - v * math.sqrt(t)

    call_price = q_curr(Decimal(s * _norm_cdf(d1) - k * math.exp(-r * t) * _norm_cdf(d2)))
    put_price = q_curr(Decimal(k * math.exp(-r * t) * _norm_cdf(-d2) - s * _norm_cdf(-d1)))
    delta_call = q_rate(Decimal(_norm_cdf(d1)))

    return CalculationResult(
        formula_id="form_o_black_scholes",
        formula_name="Black-Scholes European Option Pricing",
        result={
            "call_price": float(call_price),
            "put_price": float(put_price),
            "delta_call": float(delta_call),
            "d1": round(d1, 4),
            "d2": round(d2, 4)
        },
        result_formatted=f"Call: ${call_price:,.2f}, Put: ${put_price:,.2f} (Delta: {delta_call})",
        output_units="USD",
        inputs={"spot_price": s, "strike_price": k, "time_years": t, "risk_free_rate_pct": float(r * 100), "volatility_pct": float(v * 100)},
        explanation=f"European option on ${s:,.2f} asset with ${k:,.2f} strike: Call = ${call_price:,.2f}, Put = ${put_price:,.2f}.",
        assumptions=["Log-normal underlying asset returns, constant risk-free rate, European-style exercise only."],
        is_exact=True
    )

# =========================================================================
# DOMAIN P: FINANCIAL DECISION METRICS
# =========================================================================

def calc_purchase_affordability(
    purchase_price: Any,
    available_liquid_cash: Any,
    monthly_surplus: Any,
    minimum_emergency_reserve: Any = 1000.0
) -> CalculationResult:
    cost = to_d(purchase_price)
    cash = to_d(available_liquid_cash)
    surplus = to_d(monthly_surplus)
    reserve = to_d(minimum_emergency_reserve)

    post_purchase_cash = cash - cost
    cushion_remaining = post_purchase_cash - reserve

    if post_purchase_cash < Decimal("0.00"):
        verdict = "NOT_RECOMMENDED"
        msg = "Purchase exceeds total available liquid cash. Would trigger overdraft."
    elif post_purchase_cash < reserve:
        verdict = "AFFORDABLE_WITH_CAUTION"
        months_to_replenish = q_pct(s_div(cost, surplus)) if surplus > Decimal("0") else Decimal("99.0")
        msg = f"Affordable, but breaches minimum emergency reserve of ${reserve:,.2f}. Takes {months_to_replenish} months of surplus to replenish."
    else:
        verdict = "AFFORDABLE"
        msg = f"Comfortably affordable. Leaves ${post_purchase_cash:,.2f} liquid cash after purchase (${cushion_remaining:,.2f} above reserve)."

    return CalculationResult(
        formula_id="form_p_purchase_affordability",
        formula_name="Discretionary Purchase Affordability",
        result={
            "verdict": verdict,
            "post_purchase_liquid_cash": float(q_curr(post_purchase_cash)),
            "safety_cushion_above_reserve": float(q_curr(cushion_remaining)),
            "interpretation": msg
        },
        result_formatted=f"{verdict} (Remaining Cash: ${post_purchase_cash:,.2f})",
        output_units="STATUS",
        inputs={"purchase_price": float(cost), "available_liquid_cash": float(cash), "monthly_surplus": float(surplus), "minimum_reserve": float(reserve)},
        explanation=msg,
        is_exact=True
    )

def calc_financial_health_index(
    savings_rate_pct: Any,
    dti_ratio_pct: Any,
    emergency_coverage_months: Any,
    credit_utilization_pct: Any
) -> CalculationResult:
    sav = max(Decimal("0.0"), to_d(savings_rate_pct))
    dti = max(Decimal("0.0"), to_d(dti_ratio_pct))
    emg = max(Decimal("0.0"), to_d(emergency_coverage_months))
    util = max(Decimal("0.0"), to_d(credit_utilization_pct))

    # Weighted scoring out of 100
    # 1. Savings score (max 25): 20% savings gives full 25
    s_score = min(Decimal("25.0"), (sav / Decimal("20.0")) * Decimal("25.0"))
    # 2. DTI score (max 25): DTI 0% gives 25, DTI 50% gives 0
    d_score = max(Decimal("0.0"), Decimal("25.0") - (dti / Decimal("2.0")))
    # 3. Emergency fund score (max 25): 6 months gives full 25
    e_score = min(Decimal("25.0"), (emg / Decimal("6.0")) * Decimal("25.0"))
    # 4. Credit utilization score (max 25): 0% util gives 25, 100% gives 0
    u_score = max(Decimal("0.0"), Decimal("25.0") - (util / Decimal("4.0")))

    total_score = q_pct(s_score + d_score + e_score + u_score)
    tier = "EXCELLENT" if total_score >= Decimal("80.0") else ("GOOD" if total_score >= Decimal("65.0") else ("FAIR" if total_score >= Decimal("50.0") else "POOR"))

    return CalculationResult(
        formula_id="form_p_financial_health_index",
        formula_name="Composite Financial Health Index",
        result={
            "composite_score": float(total_score),
            "tier": tier,
            "savings_component": float(s_score),
            "debt_component": float(d_score),
            "emergency_component": float(e_score),
            "credit_component": float(u_score)
        },
        result_formatted=f"{total_score}/100 ({tier})",
        output_units="score",
        inputs={"savings_rate_pct": float(sav), "dti_pct": float(dti), "emergency_months": float(emg), "credit_util_pct": float(util)},
        explanation=f"Evaluated financial health score of {total_score}/100 based on savings, debt service, liquidity, and credit usage.",
        is_exact=True
    )

def calc_opportunity_cost(
    expenditure_amount: Any,
    expected_annual_return_pct: Any = 7.0,
    horizon_years: int = 10
) -> CalculationResult:
    amt = to_d(expenditure_amount)
    r_pct = to_d(expected_annual_return_pct)
    yrs = max(1, int(horizon_years))
    r = float(r_pct / Decimal("100"))
    future_forgone = q_curr(amt * to_d(math.pow(1.0 + r, yrs)))
    growth_forgone = q_curr(future_forgone - amt)
    return CalculationResult(
        formula_id="form_p_opportunity_cost",
        formula_name="Opportunity Cost of Spending vs. Investing",
        result={"future_forgone_wealth": float(future_forgone), "lost_investment_gain": float(growth_forgone)},
        result_formatted=f"${future_forgone:,.2f} forgone (Lost Gain: ${growth_forgone:,.2f})",
        output_units="USD",
        inputs={"expenditure_amount": float(amt), "annual_return_pct": float(r_pct), "horizon_years": yrs},
        explanation=f"Investing ${amt:,.2f} at {r_pct}% compound return over {yrs} years would grow to ${future_forgone:,.2f}.",
        is_exact=True
    )

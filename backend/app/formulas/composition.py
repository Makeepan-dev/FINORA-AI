from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .models import CalculationResult
from .registry import global_formula_registry
from .decimal_engine import (
    to_d, q_curr, q_pct, s_div,
    calc_cost_per_use,
    calc_commerce_tco,
    calc_loan_amortization_schedule,
    calc_loan_early_repayment_savings,
    calc_emergency_fund_target,
    calc_purchase_affordability,
    calc_fixed_deposit_maturity,
    calc_after_tax_deposit_yield,
    calc_opportunity_cost,
    calc_straight_line_depreciation
)

class CompositionWorkflowResult(BaseModel):
    recipe_id: str
    recipe_name: str
    decision_verdict: str  # e.g., "KEEP", "REPLACE", "ELIMINATE", "AFFORDABLE", "EARLY_PAYOFF_FAVORABLE"
    summary_explanation: str
    step_results: Dict[str, Any]
    metrics: Dict[str, Any]
    recommendations: List[str]
    warnings: List[str] = Field(default_factory=list)
    confidence_score: float = 1.0

class FormulaCompositionEngine:
    """
    Multi-Formula Composition Engine for Complex Financial Decisions.
    Orchestrates sequential and multi-branch execution across registered formulas
    to generate authoritative, mathematically verified recommendations.
    """
    def __init__(self, registry=None):
        self.registry = registry or global_formula_registry

    # -------------------------------------------------------------------------
    # RECIPE 1: SUBSCRIPTION / GYM EVALUATION (KEEP, REDUCE, REPLACE, ELIMINATE, INVESTIGATE)
    # -------------------------------------------------------------------------
    def evaluate_subscription_decision(
        self,
        subscription_name: str,
        monthly_cost: Any,
        recorded_uses_90_days: Optional[int],
        user_confirmed_active: Optional[bool] = None,
        alternative_monthly_price: Optional[Any] = None,
        alternative_name: Optional[str] = None,
        cancellation_notice_days: int = 30
    ) -> CompositionWorkflowResult:
        m_cost = to_d(monthly_cost)
        annual_cost = q_curr(m_cost * Decimal("12"))
        cost_90_days = q_curr(m_cost * Decimal("3"))
        
        step_results = {
            "monthly_commitment": float(m_cost),
            "annual_commitment": float(annual_cost)
        }
        warnings = []
        recommendations = []

        # Step 1: Cost per use evaluation
        if recorded_uses_90_days is None and user_confirmed_active is None:
            verdict = "INVESTIGATE"
            cpu_val = None
            explanation = (
                f"Usage telemetry for {subscription_name} (${m_cost:,.2f}/mo) is missing or unverified. "
                "FINORA does not assume non-use merely because telemetry is absent. Verification required."
            )
            warnings.append("Missing usage telemetry; check with user before proposing cancellation.")
            recommendations.append("Confirm active monthly utilization or check external activity history.")
        elif recorded_uses_90_days == 0 and user_confirmed_active is False:
            verdict = "ELIMINATE"
            cpu_val = None
            explanation = (
                f"Zero utilization confirmed over 90 days ($0.00 value retrieved on ${cost_90_days:,.2f} spent). "
                f"Eliminating this commitment recovers ${m_cost:,.2f}/mo (${annual_cost:,.2f}/yr) with zero functional loss."
            )
            recommendations.append(f"Prepare cancellation letter respecting {cancellation_notice_days}-day notice period.")
        else:
            uses = recorded_uses_90_days or (1 if user_confirmed_active else 0)
            cpu_res = calc_cost_per_use(cost_90_days, uses)
            cpu_val = cpu_res.result
            step_results["cost_per_use_90_days"] = cpu_val

            # Step 2: Compare against alternative if available
            if alternative_monthly_price is not None:
                alt_cost = to_d(alternative_monthly_price)
                step_results["alternative_monthly"] = float(alt_cost)
                alt_annual = q_curr(alt_cost * Decimal("12"))
                annual_net_savings = q_curr(annual_cost - alt_annual)
                step_results["annual_net_savings_with_alt"] = float(annual_net_savings)

                if alt_cost < m_cost and (cpu_val is None or cpu_val > float(alt_cost)):
                    verdict = "REPLACE"
                    explanation = (
                        f"{subscription_name} costs ${m_cost:,.2f}/mo (${cpu_val:,.2f} per use). "
                        f"Switching to {alternative_name or 'verified alternative'} (${alt_cost:,.2f}/mo) saves "
                        f"${m_cost - alt_cost:,.2f}/mo (+${annual_net_savings:,.2f}/yr)."
                    )
                    recommendations.append(f"Switch to {alternative_name or 'lower-tier plan'} to capture annual net savings.")
                elif uses >= 8:  # 8+ workouts in 90 days (~2-3/month)
                    verdict = "KEEP"
                    explanation = f"Active regular utilization ({uses} visits in 90 days; ${cpu_val:,.2f}/visit). Healthy value delivered."
                    recommendations.append("Maintain active subscription; monitor annual price increase notices.")
                else:
                    verdict = "REDUCE"
                    explanation = f"Low frequency utilization ({uses} uses in 90 days; ${cpu_val:,.2f}/use). Recommend downgrade or pay-per-visit tier."
                    recommendations.append("Downgrade to basic tier or purchase flexible drop-in session packs.")
            else:
                if uses >= 8:
                    verdict = "KEEP"
                    explanation = f"Active utilization verified ({uses} uses in 90 days). Delivers solid utility for ${m_cost:,.2f}/mo."
                elif uses > 0:
                    verdict = "REDUCE"
                    explanation = f"Low utilization ({uses} uses in 90 days; ${cpu_val:,.2f}/use). Consider pausing or downgrading."
                else:
                    verdict = "INVESTIGATE"
                    explanation = f"Only 0 telemetry check-ins logged, but user confirmation needed before classifying as idle."

        return CompositionWorkflowResult(
            recipe_id="recipe_subscription_optimization",
            recipe_name="Subscription Retention & Optimization Workflow",
            decision_verdict=verdict,
            summary_explanation=explanation,
            step_results=step_results,
            metrics={
                "monthly_cost": float(m_cost),
                "annual_cost": float(annual_cost),
                "cost_per_use": cpu_val,
                "recorded_uses": recorded_uses_90_days
            },
            recommendations=recommendations,
            warnings=warnings
        )

    # -------------------------------------------------------------------------
    # RECIPE 2: LOAN EARLY REPAYMENT DECISION
    # -------------------------------------------------------------------------
    def evaluate_loan_early_repayment(
        self,
        loan_principal: Any,
        annual_interest_rate_pct: Any,
        remaining_months: int,
        extra_monthly_repayment: Any,
        liquid_cash_reserves: Any,
        monthly_essential_expenses: Any
    ) -> CompositionWorkflowResult:
        p = to_d(loan_principal)
        r_pct = to_d(annual_interest_rate_pct)
        n = max(1, int(remaining_months))
        extra = to_d(extra_monthly_repayment)
        liquid = to_d(liquid_cash_reserves)
        essential = to_d(monthly_essential_expenses)

        # 1. Base amortization
        base_amort = calc_loan_amortization_schedule(p, r_pct, n)
        monthly_pmt = to_d(base_amort.result["monthly_payment"])
        total_orig_int = to_d(base_amort.result["total_interest"])

        # 2. Early payoff simulation
        early_res = calc_loan_early_repayment_savings(p, r_pct, n, extra)
        interest_saved = to_d(early_res.result["interest_saved"])
        months_saved = early_res.result["months_saved"]

        # 3. Liquidity impact & emergency reserve check
        emergency_min = q_curr(essential * Decimal("3.0"))  # 3-month survival floor
        remaining_cash_after_1yr_extra = liquid - (extra * Decimal("12"))

        warnings = []
        recommendations = []

        if remaining_cash_after_1yr_extra < emergency_min:
            verdict = "CAUTION_RESERVES_AT_RISK"
            explanation = (
                f"Paying an extra ${extra:,.2f}/mo would save ${interest_saved:,.2f} in interest, "
                f"but it reduces liquid cash below your 3-month emergency safety floor (${emergency_min:,.2f})."
            )
            warnings.append("Early prepayment accelerates debt reduction but increases short-term liquidity risk.")
            recommendations.append("Build emergency cushion to 6 months before committing to aggressive loan payoff.")
        else:
            verdict = "EARLY_PAYOFF_RECOMMENDED"
            explanation = (
                f"Making extra payments of ${extra:,.2f}/mo saves ${interest_saved:,.2f} in interest and eliminates "
                f"the debt {months_saved} months early ({months_saved // 12} yrs, {months_saved % 12} mo sooner) "
                f"while maintaining safe emergency reserves."
            )
            recommendations.append(f"Set up automated extra monthly principal payment of ${extra:,.2f}.")
            recommendations.append("Instruct lender to apply additional funds directly to principal, not future interest.")

        return CompositionWorkflowResult(
            recipe_id="recipe_loan_early_payoff",
            recipe_name="Loan Early Repayment & Liquidity Assessment",
            decision_verdict=verdict,
            summary_explanation=explanation,
            step_results={
                "base_monthly_installment": float(monthly_pmt),
                "total_original_interest": float(total_orig_int),
                "interest_saved": float(interest_saved),
                "months_shortened": months_saved,
                "emergency_floor_required": float(emergency_min)
            },
            metrics={
                "interest_saved_usd": float(interest_saved),
                "months_saved": months_saved,
                "monthly_commitment": float(monthly_pmt + extra)
            },
            recommendations=recommendations,
            warnings=warnings
        )

    # -------------------------------------------------------------------------
    # RECIPE 3: PURCHASE AFFORDABILITY & BUDGET IMPACT
    # -------------------------------------------------------------------------
    def evaluate_purchase_affordability(
        self,
        item_name: str,
        price: Any,
        shipping: Any = 0.0,
        tax_pct: Any = 0.0,
        available_liquid_cash: Any = 0.0,
        monthly_income: Any = 0.0,
        monthly_expenses: Any = 0.0,
        essential_expenses: Any = 0.0
    ) -> CompositionWorkflowResult:
        p, shp, tax = to_d(price), to_d(shipping), to_d(tax_pct)
        cash = to_d(available_liquid_cash)
        inc, exp, ess = to_d(monthly_income), to_d(monthly_expenses), to_d(essential_expenses)

        # 1. Total acquisition cost
        tax_amt = q_curr(p * (tax / Decimal("100")))
        total_price = q_curr(p + shp + tax_amt)

        # 2. Monthly surplus
        surplus = q_curr(inc - exp)
        emergency_floor = q_curr(ess * Decimal("3.0"))  # 3 months essential cushion

        # 3. Execute affordability formula
        aff_res = calc_purchase_affordability(total_price, cash, surplus, emergency_floor)
        verdict = aff_res.result["verdict"]

        # 4. Opportunity cost calculation
        opp_res = calc_opportunity_cost(total_price, Decimal("7.0"), 10)
        opp_forgone = opp_res.result["future_forgone_wealth"]

        recommendations = []
        warnings = []

        if verdict == "AFFORDABLE":
            explanation = (
                f"The purchase of {item_name} for ${total_price:,.2f} is fully affordable. "
                f"It leaves ${cash - total_price:,.2f} liquid cash, comfortably preserving your emergency reserve (${emergency_floor:,.2f})."
            )
            recommendations.append("Proceed through standard PayPal checkout with Step 14 user authorization.")
        elif verdict == "AFFORDABLE_WITH_CAUTION":
            explanation = (
                f"{item_name} (${total_price:,.2f}) can be purchased from current cash, but it dips into your "
                f"recommended emergency reserve floor of ${emergency_floor:,.2f}."
            )
            warnings.append("Emergency cash cushion will be reduced below the safe 3-month threshold.")
            recommendations.append("Consider postponing purchase until surplus replenishes cash buffer.")
        else:
            explanation = (
                f"{item_name} (${total_price:,.2f}) exceeds available liquidity (${cash:,.2f}). "
                "Purchasing would trigger overdraft or high-interest revolving credit card balances."
            )
            warnings.append("Insufficient liquid funds. Purchase rejected by financial safety policy.")
            recommendations.append("Set up a targeted monthly savings sinking fund.")

        return CompositionWorkflowResult(
            recipe_id="recipe_purchase_affordability",
            recipe_name="Purchase Affordability & Budget Impact Workflow",
            decision_verdict=verdict,
            summary_explanation=explanation,
            step_results={
                "total_checkout_price": float(total_price),
                "liquid_cash_before": float(cash),
                "liquid_cash_after": float(q_curr(cash - total_price)),
                "emergency_reserve_floor": float(emergency_floor),
                "ten_year_opportunity_cost": float(opp_forgone)
            },
            metrics={
                "total_cost": float(total_price),
                "affordability_verdict": verdict,
                "opportunity_cost_10yr": float(opp_forgone)
            },
            recommendations=recommendations,
            warnings=warnings
        )

    # -------------------------------------------------------------------------
    # RECIPE 4: BANK DEPOSIT COMPARISON (FD vs SAVINGS vs APY)
    # -------------------------------------------------------------------------
    def compare_deposit_options(
        self,
        principal: Any,
        tenure_months: int,
        option_a_name: str,
        option_a_rate_pct: Any,
        option_a_compound_freq: int,
        option_b_name: str,
        option_b_rate_pct: Any,
        option_b_compound_freq: int,
        marginal_tax_rate_pct: Any = 22.0
    ) -> CompositionWorkflowResult:
        p = to_d(principal)
        m = max(1, int(tenure_months))
        tax = to_d(marginal_tax_rate_pct)

        # Deposit A
        res_a = calc_fixed_deposit_maturity(p, option_a_rate_pct, m, option_a_compound_freq)
        yield_a = calc_after_tax_deposit_yield(option_a_rate_pct, tax)
        
        # Deposit B
        res_b = calc_fixed_deposit_maturity(p, option_b_rate_pct, m, option_b_compound_freq)
        yield_b = calc_after_tax_deposit_yield(option_b_rate_pct, tax)

        mat_a = to_d(res_a.result["maturity_amount"])
        mat_b = to_d(res_b.result["maturity_amount"])
        diff = q_curr(abs(mat_a - mat_b))

        if mat_a >= mat_b:
            winner = option_a_name
            verdict = f"OPTION_A_FAVORABLE ({option_a_name})"
            explanation = (
                f"{option_a_name} yields ${mat_a:,.2f} vs ${mat_b:,.2f} for {option_b_name} after {m} months. "
                f"Net advantage: +${diff:,.2f} (After-tax yield: {yield_a.result}% vs {yield_b.result}%)."
            )
        else:
            winner = option_b_name
            verdict = f"OPTION_B_FAVORABLE ({option_b_name})"
            explanation = (
                f"{option_b_name} yields ${mat_b:,.2f} vs ${mat_a:,.2f} for {option_a_name} after {m} months. "
                f"Net advantage: +${diff:,.2f} (After-tax yield: {yield_b.result}% vs {yield_a.result}%)."
            )

        return CompositionWorkflowResult(
            recipe_id="recipe_deposit_comparison",
            recipe_name="Deposit Yield & After-Tax Comparison",
            decision_verdict=verdict,
            summary_explanation=explanation,
            step_results={
                "option_a": {"name": option_a_name, "maturity": float(mat_a), "after_tax_yield": yield_a.result},
                "option_b": {"name": option_b_name, "maturity": float(mat_b), "after_tax_yield": yield_b.result},
                "net_dollar_difference": float(diff)
            },
            metrics={"winner": winner, "extra_yield_usd": float(diff)},
            recommendations=[f"Allocate deposit capital to {winner} for optimal yield."],
            warnings=[]
        )

    # -------------------------------------------------------------------------
    # RECIPE 5: VEHICLE / LARGE ASSET TOTAL COST OF OWNERSHIP & AFFORDABILITY
    # -------------------------------------------------------------------------
    def evaluate_vehicle_ownership_affordability(
        self,
        vehicle_model: str,
        purchase_price: Any,
        down_payment: Any,
        loan_rate_pct: Any,
        loan_months: int,
        fuel_monthly: Any,
        insurance_monthly: Any,
        maintenance_monthly: Any,
        monthly_income: Any,
        monthly_existing_expenses: Any
    ) -> CompositionWorkflowResult:
        price = to_d(purchase_price)
        dp = to_d(down_payment)
        r_pct = to_d(loan_rate_pct)
        n = max(1, int(loan_months))
        fuel, ins, maint = to_d(fuel_monthly), to_d(insurance_monthly), to_d(maintenance_monthly)
        inc, exp = to_d(monthly_income), to_d(monthly_existing_expenses)

        # 1. Loan repayment calculation on financed portion
        loan_amt = max(Decimal("0.00"), price - dp)
        amort = calc_loan_amortization_schedule(loan_amt, r_pct, n)
        loan_pmt = to_d(amort.result["monthly_payment"])

        # 2. Total recurring running cost per month
        running_costs = fuel + ins + maint
        total_monthly_commitment = q_curr(loan_pmt + running_costs)

        # 3. Depreciation over 5 years (assuming 40% salvage)
        salvage = q_curr(price * Decimal("0.40"))
        depr = calc_straight_line_depreciation(price, salvage, 5)
        monthly_depreciation = to_d(depr.result["monthly_depreciation"])

        # 4. Total true economic cost (cash out + depreciation)
        economic_monthly_cost = q_curr(total_monthly_commitment + monthly_depreciation)

        # 5. Affordability check (car costs should not exceed 15-20% of monthly income)
        cost_to_income_pct = q_pct(s_div(total_monthly_commitment * Decimal("100"), inc))
        surplus_before = inc - exp
        surplus_after = surplus_before - total_monthly_commitment

        warnings = []
        recommendations = []

        if surplus_after < Decimal("0.00"):
            verdict = "UNAFFORDABLE"
            explanation = (
                f"Financing and running {vehicle_model} requires ${total_monthly_commitment:,.2f}/mo "
                f"(${loan_pmt:,.2f} loan + ${running_costs:,.2f} fuel/ins/maint). "
                f"This creates a monthly cash deficit of ${abs(surplus_after):,.2f}."
            )
            warnings.append("Vehicle costs exceed monthly unallocated cash flow.")
            recommendations.append("Consider a lower purchase tier or higher down payment to reduce loan EMI.")
        elif cost_to_income_pct > Decimal("20.0"):
            verdict = "HEAVY_BUDGET_BURDEN"
            explanation = (
                f"{vehicle_model} consumes {cost_to_income_pct}% of your monthly gross income "
                f"(${total_monthly_commitment:,.2f}/mo). Standard automotive affordability guideline is <= 15-20%."
            )
            warnings.append("Automotive expenses exceed 20% of monthly income.")
            recommendations.append("Shop for cheaper insurance or choose certified pre-owned to reduce depreciation.")
        else:
            verdict = "AFFORDABLE"
            explanation = (
                f"{vehicle_model} is comfortably affordable at ${total_monthly_commitment:,.2f}/mo "
                f"({cost_to_income_pct}% of income). Preserves ${surplus_after:,.2f}/mo in ongoing savings."
            )
            recommendations.append("Ensure comprehensive insurance policy coverage is secured before collection.")

        return CompositionWorkflowResult(
            recipe_id="recipe_vehicle_tco_affordability",
            recipe_name="Vehicle True Cost of Ownership & Affordability",
            decision_verdict=verdict,
            summary_explanation=explanation,
            step_results={
                "loan_principal": float(loan_amt),
                "monthly_loan_installment": float(loan_pmt),
                "monthly_running_costs": float(running_costs),
                "total_monthly_cash_outflow": float(total_monthly_commitment),
                "monthly_depreciation": float(monthly_depreciation),
                "true_economic_monthly_cost": float(economic_monthly_cost),
                "cost_to_income_ratio_pct": float(cost_to_income_pct)
            },
            metrics={
                "monthly_cash_commitment": float(total_monthly_commitment),
                "cost_to_income_pct": float(cost_to_income_pct),
                "monthly_surplus_remaining": float(surplus_after)
            },
            recommendations=recommendations,
            warnings=warnings
        )

global_composition_engine = FormulaCompositionEngine()

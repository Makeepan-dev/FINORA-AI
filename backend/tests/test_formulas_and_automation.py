import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.formulas.registry import global_formula_registry
from app.formulas.models import FormulaDomain, FormulaStatus
from app.formulas.decimal_engine import (
    calc_percentage_change,
    calc_simple_interest,
    calc_compound_interest,
    calc_present_value,
    calc_effective_annual_rate,
    calc_rule_of_72,
    calc_inflation_adjusted_value,
    calc_disposable_income,
    calc_monthly_cash_flow,
    calc_savings_rate,
    calc_expense_ratios,
    calc_income_volatility,
    calc_required_monthly_savings,
    calc_emergency_fund_target,
    calc_emergency_fund_coverage,
    calc_fixed_deposit_maturity,
    calc_after_tax_deposit_yield,
    calc_loan_amortization_schedule,
    calc_loan_early_repayment_savings,
    calc_debt_to_income_ratio,
    calc_loan_to_value_ratio,
    calc_credit_utilization,
    calc_credit_card_interest_charge,
    calc_net_worth,
    calc_cagr,
    calc_roi,
    calc_progressive_income_tax,
    calc_insurance_claim_payout,
    calc_fx_conversion,
    calc_commerce_tco,
    calc_cost_per_use,
    calc_unit_price,
    calc_buy_vs_subscribe_break_even,
    calc_straight_line_depreciation,
    calc_rental_yield,
    calc_effective_hourly_rate,
    calc_simple_moving_average,
    calc_bond_price,
    calc_black_scholes,
    calc_purchase_affordability,
    calc_financial_health_index,
    calc_opportunity_cost
)
from app.formulas.composition import global_composition_engine
from app.automation.engine import global_automation_engine
from app.automation.safety import global_safety_manager, ActionSafetyLevel, ActionStatus
from app.automation.models import TriggerType
from app.optimization.engine import global_financial_optimization_engine

client = TestClient(app)

# =========================================================================
# PART 1: FORMULA MATHEMATICAL ACCURACY TESTS
# =========================================================================

def test_percentage_change_math():
    # +50% increase
    res = calc_percentage_change(100, 150)
    assert res.result == 50.0
    # -20% decrease
    res2 = calc_percentage_change(50, 40)
    assert res2.result == -20.0
    # Zero baseline handling
    res3 = calc_percentage_change(0, 100)
    assert len(res3.warnings) > 0

def test_simple_interest_math():
    # P = 1000, r = 5%, t = 2 yrs -> I = 100, A = 1100
    res = calc_simple_interest(1000, 5, 2)
    assert res.result["interest_amount"] == 100.00
    assert res.result["total_accrued_amount"] == 1100.00

def test_compound_interest_math():
    # P = 1000, r = 10%, t = 2 yrs, annual compounding -> FV = 1000 * 1.10^2 = 1210.00
    res = calc_compound_interest(1000, 10, 2, compound_freq=1)
    assert res.result["future_value"] == 1210.00
    assert res.result["interest_earned"] == 210.00

def test_present_value_discounting():
    # FV = 1210, r = 10%, t = 2 yrs -> PV = 1000.00
    res = calc_present_value(1210, 10, 2)
    assert res.result == 1000.00

def test_effective_annual_rate():
    # Nominal 12% compounded monthly (1% per month) -> (1.01)^12 - 1 = 12.6825%
    res = calc_effective_annual_rate(12, 12)
    assert abs(res.result - 12.68) < 0.05

def test_rule_of_72():
    # r = 8% -> 72 / 8 = 9.0 years
    res = calc_rule_of_72(8)
    assert res.result == 9.0

def test_disposable_income_math():
    # Gross 6000, Tax 1200, Deductions 300 -> 4500
    res = calc_disposable_income(6000, 1200, 300)
    assert res.result["disposable_income"] == 4500.00
    assert res.result["take_home_ratio_pct"] == 75.00

def test_monthly_cash_flow_and_status():
    res_surplus = calc_monthly_cash_flow(5000, 3500)
    assert res_surplus.result["net_cash_flow"] == 1500.00
    assert res_surplus.result["status"] == "SURPLUS"

    res_deficit = calc_monthly_cash_flow(3000, 4000)
    assert res_deficit.result["net_cash_flow"] == -1000.00
    assert res_deficit.result["status"] == "DEFICIT"
    assert len(res_deficit.warnings) > 0

def test_emergency_fund_calculations():
    # Essential = 2500, Target 6 months -> 15000
    tgt = calc_emergency_fund_target(2500, 6)
    assert tgt.result == 15000.00

    # Current liquid = 7500 on 2500 essential -> 3.0 months (ADEQUATE)
    cov = calc_emergency_fund_coverage(7500, 2500)
    assert cov.result["coverage_months"] == 3.0
    assert cov.result["status"] == "ADEQUATE"

def test_fixed_deposit_maturity():
    # P = 5000, r = 6%, 12 months, quarterly compounding (n=4)
    res = calc_fixed_deposit_maturity(5000, 6, 12, compound_freq=4)
    # (1 + 0.06/4)^4 = (1.015)^4 = 1.06136355 -> 5306.82
    assert abs(res.result["maturity_amount"] - 5306.82) < 0.10

def test_loan_amortization_schedule():
    # P = 10,000, r = 6%, n = 12 months -> Monthly payment ~$860.66
    res = calc_loan_amortization_schedule(10000, 6, 12)
    assert abs(res.result["monthly_payment"] - 860.66) < 0.20
    assert res.result["total_payment"] > 10000.00

def test_loan_early_repayment():
    # P = 10,000, r = 6%, n = 36 months, extra $100/mo
    res = calc_loan_early_repayment_savings(10000, 6, 36, extra_monthly_payment=100)
    assert res.result["interest_saved"] > 0.0
    assert res.result["months_saved"] > 0

def test_debt_to_income_ratio():
    # Debt = 1500, Gross = 5000 -> 30% (HEALTHY)
    res = calc_debt_to_income_ratio(1500, 5000)
    assert res.result["dti_percent"] == 30.0
    assert res.result["risk_tier"] == "HEALTHY"

def test_credit_utilization():
    # Balance = 1500, Limit = 10000 -> 15% (GOOD)
    res = calc_credit_utilization(1500, 10000)
    assert res.result["utilization_pct"] == 15.0
    assert res.result["status"] == "GOOD"

def test_net_worth():
    # Assets 250,000, Liabilities 100,000 -> 150,000
    res = calc_net_worth(250000, 100000)
    assert res.result["net_worth"] == 150000.00

def test_progressive_tax_us():
    # US Single 2024: $50,000 taxable income
    # First $11,600 at 10% = $1,160
    # Next ($47,150 - $11,600) = $35,550 at 12% = $4,266
    # Remaining ($50,000 - $47,150) = $2,850 at 22% = $627
    # Total tax = 1160 + 4266 + 627 = $6,053.00
    res = calc_progressive_income_tax(50000, "US_SINGLE_2024")
    assert abs(res.result["tax_liability"] - 6053.00) < 1.0
    assert res.result["marginal_tax_rate_pct"] == 22.0

def test_insurance_claim_payout():
    # Loss 10,000, Deductible 1,000, Coinsurance 20%
    # Covered = 9,000; Insurer 80% = 7,200; User out of pocket = 2,800
    res = calc_insurance_claim_payout(10000, 1000, coinsurance_pct=20)
    assert res.result["net_payout"] == 7200.00
    assert res.result["out_of_pocket_expense"] == 2800.00

def test_fx_conversion():
    # Send $1,000 USD to EUR at rate 0.92 with 1.5% spread and $5 fee
    res = calc_fx_conversion(1000, 0.92, spread_markup_pct=1.5, fixed_transfer_fee=5)
    assert res.result["target_received_amount"] > 890.0
    assert res.result["total_fees_and_spread"] > 15.0

def test_commerce_cost_per_use():
    # $360 spent over 12 uses -> $30/use
    res = calc_cost_per_use(360, 12)
    assert res.result == 30.00
    # Zero uses -> None with warning
    res_zero = calc_cost_per_use(360, 0)
    assert res_zero.result is None
    assert len(res_zero.warnings) > 0

def test_straight_line_depreciation():
    # Cost 30,000, Salvage 6,000, 5 years -> (24,000 / 5) = 4,800/yr ($400/mo)
    res = calc_straight_line_depreciation(30000, 6000, 5)
    assert res.result["annual_depreciation"] == 4800.00
    assert res.result["monthly_depreciation"] == 400.00

def test_black_scholes_option_pricing():
    # Spot 100, Strike 100, 1 Year, r = 5%, vol = 20% -> Standard benchmark call price ~$10.45
    res = calc_black_scholes(100, 100, 1.0, 5.0, 20.0)
    assert abs(res.result["call_price"] - 10.45) < 0.20
    assert res.result["put_price"] > 0.0

def test_financial_health_index():
    # 20% savings, 20% DTI, 6 months emergency, 10% credit util -> High score
    res = calc_financial_health_index(20.0, 20.0, 6.0, 10.0)
    assert res.result["composite_score"] >= 80.0
    assert res.result["tier"] == "EXCELLENT"

# =========================================================================
# PART 2: FORMULA REGISTRY TESTS
# =========================================================================

def test_registry_coverage_and_metadata():
    summary = global_formula_registry.get_summary()
    assert summary["total_registered_formulas"] >= 25
    assert summary["executable_count"] >= 20
    # Verify all domains are present
    assert len(summary["domain_breakdown"]) >= 10

def test_registry_execution_via_id():
    inputs = {"old_val": 200, "new_val": 300}
    res = global_formula_registry.execute("form_a_pct_change", inputs)
    assert res.result == 50.0

def test_registry_missing_input_validation():
    with pytest.raises(ValueError):
        global_formula_registry.execute("form_a_pct_change", {"old_val": 100})

# =========================================================================
# PART 3: FORMULA COMPOSITION TESTS
# =========================================================================

def test_composition_subscription_decision_replace():
    res = global_composition_engine.evaluate_subscription_decision(
        subscription_name="Apex Athletic",
        monthly_cost=120.0,
        recorded_uses_90_days=1,
        alternative_monthly_price=49.0,
        alternative_name="MetroFit"
    )
    assert res.decision_verdict == "REPLACE"
    assert "MetroFit" in res.summary_explanation
    assert res.step_results["annual_net_savings_with_alt"] == 852.0

def test_composition_subscription_decision_eliminate():
    res = global_composition_engine.evaluate_subscription_decision(
        subscription_name="Unused Cloud Host",
        monthly_cost=50.0,
        recorded_uses_90_days=0,
        user_confirmed_active=False
    )
    assert res.decision_verdict == "ELIMINATE"
    assert len(res.recommendations) > 0

def test_composition_purchase_affordability():
    # Case 1: Affordable (liquid cash 8000 > essential 2000 * 3 + 150)
    res_aff = global_composition_engine.evaluate_purchase_affordability(
        item_name="Mechanical Keyboard",
        price=150.0,
        available_liquid_cash=8000.0,
        monthly_income=5000.0,
        monthly_expenses=3200.0,
        essential_expenses=2000.0
    )
    assert res_aff.decision_verdict == "AFFORDABLE"

    # Case 2: Not recommended (exceeds liquid cash)
    res_unaff = global_composition_engine.evaluate_purchase_affordability(
        item_name="Luxury Watch",
        price=10000.0,
        available_liquid_cash=2000.0,
        monthly_income=5000.0,
        monthly_expenses=3200.0,
        essential_expenses=2000.0
    )
    assert res_unaff.decision_verdict == "NOT_RECOMMENDED"

def test_composition_deposit_comparison():
    res = global_composition_engine.compare_deposit_options(
        principal=10000,
        tenure_months=12,
        option_a_name="Bank Alpha 5.5% CD",
        option_a_rate_pct=5.5,
        option_a_compound_freq=4,
        option_b_name="Bank Beta 4.8% CD",
        option_b_rate_pct=4.8,
        option_b_compound_freq=12
    )
    assert "Bank Alpha" in res.decision_verdict
    assert res.metrics["extra_yield_usd"] > 0

# =========================================================================
# PART 4: AUTOMATION & SAFETY TESTS
# =========================================================================

def test_automation_rules_registry():
    rules = global_automation_engine.get_rules()
    assert len(rules) >= 5
    # Verify rule categories cover Income, Expense, Subscription, Savings, Debt
    categories = {r["category"] for r in rules}
    assert "INCOME" in categories
    assert "EXPENSE" in categories
    assert "SUBSCRIPTION" in categories

def test_automation_toggle_rule():
    rule_id = "rule_unusual_spend_alert"
    res1 = global_automation_engine.set_rule_enabled(rule_id, False)
    assert res1 is True
    assert global_automation_engine.get_rule(rule_id).is_enabled is False
    # Re-enable
    global_automation_engine.set_rule_enabled(rule_id, True)
    assert global_automation_engine.get_rule(rule_id).is_enabled is True

def test_automation_trigger_event_evaluation():
    # Test triggering unusual spend event
    logs = global_automation_engine.evaluate_event(
        trigger_type=TriggerType.NEW_TRANSACTION,
        context={"amount": 450.0, "merchant": "High-End Electronics", "is_duplicate_candidate": False}
    )
    assert len(logs) > 0
    rule_ids = [l.rule_id for l in logs]
    assert "rule_unusual_spend_alert" in rule_ids

def test_action_safety_manager_lifecycle():
    # 1. Create a Level 3 action
    action = global_safety_manager.create_action(
        safety_level=ActionSafetyLevel.LEVEL_3_USER_APPROVED,
        title="Test Subscription Cancellation",
        description="Cancel unused service",
        action_type="subscription_cancellation_dispatch",
        target_merchant_or_payee="Test Streaming",
        amount=19.99
    )
    assert action.status == ActionStatus.PENDING_APPROVAL

    # 2. Level 4 must raise PermissionError
    with pytest.raises(PermissionError):
        global_safety_manager.create_action(
            safety_level=ActionSafetyLevel.LEVEL_4_RESTRICTED,
            title="Forbidden Autonomous Spend",
            description="Bypasses user",
            action_type="unrestricted_wire",
            target_merchant_or_payee="Attacker",
            amount=50000.0
        )

    # 3. Approve action
    appr = global_safety_manager.approve_action(action.action_id, user_id="usr_alex_chen")
    assert appr["success"] is True
    assert appr["status"] == "EXECUTED"

# =========================================================================
# PART 5: OPTIMIZATION ENGINE TESTS
# =========================================================================

def test_optimization_opportunities_ranking():
    opps = global_financial_optimization_engine.generate_ranked_opportunities(user_id="usr_alex_chen")
    assert len(opps) >= 2
    # Verify ranking (highest rank_score first)
    for i in range(len(opps) - 1):
        assert opps[i].rank_score >= opps[i + 1].rank_score

# =========================================================================
# PART 6: REST API ROUTE TESTS
# =========================================================================

def test_api_formulas_endpoints():
    # List formulas
    res = client.get("/api/v1/formulas")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 20

    # Summary
    res_sum = client.get("/api/v1/formulas/catalog/summary")
    assert res_sum.status_code == 200
    assert res_sum.json()["total_registered_formulas"] >= 20

    # Execute formula
    res_calc = client.post(
        "/api/v1/formulas/form_a_pct_change/calculate",
        json={"old_val": 100, "new_val": 125}
    )
    assert res_calc.status_code == 200
    assert res_calc.json()["result"] == 25.0

def test_api_composition_endpoints():
    res = client.get("/api/v1/composition/recipes")
    assert res.status_code == 200
    assert len(res.json()) >= 3

    res_aff = client.post(
        "/api/v1/composition/purchase-affordability",
        json={
            "item_name": "Ergonomic Chair",
            "price": 350.0,
            "shipping": 0.0,
            "tax_pct": 8.0,
            "available_liquid_cash": 7000.0,
            "monthly_income": 6000.0,
            "monthly_expenses": 3400.0,
            "essential_expenses": 2200.0
        }
    )
    assert res_aff.status_code == 200
    assert res_aff.json()["decision_verdict"] == "AFFORDABLE"

def test_api_automation_endpoints():
    res_rules = client.get("/api/v1/automation/rules")
    assert res_rules.status_code == 200
    assert len(res_rules.json()) >= 5

    res_pending = client.get("/api/v1/automation/pending-actions")
    assert res_pending.status_code == 200
    assert isinstance(res_pending.json(), list)

def test_api_optimization_opportunities():
    res = client.get("/api/v1/optimization/opportunities")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert "first_year_net_savings" in data[0]

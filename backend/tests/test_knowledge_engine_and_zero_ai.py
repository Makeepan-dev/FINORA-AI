"""
Acceptance Test Suite for FINORA Knowledge-First Financial & Commerce Intelligence Engine.

Validates:
1. 100% Deterministic Financial & Commerce Algorithms (Decimal-precision math, zero binary float drift).
2. Internal Knowledge Base retrieval across all 5 domains without AI.
3. 7-Stage Knowledge Orchestrator routing (Internal-only vs. Gemini Escalation).
4. Zero-AI acceptance tests (Gym optimization, TCO, Break-even, Amortization with empty/absent API key).
5. User approval governance gate for all financial actions.
"""

from decimal import Decimal
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.algorithms.decimal_math import round_currency, safe_divide, to_decimal
from app.algorithms.financial_calculations import (
    calculate_loan_amortization,
    calculate_break_even,
    calculate_profit_margins,
    calculate_savings_rate,
    calculate_depreciation_straight_line,
)
from app.algorithms.financial_intelligence import (
    detect_duplicate_transactions,
    detect_recurring_commitments,
    detect_spending_anomalies,
    calculate_cash_flow_runway,
)
from app.algorithms.commerce_intelligence import (
    calculate_total_cost_of_ownership,
    calculate_cost_per_use,
    calculate_value_adjusted_score,
)
from app.knowledge.repository import global_knowledge_repository
from app.location.discovery import global_business_discovery
from app.location.service import global_location_service
from app.optimization.comparison import compare_recurring_alternatives
from app.optimization.expense_optimizer import global_expense_optimizer
from app.agents.financial_guardian import global_financial_guardian
from app.automation.engine import global_automation_engine


# ---------------------------------------------------------------------------
# 1. Deterministic Math & Calculation Tests (Zero Float Drift)
# ---------------------------------------------------------------------------

def test_decimal_precision_loan_amortization():
    """Loan amortization calculation must return mathematically exact schedules."""
    principal = Decimal("10000.00")
    rate = Decimal("6.5")
    months = 36

    result = calculate_loan_amortization(principal, rate, months)

    # Monthly payment for 10k @ 6.5% for 36 months is $306.49
    assert result["monthly_payment"] == 306.49
    assert result["total_payment"] == 11033.64
    assert result["total_interest"] == 1033.64
    assert len(result["sample_schedule"]) > 0


def test_break_even_and_profit_margins():
    """Break-even and multi-tier margins computed deterministically."""
    # Break-even: Fixed $5,000, Price $50, Variable $20 -> Q = 5000 / (50 - 20) = 166.67 -> 167 units
    be = calculate_break_even(Decimal("5000.00"), Decimal("50.00"), Decimal("20.00"))
    assert be["break_even_units"] == 167
    assert be["break_even_revenue"] == 8350.00

    # Margins: Revenue $100k, COGS $40k, OpEx $30k, 20% tax
    margins = calculate_profit_margins(
        revenue=Decimal("100000.00"),
        cogs=Decimal("40000.00"),
        operating_expenses=Decimal("30000.00"),
        tax_rate=Decimal("0.20")
    )
    assert margins["gross_margin_percent"] == 60.00
    assert margins["operating_margin_percent"] == 30.00
    assert margins["net_margin_percent"] == 24.00


def test_straight_line_depreciation():
    """Computes straight-line asset depreciation correctly."""
    dep = calculate_depreciation_straight_line(
        asset_cost=Decimal("12000.00"),
        salvage_value=Decimal("2000.00"),
        useful_life_years=5
    )
    assert dep["depreciable_base"] == 10000.00
    assert dep["annual_depreciation"] == 2000.00
    assert dep["monthly_depreciation"] == 166.67
    assert len(dep["schedule"]) == 5
    assert dep["schedule"][-1]["ending_book_value"] == 2000.00


def test_tco_and_cost_per_use():
    """TCO across 3 years and Cost-Per-Use with setup and maintenance."""
    tco = calculate_total_cost_of_ownership(
        base_price=Decimal("1200.00"),
        shipping_cost=Decimal("20.00"),
        tax_rate_percent=Decimal("8.5"),
        setup_fee=Decimal("50.00"),
        annual_maintenance=Decimal("100.00"),
        recurring_monthly_fee=Decimal("15.00"),
        lifespan_years=3
    )
    # Acquisition = 1200 + 20 + 102 + 50 = 1372
    # Recurring = 15 * 12 * 3 = 540
    # Maintenance = 100 * 3 = 300
    # Total = 1372 + 540 + 300 = 2212.00
    assert tco["initial_acquisition_cost"] == 1372.00
    assert tco["total_cost_of_ownership"] == 2212.00
    assert tco["annualized_tco"] == 737.33

    cpu = calculate_cost_per_use(
        total_cost=Decimal("1200.00"),
        total_uses=600
    )
    assert cpu["cost_per_use"] == 2.00


def test_duplicate_transaction_detection_with_whitelist():
    """Duplicate detection flags identical charges while respecting developer seat licenses."""
    txs = [
        {"transaction_id": "tx-1", "type": "expense", "merchant_id": "Figma", "amount": 15.00, "timestamp": "2026-03-01T10:00:00Z", "description": "Seat Alex"},
        {"transaction_id": "tx-2", "type": "expense", "merchant_id": "Figma", "amount": 15.00, "timestamp": "2026-03-01T10:05:00Z", "description": "Seat Maya"},
        {"transaction_id": "tx-3", "type": "expense", "merchant_id": "Uber", "amount": 34.50, "timestamp": "2026-03-02T12:00:00Z", "description": "Ride downtown"},
        {"transaction_id": "tx-4", "type": "expense", "merchant_id": "Uber", "amount": 34.50, "timestamp": "2026-03-02T12:01:00Z", "description": "Ride downtown duplicate"},
    ]
    dups = detect_duplicate_transactions(txs)
    # Figma seat licenses should be identified as legitimate distinct, Uber flagged as potential duplicate error
    uber_dup = next((d for d in dups if d["merchant_id"] == "Uber"), None)
    assert uber_dup is not None
    assert uber_dup["amount"] == 34.50
    assert uber_dup["investigation_verdict"] == "POTENTIAL_DUPLICATE_ERROR"
    assert uber_dup["requires_dispute"] is True

    figma_dup = next((d for d in dups if d["merchant_id"] == "Figma"), None)
    assert figma_dup is not None
    assert figma_dup["is_legitimate_distinct"] is True
    assert figma_dup["requires_dispute"] is False


# ---------------------------------------------------------------------------
# 2. Structured Financial Knowledge Base & Offline Routing Tests
# ---------------------------------------------------------------------------

def test_knowledge_repository_all_domains_populated():
    """Verify all 5 required domains exist and contain verified entries."""
    repo = global_knowledge_repository
    inv = repo.get_inventory_summary()
    domains = inv["domains"]
    assert "PersonalFinanceKnowledge" in domains
    assert "BusinessFinanceKnowledge" in domains
    assert "AccountingKnowledge" in domains
    assert "PaymentsCommerceKnowledge" in domains
    assert "ConsumerCommerceKnowledge" in domains

    # Verify key topics
    assert repo.get_by_topic("double_entry_equation") is not None
    assert repo.get_by_topic("cash_flow_margin") is not None
    assert repo.get_by_topic("merchant_fees") is not None
    assert repo.get_by_topic("total_cost_of_ownership") is not None


@pytest.mark.asyncio
async def test_subscription_total_without_gemini():
    """Direct subscription total questions run 100% internally with Zero AI calls."""
    result = await global_financial_guardian.chat(
        user_prompt="What is my total monthly subscription spending?",
        user_id="usr_alex_chen",
    )
    ai_resp = result["ai_response"]
    assert ai_resp["escalated_to_ai"] is False
    assert ai_resp["knowledge_sufficiency"] == "SUFFICIENT"
    assert "$291.97" in ai_resp["response"]
    assert "7 active recurring commitments" in ai_resp["response"]


@pytest.mark.asyncio
async def test_known_accounting_equation_without_gemini():
    """Accounting fundamental equation lookup must resolve internally without AI escalation."""
    result = await global_financial_guardian.chat(
        user_prompt="What is the fundamental accounting equation?",
        user_id="usr_alex_chen",
    )
    ai_resp = result["ai_response"]
    assert ai_resp["escalated_to_ai"] is False
    assert ai_resp["knowledge_sufficiency"] == "SUFFICIENT"
    assert "Assets = Liabilities + Equity" in ai_resp["response"]


@pytest.mark.asyncio
async def test_loan_amortization_question_without_gemini():
    """Loan repayment calculation query must resolve deterministically."""
    result = await global_financial_guardian.chat(
        user_prompt="Calculate loan payment for $10000 principal at 6.5% interest over 36 months",
        user_id="usr_alex_chen",
    )
    ai_resp = result["ai_response"]
    assert ai_resp["escalated_to_ai"] is False
    assert ai_resp["knowledge_sufficiency"] == "SUFFICIENT"
    assert "$306.49" in ai_resp["response"]
    assert "$1,033.64" in ai_resp["response"]


# ---------------------------------------------------------------------------
# 3. Location Intelligence & Zero-AI Autonomous Optimization
# ---------------------------------------------------------------------------

def test_location_discovery_haversine():
    """Location service calculates Haversine distance and finds verified nearby alternatives."""
    alternatives = global_business_discovery.find_nearby_alternatives(
        category="fitness",
        user_id="usr_alex_chen",
        max_distance_miles=5.0
    )
    assert len(alternatives) >= 2
    names = [alt["business_name"] for alt in alternatives]
    assert "MetroFit Downtown Flex" in names
    assert "IronPulse Community Gym" in names


def test_zero_ai_gym_optimization_workflow():
    """Complete recurring commitment comparison runs with ZERO AI calls."""
    # Current: Bay Club SF $220.00/mo; Alternative: MetroFit $49.00/mo ($0 setup)
    comparison = compare_recurring_alternatives(
        current_monthly_cost=Decimal("220.00"),
        alternative_monthly_cost=Decimal("49.00"),
        alternative_setup_fee=Decimal("0.00"),
        current_cancellation_fee=Decimal("0.00")
    )
    # Monthly savings = 220 - 49 = $171.00
    # Annual gross savings = 171 * 12 = $2,052.00
    assert comparison["monthly_run_rate_savings"] == 171.00
    assert comparison["first_year_net_savings"] == 2052.00
    assert comparison["break_even_months"] == 0.0
    assert comparison["is_economically_viable"] is True


def test_full_autonomous_optimization_pipeline():
    """Runs the 14-step expense optimizer and verifies action proposal generation."""
    proposal = global_expense_optimizer.run_optimization_workflow(user_id="usr_alex_chen")
    assert proposal["total_active_commitments"] == 7
    assert proposal["total_monthly_commitment"] == 291.97
    assert proposal["total_potential_monthly_savings"] > 100.0
    assert len(proposal["optimization_opportunities"]) == 7

    # Find the gym opportunity
    gym_opp = next(
        (opp for opp in proposal["optimization_opportunities"] if opp["category"] == "fitness"),
        None
    )
    assert gym_opp is not None
    assert gym_opp["best_alternative"] is not None
    assert gym_opp["best_alternative"]["business_name"] in ["MetroFit Downtown Flex", "IronPulse Community Gym"]
    assert gym_opp["best_alternative"]["monthly_price"] in [45.00, 49.00]
    assert gym_opp["best_alternative"]["comparison"]["first_year_net_savings"] > 800.00
    assert gym_opp["requires_user_approval"] is True


# ---------------------------------------------------------------------------
# 4. User Governance & Approval Gate Security
# ---------------------------------------------------------------------------

def test_governance_rule_present_in_optimization():
    """Step 14 User Approval Gate must be present in every optimization plan."""
    proposal = global_expense_optimizer.run_optimization_workflow(user_id="usr_alex_chen")
    assert "Step 14 User Approval Gate" in proposal["governance_rule"]
    assert "explicit user authorization" in proposal["governance_rule"].lower()


# ---------------------------------------------------------------------------
# 5. API Endpoints Acceptance Tests (FastAPI TestClient)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_knowledge_api_endpoints():
    """Test knowledge inventory, retrieval, and search endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Inventory
        inv_res = await client.get("/api/knowledge/inventory")
        assert inv_res.status_code == 200
        inv_data = inv_res.json()
        assert inv_data["total_knowledge_entries"] >= 15
        assert "PersonalFinanceKnowledge" in inv_data["domains"]

        # Topic lookup
        topic_res = await client.get("/api/knowledge/cash_flow_margin")
        assert topic_res.status_code == 200
        assert topic_res.json()["domain"] == "PersonalFinanceKnowledge"

        # Search
        search_res = await client.get("/api/knowledge/search?q=depreciation")
        assert search_res.status_code == 200
        assert len(search_res.json()) >= 1


@pytest.mark.asyncio
async def test_location_and_optimization_api_endpoints():
    """Test location status, nearby search, and optimization audit endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Location status
        loc_res = await client.get("/api/location/status")
        assert loc_res.status_code == 200
        assert loc_res.json()["is_granted"] is True

        # Nearby fitness search
        nearby_res = await client.get("/api/location/nearby?category=fitness&max_distance_miles=5.0")
        assert nearby_res.status_code == 200
        nearby_data = nearby_res.json()
        assert len(nearby_data) >= 2

        # Autonomous optimization audit
        opt_res = await client.get("/api/optimization/audit")
        assert opt_res.status_code == 200
        opt_data = opt_res.json()
        assert float(opt_data["total_potential_annual_savings"]) > 1500.0

        # Compare endpoint
        comp_res = await client.post("/api/optimization/compare", json={
            "current_monthly": 220.0,
            "alternative_monthly": 49.0,
            "alternative_setup_fee": 0.0,
            "current_cancellation_fee": 0.0
        })
        assert comp_res.status_code == 200
        assert comp_res.json()["first_year_net_savings"] == 2052.00


@pytest.mark.asyncio
async def test_automation_rules_endpoint():
    """Test event-driven and scheduled automation rules."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        rules_res = await client.get("/api/automation/rules")
        assert rules_res.status_code == 200
        rules = rules_res.json()
        assert len(rules) >= 3
        rule_ids = [r["rule_id"] for r in rules]
        assert "rule_renewal_monitor" in rule_ids

        # History endpoint
        hist_res = await client.get("/api/automation/history")
        assert hist_res.status_code == 200
        assert len(hist_res.json()) >= 1


@pytest.mark.asyncio
async def test_question_triggering_gemini_escalation():
    """Contextual trade-offs and circumstantial shifts trigger Gemini escalation."""
    question = (
        "I have changed my circumstances. I am now using AI APIs every day for my development work "
        "and consuming approximately 50,000 tokens daily. Should I still downgrade Cognition Engine Pro ($35/month), "
        "considering that its usage was previously zero for 45 days?"
    )
    result = await global_financial_guardian.chat(
        user_prompt=question,
        user_id="usr_alex_chen",
    )
    ai_resp = result["ai_response"]
    assert ai_resp["knowledge_sufficiency"] in ["REQUIRES_EXTERNAL_DATA", "PARTIAL"]
    # Either successfully escalated to live Gemini or gracefully fell back with clear provider flag
    assert ai_resp["provider"] in ["gemini", "deterministic_financial_engine"]
    if ai_resp["provider"] == "gemini":
        assert ai_resp["escalated_to_ai"] is True


def test_zero_ai_offline_execution_when_api_key_empty(monkeypatch):
    """When GEMINI_API_KEY is empty, internal math and optimizations run with 0 errors."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    # Rerun loan amortization
    amort = calculate_loan_amortization(Decimal("5000.00"), Decimal("5.0"), 24)
    assert amort["monthly_payment"] == 219.36

    # Rerun break-even
    be = calculate_break_even(Decimal("2000.00"), Decimal("25.00"), Decimal("10.00"))
    assert be["break_even_units"] == 133

    # Rerun optimization workflow
    proposal = global_expense_optimizer.run_optimization_workflow(user_id="usr_alex_chen")
    assert proposal["total_active_commitments"] == 7
    assert proposal["total_potential_annual_savings"] > 1000.0


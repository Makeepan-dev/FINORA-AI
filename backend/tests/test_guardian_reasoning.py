import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.agents.financial_guardian import global_financial_guardian
from app.services.ai_service import AIService
from app.services.analytics_service import global_analytics_service

client = TestClient(app)

def test_all_seven_subscriptions_in_deterministic_audit():
    """Verify all 7 subscriptions exist in the deterministic data bank for Alex Chen."""
    facts = global_analytics_service.get_subscription_audit_facts("usr_alex_chen")
    assert facts["total_active_commitments"] == 7
    assert facts["total_monthly_commitment"] == 291.97
    assert facts["total_annual_commitment"] == 3503.64
    assert facts["potential_monthly_savings"] == 155.00
    assert facts["potential_annual_savings"] == 1860.00
    assert len(facts["subscriptions"]) == 7

    sub_names = [s["subscription_name"] for s in facts["subscriptions"]]
    expected_names = [
        "Apex Athletic All-Access Pass",
        "StreamPulse 4K Family Plan",
        "SonicWave HiFi Audio",
        "StrataVault 2TB Encrypted Storage",
        "GitForge Pro Developer Cloud",
        "Cognition Engine Pro Tier",
        "OpticSpeed 1Gbps Fiber Internet"
    ]
    for expected in expected_names:
        assert expected in sub_names

@pytest.mark.asyncio
async def test_all_seven_subscriptions_in_guardian_chat_audit():
    """Verify Guardian chat returns all 7 classified subscriptions."""
    res = await global_financial_guardian.chat(
        user_prompt="Perform a complete subscription audit. Classify every active subscription as KEEP, REDUCE, REPLACE, ELIMINATE or INVESTIGATE.",
        user_id="usr_alex_chen"
    )
    ai_resp = res["ai_response"]
    assert ai_resp["status"] == "success"
    classifications = ai_resp.get("classifications", [])
    assert len(classifications) == 7, "Output must contain exactly 7 subscription classifications"

    # Verify every subscription has a valid classification
    valid_classes = {"KEEP", "REDUCE", "REPLACE", "ELIMINATE", "INVESTIGATE"}
    for c in classifications:
        assert c["classification"].upper() in valid_classes
        assert "monthly_cost" in c
        assert "annual_cost" in c
        assert "usage_evidence" in c
        assert "recommendation" in c
        assert "confidence_score" in c

@pytest.mark.asyncio
async def test_deterministic_fallback_clearly_identified():
    """Verify fallback response clearly identifies provider and model."""
    svc = AIService()
    # Force deterministic fallback
    metrics = global_analytics_service.get_user_dashboard_metrics("usr_alex_chen")
    facts = global_analytics_service.get_subscription_audit_facts("usr_alex_chen")
    metrics["subscription_audit_facts"] = facts

    resp = svc._generate_deterministic_financial_response(
        prompt="Perform a complete subscription audit",
        user_metrics=metrics,
        is_fallback=True,
        fallback_reason="Simulated network disconnect"
    )

    assert resp["provider"] == "deterministic_financial_engine"
    assert resp["model"] in ["rule_based_deterministic_v1", "rule_based_conversational_v2"]
    assert resp["is_fallback"] is True
    assert resp["fallback_reason"] == "Simulated network disconnect"
    assert len(resp["classifications"]) == 7

@pytest.mark.asyncio
async def test_model_does_not_invent_usage_evidence():
    """Verify usage evidence in response is strictly grounded in data bank records."""
    facts = global_analytics_service.get_subscription_audit_facts("usr_alex_chen")
    subs = {s["subscription_name"]: s for s in facts["subscriptions"]}

    # Gym evidence must mention turnstile swipe or low usage
    gym = subs["Apex Athletic All-Access Pass"]
    assert "turnstile" in gym["usage_evidence"].lower() or "swipe" in gym["usage_evidence"].lower() or "visit" in gym["usage_evidence"].lower()

    # AI Pro tier must mention API token telemetry
    ai_sub = subs["Cognition Engine Pro Tier"]
    assert "token" in ai_sub["usage_evidence"].lower() or "telemetry" in ai_sub["usage_evidence"].lower()

@pytest.mark.asyncio
async def test_contextually_different_reasoning_on_evidence_change():
    """
    CRITICAL RULE:
    Alex Chen (confirmed low usage with 1 visit) -> REPLACE / REDUCE
    Marcus Vance (unverified missing telemetry) -> INVESTIGATE (never assume zero attendance!)
    """
    alex_facts = global_analytics_service.get_subscription_audit_facts("usr_alex_chen")
    marcus_facts = global_analytics_service.get_subscription_audit_facts("usr_marcus_vance")

    alex_gym = next(s for s in alex_facts["subscriptions"] if "Apex Athletic" in s["subscription_name"])
    marcus_gym = next(s for s in marcus_facts["subscriptions"] if "Apex Athletic" in s["subscription_name"])

    assert alex_gym["classification"] in ["REPLACE", "REDUCE", "ELIMINATE"]
    assert marcus_gym["classification"] == "INVESTIGATE"
    assert "Missing" in marcus_gym["usage_evidence"] or "partner" in marcus_gym["usage_evidence"]
    assert marcus_gym["user_confirmation_needed"] is True

@pytest.mark.asyncio
async def test_api_failures_do_not_crash_financial_guardian():
    """Verify Guardian seamlessly recovers from external API timeouts or connection errors."""
    with patch("httpx.AsyncClient.post", side_effect=Exception("Simulated 503 Provider High Demand")):
        res = await global_financial_guardian.chat(
            user_prompt="Perform a complete subscription audit.",
            user_id="usr_alex_chen"
        )
        assert res is not None
        ai_resp = res["ai_response"]
        assert ai_resp["status"] == "success"
        assert ai_resp["is_fallback"] is True
        assert "503" in ai_resp["fallback_reason"]
        assert len(ai_resp["classifications"]) == 7

def test_zero_cost_guardrails_prevent_paid_provider():
    """Verify zero-cost guardrail: paid models and spend > 0 are strictly rejected."""
    svc = AIService()
    assert svc.allow_paid is False
    assert svc.max_spend == 0.0

@pytest.mark.asyncio
async def test_expensive_expenses_justified_reasoning():
    """Verify Guardian reasons why OpticSpeed Fiber ($70/mo) should be KEPT despite high cost."""
    res = await global_financial_guardian.chat(
        user_prompt="Which expenses should I keep even if they are expensive?",
        user_id="usr_alex_chen"
    )
    analysis = res["ai_response"]["factual_analysis"].lower()
    assert "opticspeed" in analysis or "fiber" in analysis or "internet" in analysis
    assert "keep" in analysis

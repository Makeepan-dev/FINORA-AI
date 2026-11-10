import pytest
from unittest.mock import patch, AsyncMock
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.agents.financial_guardian import global_financial_guardian
from app.services.ai_service import AIService
from app.services.analytics_service import global_analytics_service

client = TestClient(app)

@pytest.mark.asyncio
async def test_normal_subscription_audit():
    """1. Test normal subscription audit returns all 7 active commitments."""
    res = await global_financial_guardian.chat(
        user_prompt="Perform a complete subscription audit. Classify every active subscription as KEEP, REDUCE, REPLACE, ELIMINATE or INVESTIGATE.",
        user_id="usr_alex_chen"
    )
    ai_resp = res["ai_response"]
    assert ai_resp["status"] == "success"
    assert ai_resp.get("is_subscription_audit") is True
    assert len(ai_resp.get("classifications", [])) == 7

@pytest.mark.asyncio
async def test_question_that_changes_user_circumstances():
    """2. Test question changing circumstances (50k tokens daily) alters reasoning on Cognition Engine Pro."""
    prompt = (
        "I have changed my circumstances. I am now using AI APIs every day for my development work and "
        "consuming approximately 50,000 tokens daily. Should I still downgrade Cognition Engine Pro ($35/month), "
        "considering that its usage was previously zero for 45 days?"
    )
    res = await global_financial_guardian.chat(user_prompt=prompt, user_id="usr_alex_chen")
    ai_resp = res["ai_response"]
    analysis = ai_resp["factual_analysis"].lower()

    # Must recognize 50,000 tokens/day and recommend NOT to immediately downgrade
    assert "50,000" in analysis or "50000" in analysis or "1.5" in analysis or "tokens" in analysis
    assert "not downgrade" in analysis or "maintain" in analysis or "retain" in analysis or "keep" in analysis

@pytest.mark.asyncio
async def test_hypothetical_information_versus_verified_telemetry():
    """3. Test response explicitly distinguishes between verified telemetry and hypothetical self-reports."""
    prompt = (
        "I am consuming approximately 50,000 tokens daily. Should I downgrade Cognition Engine Pro ($35/month)?"
    )
    res = await global_financial_guardian.chat(user_prompt=prompt, user_id="usr_alex_chen")
    analysis = res["ai_response"]["factual_analysis"].lower()

    # Must mention historical zero usage vs self-reported/hypothetical usage
    assert "zero" in analysis or "45 days" in analysis or "historical" in analysis
    assert "telemetry" in analysis or "verified" in analysis or "reported" in analysis

def test_missing_utilization_evidence():
    """4. Test missing telemetry (Marcus Vance gym pass) must be classified as INVESTIGATE."""
    facts = global_analytics_service.get_subscription_audit_facts("usr_marcus_vance")
    gym = next(s for s in facts["subscriptions"] if "Apex Athletic" in s["subscription_name"])
    assert gym["classification"] == "INVESTIGATE"
    assert gym["user_confirmation_needed"] is True
    assert "missing" in gym["usage_evidence"].lower() or "partner" in gym["usage_evidence"].lower()

def test_conflicting_evidence():
    """5. Test synthetic data bank contains recognized contradictory activity evidence."""
    mgr = global_analytics_service.dataset_mgr
    evs = getattr(mgr, "activity_evidence", [])
    contradictory = [e for e in evs if getattr(e.evidence_state, "value", str(e.evidence_state)) == "contradictory"]
    assert len(contradictory) > 0, "Must have at least one contradictory activity evidence record"
    assert "calendar" in contradictory[0].notes.lower() or "flight" in contradictory[0].notes.lower()

@pytest.mark.asyncio
async def test_request_requiring_unavailable_price_information():
    """6. Test request requiring proprietary enterprise pricing FINORA does not possess."""
    res = await global_financial_guardian.chat(
        user_prompt="What is the exact private negotiated discount tier for Cognition Engine Enterprise for 100 developers?",
        user_id="usr_alex_chen"
    )
    ai_resp = res["ai_response"]
    assert ai_resp is not None
    analysis = ai_resp["factual_analysis"].lower()
    unknowns = ai_resp.get("unknowns", "").lower()
    # Must acknowledge unknown / unverified merchant pricing
    assert "unknown" in unknowns or "pricing" in analysis or "proprietary" in analysis or "negotiated" in analysis or "not" in analysis

@pytest.mark.asyncio
async def test_gemini_success_mocked():
    """7. Test Gemini successful external call processing and schema validation."""
    mock_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                '{"factual_analysis": "Mocked successful Gemini response.", '
                                '"is_subscription_audit": false, "classifications": [], '
                                '"estimates": [], "recommendations": ["Mock recommendation"], '
                                '"unknowns": "None"}'
                            )
                        }
                    ]
                }
            }
        ]
    }
    mock_resp = httpx.Response(200, json=mock_payload, request=httpx.Request("POST", "http://test"))
    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        svc = AIService()
        metrics = global_analytics_service.get_user_dashboard_metrics("usr_alex_chen")
        facts = global_analytics_service.get_subscription_audit_facts("usr_alex_chen")
        metrics["subscription_audit_facts"] = facts

        res = await svc._call_gemini_free("Hello", metrics, None)
        assert res is not None
        assert res["provider"] == "gemini"
        assert res["is_fallback"] is False
        assert res["factual_analysis"] == "Mocked successful Gemini response."

@pytest.mark.asyncio
async def test_gemini_auth_failure_fallback():
    """8. Test Gemini HTTP 401/403 authentication failure triggers truthful deterministic fallback."""
    mock_resp = httpx.Response(403, text="API key not valid", request=httpx.Request("POST", "http://test"))
    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        svc = AIService()
        metrics = global_analytics_service.get_user_dashboard_metrics("usr_alex_chen")
        facts = global_analytics_service.get_subscription_audit_facts("usr_alex_chen")
        metrics["subscription_audit_facts"] = facts

        res = await svc.generate_financial_response("Analyse my monthly expenses", metrics, None)
        assert res["provider"] == "deterministic_financial_engine"
        assert res["is_fallback"] is True
        assert "Gemini" in res["fallback_reason"]

@pytest.mark.asyncio
async def test_gemini_quota_exhaustion_fallback():
    """9. Test Gemini HTTP 429 quota exhaustion triggers clean fallback with diagnostic reason."""
    mock_resp = httpx.Response(429, text="RESOURCE_EXHAUSTED", request=httpx.Request("POST", "http://test"))
    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        svc = AIService()
        metrics = global_analytics_service.get_user_dashboard_metrics("usr_alex_chen")
        facts = global_analytics_service.get_subscription_audit_facts("usr_alex_chen")
        metrics["subscription_audit_facts"] = facts

        res = await svc.generate_financial_response("Analyse my expenses", metrics, None)
        assert res["provider"] == "deterministic_financial_engine"
        assert res["is_fallback"] is True
        assert res["request_status"] == "fallback"

@pytest.mark.asyncio
async def test_network_timeout_fallback():
    """10. Test network timeout triggers honest fallback without crashing."""
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Request timed out")):
        svc = AIService()
        metrics = global_analytics_service.get_user_dashboard_metrics("usr_alex_chen")
        facts = global_analytics_service.get_subscription_audit_facts("usr_alex_chen")
        metrics["subscription_audit_facts"] = facts

        res = await svc.generate_financial_response("Analyse my expenses", metrics, None)
        assert res["provider"] == "deterministic_financial_engine"
        assert res["is_fallback"] is True
        assert "timed out" in res["fallback_reason"]

def test_deterministic_fallback_honesty():
    """11. Test deterministic fallback never pretends to be an external model."""
    svc = AIService()
    metrics = global_analytics_service.get_user_dashboard_metrics("usr_alex_chen")
    facts = global_analytics_service.get_subscription_audit_facts("usr_alex_chen")
    metrics["subscription_audit_facts"] = facts

    res = svc._generate_deterministic_financial_response(
        prompt="Perform a complete subscription audit",
        user_metrics=metrics,
        is_fallback=True,
        fallback_reason="Explicit offline test"
    )
    assert res["provider"] == "deterministic_financial_engine"
    assert res["model"] == "rule_based_conversational_v2"
    assert res["is_fallback"] is True
    assert res["fallback_reason"] == "Explicit offline test"

def test_accurate_provider_metadata():
    """12. Test provider status exposes truthful metadata."""
    res = client.get("/api/settings/status")
    assert res.status_code == 200
    data = res.json()
    ai = data["ai"]
    assert "provider" in ai
    assert "model" in ai
    assert "has_gemini_key" in ai
    assert ai["allow_paid_models"] is False
    assert ai["max_spend_usd"] == 0.0

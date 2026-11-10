import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.paypal_service import global_paypal_service

client = TestClient(app)

def test_api_status_and_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}

    res_demo = client.get("/api/demo-data/status")
    assert res_demo.status_code == 200
    data = res_demo.json()
    assert data["status"] == "active"
    assert data["counts"]["users"] >= 3
    assert data["counts"]["products"] >= 100

def test_api_validation_report():
    res = client.post("/api/demo-data/validate")
    assert res.status_code == 200
    report = res.json()
    assert report["overall_status"] == "PASS"
    assert report["referential_integrity"]["passed"] is True
    assert report["balance_reconciliation"]["passed"] is True

def test_dashboard_analytics_endpoint():
    res = client.get("/api/analytics/dashboard?user_id=usr_alex_chen")
    assert res.status_code == 200
    dash = res.json()
    assert "summary" in dash
    assert dash["summary"]["monthly_income"] > 0
    assert dash["summary"]["total_balance"] > 0
    assert len(dash["budget_progress"]) > 0
    assert len(dash["recurring_payments"]) > 0

def test_financial_guardian_chat():
    res = client.post(
        "/api/guardian/chat",
        json={"prompt": "Analyse my monthly expenses", "user_id": "usr_alex_chen"}
    )
    assert res.status_code == 200
    reply = res.json()
    assert "ai_response" in reply
    assert reply["ai_response"]["status"] == "success"
    assert "monthly_income" in reply["metrics_snapshot"]

def test_shopping_agent_product_search_and_budget_eval():
    res = client.get("/api/shopping/products?category=electronics")
    assert res.status_code == 200
    products = res.json()
    assert len(products) > 0

    first_product_id = products[0]["product_id"]
    eval_res = client.post(
        "/api/shopping/evaluate-budget",
        json={"product_id": first_product_id, "user_id": "usr_alex_chen"}
    )
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert "total_cost" in eval_data
    assert "is_within_budget" in eval_data

@pytest.mark.asyncio
async def test_paypal_order_lifecycle_and_duplicate_prevention():
    order = await global_paypal_service.create_order(product_id="prd_008_voltkey_wireless")
    assert "id" in order
    order_id = order["id"]

    # First capture
    capture = await global_paypal_service.capture_order(order_id)
    assert capture["status"] == "COMPLETED"

    # Second capture attempt (duplicate prevention)
    dup_capture = await global_paypal_service.capture_order(order_id)
    assert dup_capture["status"] == "ALREADY_CAPTURED"

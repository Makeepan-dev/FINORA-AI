import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_income_intelligence_endpoint():
    res = client.get("/api/income/intelligence?user_id=usr_alex_chen")
    assert res.status_code == 200
    data = res.json()
    assert "income_summary" in data
    assert "received_income" in data["income_summary"]
    assert "expected_income" in data["income_summary"]
    assert "stability_analysis" in data
    assert len(data["source_breakdown"]) > 0
    assert len(data["cash_flow_forecast"]) == 3
    # Check invariant: expected income must not equal received income
    assert data["income_summary"]["expected_income"] > 0
    assert data["income_summary"]["received_income"] > 0

def test_freelance_income_irregularity_detection():
    # Sarah Jenkins has freelance variable income
    res = client.get("/api/income/intelligence?user_id=usr_sarah_jenkins")
    assert res.status_code == 200
    data = res.json()
    assert data["employment_type"] == "Self-Employed Freelance"
    assert len(data["expected_streams"]) > 0

def test_connected_accounts_lifecycle():
    # 1. List supported institutions
    res_inst = client.get("/api/connections/institutions")
    assert res_inst.status_code == 200
    insts = res_inst.json()
    assert len(insts) >= 4

    # 2. List user connections
    res_conns = client.get("/api/connections/?user_id=usr_alex_chen")
    assert res_conns.status_code == 200
    conns = res_conns.json()
    assert len(conns) >= 2

    # 3. Connect new bank account
    res_link = client.post(
        "/api/connections/connect",
        json={"institution_id": "inst_fidelity", "account_type": "investment_cash", "user_id": "usr_alex_chen"}
    )
    assert res_link.status_code == 200
    link_data = res_link.json()
    assert link_data["status"] == "connected"
    conn_id = link_data["connection_id"]

    # 4. Trigger auto-sync
    res_sync = client.post(f"/api/connections/{conn_id}/sync")
    assert res_sync.status_code == 200
    sync_data = res_sync.json()
    assert sync_data["status"] == "success"
    assert sync_data["records_synchronized"] > 0

    # 5. Revoke connection
    res_revoke = client.post(f"/api/connections/{conn_id}/revoke")
    assert res_revoke.status_code == 200
    assert res_revoke.json()["status"] == "revoked"

def test_paypal_connection_test_endpoint():
    res = client.post("/api/payments/test-connection")
    assert res.status_code == 200
    data = res.json()
    assert "configured" in data
    assert "mode" in data

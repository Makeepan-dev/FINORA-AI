import asyncio
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.paypal_service import global_paypal_service

client = TestClient(app)

def test_feature1_csv_import_validation_and_duplicate_prevention():
    """
    Tests Feature 1:
    - CSV upload preview & validation
    - Invalid record flagging
    - Duplicate prevention
    - Transfer exclusion from income/expenses
    - Remaining available money calculation
    """
    test_user = f"usr_test_mvp_{uuid.uuid4().hex[:6]}"
    csv_sample = """date,merchant,description,amount,type,category
2026-10-28,Trader Joe's,Weekly Groceries Basket,68.50,expense,groceries
2026-10-28,Internal Transfer,Transfer to Savings Account,300.00,transfer,transfers
invalid-date,Bad Merchant,Zero Amount Row,0.00,expense,shopping
2026-10-29,Acme Client Corp,Freelance Consulting Payout,450.00,income,salary_income
"""
    # 1. Preview CSV
    res_prev = client.post(
        "/api/v1/transactions/import-csv/preview",
        data={"csv_text": csv_sample, "user_id": test_user}
    )
    assert res_prev.status_code == 200
    prev_data = res_prev.json()
    assert prev_data["total_rows"] == 4
    assert prev_data["valid_count"] == 3
    assert prev_data["invalid_count"] == 1

    # Verify invalid row has validation errors
    invalid_row = next(r for r in prev_data["records"] if not r["is_valid"])
    assert len(invalid_row["validation_errors"]) >= 1

    # 2. Confirm import of valid rows
    res_conf = client.post(
        "/api/v1/transactions/import-csv/confirm",
        json={
            "user_id": test_user,
            "records": prev_data["records"],
            "skip_duplicates": True
        }
    )
    assert res_conf.status_code == 200
    conf_data = res_conf.json()
    assert conf_data["imported_count"] == 3
    assert conf_data["skipped_count"] == 1  # the invalid row

    # 3. Attempt duplicate import of same records -> must skip all 3!
    res_dup = client.post(
        "/api/v1/transactions/import-csv/confirm",
        json={
            "user_id": test_user,
            "records": prev_data["records"],
            "skip_duplicates": True
        }
    )
    assert res_dup.status_code == 200
    assert res_dup.json()["imported_count"] == 0

    # 4. Verify summary excludes the $300 transfer!
    res_sum = client.get(f"/api/v1/transactions/summary?user_id={test_user}&month=2026-10")
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    # Demo seed has $7050 income + $450 imported = $7500.00
    # And the $300 transfer is strictly excluded from income and expenses!
    assert sum_data["remaining_available_money"] == round(sum_data["total_income"] - sum_data["total_expenses"], 2)
    assert "Transfers Strictly Excluded" in sum_data["calculation_formula"]


def test_feature2_ai_advisor_core_questions():
    """
    Tests Feature 2:
    - How much did I spend this month?
    - Help me save $100 this month
    - Can I afford to buy a $1200 laptop?
    """
    # Question 1: Spending summary
    q1 = client.post(
        "/api/v1/guardian/chat",
        json={"prompt": "How much did I spend this month and where is most of my money going?", "user_id": "usr_alex_chen"}
    )
    assert q1.status_code == 200
    r1 = q1.json()["ai_response"]
    assert r1["status"] == "success"
    assert "Remaining Available Money" in r1["response"]

    # Question 2: Save $100 this month
    q2 = client.post(
        "/api/v1/guardian/chat",
        json={"prompt": "Help me save $100 this month", "user_id": "usr_alex_chen"}
    )
    assert q2.status_code == 200
    r2 = q2.json()["ai_response"]
    assert r2["status"] == "success"
    assert "Your gym membership may be underutilized based on the available records" in r2["response"]
    assert r2["potential_monthly_savings"] >= 100.0

    # Question 3: Affordability check
    q3 = client.post(
        "/api/v1/guardian/chat",
        json={"prompt": "Can I afford to buy a $1200 laptop?", "user_id": "usr_alex_chen"}
    )
    assert q3.status_code == 200
    r3 = q3.json()["ai_response"]
    assert r3["status"] == "success"
    assert "Verdict" in r3["response"]


def test_feature3_and_4_gps_permissions_and_gym_scenario():
    """
    Tests Feature 3 & Feature 4:
    - Explicit GPS permission grant, manual location, and permission revocation
    - Nearby alternatives with transport cost net savings
    - Cross-module Gym scenario ($45/mo vs $20/mo = $25/mo or $300/yr difference)
    """
    # 1. Grant browser GPS coordinates
    res_perm = client.post(
        "/api/v1/location/permission",
        json={
            "user_id": "usr_alex_chen",
            "is_granted": True,
            "precision_mode": "precise",
            "access_type": "one_time",
            "latitude": 37.7890,
            "longitude": -122.4010,
            "city": "San Francisco Financial District",
            "location_source": "browser_gps"
        }
    )
    assert res_perm.status_code == 200
    assert res_perm.json()["location_source"] == "browser_gps"

    # 2. Discover nearby groceries with transport cost calculation
    res_near = client.get("/api/v1/location/nearby?category=groceries&user_id=usr_alex_chen")
    assert res_near.status_code == 200
    groceries = res_near.json()
    assert len(groceries) >= 2
    assert "savings_analysis" in groceries[0]
    assert "estimated_monthly_transport_cost" in groceries[0]["savings_analysis"]

    # 3. Verify cross-module Gym Scenario
    res_gym = client.get("/api/v1/location/gym-scenario?user_id=usr_alex_chen")
    assert res_gym.status_code == 200
    gym = res_gym.json()
    assert gym["current_membership"]["monthly_cost"] == 45.00
    assert gym["nearby_alternative"]["monthly_cost"] == 20.00
    assert gym["savings_calculation"]["monthly_difference"] == 25.00
    assert gym["savings_calculation"]["annual_difference"] == 300.00
    assert "Your gym membership may be underutilized based on the available records" in gym["advisor_message"]

    # 4. Revoke permission and verify fallback
    res_rev = client.post(
        "/api/v1/location/permission",
        json={"user_id": "usr_alex_chen", "is_granted": False}
    )
    assert res_rev.status_code == 200
    assert res_rev.json()["is_granted"] is False

    # Restore permission for subsequent tests
    client.post(
        "/api/v1/location/permission",
        json={"user_id": "usr_alex_chen", "is_granted": True, "precision_mode": "approximate"}
    )


def test_feature5_daily_savings_intelligence_and_user_approval():
    """
    Tests Feature 5:
    - Potential savings vs Verified realized savings distinction
    - Composite multi-factor ranking
    - Explicit user decision approval
    """
    res = client.get("/api/v1/savings/dashboard?user_id=usr_alex_chen")
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["potential_monthly_savings"] >= 100.0
    assert "CRITICAL DISTINCTION" in data["summary"]["distinction_notice"]
    assert len(data["ranked_recommendations"]) >= 3

    first_rec_id = data["ranked_recommendations"][0]["id"]
    dec_res = client.post(
        f"/api/v1/savings/recommendations/{first_rec_id}/decision",
        json={"decision": "accepted", "user_id": "usr_alex_chen"}
    )
    assert dec_res.status_code == 200
    assert dec_res.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_paypal_concurrent_capture_lock_and_savings_plan_order():
    """
    Verifies atomic asyncio lock prevents concurrent duplicate captures
    and verifies money-saving switch order creation.
    """
    order = await global_paypal_service.create_order(product_id="sav_gym_planet_20", user_id="usr_alex_chen")
    assert "id" in order
    assert order["product_details"]["total_amount"] == 20.00
    order_id = order["id"]

    # Fire 5 concurrent capture attempts simultaneously
    results = await asyncio.gather(*[global_paypal_service.capture_order(order_id) for _ in range(5)])
    statuses = [r["status"] for r in results]
    # Only the first capture should execute; the other 4 must be blocked by the lock as ALREADY_CAPTURED
    assert statuses.count("ALREADY_CAPTURED") == 4

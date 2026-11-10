import io
import uuid
import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_session_token, CONTROLLED_SESSION_USER_ID
from app.services.paypal_service import global_paypal_service
from app.services.transaction_service import MAX_CSV_SIZE_BYTES, MAX_CSV_ROWS
from app.database.session import SessionLocal
from app.models.db_models import TransactionRecord

client = TestClient(app)


# =====================================================================
# P0.1 — FINANCIAL DATA INTEGRITY: DEMO VS PERSONAL DATA SEPARATION
# =====================================================================
def test_p0_demo_vs_personal_data_separation():
    """
    Verifies that:
    - Demo Mode and Personal Mode operate independently.
    - Importing CSV or adding manual transactions switches 'auto' scope to 'personal'
      and NEVER mixes demo seed amounts ($7,050 income / $1,200.51 expenses) with personal records.
    - Explicit data_scope='demo' still preserves full demo functionality.
    """
    test_user = f"usr_test_sep_{uuid.uuid4().hex[:6]}"
    token = create_session_token(test_user)
    headers = {"X-Finora-Session-Token": token}

    # 1. Before any personal import, 'auto' resolves to 'demo' mode
    res_demo_init = client.get(f"/api/v1/transactions/summary?user_id={test_user}", headers=headers)
    assert res_demo_init.status_code == 200
    demo_sum = res_demo_init.json()
    assert demo_sum["active_data_scope"] == "demo"
    assert demo_sum["total_income"] == 7050.00
    assert demo_sum["total_expenses"] == 1200.51
    assert demo_sum["remaining_available_money"] == 5849.49

    # 2. Import personal CSV ($1,000.00 income, $200.00 food_dining expense, $150.00 transfer)
    csv_personal = """date,merchant,description,amount,type,category
2026-10-25,Acme Consulting,Personal Freelance Income,1000.00,income,salary_income
2026-10-26,DoorDash,Personal Dinner Order,200.00,expense,food_dining
2026-10-27,Internal Transfer,Move to Personal Savings,150.00,transfer,transfers
"""
    prev = client.post(
        "/api/v1/transactions/import-csv/preview",
        data={"csv_text": csv_personal, "user_id": test_user},
        headers=headers
    )
    assert prev.status_code == 200
    prev_json = prev.json()
    assert prev_json["valid_count"] == 3

    conf = client.post(
        "/api/v1/transactions/import-csv/confirm",
        json={"user_id": test_user, "records": prev_json["records"], "skip_duplicates": True},
        headers=headers
    )
    assert conf.status_code == 200
    assert conf.json()["imported_count"] == 3
    assert conf.json()["active_data_scope"] == "personal"

    # 3. Verify 'auto' summary now reflects ONLY personal records (Zero demo contamination!)
    res_pers_sum = client.get(f"/api/v1/transactions/summary?user_id={test_user}", headers=headers)
    assert res_pers_sum.status_code == 200
    pers_sum = res_pers_sum.json()
    assert pers_sum["active_data_scope"] == "personal"
    assert pers_sum["total_income"] == 1000.00  # NOT 7050 + 1000!
    assert pers_sum["total_expenses"] == 200.00  # NOT 1200.51 + 200!
    assert pers_sum["remaining_available_money"] == 800.00
    assert pers_sum["transaction_count"] == 3

    # 4. Verify Analytics Dashboard also isolates personal records without demo contamination
    res_analytics = client.get(f"/api/v1/analytics/dashboard?user_id={test_user}", headers=headers)
    assert res_analytics.status_code == 200
    ana = res_analytics.json()
    assert ana["active_data_scope"] == "personal"
    assert ana["summary"]["monthly_income"] == 1000.00
    assert ana["summary"]["monthly_expenses"] == 200.00
    assert all(not tx["is_demo"] for tx in ana["recent_transactions"])

    # 5. Verify explicit data_scope='demo' still works independently without deleting personal records
    res_explicit_demo = client.get(
        f"/api/v1/transactions/summary?user_id={test_user}&data_scope=demo",
        headers=headers
    )
    assert res_explicit_demo.status_code == 200
    assert res_explicit_demo.json()["active_data_scope"] == "demo"
    assert res_explicit_demo.json()["total_income"] == 7050.00


# =====================================================================
# P0.2 — USER DATA OWNERSHIP AND AUTHORIZATION
# =====================================================================
def test_p0_unauthorized_user_id_and_cross_user_access_blocked():
    """
    Verifies that:
    - Arbitrary client-supplied user_id values in query params or JSON body are rejected with 403.
    - Cross-user attempts to read or delete another user's transactions or modify their
      recommendations are rejected with 403 Forbidden.
    """
    # 1. Arbitrary foreign user_id without valid session token must be rejected (403)
    for ep in [
        "/api/v1/transactions?user_id=usr_unauthorized_victim",
        "/api/v1/transactions/summary?user_id=usr_unauthorized_victim",
        "/api/v1/savings/dashboard?user_id=usr_unauthorized_victim",
        "/api/v1/analytics/dashboard?user_id=usr_unauthorized_victim",
        "/api/v1/location/status?user_id=usr_unauthorized_victim"
    ]:
        res = client.get(ep)
        assert res.status_code == 403, f"Expected 403 on {ep}, got {res.status_code}"

    res_chat = client.post(
        "/api/v1/guardian/chat",
        json={"prompt": "How much did I spend?", "user_id": "usr_unauthorized_victim"}
    )
    assert res_chat.status_code == 403

    # 2. Create a transaction as User A, then attempt to delete it as User B
    user_a = f"usr_test_owner_a_{uuid.uuid4().hex[:6]}"
    user_b = f"usr_test_owner_b_{uuid.uuid4().hex[:6]}"
    token_a = create_session_token(user_a)
    token_b = create_session_token(user_b)

    add_res = client.post(
        f"/api/v1/transactions?user_id={user_a}",
        json={"merchant": "Private Clinic", "amount": 125.00, "transaction_type": "expense"},
        headers={"X-Finora-Session-Token": token_a}
    )
    assert add_res.status_code == 200
    tx_id_a = add_res.json()["transaction"]["id"]

    # User B tries to delete User A's transaction -> 403 Forbidden
    del_by_b = client.delete(
        f"/api/v1/transactions/{tx_id_a}?user_id={user_b}",
        headers={"X-Finora-Session-Token": token_b}
    )
    assert del_by_b.status_code == 403

    # User B tries to pass User A's user_id with User B's token -> 403 Forbidden
    spoof_res = client.get(
        f"/api/v1/transactions?user_id={user_a}",
        headers={"X-Finora-Session-Token": token_b}
    )
    assert spoof_res.status_code == 403

    # User B tries to modify User A's savings recommendation -> 403 Forbidden
    dash_a = client.get(
        f"/api/v1/savings/dashboard?user_id={user_a}&data_scope=demo",
        headers={"X-Finora-Session-Token": token_a}
    ).json()
    rec_id_a = dash_a["ranked_recommendations"][0]["id"]

    mod_by_b = client.post(
        f"/api/v1/savings/recommendations/{rec_id_a}/decision",
        json={"decision": "accepted", "user_id": user_b},
        headers={"X-Finora-Session-Token": token_b}
    )
    assert mod_by_b.status_code == 403


# =====================================================================
# P0.3 — PAYPAL ORDER AND REFUND OWNERSHIP & IDEMPOTENCY
# =====================================================================
@pytest.mark.asyncio
async def test_p0_paypal_order_and_refund_ownership():
    """
    Verifies:
    - Order is bound to originating user.
    - Cross-user order status lookup, capture, and refund are rejected.
    - Duplicate captures and duplicate refunds are blocked.
    - Refund amounts exceeding captured amount are rejected.
    """
    user_a = f"usr_test_pp_a_{uuid.uuid4().hex[:6]}"
    user_b = f"usr_test_pp_b_{uuid.uuid4().hex[:6]}"
    token_a = create_session_token(user_a)
    token_b = create_session_token(user_b)

    # 1. User A creates a simulated order for test speed/isolation
    sim_order_id = f"SANDBOX-ORD-OWN-{uuid.uuid4().hex[:8].upper()}"
    global_paypal_service._persist_order_to_db(sim_order_id, user_a, "sav_gym_planet_20", 20.00, True, [])
    global_paypal_service._in_memory_orders[sim_order_id] = {
        "id": sim_order_id,
        "user_id": user_a,
        "status": "CREATED",
        "product_details": {"product_id": "sav_gym_planet_20", "total_amount": 20.00}
    }

    # 2. User B attempts to view User A's order -> 403
    view_b = client.get(
        f"/api/v1/payments/orders/{sim_order_id}?user_id={user_b}",
        headers={"X-Finora-Session-Token": token_b}
    )
    assert view_b.status_code == 403

    # 3. User B attempts to capture User A's order -> rejected (400/403)
    cap_b = client.post(
        "/api/v1/payments/capture-order",
        json={"order_id": sim_order_id, "user_id": user_b},
        headers={"X-Finora-Session-Token": token_b}
    )
    assert cap_b.status_code in [400, 403]

    # 4. User A captures their own order -> 200 COMPLETED
    cap_a = client.post(
        "/api/v1/payments/capture-order",
        json={"order_id": sim_order_id, "user_id": user_a},
        headers={"X-Finora-Session-Token": token_a}
    )
    assert cap_a.status_code == 200
    cap_data = cap_a.json()
    assert cap_data["status"] == "COMPLETED"
    capture_id = cap_data["capture_id"]

    # 5. User B attempts to refund User A's capture -> 403 Forbidden
    ref_b = client.post(
        "/api/v1/payments/refund",
        json={"capture_id": capture_id, "amount": 10.00, "user_id": user_b},
        headers={"X-Finora-Session-Token": token_b}
    )
    assert ref_b.status_code == 403

    # 6. User A attempts to refund MORE than the $20.00 captured amount ($50.00) -> 400 Bad Request
    ref_excess = client.post(
        "/api/v1/payments/refund",
        json={"capture_id": capture_id, "amount": 50.00, "user_id": user_a},
        headers={"X-Finora-Session-Token": token_a}
    )
    assert ref_excess.status_code == 400

    # 7. User A executes valid $20.00 refund -> 200 REFUNDED
    ref_valid = client.post(
        "/api/v1/payments/refund",
        json={"capture_id": capture_id, "amount": 20.00, "user_id": user_a},
        headers={"X-Finora-Session-Token": token_a}
    )
    assert ref_valid.status_code == 200
    assert ref_valid.json()["status"] == "REFUNDED"

    # 8. User A attempts duplicate refund on already refunded capture -> 400 Bad Request
    ref_dup = client.post(
        "/api/v1/payments/refund",
        json={"capture_id": capture_id, "amount": 20.00, "user_id": user_a},
        headers={"X-Finora-Session-Token": token_a}
    )
    assert ref_dup.status_code == 400


# =====================================================================
# P1.1 — UNIFIED SAVINGS CALCULATION ACROSS ALL THREE ENDPOINTS
# =====================================================================
def test_p1_unified_savings_calculation_across_all_three_endpoints():
    """
    Verifies that:
    - /api/v1/savings/dashboard
    - /api/v1/transactions/summary
    - /api/v1/guardian/chat ("Help me save $100 this month")
    all return the exact same potential_monthly_savings and potential_annual_savings
    in both Demo Mode ($115.77/mo, $1,389.24/yr) and Personal Mode, and that
    annual == monthly * 12 across all records.
    Also verifies consistent gym transport cost ($4.29/mo -> $20.71/mo net) across services.
    """
    # Part A: Demo Mode Consistency ($115.77/mo, $1,389.24/yr)
    demo_user = f"usr_test_unif_demo_{uuid.uuid4().hex[:6]}"
    token_demo = create_session_token(demo_user)
    headers_demo = {"X-Finora-Session-Token": token_demo}

    s_sum = client.get(f"/api/v1/transactions/summary?user_id={demo_user}&data_scope=demo", headers=headers_demo).json()
    s_dash = client.get(f"/api/v1/savings/dashboard?user_id={demo_user}&data_scope=demo", headers=headers_demo).json()
    s_chat = client.post(
        "/api/v1/guardian/chat",
        json={"prompt": "Help me save $100 this month", "user_id": demo_user, "data_scope": "demo"},
        headers=headers_demo
    ).json()

    assert s_sum["potential_monthly_savings"] == 115.77
    assert s_sum["potential_annual_savings"] == 1389.24

    assert s_dash["summary"]["potential_monthly_savings"] == 115.77
    assert s_dash["summary"]["potential_annual_savings"] == 1389.24

    assert s_chat["ai_response"]["potential_monthly_savings"] == 115.77
    assert s_chat["ai_response"]["potential_annual_savings"] == 1389.24
    assert s_chat["metrics_snapshot"]["potential_monthly_savings"] == 115.77
    assert "$115.77/month ($1,389.24/year)" in s_chat["ai_response"]["response"]

    # Check annual == monthly * 12 for every recommendation
    for rec in s_dash["ranked_recommendations"]:
        assert round(rec["estimated_monthly_savings"] * 12.0, 2) == rec["estimated_annual_savings"]

    # Part B: Personal Mode Consistency Across All Three Endpoints
    pers_user = f"usr_test_unif_pers_{uuid.uuid4().hex[:6]}"
    token_pers = create_session_token(pers_user)
    headers_pers = {"X-Finora-Session-Token": token_pers}

    # Add personal income ($3,000), personal gym ($55 -> $35/mo savings vs $20 Planet Fitness), and food ($250 -> 20% = $50/mo savings)
    # Total expected personal savings = $35.00 + $50.00 = $85.00/mo ($1,020.00/yr)
    csv_pers = """date,merchant,description,amount,type,category
2026-10-01,Employer Inc,Monthly Salary,3000.00,income,salary_income
2026-10-05,Equinox Fitness,Monthly Gym Membership,55.00,expense,fitness_wellness
2026-10-10,DoorDash,Food Delivery Orders,250.00,expense,food_dining
"""
    prev = client.post(
        "/api/v1/transactions/import-csv/preview",
        data={"csv_text": csv_pers, "user_id": pers_user},
        headers=headers_pers
    ).json()
    client.post(
        "/api/v1/transactions/import-csv/confirm",
        json={"user_id": pers_user, "records": prev["records"]},
        headers=headers_pers
    )

    p_sum = client.get(f"/api/v1/transactions/summary?user_id={pers_user}", headers=headers_pers).json()
    p_dash = client.get(f"/api/v1/savings/dashboard?user_id={pers_user}", headers=headers_pers).json()
    p_chat = client.post(
        "/api/v1/guardian/chat",
        json={"prompt": "Help me save $100 this month", "user_id": pers_user},
        headers=headers_pers
    ).json()

    assert p_sum["active_data_scope"] == "personal"
    assert p_sum["potential_monthly_savings"] == 85.00
    assert p_sum["potential_annual_savings"] == 1020.00

    assert p_dash["summary"]["potential_monthly_savings"] == 85.00
    assert p_dash["summary"]["potential_annual_savings"] == 1020.00

    assert p_chat["ai_response"]["potential_monthly_savings"] == 85.00
    assert p_chat["ai_response"]["potential_annual_savings"] == 1020.00

    # Part C: Consistent Gym Transport Cost ($4.29/mo transport, $20.71/mo net savings)
    gym_scen = client.get("/api/v1/location/gym-scenario").json()
    near_fit = client.get("/api/v1/location/nearby?category=fitness").json()
    planet = next(c for c in near_fit if c["candidate_id"] == "cand_gym_planet")

    assert gym_scen["savings_calculation"]["estimated_transport_cost_monthly"] == 4.29
    assert gym_scen["savings_calculation"]["net_monthly_savings_after_transport"] == 20.71
    assert planet["savings_analysis"]["estimated_monthly_transport_cost"] == 4.29
    assert planet["savings_analysis"]["net_monthly_savings"] == 20.71


# =====================================================================
# P1.2 — GPS PERMISSION PRIVACY (REVOKED / DENIED BEHAVIOR)
# =====================================================================
def test_p1_gps_revocation_never_falls_back_to_san_francisco():
    """
    Verifies that:
    - Revoking or denying GPS permission clears coordinates to None.
    - /api/v1/location/nearby returns [] (empty) when permission is revoked, never
      silently using San Francisco default coordinates.
    - /api/v1/location/live-osm rejects with 403 when permission is revoked.
    - Manual location entry works and restores discovery.
    """
    gps_user = f"usr_test_gps_{uuid.uuid4().hex[:6]}"
    token = create_session_token(gps_user)
    headers = {"X-Finora-Session-Token": token}

    # 1. Revoke/deny GPS permission
    rev = client.post(
        "/api/v1/location/permission",
        json={"user_id": gps_user, "is_granted": False},
        headers=headers
    )
    assert rev.status_code == 200
    rev_data = rev.json()
    assert rev_data["is_granted"] is False
    assert rev_data["location_source"] == "revoked"
    assert rev_data["latitude"] is None
    assert rev_data["longitude"] is None

    # 2. Verify /api/v1/location/nearby returns empty list [] (no silent SF fallback!)
    near_revoked = client.get(f"/api/v1/location/nearby?category=fitness&user_id={gps_user}", headers=headers)
    assert near_revoked.status_code == 200
    assert near_revoked.json() == []

    # 3. Verify /api/v1/location/live-osm is blocked (403) when permission is revoked
    osm_revoked = client.get(
        f"/api/v1/location/live-osm?latitude=37.7749&longitude=-122.4194&user_id={gps_user}",
        headers=headers
    )
    assert osm_revoked.status_code == 403

    # 4. Verify explicit Demo Benchmark mode opt-in works if requested
    near_bench = client.get(
        f"/api/v1/location/nearby?category=fitness&user_id={gps_user}&allow_demo_benchmark=true",
        headers=headers
    )
    assert near_bench.status_code == 200
    assert len(near_bench.json()) >= 1
    assert near_bench.json()[0]["location_source"] == "demo_benchmark_explicit"

    # 5. Verify manual location entry restores discovery with manual_selection source
    man = client.post(
        "/api/v1/location/permission",
        json={
            "user_id": gps_user,
            "is_granted": True,
            "precision_mode": "approximate",
            "access_type": "one_time",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "city": "Manual SF Entry",
            "location_source": "manual_selection"
        },
        headers=headers
    )
    assert man.status_code == 200
    assert man.json()["location_source"] == "manual_selection"

    near_manual = client.get(f"/api/v1/location/nearby?category=fitness&user_id={gps_user}", headers=headers)
    assert near_manual.status_code == 200
    assert len(near_manual.json()) >= 1
    assert near_manual.json()[0]["location_source"] == "manual_selection"


# =====================================================================
# P1.3 — CSV UPLOAD PROTECTION (2 MB & 5,000 ROWS LIMITS)
# =====================================================================
def test_p1_csv_upload_limits_and_malformed_protection():
    """
    Verifies:
    - CSV upload below 2 MB and <= 5,000 rows succeeds.
    - CSV upload > 2 MB is rejected with 413.
    - CSV upload > 5,000 rows is rejected with 400.
    - Invalid file extension (.exe / .png) and binary null bytes are rejected with 400.
    """
    csv_user = f"usr_test_csv_lim_{uuid.uuid4().hex[:6]}"
    token = create_session_token(csv_user)
    headers = {"X-Finora-Session-Token": token}

    # 1. Valid CSV below both limits succeeds
    valid_csv = "date,merchant,description,amount,type,category\n2026-10-01,Safeway,Groceries,45.00,expense,groceries\n"
    res_ok = client.post(
        "/api/v1/transactions/import-csv/preview",
        files={"file": ("statement.csv", valid_csv.encode("utf-8"), "text/csv")},
        data={"user_id": csv_user},
        headers=headers
    )
    assert res_ok.status_code == 200
    assert res_ok.json()["valid_count"] == 1

    # 2. CSV exceeding 2 MB limit (2,097,152 bytes) is rejected with 413
    oversized_bytes = b"date,merchant,description,amount\n" + (b"2026-10-01,Store,Item,10.00\n" * 80000)
    assert len(oversized_bytes) > MAX_CSV_SIZE_BYTES
    res_too_big = client.post(
        "/api/v1/transactions/import-csv/preview",
        files={"file": ("huge.csv", oversized_bytes, "text/csv")},
        data={"user_id": csv_user},
        headers=headers
    )
    assert res_too_big.status_code == 413

    # 3. CSV exceeding 5,000 rows (5,005 rows, under 2 MB) is rejected with 400
    row_line = "2026-10-01,S,D,1.00\n"
    too_many_rows_csv = "date,merchant,description,amount\n" + (row_line * (MAX_CSV_ROWS + 5))
    assert len(too_many_rows_csv.encode("utf-8")) < MAX_CSV_SIZE_BYTES
    res_too_many_rows = client.post(
        "/api/v1/transactions/import-csv/preview",
        files={"file": ("many_rows.csv", too_many_rows_csv.encode("utf-8"), "text/csv")},
        data={"user_id": csv_user},
        headers=headers
    )
    assert res_too_many_rows.status_code == 400
    assert "5,000 rows" in res_too_many_rows.json()["detail"]

    # 4. Disallowed file extension (.exe) is rejected with 400
    res_bad_ext = client.post(
        "/api/v1/transactions/import-csv/preview",
        files={"file": ("malware.exe", b"date,merchant,amount\n", "application/octet-stream")},
        data={"user_id": csv_user},
        headers=headers
    )
    assert res_bad_ext.status_code == 400

    # 5. Binary null bytes in file are rejected safely with 400
    res_null = client.post(
        "/api/v1/transactions/import-csv/preview",
        files={"file": ("binary.csv", b"date,merchant\x00,amount\n2026-10-01,Test,10.00", "text/csv")},
        data={"user_id": csv_user},
        headers=headers
    )
    assert res_null.status_code == 400


# =====================================================================
# DATABASE INTEGRITY CHECK
# =====================================================================
def test_existing_database_records_intact():
    """Verifies that existing records for usr_alex_chen in finora.db remain intact."""
    with SessionLocal() as db:
        count = db.query(TransactionRecord).filter(
            TransactionRecord.user_id == CONTROLLED_SESSION_USER_ID
        ).count()
        assert count >= 25


# =====================================================================
# SURGICAL PRE-SUBMISSION REGRESSION TESTS
# =====================================================================
def test_surgical_fix1_persona_switcher_locked_to_alex_chen():
    """
    Verifies that unsupported personas (Sarah Jenkins, Marcus Vance) are removed
    from Navbar.tsx and Settings.tsx, and App.tsx locks activeUserId to usr_alex_chen.
    """
    from pathlib import Path
    root_dir = Path(__file__).resolve().parent.parent.parent
    navbar_text = (root_dir / "frontend" / "src" / "components" / "Navbar.tsx").read_text(encoding="utf-8")
    settings_text = (root_dir / "frontend" / "src" / "pages" / "Settings.tsx").read_text(encoding="utf-8")
    app_text = (root_dir / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")

    assert "usr_sarah_jenkins" not in navbar_text
    assert "usr_marcus_vance" not in navbar_text
    assert "usr_sarah_jenkins" not in settings_text
    assert "usr_marcus_vance" not in settings_text
    assert "usr_alex_chen" in navbar_text
    assert "usr_alex_chen" in settings_text
    assert "if (userId !== 'usr_alex_chen')" in app_text


def test_surgical_fix2_demo_mode_dashboard_transactions_savings_guardian_agreement():
    """
    Verifies that Demo Mode dashboard (/api/analytics/dashboard), Sidebar,
    Transactions (/api/v1/transactions/summary), Savings (/api/v1/savings/dashboard),
    and AI Advisor (/api/v1/guardian/chat) all return identical, SQLite-backed figures.
    """
    res_dash = client.get("/api/analytics/dashboard?user_id=usr_alex_chen&data_scope=demo")
    res_tx = client.get("/api/v1/transactions/summary?user_id=usr_alex_chen&data_scope=demo")
    res_sav = client.get("/api/v1/savings/dashboard?user_id=usr_alex_chen&data_scope=demo")
    res_guard_plan = client.post(
        "/api/v1/guardian/chat",
        json={"prompt": "Help me save $100 this month", "user_id": "usr_alex_chen", "data_scope": "demo"}
    )
    res_guard_sum = client.post(
        "/api/v1/guardian/chat",
        json={"prompt": "How much did I spend this month and where is most of my money going?", "user_id": "usr_alex_chen", "data_scope": "demo"}
    )

    assert res_dash.status_code == 200
    assert res_tx.status_code == 200
    assert res_sav.status_code == 200
    assert res_guard_plan.status_code == 200
    assert res_guard_sum.status_code == 200

    dash = res_dash.json()
    tx = res_tx.json()
    sav = res_sav.json()
    g_plan = res_guard_plan.json()
    g_sum = res_guard_sum.json()

    # Income, expenses, remaining available money, subscription totals, and savings must agree 100%
    assert dash["summary"]["monthly_income"] == tx["total_income"] == sav["financial_context"]["monthly_income"] == g_plan["metrics_snapshot"]["monthly_income"] == 7050.00
    assert dash["summary"]["monthly_expenses"] == tx["total_expenses"] == sav["financial_context"]["monthly_expenses"] == g_plan["metrics_snapshot"]["monthly_expenses"] == 1200.51
    assert dash["summary"]["remaining_available_money"] == tx["remaining_available_money"] == sav["financial_context"]["remaining_available_money"] == g_plan["metrics_snapshot"]["net_cash_flow"] == 5849.49
    assert dash["summary"]["total_subscription_cost"] == tx["recurring_monthly_expenses"] == g_plan["metrics_snapshot"]["total_subscription_cost"] == 126.47
    assert dash["summary"]["potential_monthly_savings"] == tx["potential_monthly_savings"] == sav["summary"]["potential_monthly_savings"] == g_plan["ai_response"]["potential_monthly_savings"] == 115.77
    assert dash["summary"]["potential_annual_savings"] == tx["potential_annual_savings"] == sav["summary"]["potential_annual_savings"] == g_plan["ai_response"]["potential_annual_savings"] == 1389.24
    assert "$7,050.00" in g_sum["ai_response"]["response"]
    assert "$1,200.51" in g_sum["ai_response"]["response"]
    assert "$115.77" in g_sum["ai_response"]["recommendations"][1]


def test_surgical_fix3_secondary_endpoints_authorization_and_ownership():
    """
    Verifies that shopping, optimization, automation, connections, and demo_data
    endpoints enforce resolve_authorized_user and resource ownership.
    """
    # 1. Unauthorized user_id rejected across all secondary routers
    assert client.post("/api/shopping/evaluate-budget", json={"product_id": "prd_008_voltkey_wireless", "user_id": "usr_sarah_jenkins"}).status_code == 403
    assert client.post("/api/shopping/compare", json={"product_ids": ["prd_008_voltkey_wireless"], "user_id": "usr_marcus_vance"}).status_code == 403
    assert client.get("/api/optimization/opportunities?user_id=usr_sarah_jenkins").status_code == 403
    assert client.get("/api/optimization/audit?user_id=usr_marcus_vance").status_code == 403
    assert client.post("/api/optimization/compare", json={"current_monthly": 100.0, "alternative_monthly": 50.0, "user_id": "usr_attacker"}).status_code == 403
    assert client.get("/api/automation/rules?user_id=usr_attacker").status_code == 403
    assert client.get("/api/automation/pending-actions?user_id=usr_attacker").status_code == 403
    assert client.post("/api/automation/actions/act_gym_downgrade_001/approve", json={"user_id": "usr_attacker"}).status_code == 403
    assert client.post("/api/automation/actions/act_gym_downgrade_001/reject", json={"reason": "No", "user_id": "usr_attacker"}).status_code == 403
    assert client.post("/api/connections/conn_alex_paypal/sync?user_id=usr_attacker").status_code == 403
    assert client.post("/api/connections/conn_alex_paypal/revoke?user_id=usr_attacker").status_code == 403
    assert client.get("/api/demo-data/accounts?owner_id=usr_sarah_jenkins").status_code == 403
    assert client.get("/api/demo-data/transactions?user_id=usr_sarah_jenkins").status_code == 403
    assert client.get("/api/demo-data/subscriptions?user_id=usr_marcus_vance").status_code == 403
    assert client.post("/api/demo-data/reset?user_id=usr_attacker").status_code == 403

    # 2. Cross-user resource ownership check even with a valid session token for another user
    other_user = f"usr_other_{uuid.uuid4().hex[:6]}"
    other_headers = {"X-Finora-Session-Token": create_session_token(other_user)}

    # Other user cannot sync or revoke usr_alex_chen's connection
    assert client.post(f"/api/connections/conn_alex_paypal/sync?user_id={other_user}", headers=other_headers).status_code == 403
    assert client.post(f"/api/connections/conn_alex_paypal/revoke?user_id={other_user}", headers=other_headers).status_code == 403

    # Other user cannot approve or reject usr_alex_chen's prepared automation action
    from app.automation.safety import global_safety_manager, ActionSafetyLevel
    alex_act = global_safety_manager.create_action(
        safety_level=ActionSafetyLevel.LEVEL_3_USER_APPROVED,
        title="Alex Protected Action",
        description="Test ownership",
        action_type="subscription_cancellation_dispatch",
        target_merchant_or_payee="Merchant",
        amount=25.0
    )
    assert client.post(
        f"/api/automation/actions/{alex_act.action_id}/approve",
        json={"user_id": other_user},
        headers=other_headers
    ).status_code == 403
    assert client.post(
        f"/api/automation/actions/{alex_act.action_id}/reject",
        json={"reason": "Hijack attempt", "user_id": other_user},
        headers=other_headers
    ).status_code == 403


@pytest.mark.asyncio
async def test_surgical_fix4_paypal_webhook_hardening_and_mode_separation(monkeypatch):
    """
    Verifies that:
    1. Unsigned webhook events are rejected (never accepted as verified PayPal events).
    2. Missing PAYPAL_WEBHOOK_ID or missing transmission headers are rejected with HTTP 400.
    3. verify_webhook_signature returns False when unconfigured or when cert_url mismatches environment.
    4. Sandbox and Live API base URLs are strictly separated.
    """
    from app.services.paypal_service import PayPalService, global_paypal_service
    from app.core.config import settings

    sample_event = {
        "id": f"WH-SEC-{uuid.uuid4().hex[:8]}",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {"id": "CAP-123"}
    }

    # 1. process_webhook_event with signature_verified=False must reject
    unverified_res = await global_paypal_service.process_webhook_event(sample_event, signature_verified=False)
    assert unverified_res["status"] == "REJECTED_UNSIGNED_WEBHOOK"

    # 2. HTTP POST without headers or without PAYPAL_WEBHOOK_ID must be rejected with 400
    res_no_headers = client.post("/api/payments/webhooks", json=sample_event)
    assert res_no_headers.status_code == 400

    monkeypatch.setattr(settings, "PAYPAL_WEBHOOK_ID", "")
    res_no_wh_id = client.post(
        "/api/payments/webhooks",
        json=sample_event,
        headers={
            "paypal-transmission-id": "t-1",
            "paypal-transmission-time": "2026-11-10T12:00:00Z",
            "paypal-transmission-sig": "sig-1",
            "paypal-cert-url": "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-1",
            "paypal-auth-algo": "SHA256withRSA"
        }
    )
    assert res_no_wh_id.status_code == 400
    assert "PAYPAL_WEBHOOK_ID is not configured" in res_no_wh_id.json()["detail"]

    # 3. verify_webhook_signature rejects empty webhook_id and cross-environment cert_url
    svc = PayPalService()
    assert await svc.verify_webhook_signature(
        transmission_id="t-1",
        transmission_time="2026-11-10T12:00:00Z",
        cert_url="https://api.sandbox.paypal.com/v1/notifications/certs/CERT-1",
        auth_algo="SHA256withRSA",
        transmission_sig="sig-1",
        webhook_id="",
        event_body=sample_event
    ) is False

    # Non-sandbox cert URL in sandbox mode must be rejected
    assert await svc.verify_webhook_signature(
        transmission_id="t-1",
        transmission_time="2026-11-10T12:00:00Z",
        cert_url="https://api.paypal.com/v1/notifications/certs/CERT-LIVE",
        auth_algo="SHA256withRSA",
        transmission_sig="sig-1",
        webhook_id="WH-ID-123",
        event_body=sample_event
    ) is False

    # 4. Strict Sandbox vs Live API Base separation
    with pytest.raises(ValueError, match="sandbox"):
        PayPalService._validate_and_resolve_api_base("sandbox", "https://api-m.paypal.com")
    with pytest.raises(ValueError, match="live"):
        PayPalService._validate_and_resolve_api_base("live", "https://api-m.sandbox.paypal.com")


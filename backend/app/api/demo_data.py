from fastapi import APIRouter, HTTPException, Query, Body, Header
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Optional, List, Dict, Any
from ..demo_data.dataset_manager import global_dataset_manager
from ..demo_data.scenarios.catalogue import get_predefined_scenarios
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/demo-data", tags=["Synthetic Data Bank"])

@router.get("/status")
def get_data_bank_status(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    return global_dataset_manager.get_statistics()

@router.get("/statistics")
def get_data_bank_statistics(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    return global_dataset_manager.get_statistics()

@router.get("/users")
def list_users(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return [u.model_dump() for u in global_dataset_manager.users if u.user_id == auth_user]

@router.get("/accounts")
def list_accounts(
    owner_id: Optional[str] = None,
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(owner_id, x_finora_session_token)
    accounts = [a for a in global_dataset_manager.accounts if a.owner_id == auth_user]
    return [a.model_dump() for a in accounts]

@router.get("/transactions")
def list_transactions(
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    txs = [t for t in global_dataset_manager.transactions if t.user_id == auth_user]
    if category:
        txs = [t for t in txs if t.category.lower() == category.lower()]
    paginated = txs[offset:offset + limit]
    return {
        "total": len(txs),
        "offset": offset,
        "limit": limit,
        "items": [t.model_dump() for t in paginated]
    }

@router.get("/subscriptions")
def list_subscriptions(
    user_id: Optional[str] = None,
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    subs = [s for s in global_dataset_manager.subscriptions if s.user_id == auth_user]
    return [s.model_dump() for s in subs]

@router.get("/businesses")
def list_businesses(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    return [b.model_dump() for b in global_dataset_manager.businesses]

@router.get("/invoices")
def list_invoices(
    business_id: Optional[str] = None,
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    invs = global_dataset_manager.invoices
    if business_id:
        invs = [i for i in invs if i.business_id == business_id]
    return [i.model_dump() for i in invs]

@router.get("/products")
def list_products(category: Optional[str] = None):
    prods = global_dataset_manager.products
    if category and category != "all":
        prods = [p for p in prods if p.category.value == category]
    return [p.model_dump() for p in prods]

@router.get("/scenarios")
def list_scenarios():
    return [s.model_dump() for s in get_predefined_scenarios()]

@router.post("/generate")
def regenerate_data_bank(
    seed: int = Body(default=42, embed=True),
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    stats = global_dataset_manager.generate_complete_dataset(seed=seed)
    return {"message": "Data bank regenerated successfully", "stats": stats}

@router.post("/reset")
def reset_data_bank(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    stats = global_dataset_manager.reset_dataset()
    return {"message": "Data bank reset to default state", "stats": stats}

@router.post("/load-scenario")
def load_scenario(
    scenario_id: str = Body(..., embed=True),
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    scen = global_dataset_manager.load_scenario(scenario_id)
    if not scen:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found.")
    return {"message": f"Scenario {scenario_id} activated", "scenario": scen.model_dump()}

@router.post("/validate")
def validate_data_bank(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    report = global_dataset_manager.validate()
    return report.to_dict()

@router.get("/export/json")
def export_json(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    json_data = global_dataset_manager.export_to_json()
    return PlainTextResponse(content=json_data, media_type="application/json")

@router.get("/export/csv")
def export_csv(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    csv_data = global_dataset_manager.export_transactions_to_csv()
    return PlainTextResponse(content=csv_data, media_type="text/csv")

@router.post("/import/json")
def import_json(
    payload: Dict[str, Any] = Body(...),
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    import json
    try:
        json_str = json.dumps(payload)
        res = global_dataset_manager.import_from_json(json_str)
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

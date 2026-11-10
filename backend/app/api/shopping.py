from fastapi import APIRouter, Query, Body, HTTPException, Header
from typing import Optional, List
from ..agents.shopping_agent import global_shopping_agent
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/shopping", tags=["Autonomous Shopping Agent"])

@router.get("/products")
def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    max_price: Optional[float] = None
):
    return global_shopping_agent.search_products(query=query, category=category, max_price=max_price)

@router.post("/evaluate-budget")
def evaluate_budget(
    product_id: str = Body(..., embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        return global_shopping_agent.evaluate_purchase_budget(product_id=product_id, user_id=auth_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/compare")
def compare_products(
    product_ids: List[str] = Body(..., embed=True),
    target_budget: Optional[float] = Body(default=None, embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    resolve_authorized_user(user_id, x_finora_session_token)
    return global_shopping_agent.compare_products(product_ids=product_ids, target_budget=target_budget)

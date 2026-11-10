from fastapi import APIRouter, Body, Query, Header
from typing import Dict, Any, Optional
from ..agents.financial_guardian import global_financial_guardian
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/guardian", tags=["Financial Guardian Agent"])

@router.post("/chat")
async def chat_with_guardian(
    prompt: str = Body(..., embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    data_scope: str = Body(default="auto", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return await global_financial_guardian.chat(
        user_prompt=prompt,
        user_id=auth_user,
        data_scope=data_scope
    )

@router.get("/audit-subscriptions")
def audit_subscriptions(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return global_financial_guardian.get_subscription_audit(user_id=auth_user)

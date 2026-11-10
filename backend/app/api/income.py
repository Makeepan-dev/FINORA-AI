from fastapi import APIRouter, Query, Header
from typing import Optional
from ..services.income_service import global_income_service
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/income", tags=["Income Intelligence"])

@router.get("/intelligence")
def get_income_intelligence(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token, allow_test_personas=True)
    return global_income_service.get_user_income_intelligence(user_id=auth_user)

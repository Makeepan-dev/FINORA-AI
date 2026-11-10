from fastapi import APIRouter, Query, Header
from typing import Optional
from ..services.analytics_service import global_analytics_service
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/analytics", tags=["Financial Analytics"])

@router.get("/dashboard")
def get_dashboard_metrics(
    user_id: str = Query(default="usr_alex_chen"),
    data_scope: str = Query(default="auto", description="Data scope: 'auto', 'personal', or 'demo'"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return global_analytics_service.get_user_dashboard_metrics(user_id=auth_user, data_scope=data_scope)

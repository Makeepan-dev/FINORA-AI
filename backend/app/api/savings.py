from fastapi import APIRouter, Query, Body, HTTPException, Header
from typing import Dict, Any, Optional
from ..services.savings_service import global_savings_service
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/savings", tags=["Daily Money-Saving Intelligence"])

@router.get("/dashboard")
def get_savings_dashboard(
    user_id: str = Query(default="usr_alex_chen"),
    data_scope: str = Query(default="auto", description="Data scope: 'auto', 'personal', or 'demo'"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """
    Returns unified Daily Money-Saving Intelligence:
    - Potential vs Accepted vs Verified Realized savings
    - Daily personalized insights
    - Multi-factor ranked savings recommendations
    - Savings goal progress
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return global_savings_service.get_savings_dashboard(user_id=auth_user, data_scope=data_scope)

@router.post("/recommendations/{rec_id}/decision")
def update_recommendation_decision(
    rec_id: str,
    decision: str = Body(..., embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """
    User explicitly accepts, rejects, or resets a money-saving recommendation.
    Verifies server-side user ownership before modifying any recommendation.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        res = global_savings_service.update_recommendation_decision(
            user_id=auth_user,
            rec_id=rec_id,
            decision=decision
        )
        if not res:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        return res
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

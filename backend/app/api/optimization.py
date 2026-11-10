from fastapi import APIRouter, Query, Body, Header
from typing import Dict, Any, List, Optional
from decimal import Decimal
from ..optimization.expense_optimizer import global_expense_optimizer
from ..optimization.comparison import compare_recurring_alternatives
from ..optimization.engine import global_financial_optimization_engine, OptimizationOpportunity
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/optimization", tags=["Autonomous Financial Optimization"])

@router.get("/opportunities", response_model=List[OptimizationOpportunity])
def get_ranked_opportunities(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> List[OptimizationOpportunity]:
    """
    Returns ranked personal financial optimization opportunities across subscriptions,
    banking, debt, and commerce, evaluated with evidence quality and break-even math.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return global_financial_optimization_engine.generate_ranked_opportunities(user_id=auth_user)

@router.get("/audit")
def get_autonomous_optimization_audit(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """
    Executes the 14-step autonomous expense optimization workflow.
    Ranks commitments, assesses utilization evidence, discovers local alternatives,
    and calculates first-year net savings under user approval governance.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return global_expense_optimizer.run_optimization_workflow(user_id=auth_user)

@router.post("/compare")
def compare_commitment_alternatives(
    current_monthly: float = Body(..., embed=True),
    alternative_monthly: float = Body(..., embed=True),
    alternative_setup_fee: float = Body(default=0.0, embed=True),
    current_cancellation_fee: float = Body(default=0.0, embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """Compares current commitment with an alternative on first-year total costs and net savings."""
    resolve_authorized_user(user_id, x_finora_session_token)
    return compare_recurring_alternatives(
        current_monthly_cost=Decimal(str(current_monthly)),
        alternative_monthly_cost=Decimal(str(alternative_monthly)),
        alternative_setup_fee=Decimal(str(alternative_setup_fee)),
        current_cancellation_fee=Decimal(str(current_cancellation_fee))
    )

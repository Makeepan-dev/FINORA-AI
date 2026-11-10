from fastapi import APIRouter, Body, HTTPException, Query, Header
from typing import Dict, Any, List, Optional
from ..automation.engine import global_automation_engine
from ..automation.safety import global_safety_manager, PreparedAction
from ..automation.models import AutomationRule
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/automation", tags=["Autonomous Financial Automation & Action Safety"])

@router.get("/rules")
def get_automation_rules(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> List[Dict[str, Any]]:
    """Returns all active event-driven and scheduled automation rules."""
    resolve_authorized_user(user_id, x_finora_session_token)
    return global_automation_engine.get_rules()

@router.post("/rules")
def create_automation_rule(
    rule: AutomationRule,
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """Registers a new custom automation rule in the registry."""
    resolve_authorized_user(user_id, x_finora_session_token)
    global_automation_engine.register_rule(rule)
    return {"rule_id": rule.rule_id, "status": "registered", "rule": rule.model_dump()}

@router.get("/history")
def get_automation_history(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> List[Dict[str, Any]]:
    """Returns execution logs of evaluated triggers and prepared actions."""
    resolve_authorized_user(user_id, x_finora_session_token)
    return global_automation_engine.get_execution_history()

@router.post("/rules/{rule_id}/toggle")
def toggle_automation_rule(
    rule_id: str,
    enabled: bool = Body(..., embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """Enables or disables an automated financial monitor rule."""
    resolve_authorized_user(user_id, x_finora_session_token)
    success = global_automation_engine.set_rule_enabled(rule_id, enabled)
    if not success:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found.")
    return {"rule_id": rule_id, "is_enabled": enabled, "updated": success}

@router.post("/rules/{rule_id}/trigger")
def trigger_rule_test(
    rule_id: str,
    context: Optional[Dict[str, Any]] = Body(None, description="Optional trigger simulation context"),
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """Manually test-triggers an automation rule to verify condition evaluation and action preparation."""
    resolve_authorized_user(user_id, x_finora_session_token)
    try:
        log = global_automation_engine.trigger_rule_manually(rule_id, context or {})
        return {"success": True, "log": log.model_dump()}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-actions", response_model=List[PreparedAction])
def get_pending_actions(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> List[PreparedAction]:
    """
    Returns all Level 2 and Level 3 prepared financial actions awaiting explicit user approval.
    FINORA never executes funds transfers or subscription cancellations autonomously.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return [a for a in global_safety_manager.get_pending_actions() if a.user_id == auth_user]

@router.get("/actions", response_model=List[PreparedAction])
def get_all_actions(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> List[PreparedAction]:
    """Returns all prepared, approved, executed, and rejected action audit records."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return [a for a in global_safety_manager.get_all_actions() if a.user_id == auth_user]

@router.post("/actions/{action_id}/approve")
def approve_action(
    action_id: str,
    user_id: str = Body("usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """
    Step 14 User Authorization Gate: Explicitly approves and executes a prepared financial action.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        return global_safety_manager.approve_action(action_id, user_id=auth_user)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actions/{action_id}/reject")
def reject_action(
    action_id: str,
    reason: str = Body("User declined this recommendation", embed=True),
    user_id: str = Body("usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """Rejects a prepared financial action and marks it declined in the audit ledger."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        return global_safety_manager.reject_action(action_id, reason=reason, user_id=auth_user)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

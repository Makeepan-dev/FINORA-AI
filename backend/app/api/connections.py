from fastapi import APIRouter, Body, HTTPException, Query, Header
from typing import Optional
from ..services.sync_service import global_sync_service
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/connections", tags=["Connected Financial Accounts"])

@router.get("/institutions")
def get_supported_institutions():
    return global_sync_service.get_supported_institutions()

@router.get("/")
def list_connected_accounts(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return global_sync_service.list_connections(user_id=auth_user)

@router.post("/connect")
def connect_account(
    institution_id: str = Body(..., embed=True),
    account_type: str = Body(default="checking", embed=True),
    user_id: str = Body(default="usr_alex_chen", embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        return global_sync_service.connect_account(
            user_id=auth_user,
            institution_id=institution_id,
            account_type=account_type
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{connection_id}/sync")
def trigger_synchronization(
    connection_id: str,
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        return global_sync_service.trigger_synchronization(connection_id=connection_id, user_id=auth_user)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{connection_id}/revoke")
def revoke_connection(
    connection_id: str,
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        return global_sync_service.revoke_connection(connection_id=connection_id, user_id=auth_user)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history")
def get_sync_history(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return global_sync_service.get_sync_history(user_id=auth_user)

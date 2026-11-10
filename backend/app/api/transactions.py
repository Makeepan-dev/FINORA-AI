from fastapi import APIRouter, Query, UploadFile, File, Form, HTTPException, Body, Header
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..services.transaction_service import (
    global_transaction_service,
    MAX_CSV_SIZE_BYTES,
    MAX_CSV_ROWS
)
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/transactions", tags=["Personal Financial Transactions"])

ALLOWED_CSV_EXTENSIONS = (".csv", ".txt")
DISALLOWED_MIME_PREFIXES = ("image/", "video/", "audio/", "application/pdf", "application/zip", "application/x-msdownload")

class ManualTransactionCreate(BaseModel):
    date: Optional[str] = None
    merchant: str
    description: Optional[str] = None
    amount: float
    currency: str = "USD"
    transaction_type: Optional[str] = "expense"
    category: Optional[str] = None
    is_recurring: bool = False
    account_id: Optional[str] = "acc_manual"

class CsvConfirmRequest(BaseModel):
    user_id: str = "usr_alex_chen"
    records: List[Dict[str, Any]]
    skip_duplicates: bool = True

@router.get("")
def get_transactions(
    user_id: str = Query(default="usr_alex_chen"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    category: Optional[str] = Query(default=None),
    transaction_type: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    data_scope: str = Query(default="auto", description="Data scope: 'auto', 'personal', or 'demo'"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """Retrieve persisted transactions for the authorized user strictly scoped by data_scope."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    active_scope = global_transaction_service.resolve_data_scope(auth_user, data_scope)
    items = global_transaction_service.get_transactions(
        user_id=auth_user,
        limit=limit,
        offset=offset,
        category=category,
        transaction_type=transaction_type,
        search=search,
        data_scope=active_scope
    )
    return {
        "user_id": auth_user,
        "active_data_scope": active_scope,
        "has_personal_records": global_transaction_service.has_personal_records(auth_user),
        "count": len(items),
        "transactions": items
    }

@router.post("")
def add_transaction(
    payload: ManualTransactionCreate,
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """Log a manual personal transaction with Decimal precision and automatic categorization."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Transaction amount must be strictly positive")
    
    result = global_transaction_service.add_transaction(user_id=auth_user, data=payload.model_dump())
    return {"status": "success", "transaction": result, "active_data_scope": "personal"}

@router.delete("/{tx_id}")
def delete_transaction(
    tx_id: str,
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """Delete a user transaction after verifying server-side ownership."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    try:
        ok = global_transaction_service.delete_transaction(user_id=auth_user, tx_id=tx_id)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    if not ok:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"status": "success", "deleted_id": tx_id}

@router.post("/import-csv/preview")
async def preview_csv_import(
    file: Optional[UploadFile] = File(None),
    csv_text: Optional[str] = Form(None),
    user_id: str = Form(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """
    Parse uploaded CSV or raw CSV string, validate fields, flag errors and duplicates without writing to DB.
    Enforces:
    - Maximum CSV upload size: 2 MB (2,097,152 bytes)
    - Maximum CSV rows: 5,000
    - File type and content validation
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    content = ""

    if file is not None:
        filename = (file.filename or "").lower().strip()
        if filename and not filename.endswith(ALLOWED_CSV_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension '{filename}'. Only .csv or .txt files are allowed."
            )
        content_type = (file.content_type or "").lower()
        if any(content_type.startswith(p) for p in DISALLOWED_MIME_PREFIXES):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file content-type '{content_type}'. Only CSV text files are allowed."
            )

        # Read at most MAX_CSV_SIZE_BYTES + 1 bytes to prevent memory exhaustion
        content_bytes = await file.read(MAX_CSV_SIZE_BYTES + 1)
        if len(content_bytes) > MAX_CSV_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"CSV upload exceeds maximum allowed size of 2 MB ({MAX_CSV_SIZE_BYTES:,} bytes)."
            )
        if b"\x00" in content_bytes:
            raise HTTPException(
                status_code=400,
                detail="Malformed or binary file content detected. Please upload a valid UTF-8 CSV file."
            )
        try:
            content = content_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            content = content_bytes.decode("latin-1", errors="replace")

    elif csv_text is not None:
        if len(csv_text.encode("utf-8", errors="replace")) > MAX_CSV_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"CSV payload exceeds maximum allowed size of 2 MB ({MAX_CSV_SIZE_BYTES:,} bytes)."
            )
        if "\x00" in csv_text:
            raise HTTPException(
                status_code=400,
                detail="Malformed CSV content containing null bytes."
            )
        content = csv_text
    else:
        raise HTTPException(status_code=400, detail="Either a CSV file or csv_text must be provided")

    try:
        preview = global_transaction_service.preview_csv_import(user_id=auth_user, csv_content=content)
        return preview
    except ValueError as ve:
        msg = str(ve)
        status_code = 413 if "exceeds maximum allowed size" in msg else 400
        raise HTTPException(status_code=status_code, detail=msg)

@router.post("/import-csv/confirm")
def confirm_csv_import(
    request: CsvConfirmRequest,
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """
    Import validated preview records into SQLite with duplicate prevention and row limits.
    """
    auth_user = resolve_authorized_user(request.user_id, x_finora_session_token)
    if not request.records:
        raise HTTPException(status_code=400, detail="No records provided to import")
    if len(request.records) > MAX_CSV_ROWS:
        raise HTTPException(
            status_code=400,
            detail=f"Import batch exceeds maximum allowed limit of {MAX_CSV_ROWS:,} rows."
        )
    try:
        result = global_transaction_service.confirm_csv_import(
            user_id=auth_user,
            records=request.records,
            skip_duplicates=request.skip_duplicates
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.get("/summary")
def get_financial_summary(
    user_id: str = Query(default="usr_alex_chen"),
    month: Optional[str] = Query(default=None),
    data_scope: str = Query(default="auto", description="Data scope: 'auto', 'personal', or 'demo'"),
    x_finora_session_token: Optional[str] = Header(default=None)
):
    """
    Retrieve authoritative financial summary calculated with Decimal precision.
    Transfers are strictly excluded from income and expenses.
    Demo records never silently mix with personal records.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return global_transaction_service.get_financial_summary(
        user_id=auth_user,
        month_str=month,
        data_scope=data_scope
    )

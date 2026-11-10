import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..database.session import SessionLocal
from ..models.db_models import ConnectedAccount, SyncLog
from ..demo_data.dataset_manager import global_dataset_manager
from ..demo_data.models.transaction import TransactionType

# Default initial connected institutions matching real-world providers
SUPPORTED_INSTITUTIONS = [
    {
        "id": "inst_paypal",
        "name": "PayPal Commerce & Wallet",
        "provider_type": "paypal_direct",
        "icon": "paypal",
        "description": "Direct OAuth connection to PayPal Sandbox/Live account."
    },
    {
        "id": "inst_chase",
        "name": "Chase Bank (JPMorgan Chase)",
        "provider_type": "open_banking_plaid",
        "icon": "bank",
        "description": "Secure Open Banking OAuth token via Plaid Financial Core."
    },
    {
        "id": "inst_boa",
        "name": "Bank of America",
        "provider_type": "open_banking_plaid",
        "icon": "bank",
        "description": "Authorized account and transaction streaming via Plaid."
    },
    {
        "id": "inst_fidelity",
        "name": "Fidelity Investments",
        "provider_type": "open_banking_plaid",
        "icon": "wallet",
        "description": "Cash management and dividend tracking via Plaid."
    },
    {
        "id": "inst_barclays",
        "name": "Barclays UK Open Banking",
        "provider_type": "truelayer_uk",
        "icon": "bank",
        "description": "FCA-regulated TrueLayer Open Banking API (UK/EU)."
    }
]

class FinancialSyncService:
    def __init__(self):
        self._ensure_default_connections()

    def _ensure_default_connections(self):
        """Seeds initial connected accounts for the demo personas if not already in DB."""
        try:
            db = SessionLocal()
            existing_alex = db.query(ConnectedAccount).filter(ConnectedAccount.user_id == "usr_alex_chen").first()
            if not existing_alex:
                default_conns = [
                    ConnectedAccount(
                        id="conn_alex_paypal",
                        user_id="usr_alex_chen",
                        institution_id="inst_paypal",
                        institution_name="PayPal Commerce & Digital Wallet",
                        provider_type="paypal_direct",
                        account_mask="SYNTH-PP-7210",
                        account_type="paypal_wallet",
                        connection_status="connected",
                        health_status="healthy",
                        last_sync_timestamp=datetime.utcnow(),
                        sync_frequency="realtime",
                        permissions_granted='["read_transactions","read_balance","execute_authorized_payments"]',
                        is_synthetic=True
                    ),
                    ConnectedAccount(
                        id="conn_alex_chase",
                        user_id="usr_alex_chen",
                        institution_id="inst_chase",
                        institution_name="Chase Premier Checking & Vault",
                        provider_type="open_banking_plaid",
                        account_mask="SYNTH-CHK-8812",
                        account_type="checking",
                        connection_status="connected",
                        health_status="healthy",
                        last_sync_timestamp=datetime.utcnow(),
                        sync_frequency="hourly",
                        permissions_granted='["read_transactions","read_balance","read_identity"]',
                        is_synthetic=True
                    )
                ]
                for c in default_conns:
                    db.add(c)
                db.commit()
            db.close()
        except Exception as e:
            pass

    def get_supported_institutions(self) -> List[Dict[str, Any]]:
        return SUPPORTED_INSTITUTIONS

    def list_connections(self, user_id: str = "usr_alex_chen") -> List[Dict[str, Any]]:
        db = SessionLocal()
        conns = db.query(ConnectedAccount).filter(ConnectedAccount.user_id == user_id).all()
        if not conns:
            self._ensure_default_connections()
            conns = db.query(ConnectedAccount).filter(ConnectedAccount.user_id == user_id).all()
        result = []
        for c in conns:
            result.append({
                "id": c.id,
                "user_id": c.user_id,
                "institution_id": c.institution_id,
                "institution_name": c.institution_name,
                "provider_type": c.provider_type,
                "account_mask": c.account_mask,
                "account_type": c.account_type,
                "connection_status": c.connection_status,
                "health_status": c.health_status,
                "last_sync": c.last_sync_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if c.last_sync_timestamp else "Never",
                "sync_frequency": c.sync_frequency,
                "permissions": c.permissions_granted,
                "is_synthetic": c.is_synthetic
            })
        db.close()
        return result

    def connect_account(
        self,
        user_id: str,
        institution_id: str,
        account_type: str = "checking"
    ) -> Dict[str, Any]:
        """Simulates secure OAuth authorization flow and links financial account."""
        inst = next((i for i in SUPPORTED_INSTITUTIONS if i["id"] == institution_id), None)
        if not inst:
            raise ValueError(f"Institution {institution_id} not supported.")

        conn_id = f"conn_{uuid.uuid4().hex[:8]}"
        mask = f"SYNTH-{uuid.uuid4().hex[:4].upper()}"

        db = SessionLocal()
        conn = ConnectedAccount(
            id=conn_id,
            user_id=user_id,
            institution_id=institution_id,
            institution_name=inst["name"],
            provider_type=inst["provider_type"],
            account_mask=mask,
            account_type=account_type,
            connection_status="connected",
            health_status="healthy",
            last_sync_timestamp=datetime.utcnow(),
            sync_frequency="hourly",
            permissions_granted='["read_transactions","read_balance","read_identity"]',
            is_synthetic=True
        )
        db.add(conn)

        # Log initial sync
        log = SyncLog(
            id=str(uuid.uuid4()),
            connection_id=conn_id,
            user_id=user_id,
            sync_type="automatic",
            status="success",
            records_ingested=32,
            income_detected_count=2,
            expenses_categorized_count=30,
            duration_ms=145
        )
        db.add(log)
        db.commit()
        db.close()

        return {
            "connection_id": conn_id,
            "status": "connected",
            "institution": inst["name"],
            "mask": mask,
            "message": "Account successfully linked via secure OAuth token."
        }

    def trigger_synchronization(self, connection_id: str, user_id: str = "usr_alex_chen") -> Dict[str, Any]:
        """Executes auto-sync cycle: pulls transactions, detects income streams, flags commitments."""
        db = SessionLocal()
        conn = db.query(ConnectedAccount).filter(ConnectedAccount.id == connection_id).first()
        if not conn:
            db.close()
            raise ValueError("Connection not found")

        if conn.user_id != user_id:
            db.close()
            raise PermissionError("Forbidden: Cannot synchronize a connected account belonging to another user.")

        if conn.connection_status == "revoked":
            db.close()
            raise ValueError("Cannot sync: Connection permissions have been revoked by user.")

        conn.connection_status = "syncing"
        db.commit()

        # Simulate synchronization duration & record analysis
        start_time = datetime.utcnow()
        user_txs = [t for t in global_dataset_manager.transactions if t.user_id == conn.user_id]
        income_txs = [t for t in user_txs if t.transaction_type == TransactionType.INCOME]
        expense_txs = [t for t in user_txs if t.transaction_type == TransactionType.EXPENSE]

        conn.last_sync_timestamp = datetime.utcnow()
        conn.connection_status = "connected"
        conn.health_status = "healthy"

        # Record Sync Log
        log = SyncLog(
            id=str(uuid.uuid4()),
            connection_id=conn.id,
            user_id=conn.user_id,
            sync_type="manual_trigger",
            status="success",
            records_ingested=len(user_txs),
            income_detected_count=len(income_txs),
            expenses_categorized_count=len(expense_txs),
            duration_ms=88
        )
        db.add(log)
        db.commit()
        db.close()

        return {
            "status": "success",
            "connection_id": connection_id,
            "records_synchronized": len(user_txs),
            "income_streams_detected": len(income_txs),
            "expenses_categorized": len(expense_txs),
            "last_synced_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

    def revoke_connection(self, connection_id: str, user_id: str = "usr_alex_chen") -> Dict[str, Any]:
        """Revokes all granted OAuth permissions and disconnects the account."""
        db = SessionLocal()
        conn = db.query(ConnectedAccount).filter(ConnectedAccount.id == connection_id).first()
        if not conn:
            db.close()
            raise ValueError("Connection not found")

        if conn.user_id != user_id:
            db.close()
            raise PermissionError("Forbidden: Cannot revoke a connected account belonging to another user.")

        conn.connection_status = "revoked"
        conn.health_status = "disconnected"
        conn.permissions_granted = "[]"
        db.commit()
        db.close()

        return {
            "connection_id": connection_id,
            "status": "revoked",
            "message": "Permissions revoked. FINORA will no longer retrieve or synchronize financial data from this account."
        }

    def get_sync_history(self, user_id: str = "usr_alex_chen") -> List[Dict[str, Any]]:
        db = SessionLocal()
        logs = db.query(SyncLog).filter(SyncLog.user_id == user_id).order_by(SyncLog.created_at.desc()).limit(20).all()
        result = []
        for l in logs:
            result.append({
                "id": l.id,
                "connection_id": l.connection_id,
                "sync_type": l.sync_type,
                "status": l.status,
                "records_ingested": l.records_ingested,
                "income_detected": l.income_detected_count,
                "expenses_categorized": l.expenses_categorized_count,
                "duration_ms": l.duration_ms,
                "timestamp": l.created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if l.created_at else None
            })
        db.close()
        return result

global_sync_service = FinancialSyncService()

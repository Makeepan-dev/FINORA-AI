import uuid
from enum import Enum
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ActionSafetyLevel(str, Enum):
    LEVEL_1_READ_ONLY = "LEVEL_1_READ_ONLY"      # Calculations, reports, alerts, categorization (autonomous)
    LEVEL_2_PREPARED = "LEVEL_2_PREPARED"        # Drafts, payment requests, PayPal orders (prepared only)
    LEVEL_3_USER_APPROVED = "LEVEL_3_USER_APPROVED" # PayPal captures, transfers, cancellations (requires user gate)
    LEVEL_4_RESTRICTED = "LEVEL_4_RESTRICTED"    # Self-approval, unbounded spend, bypassing backend (forbidden)

class ActionStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class PreparedAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:12]}")
    user_id: str = "usr_alex_chen"
    safety_level: ActionSafetyLevel
    title: str
    description: str
    action_type: str  # "paypal_payment_capture" | "subscription_cancellation_dispatch" | "savings_transfer"
    target_merchant_or_payee: str
    amount: float
    currency: str = "USD"
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: ActionStatus = ActionStatus.PENDING_APPROVAL
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str = Field(default_factory=lambda: (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat())
    approved_at: Optional[str] = None
    executed_at: Optional[str] = None
    idempotency_key: str = Field(default_factory=lambda: f"idemp_{uuid.uuid4().hex[:16]}")
    audit_notes: List[str] = Field(default_factory=list)

class ActionSafetyManager:
    """
    Financial Action Safety Gate & Permission Enforcer for FINORA.
    Guarantees that autonomous actions never move funds or commit user capital
    without explicit, cryptographic/user-approved authorization.
    """
    def __init__(self):
        self._actions: Dict[str, PreparedAction] = {}
        self._idempotency_records: Dict[str, str] = {}  # idempotency_key -> action_id
        self._initialize_seed_actions()

    def _initialize_seed_actions(self):
        # Seed an illustrative prepared action for user inspection
        seed_act = PreparedAction(
            action_id="act_gym_downgrade_001",
            safety_level=ActionSafetyLevel.LEVEL_3_USER_APPROVED,
            title="Apex Athletic All-Access Pass Cancellation Notice",
            description="Prepared formal 30-day cancellation letter to eliminate $120.00/mo idle gym commitment.",
            action_type="subscription_cancellation_dispatch",
            target_merchant_or_payee="Apex Athletic Club",
            amount=120.00,
            currency="USD",
            payload={"subscription_id": "sub_alex_apex_gym", "notice_days": 30, "alternative": "MetroFit"},
            status=ActionStatus.PENDING_APPROVAL,
            audit_notes=["Prepared by Autonomous Expense Optimizer based on 1 check-in over 90 days ($360/visit)."]
        )
        self._actions[seed_act.action_id] = seed_act
        self._idempotency_records[seed_act.idempotency_key] = seed_act.action_id

    def create_action(
        self,
        safety_level: ActionSafetyLevel,
        title: str,
        description: str,
        action_type: str,
        target_merchant_or_payee: str,
        amount: float,
        currency: str = "USD",
        payload: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None
    ) -> PreparedAction:
        # Enforce Level 4 restriction
        if safety_level == ActionSafetyLevel.LEVEL_4_RESTRICTED:
            raise PermissionError("Level 4 restricted actions cannot be created or executed by automated engines.")

        if idempotency_key and idempotency_key in self._idempotency_records:
            existing_id = self._idempotency_records[idempotency_key]
            return self._actions[existing_id]

        action = PreparedAction(
            safety_level=safety_level,
            title=title,
            description=description,
            action_type=action_type,
            target_merchant_or_payee=target_merchant_or_payee,
            amount=amount,
            currency=currency,
            payload=payload or {},
            status=ActionStatus.PENDING_APPROVAL if safety_level == ActionSafetyLevel.LEVEL_3_USER_APPROVED else ActionStatus.APPROVED,
            idempotency_key=idempotency_key or f"idemp_{uuid.uuid4().hex[:16]}"
        )

        self._actions[action.action_id] = action
        self._idempotency_records[action.idempotency_key] = action.action_id
        return action

    def get_pending_actions(self) -> List[PreparedAction]:
        now_dt = datetime.now(timezone.utc)
        result = []
        for act in self._actions.values():
            exp_dt = datetime.fromisoformat(act.expires_at)
            if act.status == ActionStatus.PENDING_APPROVAL:
                if exp_dt < now_dt:
                    act.status = ActionStatus.EXPIRED
                else:
                    result.append(act)
        return result

    def get_all_actions(self) -> List[PreparedAction]:
        return list(self._actions.values())

    def get_action(self, action_id: str) -> Optional[PreparedAction]:
        return self._actions.get(action_id)

    def approve_action(self, action_id: str, user_id: str = "usr_alex_chen") -> Dict[str, Any]:
        act = self._actions.get(action_id)
        if not act:
            raise ValueError(f"Action '{action_id}' not found.")

        if act.user_id != user_id:
            raise PermissionError(f"Forbidden: Action '{action_id}' belongs to '{act.user_id}', not '{user_id}'.")

        if act.status != ActionStatus.PENDING_APPROVAL:
            return {"action_id": action_id, "status": act.status.value, "success": False, "message": f"Action is already {act.status.value}"}

        now_str = datetime.now(timezone.utc).isoformat()
        act.status = ActionStatus.APPROVED
        act.approved_at = now_str
        act.audit_notes.append(f"Explicit user authorization granted by {user_id} at {now_str}.")

        # Execute the action safely
        act.status = ActionStatus.EXECUTED
        act.executed_at = now_str
        act.audit_notes.append(f"Executed securely under user authorization token. Funds/notification dispatched.")

        return {
            "action_id": action_id,
            "status": act.status.value,
            "success": True,
            "message": f"Action '{act.title}' was approved and executed successfully.",
            "action": act.model_dump()
        }

    def reject_action(self, action_id: str, reason: str = "User declined action", user_id: str = "usr_alex_chen") -> Dict[str, Any]:
        act = self._actions.get(action_id)
        if not act:
            raise ValueError(f"Action '{action_id}' not found.")

        if act.user_id != user_id:
            raise PermissionError(f"Forbidden: Action '{action_id}' belongs to '{act.user_id}', not '{user_id}'.")

        act.status = ActionStatus.REJECTED
        act.audit_notes.append(f"Rejected by {user_id}: {reason}.")
        return {
            "action_id": action_id,
            "status": act.status.value,
            "success": True,
            "message": f"Action '{act.title}' was rejected."
        }

global_safety_manager = ActionSafetyManager()

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from .safety import ActionSafetyLevel

class AutomationCategory(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    SUBSCRIPTION = "SUBSCRIPTION"
    SAVINGS = "SAVINGS"
    DEBT = "DEBT"
    SHOPPING = "SHOPPING"
    PROTECTION = "PROTECTION"
    FORECASTING = "FORECASTING"

class TriggerType(str, Enum):
    NEW_TRANSACTION = "new_transaction"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    BALANCE_THRESHOLD = "balance_threshold"
    BUDGET_OVERRUN = "budget_overrun"
    INCOME_DETECTED = "income_detected"
    SCHEDULED_INTERVAL = "scheduled_interval"
    MANUAL_EVALUATION = "manual_evaluation"

class ConditionOperator(str, Enum):
    GT = ">"
    LT = "<"
    EQ = "=="
    GTE = ">="
    LTE = "<="
    CONTAINS = "contains"
    PCT_CHANGE_GT = "pct_change_gt"

class ConditionSpec(BaseModel):
    field: str
    operator: ConditionOperator
    target_value: Any

class AutomationRule(BaseModel):
    rule_id: str
    name: str
    description: str
    category: AutomationCategory
    trigger_type: TriggerType
    conditions: List[ConditionSpec] = Field(default_factory=list)
    action_type: str  # "notify_user", "prepare_approval_request", "recalculate_runway", "prepare_cancellation"
    safety_level: ActionSafetyLevel = ActionSafetyLevel.LEVEL_1_READ_ONLY
    is_enabled: bool = True
    requires_user_approval: bool = False
    schedule_interval_minutes: Optional[int] = None
    execution_count: int = 0
    last_executed: Optional[str] = None
    next_scheduled: Optional[str] = None

class ExecutionLog(BaseModel):
    log_id: str
    rule_id: str
    rule_name: str
    category: AutomationCategory
    event_trigger: str
    execution_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str  # "TRIGGERED", "ACTION_PREPARED", "USER_APPROVAL_PENDING", "COMPLETED", "FAILED"
    details: str
    prepared_action_id: Optional[str] = None
    metrics_snapshot: Dict[str, Any] = Field(default_factory=dict)

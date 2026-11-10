import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from .models import (
    AutomationCategory,
    TriggerType,
    ConditionOperator,
    ConditionSpec,
    AutomationRule,
    ExecutionLog
)
from .safety import ActionSafetyLevel, global_safety_manager
from ..formulas.decimal_engine import to_d, calc_monthly_cash_flow, calc_emergency_fund_coverage, calc_financial_health_index

class AutomationEngine:
    """
    Central Autonomous Event-Driven & Scheduled Financial Automation Engine for FINORA.
    Orchestrates continuous monitoring, condition evaluation, formula-based analysis,
    and safe, user-gated financial action preparation.
    """
    def __init__(self, safety_mgr=None):
        self.safety = safety_mgr or global_safety_manager
        self._rules: Dict[str, AutomationRule] = {}
        self._history: List[ExecutionLog] = []
        self._last_scheduled_run: Optional[datetime] = None
        self._seed_rules()
        self._seed_initial_history()

    def _seed_rules(self):
        # 1. Income Automation
        self.register_rule(AutomationRule(
            rule_id="rule_income_deposit_tracker",
            name="Income Inflow & Spending Capacity Recalculator",
            description="Detects incoming payroll/freelance revenue, recalculates monthly surplus and updates cash runway.",
            category=AutomationCategory.INCOME,
            trigger_type=TriggerType.INCOME_DETECTED,
            conditions=[ConditionSpec(field="amount", operator=ConditionOperator.GT, target_value=500.0)],
            action_type="recalculate_runway",
            safety_level=ActionSafetyLevel.LEVEL_1_READ_ONLY,
            is_enabled=True,
            requires_user_approval=False
        ))

        # 2. Expense: Unusual Spend
        self.register_rule(AutomationRule(
            rule_id="rule_unusual_spend_alert",
            name="Unusual High-Value Transaction Warning",
            description="Monitors debits exceeding $300 to prevent undetected budget leakage.",
            category=AutomationCategory.EXPENSE,
            trigger_type=TriggerType.NEW_TRANSACTION,
            conditions=[ConditionSpec(field="amount", operator=ConditionOperator.GT, target_value=300.0)],
            action_type="notify_user",
            safety_level=ActionSafetyLevel.LEVEL_1_READ_ONLY,
            is_enabled=True,
            requires_user_approval=False
        ))

        # 3. Expense: Duplicate Charge Watch
        self.register_rule(AutomationRule(
            rule_id="rule_duplicate_charge_watch",
            name="Duplicate Transaction Error Watch",
            description="Identifies potential duplicate charges with identical amounts from the same merchant within 48h.",
            category=AutomationCategory.EXPENSE,
            trigger_type=TriggerType.NEW_TRANSACTION,
            conditions=[ConditionSpec(field="is_duplicate_candidate", operator=ConditionOperator.EQ, target_value=True)],
            action_type="notify_user",
            safety_level=ActionSafetyLevel.LEVEL_1_READ_ONLY,
            is_enabled=True,
            requires_user_approval=False
        ))

        # 4. Subscription: Renewal Notice
        self.register_rule(AutomationRule(
            rule_id="rule_renewal_monitor",
            name="Subscription 7-Day Renewal Advance Reminder",
            description="Scans recurring commitments and alerts user 7 days before automated renewal debits.",
            category=AutomationCategory.SUBSCRIPTION,
            trigger_type=TriggerType.SUBSCRIPTION_RENEWAL,
            conditions=[ConditionSpec(field="days_until_renewal", operator=ConditionOperator.LTE, target_value=7)],
            action_type="notify_user",
            safety_level=ActionSafetyLevel.LEVEL_1_READ_ONLY,
            is_enabled=True,
            requires_user_approval=False
        ))

        # 5. Subscription: Low Usage Optimizer (Level 3 Gate)
        self.register_rule(AutomationRule(
            rule_id="rule_low_usage_optimizer",
            name="Idle Commitment Optimization Trigger",
            description="Detects recurring services with zero or near-zero utilization and prepares a user-approved cancellation draft.",
            category=AutomationCategory.SUBSCRIPTION,
            trigger_type=TriggerType.SCHEDULED_INTERVAL,
            conditions=[ConditionSpec(field="potential_savings", operator=ConditionOperator.GT, target_value=20.0)],
            action_type="prepare_approval_request",
            safety_level=ActionSafetyLevel.LEVEL_3_USER_APPROVED,
            is_enabled=True,
            requires_user_approval=True,
            schedule_interval_minutes=1440
        ))

        # 6. Savings: Emergency Reserve Floor Monitor
        self.register_rule(AutomationRule(
            rule_id="rule_emergency_floor_watch",
            name="Emergency Cash Runway 3-Month Floor Guard",
            description="Alerts user when checking/savings liquid reserves drop below 3 months of essential expenses.",
            category=AutomationCategory.SAVINGS,
            trigger_type=TriggerType.BALANCE_THRESHOLD,
            conditions=[ConditionSpec(field="emergency_coverage_months", operator=ConditionOperator.LT, target_value=3.0)],
            action_type="notify_user",
            safety_level=ActionSafetyLevel.LEVEL_1_READ_ONLY,
            is_enabled=True,
            requires_user_approval=False
        ))

        # 7. Debt: Early Repayment Opportunity
        self.register_rule(AutomationRule(
            rule_id="rule_debt_early_payoff_eval",
            name="Debt Early Repayment Surplus Opportunity",
            description="Identifies when monthly surplus exceeds $400 and models interest saved by prepaying highest-rate debt.",
            category=AutomationCategory.DEBT,
            trigger_type=TriggerType.SCHEDULED_INTERVAL,
            conditions=[ConditionSpec(field="monthly_surplus", operator=ConditionOperator.GT, target_value=400.0)],
            action_type="prepare_approval_request",
            safety_level=ActionSafetyLevel.LEVEL_2_PREPARED,
            is_enabled=True,
            requires_user_approval=False,
            schedule_interval_minutes=1440
        ))

        # 8. Protection: Suspicious Transaction Watch
        self.register_rule(AutomationRule(
            rule_id="rule_fraud_anomaly_watch",
            name="High-Risk Anomaly & Fraud Protection",
            description="Flags foreign merchant transactions or sudden midnight out-of-pattern debits.",
            category=AutomationCategory.PROTECTION,
            trigger_type=TriggerType.NEW_TRANSACTION,
            conditions=[ConditionSpec(field="risk_score", operator=ConditionOperator.GT, target_value=75.0)],
            action_type="notify_user",
            safety_level=ActionSafetyLevel.LEVEL_1_READ_ONLY,
            is_enabled=True,
            requires_user_approval=False
        ))

        # 9. Forecasting: Periodic Health Index Re-evaluator
        self.register_rule(AutomationRule(
            rule_id="rule_periodic_health_reforecast",
            name="Scheduled Financial Health Index & Cash Forecast",
            description="Periodically recomputes the 0-100 Financial Health Index and 30-day cash flow projections.",
            category=AutomationCategory.FORECASTING,
            trigger_type=TriggerType.SCHEDULED_INTERVAL,
            action_type="recalculate_runway",
            safety_level=ActionSafetyLevel.LEVEL_1_READ_ONLY,
            is_enabled=True,
            requires_user_approval=False,
            schedule_interval_minutes=720
        ))

    def _seed_initial_history(self):
        now_str = datetime.now(timezone.utc).isoformat()
        self._history = [
            ExecutionLog(
                log_id="auto_log_init_001",
                rule_id="rule_renewal_monitor",
                rule_name="Subscription 7-Day Renewal Advance Reminder",
                category=AutomationCategory.SUBSCRIPTION,
                event_trigger="System Startup Recurring Review Scan",
                execution_timestamp=now_str,
                status="COMPLETED",
                details="Scanned 7 recurring commitments. Flagged 2 commitments approaching renewal within 7 days."
            ),
            ExecutionLog(
                log_id="auto_log_init_002",
                rule_id="rule_low_usage_optimizer",
                rule_name="Idle Commitment Optimization Trigger",
                category=AutomationCategory.SUBSCRIPTION,
                event_trigger="Telemetry check for Apex Athletic Club (1 visit in 90 days)",
                execution_timestamp=now_str,
                status="USER_APPROVAL_PENDING",
                details="Prepared Level 3 cancellation action for $120.00/mo gym pass. Awaiting user approval token.",
                prepared_action_id="act_gym_downgrade_001"
            )
        ]

    def register_rule(self, rule: AutomationRule):
        self._rules[rule.rule_id] = rule

    def get_rules(self) -> List[Dict[str, Any]]:
        return [r.model_dump() for r in self._rules.values()]

    def get_rule(self, rule_id: str) -> Optional[AutomationRule]:
        return self._rules.get(rule_id)

    def set_rule_enabled(self, rule_id: str, enabled: bool) -> bool:
        if rule_id in self._rules:
            self._rules[rule_id].is_enabled = enabled
            return True
        return False

    def get_execution_history(self) -> List[Dict[str, Any]]:
        return [log.model_dump() for log in self._history]

    # -------------------------------------------------------------------------
    # CONDITION EVALUATION ENGINE
    # -------------------------------------------------------------------------
    def _evaluate_condition(self, condition: ConditionSpec, context: Dict[str, Any]) -> bool:
        field_val = context.get(condition.field)
        if field_val is None:
            return False

        target = condition.target_value
        op = condition.operator

        try:
            if op == ConditionOperator.EQ:
                return str(field_val).lower() == str(target).lower()
            
            # Numeric comparisons
            f_num = float(to_d(field_val))
            t_num = float(to_d(target))

            if op == ConditionOperator.GT:
                return f_num > t_num
            elif op == ConditionOperator.GTE:
                return f_num >= t_num
            elif op == ConditionOperator.LT:
                return f_num < t_num
            elif op == ConditionOperator.LTE:
                return f_num <= t_num
            elif op == ConditionOperator.CONTAINS:
                return str(target).lower() in str(field_val).lower()
        except Exception:
            return False

        return False

    # -------------------------------------------------------------------------
    # WORKFLOW EXECUTION & EVENT DISPATCH
    # -------------------------------------------------------------------------
    def trigger_rule_manually(self, rule_id: str, context: Optional[Dict[str, Any]] = None) -> ExecutionLog:
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Rule '{rule_id}' not found.")

        ctx = context or {}
        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.isoformat()
        rule.execution_count += 1
        rule.last_executed = now_str

        # If Level 3 action, prepare safety action
        prepared_id = None
        if rule.requires_user_approval or rule.safety_level == ActionSafetyLevel.LEVEL_3_USER_APPROVED:
            action = self.safety.create_action(
                safety_level=ActionSafetyLevel.LEVEL_3_USER_APPROVED,
                title=f"{rule.name} Action",
                description=f"Action prepared by automation rule '{rule.name}'. Requires user approval.",
                action_type=rule.action_type,
                target_merchant_or_payee=ctx.get("merchant", "Merchant / Service Provider"),
                amount=float(ctx.get("amount", ctx.get("potential_savings", 0.0))),
                payload=ctx
            )
            prepared_id = action.action_id
            status = "USER_APPROVAL_PENDING"
            details = f"Prepared Level 3 action '{action.title}' (ID: {prepared_id}). Waiting for user authorization."
        else:
            status = "COMPLETED"
            details = f"Successfully executed rule '{rule.name}' for {rule.category.value} domain."

        log = ExecutionLog(
            log_id=f"auto_log_{uuid.uuid4().hex[:8]}",
            rule_id=rule.rule_id,
            rule_name=rule.name,
            category=rule.category,
            event_trigger=f"Manual or test evaluation trigger for {rule.name}",
            execution_timestamp=now_str,
            status=status,
            details=details,
            prepared_action_id=prepared_id,
            metrics_snapshot=ctx
        )
        self._history.append(log)
        return log

    def evaluate_event(self, trigger_type: TriggerType, context: Dict[str, Any]) -> List[ExecutionLog]:
        logs = []
        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.isoformat()

        matching_rules = [
            r for r in self._rules.values()
            if r.is_enabled and (r.trigger_type == trigger_type or r.trigger_type == TriggerType.SCHEDULED_INTERVAL)
        ]

        for rule in matching_rules:
            # Check conditions (AND logic)
            all_passed = True
            for cond in rule.conditions:
                if not self._evaluate_condition(cond, context):
                    all_passed = False
                    break

            if all_passed:
                rule.execution_count += 1
                rule.last_executed = now_str

                prepared_id = None
                if rule.requires_user_approval or rule.safety_level == ActionSafetyLevel.LEVEL_3_USER_APPROVED:
                    action = self.safety.create_action(
                        safety_level=ActionSafetyLevel.LEVEL_3_USER_APPROVED,
                        title=f"{rule.name} Action",
                        description=f"Automated action generated under {rule.category.value} policy.",
                        action_type=rule.action_type,
                        target_merchant_or_payee=context.get("merchant", "Merchant"),
                        amount=float(context.get("amount", context.get("potential_savings", 0.0))),
                        payload=context
                    )
                    prepared_id = action.action_id
                    status = "USER_APPROVAL_PENDING"
                    details = f"Prepared Level 3 approval action ({prepared_id}). Requires explicit user authorization."
                else:
                    status = "COMPLETED"
                    details = f"Rule triggered and evaluated successfully on {trigger_type.value}."

                log = ExecutionLog(
                    log_id=f"auto_log_{uuid.uuid4().hex[:8]}",
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    event_trigger=f"Event '{trigger_type.value}' matched rule criteria.",
                    execution_timestamp=now_str,
                    status=status,
                    details=details,
                    prepared_action_id=prepared_id,
                    metrics_snapshot=context
                )
                logs.append(log)
                self._history.append(log)

        return logs

    # Backward-compatible method
    def evaluate_triggers(self, context: Dict[str, Any]) -> List[ExecutionLog]:
        return self.evaluate_event(TriggerType.SCHEDULED_INTERVAL, context)

global_automation_engine = AutomationEngine()

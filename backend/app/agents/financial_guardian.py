from typing import Dict, Any, Optional
from ..services.analytics_service import global_analytics_service
from ..services.knowledge_orchestrator import global_knowledge_orchestrator
from ..services.savings_service import global_savings_service
from ..services.transaction_service import global_transaction_service
from ..demo_data.dataset_manager import global_dataset_manager

class FinancialGuardianAgent:
    """
    Primary AI Agent for FINORA.
    Driven by the 7-Stage Knowledge-First Financial & Commerce Intelligence Architecture.
    Answers internal calculations and knowledge-based questions deterministically without AI API calls,
    escalating to Google Gemini only when deep contextual reasoning is required.
    """
    def __init__(self):
        self.analytics = global_analytics_service
        self.orchestrator = global_knowledge_orchestrator
        self.dataset_mgr = global_dataset_manager

    async def chat(
        self,
        user_prompt: str,
        user_id: str = "usr_alex_chen",
        data_scope: str = "auto"
    ) -> Dict[str, Any]:
        # 1. Retrieve authoritative deterministic analytics, transaction summary, and savings intelligence
        metrics = self.analytics.get_user_dashboard_metrics(user_id=user_id, data_scope=data_scope)
        facts = self.analytics.get_subscription_audit_facts(user_id=user_id)
        tx_summary = global_transaction_service.get_financial_summary(user_id=user_id, data_scope=data_scope)
        savings_dash = global_savings_service.get_savings_dashboard(user_id=user_id, data_scope=data_scope)

        metrics["subscription_audit_facts"] = facts
        metrics["tx_summary"] = tx_summary
        metrics["authoritative_savings"] = savings_dash["summary"]
        metrics["authoritative_recommendations"] = savings_dash["ranked_recommendations"]

        # 2. Retrieve active scenario context if relevant
        scenario = self.dataset_mgr.load_scenario(self.dataset_mgr.active_scenario_id)
        scenario_context = scenario.model_dump() if scenario else None

        # 3. Process via 7-stage Knowledge-First pipeline
        result = await self.orchestrator.process_question(
            prompt=user_prompt,
            user_metrics=metrics,
            scenario_context=scenario_context
        )

        return {
            "prompt": user_prompt,
            "user_id": user_id,
            "active_data_scope": tx_summary["active_data_scope"],
            "ai_response": result,
            "metrics_snapshot": {
                "active_data_scope": tx_summary["active_data_scope"],
                "monthly_income": tx_summary["total_income"],
                "monthly_expenses": tx_summary["total_expenses"],
                "net_cash_flow": tx_summary["remaining_available_money"],
                "potential_monthly_savings": savings_dash["summary"]["potential_monthly_savings"],
                "potential_annual_savings": savings_dash["summary"]["potential_annual_savings"],
                "total_subscription_cost": tx_summary["recurring_monthly_expenses"],
                "total_subscriptions": len(metrics.get("recurring_payments", [])) if tx_summary["active_data_scope"] == "demo" else len(tx_summary.get("savings_opportunities", []))
            }
        }

    def get_subscription_audit(self, user_id: str = "usr_alex_chen") -> Dict[str, Any]:
        """Returns verified deterministic facts and telemetry for all active subscription commitments."""
        return self.analytics.get_subscription_audit_facts(user_id=user_id)

global_financial_guardian = FinancialGuardianAgent()

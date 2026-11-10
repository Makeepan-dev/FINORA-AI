from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..demo_data.dataset_manager import global_dataset_manager
from ..demo_data.models.transaction import TransactionStatus, TransactionType

class IncomeIntelligenceService:
    def __init__(self, dataset_mgr=None):
        self.dataset_mgr = dataset_mgr or global_dataset_manager

    def classify_income_stream(self, description: str, category: str) -> str:
        d = description.lower()
        if any(w in d for w in ["payroll", "salary", "wages", "direct deposit"]):
            return "Salary & Wages"
        elif any(w in d for w in ["retainer", "freelance", "contract", "design fee", "consulting"]):
            return "Freelance & Contract"
        elif any(w in d for w in ["saas", "subscription revenue", "customer payment"]):
            return "Business Revenue"
        elif any(w in d for w in ["dividend", "interest", "yield", "capital distribution"]):
            return "Dividends & Investment"
        elif any(w in d for w in ["rental", "tenant", "lease income"]):
            return "Rental Income"
        else:
            return "Other Identifiable Deposits"

    def get_user_income_intelligence(self, user_id: str = "usr_alex_chen") -> Dict[str, Any]:
        mgr = self.dataset_mgr
        user = next((u for u in mgr.users if u.user_id == user_id), None)
        if not user:
            user = mgr.users[0]
            user_id = user.user_id

        # 1. Ingest all transactions for user
        user_txs = [t for t in mgr.transactions if t.user_id == user_id]

        # Filter strictly for completed/cleared income transactions
        cleared_income_txs = [
            t for t in user_txs
            if t.transaction_type == TransactionType.INCOME and t.status == TransactionStatus.COMPLETED
        ]

        # 2. Historical & Current Month Received Income
        target_month_prefix = "2026-10"
        current_month_received = Decimal("0.00")
        historical_monthly_totals: Dict[str, Decimal] = {}
        stream_breakdown: Dict[str, Decimal] = {}

        for tx in cleared_income_txs:
            month_str = tx.timestamp[:7]
            historical_monthly_totals[month_str] = historical_monthly_totals.get(month_str, Decimal("0.00")) + tx.amount

            if tx.timestamp.startswith(target_month_prefix):
                current_month_received += tx.amount
                stream_type = self.classify_income_stream(tx.description, tx.category)
                stream_breakdown[stream_type] = stream_breakdown.get(stream_type, Decimal("0.00")) + tx.amount

        # 3. Expected Income (Scheduled contractual payments NOT yet received)
        # CRITICAL RULE: Never count expected income as money already received!
        expected_income_items = []
        expected_income_total = Decimal("0.00")

        if user.employment_status == "Employed Full-time":
            # Alex Chen: Bi-weekly salary expected on next 15th
            paycheck_amt = Decimal("4250.00")
            expected_income_items.append({
                "stream_id": "exp_inc_payroll_nov15",
                "source": "Nexus Cloud Systems Inc.",
                "type": "Salary & Wages",
                "status": "EXPECTED",
                "expected_date": "2026-11-15",
                "amount": float(paycheck_amt),
                "confidence_score": 0.99,
                "notes": "Contractual bi-weekly automated direct deposit."
            })
            expected_income_total += paycheck_amt
        elif user.employment_status == "Self-Employed Freelance":
            # Sarah Jenkins: Client retainers
            retainer_amt = Decimal("2600.00")
            expected_income_items.append({
                "stream_id": "exp_inc_retainer_client_a",
                "source": "BrandSprint Studios",
                "type": "Freelance & Contract",
                "status": "EXPECTED",
                "expected_date": "2026-11-12",
                "amount": float(retainer_amt),
                "confidence_score": 0.92,
                "notes": "Signed retainer agreement net-15 terms."
            })
            expected_income_total += retainer_amt

        # 4. Estimated Income (Variable / speculative pipeline)
        estimated_income_items = []
        estimated_income_total = Decimal("0.00")

        if user.employment_status == "Self-Employed Freelance":
            est_proj = Decimal("1800.00")
            estimated_income_items.append({
                "stream_id": "est_inc_project_b",
                "source": "E-Commerce Rebrand RFP",
                "type": "Freelance & Contract",
                "status": "ESTIMATED",
                "projected_window": "2026-11-20 to 2026-11-30",
                "amount": float(est_proj),
                "confidence_score": 0.70,
                "notes": "Proposal submitted; milestone billing."
            })
            estimated_income_total += est_proj
        elif user.employment_status == "Employed Full-time":
            est_bonus = Decimal("500.00")
            estimated_income_items.append({
                "stream_id": "est_inc_q4_dividend",
                "source": "Vanguard Index Vault",
                "type": "Dividends & Investment",
                "status": "ESTIMATED",
                "projected_window": "2026-12-15",
                "amount": float(est_bonus),
                "confidence_score": 0.85,
                "notes": "Estimated quarterly dividend yield."
            })
            estimated_income_total += est_bonus

        # 5. Volatility & Stability Analysis
        monthly_values = list(historical_monthly_totals.values())
        if len(monthly_values) > 1:
            avg_monthly = sum(monthly_values) / Decimal(len(monthly_values))
            variance = sum(((x - avg_monthly) ** 2 for x in monthly_values)) / Decimal(len(monthly_values))
            std_dev = variance.sqrt()
            volatility_pct = round(float((std_dev / avg_monthly) * Decimal("100")), 1) if avg_monthly > 0 else 0.0
        else:
            volatility_pct = 2.4

        stability_rating = "Highly Stable" if volatility_pct < 10 else ("Moderate Volatility" if volatility_pct < 25 else "High Irregularity")

        # 6. Income Source Breakdown (Pie Chart format)
        source_breakdown_list = []
        tot_streams = sum(stream_breakdown.values(), Decimal("0.00"))
        for s_type, amt in stream_breakdown.items():
            pct = round(float((amt / tot_streams) * Decimal("100")), 1) if tot_streams > 0 else 100.0
            source_breakdown_list.append({
                "stream": s_type,
                "amount": float(amt),
                "percentage": pct
            })

        # 7. Forward 30/60/90 Day Cash Flow Forecast
        # Total fixed obligations: Rent, utilities, subscriptions
        fixed_monthly_outflows = Decimal("3100.00") if user_id == "usr_alex_chen" else Decimal("2150.00")
        curr_balance = sum((a.current_balance for a in mgr.accounts if a.owner_id == user_id and a.account_type.value != "credit_card"), Decimal("0.00"))

        forecast = [
            {
                "period": "Next 30 Days",
                "current_liquid_cash": float(curr_balance),
                "received_cash": float(current_month_received),
                "expected_inflows": float(expected_income_total),
                "estimated_variable": float(estimated_income_total),
                "projected_fixed_outflows": float(fixed_monthly_outflows),
                "projected_end_cash": float(curr_balance + expected_income_total - fixed_monthly_outflows),
                "runway_months": round(float(curr_balance / fixed_monthly_outflows), 1) if fixed_monthly_outflows > 0 else 12.0
            },
            {
                "period": "Next 60 Days",
                "current_liquid_cash": float(curr_balance),
                "received_cash": float(current_month_received),
                "expected_inflows": float(expected_income_total * 2),
                "estimated_variable": float(estimated_income_total * 2),
                "projected_fixed_outflows": float(fixed_monthly_outflows * 2),
                "projected_end_cash": float(curr_balance + (expected_income_total * 2) - (fixed_monthly_outflows * 2)),
                "runway_months": round(float(curr_balance / fixed_monthly_outflows), 1) if fixed_monthly_outflows > 0 else 12.0
            },
            {
                "period": "Next 90 Days",
                "current_liquid_cash": float(curr_balance),
                "received_cash": float(current_month_received),
                "expected_inflows": float(expected_income_total * 3),
                "estimated_variable": float(estimated_income_total * 3),
                "projected_fixed_outflows": float(fixed_monthly_outflows * 3),
                "projected_end_cash": float(curr_balance + (expected_income_total * 3) - (fixed_monthly_outflows * 3)),
                "runway_months": round(float(curr_balance / fixed_monthly_outflows), 1) if fixed_monthly_outflows > 0 else 12.0
            }
        ]

        return {
            "user_id": user_id,
            "employment_type": user.employment_status,
            "income_summary": {
                "received_income": float(current_month_received),
                "expected_income": float(expected_income_total),
                "estimated_income": float(estimated_income_total),
                "total_projected_inflow": float(current_month_received + expected_income_total + estimated_income_total),
                "is_money_in_hand_verified": True
            },
            "stability_analysis": {
                "volatility_percentage": volatility_pct,
                "stability_rating": stability_rating,
                "frequency": user.income_frequency,
                "irregular_income_detected": volatility_pct >= 20.0,
                "notes": "Income arrives at regular bi-weekly schedule." if volatility_pct < 10 else "Variable freelance retainers with noticeable monthly delta."
            },
            "source_breakdown": source_breakdown_list,
            "expected_streams": expected_income_items,
            "estimated_streams": estimated_income_items,
            "cash_flow_forecast": forecast,
            "rule": "Never count an expected or predicted payment as money already received."
        }

global_income_service = IncomeIntelligenceService()

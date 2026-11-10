from decimal import Decimal
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class TestScenario(BaseModel):
    scenario_id: str
    title: str
    description: str
    target_user_or_business_id: str
    triggering_prompt: str
    expected_calculation_results: Dict[str, Any]
    expected_findings: List[str]
    expected_warnings: List[str] = Field(default_factory=list)
    expected_permissions_or_approvals: List[str] = Field(default_factory=list)
    validation_rules: List[str] = Field(default_factory=list)

def get_predefined_scenarios() -> List[TestScenario]:
    return [
        TestScenario(
            scenario_id="scen_01_normal_spending",
            title="Normal Monthly Spending",
            description="Baseline consistent monthly spending pattern within allocated budget categories.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Analyze my spending pattern for the past month.",
            expected_calculation_results={"total_spend_estimate": "3800.00", "budget_status": "under_budget"},
            expected_findings=["Spending is within healthy parameters across all core categories", "Positive cash flow margin maintained"],
            expected_warnings=[],
            expected_permissions_or_approvals=[],
            validation_rules=["Monthly income exceeds monthly expenses", "No critical alerts triggered"]
        ),
        TestScenario(
            scenario_id="scen_02_income_reduction",
            title="Income Reduction Assessment",
            description="Simulation of client retainer drop or temporary salary furlough requiring cash flow adjustment.",
            target_user_or_business_id="usr_sarah_jenkins",
            triggering_prompt="What happens to my runway if my freelance income drops by 30%?",
            expected_calculation_results={"projected_monthly_income": "3640.00", "fixed_expenses": "2120.00", "remaining_cushion": "1520.00"},
            expected_findings=["Discretionary grocery and restaurant budgets must be tightened by $300/mo", "Emergency tax buffer covers up to 4.2 months"],
            expected_warnings=["Cash surplus diminishes significantly; pause optional equipment purchases"],
            validation_rules=["Runway calculation remains positive with reduced income"]
        ),
        TestScenario(
            scenario_id="scen_03_spending_spike",
            title="Unexpected Spending Increase",
            description="Detecting a single-month surge in hardware/electronics purchases above historical mean.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Why did my expenses increase in September?",
            expected_calculation_results={"category_surge": "electronics", "surge_amount": "480.00"},
            expected_findings=["Identified major one-time expense at Timber & Stone Hardware ($480.00)", "Exceeded monthly electronics budget of $500 when combined with accessories"],
            expected_warnings=["Electronics category reached 115% of monthly budget in September"],
            validation_rules=["Anomaly flagged correctly on transaction txn_alex_volt_desk_sep"]
        ),
        TestScenario(
            scenario_id="scen_04_grocery_overspend",
            title="Overspending on Groceries",
            description="Recurring monthly grocery purchases consistently surpassing the $450 limit.",
            target_user_or_business_id="usr_sarah_jenkins",
            triggering_prompt="Am I overspending on groceries?",
            expected_calculation_results={"grocery_budget": "450.00", "recent_average_grocery": "590.00", "variance": "+140.00"},
            expected_findings=["Monthly grocery expenses averaged $590, exceeding the $450 budget by $140 (+31%)", "Frequent purchases at Fresh Harvest Organic Market driving variance"],
            expected_warnings=["Grocery category in persistent warning state (>130% limit)"],
            validation_rules=["Budget progress calculation indicates overspend"]
        ),
        TestScenario(
            scenario_id="scen_05_multiple_subscriptions",
            title="Multiple Recurring Subscriptions",
            description="Cataloguing and auditing 6+ active digital subscriptions across entertainment, tools and fitness.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Find all my active subscriptions and their total monthly cost.",
            expected_calculation_results={"total_subscription_count": 7, "total_monthly_cost": "291.97"},
            expected_findings=["7 active subscriptions detected across checking, credit card and PayPal", "Total monthly commitment is $291.97"],
            expected_warnings=["Subscription total represents 7.5% of total discretionary budget"],
            validation_rules=["All 7 subscriptions retrieved with valid merchant links"]
        ),
        TestScenario(
            scenario_id="scen_06_gym_confirmed_low_attendance",
            title="Gym Subscription with Confirmed Low Attendance",
            description="Turnstile RFID evidence confirms only 1 visit in 90 days for a $120/mo gym pass.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Which subscriptions can I optimize or cancel?",
            expected_calculation_results={"gym_monthly_cost": "120.00", "recorded_visits_90d": 1, "potential_annual_savings": "1440.00"},
            expected_findings=["Apex Athletic Club ($120/mo) shows verified turnstile RFID evidence of only 1 visit in 90 days", "Cost per visit equates to $360.00"],
            expected_warnings=["High potential savings opportunity: Cancel or pause to save $120.00/month"],
            validation_rules=["Evidence state CONFIRMED links to turnstile log", "Potential savings calculated deterministically"]
        ),
        TestScenario(
            scenario_id="scen_07_gym_missing_evidence",
            title="Gym Subscription with Missing Attendance Evidence",
            description="CRITICAL REASONING: No turnstile API telemetry available; system must NOT assume zero usage.",
            target_user_or_business_id="usr_marcus_vance",
            triggering_prompt="Should I cancel my Apex Athletic membership?",
            expected_calculation_results={"membership_cost": "180.00", "attendance_telemetry_status": "MISSING"},
            expected_findings=["Attendance data is unavailable from Apex Athletic partner telemetry", "FINORA cannot verify your facility usage frequency"],
            expected_warnings=["Never assume missing evidence proves inactivity. Inquire with user first."],
            validation_rules=["System distinguishes MISSING telemetry from zero attendance"]
        ),
        TestScenario(
            scenario_id="scen_08_cheaper_alternative",
            title="Cheaper Alternative Recommendation",
            description="Recommending cost-effective substitution for unused high-tier developer API subscription.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="How can I reduce my software and cloud expenses?",
            expected_calculation_results={"current_ai_synth_tier": "35.00", "suggested_pay_as_you_go_estimate": "5.00", "monthly_savings": "30.00"},
            expected_findings=["Cognition Engine Pro ($35/mo) has zero consumed tokens over 45 days", "Switching to pay-as-you-go or free tier saves $30-$35/mo"],
            expected_warnings=[],
            validation_rules=["Suggested action grounded in real activity telemetry"]
        ),
        TestScenario(
            scenario_id="scen_09_duplicate_transaction",
            title="Duplicate-Looking Transaction Analysis",
            description="Investigating two identical charges on the same date to determine if fraudulent or legitimate.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Why was I charged twice by GitForge on October 14?",
            expected_calculation_results={"charge_1": "49.00", "charge_2": "49.00", "time_delta_seconds": 60},
            expected_findings=["Two separate transactions of $49.00 detected at GitForge within 1 minute", "Descriptions verify two distinct order numbers: Order #GF-9101 and #GF-9102 (Seat A and Seat B)"],
            expected_warnings=["Classification: LEGITIMATE_REPEATED_CHARGE (False Positive for fraud)"],
            validation_rules=["System explains alternative explanation before escalating dispute"]
        ),
        TestScenario(
            scenario_id="scen_10_legitimate_repeated_charges",
            title="Legitimate Repeated Merchant Charges",
            description="Explaining consecutive weekly grocery or transit charges as routine recurring transactions.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Check why Fresh Harvest appears multiple times every week.",
            expected_calculation_results={"frequency": "weekly", "average_amount": "135.00"},
            expected_findings=["Transactions represent regular weekly grocery replenishments on consistent days", "No duplicate charges detected"],
            expected_warnings=[],
            validation_rules=["Classification: NORMAL_RECURRING_DISCRETIONARY"]
        ),
        TestScenario(
            scenario_id="scen_11_unusual_electronics_purchase",
            title="Unusual Electronics Purchase Investigation",
            description="Analyzing a sudden out-of-pattern hardware order.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Investigate unusual transactions in the electronics category.",
            expected_calculation_results={"unusual_transaction_id": "txn_alex_volt_desk_sep", "amount": "480.00"},
            expected_findings=["Transaction $480.00 at Timber & Stone Hardware flagged for deviation from monthly mean", "Carrier delivery evidence confirms delivery to user home address"],
            expected_warnings=["Legitimate user upgrade confirmed by shipping and delivery evidence"],
            validation_rules=["Links transaction to delivery confirmation evidence"]
        ),
        TestScenario(
            scenario_id="scen_12_failed_retry_sequence",
            title="Failed Transaction Followed by Retry",
            description="Network failure on PayPal purchase followed by successful retry 3 minutes later.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Did I get double-billed for the clean duster at Silicon Bay Electronics?",
            expected_calculation_results={"failed_txn_id": "txn_alex_fail_retry_1", "success_txn_id": "txn_alex_fail_retry_2", "net_balance_impact": "-39.99"},
            expected_findings=["First transaction failed due to network timeout and did not debit your account", "Second transaction succeeded; you were billed only once ($39.99)"],
            expected_warnings=["No double charge occurred; account balance reflects single successful debit"],
            validation_rules=["Failed transaction has status FAILED and does not affect account balance"]
        ),
        TestScenario(
            scenario_id="scen_13_delayed_refund",
            title="Delayed Refund Resolution",
            description="Tracking clothing return where merchant refund took 23 days to settle.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Where is my refund for the Nordic Weave return?",
            expected_calculation_results={"return_date": "2026-10-02", "refund_posted_date": "2026-10-25", "refund_amount": "145.00", "status": "COMPLETED"},
            expected_findings=["Original purchase of $145.00 was made on October 2", "Refund of $145.00 posted on October 25 (23 days elapsed) and is fully credited"],
            expected_warnings=["Refund delay exceeded standard 14-day window but is now settled"],
            validation_rules=["Original transaction status REFUNDED, related refund transaction COMPLETED"]
        ),
        TestScenario(
            scenario_id="scen_14_unpaid_customer_invoice",
            title="Unpaid Customer Invoice Follow-up",
            description="B2B SaaS receivable pending payment from customer.",
            target_user_or_business_id="biz_aurora_tech",
            triggering_prompt="List all outstanding receivables due this month.",
            expected_calculation_results={"invoice_id": "inv_aurora_2026_02", "customer": "Delta Health Analytics", "amount_due": "8500.00", "status": "UNPAID"},
            expected_findings=["Invoice inv_aurora_2026_02 ($8,500.00) issued on Oct 15 is due on Nov 15", "Customer has not yet submitted payment"],
            expected_warnings=["Follow up with Delta Health procurement before Nov 15 due date"],
            validation_rules=["Invoice status is UNPAID, balance due matches total"]
        ),
        TestScenario(
            scenario_id="scen_15_overdue_supplier_payment",
            title="Overdue Customer Receivable & Overdue Payables",
            description="Beacon Media invoice overdue with partial payment.",
            target_user_or_business_id="biz_aurora_tech",
            triggering_prompt="Check overdue accounts receivable and cash impact.",
            expected_calculation_results={"invoice_id": "inv_aurora_2026_03", "customer": "Beacon Media Digital", "amount_overdue": "3100.00", "days_past_due": 39},
            expected_findings=["Invoice inv_aurora_2026_03 was due Oct 1 ($6,200 total, $3,100 paid)", "Remaining balance $3,100 is 39 days overdue"],
            expected_warnings=["Issue payment reminder to Beacon Media accounting"],
            validation_rules=["Calculates overdue days and partial payment accurately"]
        ),
        TestScenario(
            scenario_id="scen_16_business_cashflow_shortage",
            title="Business Cash-Flow Shortage Simulation",
            description="Consulting firm facing payroll obligations during delayed client invoice collection.",
            target_user_or_business_id="biz_nexus_consulting",
            triggering_prompt="Evaluate Nexus Advisory cash flow for the upcoming payroll cycle.",
            expected_calculation_results={"operating_cash": "34000.00", "monthly_payroll": "18000.00", "overdue_receivables": "14000.00"},
            expected_findings=["Current cash of $34,000 covers current month payroll ($18,000)", "Overdue invoice from Pinnacle Logistics ($14,000) creates pressure for next month"],
            expected_warnings=["Accelerate collection of Pinnacle Logistics receivable ($14,000)"],
            validation_rules=["Cash runway calculated accurately against fixed payroll"]
        ),
        TestScenario(
            scenario_id="scen_17_profitable_business_month",
            title="Profitable Business Month Analysis",
            description="Aurora Cloud Technologies generating $45,000 MRR against $40,000 expenses.",
            target_user_or_business_id="biz_aurora_tech",
            triggering_prompt="Calculate net profit margin for Aurora Cloud Technologies.",
            expected_calculation_results={"revenue": "45000.00", "payroll": "28000.00", "operating_costs": "12000.00", "net_profit": "5000.00", "margin_percent": "11.1"},
            expected_findings=["Monthly recurring revenue of $45,000 generates $5,000 net monthly profit (11.1% margin)", "Operating treasury stands at $68,000 with healthy 5.6 month runway"],
            expected_warnings=[],
            validation_rules=["Net profit reconciles with revenue minus expenses"]
        ),
        TestScenario(
            scenario_id="scen_18_shopping_exceeds_budget",
            title="Shopping Request Exceeding Budget",
            description="User shopping for $399.99 4K monitor when remaining monthly electronics budget is $120.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Can I afford the UltraView 27-inch 4K HDR Monitor this month?",
            expected_calculation_results={"product_total_cost": "414.99", "remaining_category_budget": "120.00", "budget_overage": "294.99"},
            expected_findings=["UltraView 27-inch costs $414.99 ($399.99 + $15.00 shipping)", "Your remaining electronics budget is $120.00, resulting in a $294.99 overage"],
            expected_warnings=["Purchase exceeds monthly electronics budget. Suggest deferring to next month or selecting portable screen."],
            expected_permissions_or_approvals=["User must explicitly override budget limit to proceed"],
            validation_rules=["Total cost includes product price and shipping"]
        ),
        TestScenario(
            scenario_id="scen_19_shopping_within_budget",
            title="Shopping Request Within Budget",
            description="User shopping for ergonomic wireless keyboard ($119.00) with sufficient budget headroom.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Find a mechanical keyboard within my remaining budget.",
            expected_calculation_results={"selected_product": "VoltKey Wireless Dual-Mode", "total_cost": "119.00", "remaining_budget_after": "1.00"},
            expected_findings=["VoltKey Dual-Mode Mechanical Keyboard costs $119.00 (free shipping)", "Fits within your remaining $120.00 electronics budget"],
            expected_warnings=[],
            expected_permissions_or_approvals=["Ready for PayPal checkout checkout approval"],
            validation_rules=["Affordability check passes, returns True"]
        ),
        TestScenario(
            scenario_id="scen_20_payment_authorization_limit",
            title="Payment Request Exceeding User Authorization Policy",
            description="AI payment network detects order amount exceeding $250 transaction limit policy.",
            target_user_or_business_id="usr_alex_chen",
            triggering_prompt="Authorize payment for the $414.99 monitor order.",
            expected_calculation_results={"order_amount": "414.99", "policy_limit": "250.00", "exceeds_limit": True},
            expected_findings=["Order total of $414.99 exceeds the preset safety policy limit of $250.00 per transaction", "Autonomous payment execution blocked by security policy"],
            expected_warnings=["Mandatory elevated user approval required. AI cannot auto-capture this order."],
            expected_permissions_or_approvals=["Direct 2FA or explicit UI review confirmation required"],
            validation_rules=["Payment request state remains REQUESTED until user explicit approval"]
        ),
    ]

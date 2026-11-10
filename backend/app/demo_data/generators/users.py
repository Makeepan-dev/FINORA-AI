from decimal import Decimal
from typing import List
from ..models.user import SyntheticUser, FinancialGoal, BudgetLimit, RiskPreference

def generate_users() -> List[SyntheticUser]:
    users = [
        # User 1: Alex Chen - Senior Software Engineer
        SyntheticUser(
            user_id="usr_alex_chen",
            full_name="Alex Chen",
            email="alex.chen.demo@finora-synthetic.example",
            country="US",
            currency="USD",
            employment_status="Employed Full-time",
            employer_name="Nexus Cloud Systems Inc.",
            monthly_income=Decimal("8500.00"),
            income_frequency="bi-weekly",
            financial_goals=[
                FinancialGoal(
                    goal_id="goal_alex_emergency",
                    name="6-Month Emergency Fund",
                    target_amount=Decimal("30000.00"),
                    current_amount=Decimal("22500.00"),
                    target_date="2027-06-30",
                    category="savings"
                ),
                FinancialGoal(
                    goal_id="goal_alex_workspace",
                    name="Ergonomic Studio Setup",
                    target_amount=Decimal("2500.00"),
                    current_amount=Decimal("1800.00"),
                    target_date="2026-12-15",
                    category="equipment"
                )
            ],
            monthly_budgets=[
                BudgetLimit(category="housing", monthly_limit=Decimal("2400.00"), alert_threshold_percent=90),
                BudgetLimit(category="groceries", monthly_limit=Decimal("650.00"), alert_threshold_percent=85),
                BudgetLimit(category="restaurants", monthly_limit=Decimal("450.00"), alert_threshold_percent=80),
                BudgetLimit(category="subscriptions", monthly_limit=Decimal("200.00"), alert_threshold_percent=85),
                BudgetLimit(category="electronics", monthly_limit=Decimal("500.00"), alert_threshold_percent=80),
                BudgetLimit(category="utilities", monthly_limit=Decimal("280.00"), alert_threshold_percent=90),
                BudgetLimit(category="transportation", monthly_limit=Decimal("250.00"), alert_threshold_percent=80),
            ],
            risk_preference=RiskPreference.MODERATE,
            financial_obligations=[
                {"type": "lease", "entity": "Metropolitan Lofts", "monthly_amount": "2400.00", "due_day": "1st"},
                {"type": "student_loan", "entity": "Federal Student Aid Demo", "monthly_amount": "320.00", "due_day": "15th"}
            ],
            notes="Tech-focused professional with high recurring digital subscriptions ($220+/mo), gym membership with verified low usage, exploring desk upgrades."
        ),

        # User 2: Sarah Jenkins - Freelance Product Designer
        SyntheticUser(
            user_id="usr_sarah_jenkins",
            full_name="Sarah Jenkins",
            email="sarah.jenkins.design@finora-synthetic.example",
            country="US",
            currency="USD",
            employment_status="Self-Employed Freelance",
            employer_name="Jenkins Design Studio LLC",
            monthly_income=Decimal("5200.00"),
            income_frequency="variable",
            financial_goals=[
                FinancialGoal(
                    goal_id="goal_sarah_tax_buffer",
                    name="Quarterly Estimated Tax Reserve",
                    target_amount=Decimal("8000.00"),
                    current_amount=Decimal("6400.00"),
                    target_date="2027-04-15",
                    category="tax_reserve"
                ),
                FinancialGoal(
                    goal_id="goal_sarah_camera",
                    name="Studio Mirrorless Camera Gear",
                    target_amount=Decimal("1800.00"),
                    current_amount=Decimal("950.00"),
                    target_date="2027-02-28",
                    category="creative_tools"
                )
            ],
            monthly_budgets=[
                BudgetLimit(category="housing", monthly_limit=Decimal("1700.00"), alert_threshold_percent=90),
                BudgetLimit(category="groceries", monthly_limit=Decimal("450.00"), alert_threshold_percent=80),
                BudgetLimit(category="software", monthly_limit=Decimal("180.00"), alert_threshold_percent=85),
                BudgetLimit(category="restaurants", monthly_limit=Decimal("300.00"), alert_threshold_percent=80),
                BudgetLimit(category="utilities", monthly_limit=Decimal("200.00"), alert_threshold_percent=85),
                BudgetLimit(category="transportation", monthly_limit=Decimal("180.00"), alert_threshold_percent=80),
            ],
            risk_preference=RiskPreference.CONSERVATIVE,
            financial_obligations=[
                {"type": "rent", "entity": "Canyon Creek Apartments", "monthly_amount": "1700.00", "due_day": "1st"}
            ],
            notes="Budget-conscious designer managing variable client retainers; experiencing grocery overspending and seeking subscription audits."
        ),

        # User 3: Marcus Vance - VP of Growth Marketing
        SyntheticUser(
            user_id="usr_marcus_vance",
            full_name="Marcus Vance",
            email="marcus.vance.exec@finora-synthetic.example",
            country="US",
            currency="USD",
            employment_status="Employed Executive",
            employer_name="Vanguard Scale Partners",
            monthly_income=Decimal("11500.00"),
            income_frequency="monthly",
            financial_goals=[
                FinancialGoal(
                    goal_id="goal_marcus_realestate",
                    name="Commercial Property Down Payment",
                    target_amount=Decimal("75000.00"),
                    current_amount=Decimal("52000.00"),
                    target_date="2027-11-30",
                    category="real_estate"
                ),
                FinancialGoal(
                    goal_id="goal_marcus_travel",
                    name="Global Sabbatical Fund",
                    target_amount=Decimal("12000.00"),
                    current_amount=Decimal("8900.00"),
                    target_date="2027-08-31",
                    category="travel"
                )
            ],
            monthly_budgets=[
                BudgetLimit(category="housing", monthly_limit=Decimal("3400.00"), alert_threshold_percent=90),
                BudgetLimit(category="travel", monthly_limit=Decimal("1200.00"), alert_threshold_percent=85),
                BudgetLimit(category="restaurants", monthly_limit=Decimal("850.00"), alert_threshold_percent=85),
                BudgetLimit(category="groceries", monthly_limit=Decimal("700.00"), alert_threshold_percent=80),
                BudgetLimit(category="subscriptions", monthly_limit=Decimal("350.00"), alert_threshold_percent=85),
                BudgetLimit(category="fitness", monthly_limit=Decimal("250.00"), alert_threshold_percent=85),
            ],
            risk_preference=RiskPreference.GROWTH,
            financial_obligations=[
                {"type": "mortgage", "entity": "Pacific Summit Bancorp Demo", "monthly_amount": "3400.00", "due_day": "1st"},
                {"type": "car_lease", "entity": "VoltPath Luxury Fleet Demo", "monthly_amount": "650.00", "due_day": "10th"}
            ],
            notes="High income executive with frequent flight travel, multiple corporate and personal cards, luxury gym with missing attendance telemetry."
        )
    ]
    return users

from typing import List
from .base import KnowledgeEntry, KnowledgeDomain, VerificationStatus

def get_personal_finance_entries() -> List[KnowledgeEntry]:
    return [
        KnowledgeEntry(
            knowledge_id="kn_pf_001_cash_flow",
            domain=KnowledgeDomain.PERSONAL_FINANCE,
            topic="cash_flow_margin",
            title="Net Cash Flow & Cash Reserve Adequacy",
            definition="Net Cash Flow is the difference between total verified inflows and total verified outflows over a defined period (e.g., monthly). Liquid cash reserves must cover core essential expenses.",
            rules=[
                "Net Cash Flow = Inflows - Outflows.",
                "A sustainable financial profile maintains an emergency reserve covering 3 to 6 months of mandatory living expenses.",
                "Inflows must not count expected or pending payments as liquid cash until settlement."
            ],
            required_inputs=["monthly_income", "monthly_expenses", "liquid_cash_balance"],
            calculation_procedure="net_cash_flow = income - expenses; reserve_months = liquid_balance / mandatory_expenses",
            output_fields=["net_cash_flow", "reserve_adequacy_months", "burn_rate"],
            authority_source="CFP Board Financial Planning Standards & Basel III Liquidity Principles",
            verification_status=VerificationStatus.VERIFIED_CANONICAL,
            confidence_score=1.0,
            limitations="Cash reserves outside connected accounts require manual disclosure."
        ),
        KnowledgeEntry(
            knowledge_id="kn_pf_002_debt_amortization",
            domain=KnowledgeDomain.PERSONAL_FINANCE,
            topic="debt_amortization",
            title="Fixed-Rate Loan Amortization & Repayment",
            definition="Amortization is the process of spreading out a loan into a series of equal periodic payments. Each payment is split between interest on the remaining principal and principal reduction.",
            rules=[
                "Early monthly payments are interest-heavy; later payments become principal-heavy.",
                "Additional principal payments directly reduce the compounding interest balance and tenure.",
                "Formula: PMT = P * [r(1 + r)^n] / [(1 + r)^n - 1]."
            ],
            required_inputs=["principal", "annual_interest_rate", "tenure_months"],
            calculation_procedure="calculate_loan_amortization(principal, rate, tenure)",
            output_fields=["monthly_payment", "total_interest", "total_payment"],
            authority_source="Federal Reserve Regulation Z (Truth in Lending)",
            verification_status=VerificationStatus.REGULATORY_STANDARD,
            confidence_score=1.0,
            limitations="Assumes fixed interest rate; variable rate loans require rate adjustment modeling."
        ),
        KnowledgeEntry(
            knowledge_id="kn_pf_003_savings_rate",
            domain=KnowledgeDomain.PERSONAL_FINANCE,
            topic="savings_rate",
            title="Personal Savings Rate & Discretionary Surplus",
            definition="The percentage of personal disposable income allocated to savings, investments, or debt reduction rather than consumption.",
            rules=[
                "Savings Rate % = (Income - Expenses) / Income * 100.",
                "Target savings benchmark: 20% of net income allocated to savings and investments (50/30/20 rule)."
            ],
            required_inputs=["total_income", "total_expenses"],
            calculation_procedure="savings_rate = (income - expenses) / income * 100",
            output_fields=["savings_rate_percent", "monthly_surplus"],
            authority_source="Bureau of Economic Analysis (BEA) Personal Savings Methodology",
            verification_status=VerificationStatus.VERIFIED_CANONICAL,
            confidence_score=1.0,
            limitations="Taxes withheld at source must be distinguished from gross earnings."
        ),
        KnowledgeEntry(
            knowledge_id="kn_pf_004_net_worth",
            domain=KnowledgeDomain.PERSONAL_FINANCE,
            topic="net_worth",
            title="Comprehensive Personal Net Worth",
            definition="Total Assets minus Total Liabilities. Quantifies economic solvency and debt vulnerability.",
            rules=[
                "Net Worth = Sum(Assets) - Sum(Liabilities).",
                "Assets include cash, investments, real estate, and titled property.",
                "Liabilities include credit cards, mortgages, auto loans, and unpaid invoices."
            ],
            required_inputs=["total_assets", "total_liabilities"],
            calculation_procedure="net_worth = assets - liabilities",
            output_fields=["net_worth", "debt_to_asset_ratio"],
            authority_source="Federal Reserve Survey of Consumer Finances",
            verification_status=VerificationStatus.VERIFIED_CANONICAL,
            confidence_score=1.0,
            limitations="Illiquid private asset valuations are estimated unless appraised."
        )
    ]

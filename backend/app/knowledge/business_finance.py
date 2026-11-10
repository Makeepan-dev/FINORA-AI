from typing import List
from .base import KnowledgeEntry, KnowledgeDomain, VerificationStatus

def get_business_finance_entries() -> List[KnowledgeEntry]:
    return [
        KnowledgeEntry(
            knowledge_id="kn_biz_001_break_even",
            domain=KnowledgeDomain.BUSINESS_FINANCE,
            topic="break_even_analysis",
            title="Break-Even Volume & Revenue",
            definition="The point at which total business revenue equals total business costs, resulting in zero net profit or loss.",
            rules=[
                "Contribution Margin Per Unit (CM) = Price - Variable Cost Per Unit.",
                "Break-Even Units = Fixed Costs / CM.",
                "Break-Even Revenue = Break-Even Units * Price.",
                "If variable cost exceeds or equals price, product unit economics are unviable."
            ],
            required_inputs=["fixed_costs", "unit_price", "unit_variable_cost"],
            calculation_procedure="calculate_break_even(fixed_costs, unit_price, unit_variable_cost)",
            output_fields=["break_even_units", "break_even_revenue", "contribution_margin"],
            authority_source="Chartered Institute of Management Accountants (CIMA) Cost Accounting Standards",
            verification_status=VerificationStatus.VERIFIED_CANONICAL,
            confidence_score=1.0,
            limitations="Assumes constant unit price and linear variable cost behavior."
        ),
        KnowledgeEntry(
            knowledge_id="kn_biz_002_profit_margins",
            domain=KnowledgeDomain.BUSINESS_FINANCE,
            topic="profit_margins",
            title="Gross Margin, Operating Margin & Net Profit Margin",
            definition="Key profitability ratios measuring what percentage of top-line revenue is retained across production, operating, and after-tax levels.",
            rules=[
                "Gross Profit = Revenue - Cost of Goods Sold (COGS).",
                "Gross Margin % = Gross Profit / Revenue * 100.",
                "Operating Profit = Gross Profit - Operating Expenses (OPEX).",
                "Net Profit = Operating Profit - Taxes - Interest.",
                "Net Margin % = Net Profit / Revenue * 100."
            ],
            required_inputs=["revenue", "cogs", "operating_expenses", "taxes"],
            calculation_procedure="calculate_profit_margins(revenue, cogs, operating_expenses, tax_rate)",
            output_fields=["gross_margin_percent", "operating_margin_percent", "net_margin_percent"],
            authority_source="Financial Accounting Standards Board (FASB) ASC 220",
            verification_status=VerificationStatus.VERIFIED_CANONICAL,
            confidence_score=1.0,
            limitations="Non-recurring one-time charges should be isolated to assess underlying EBITDA."
        ),
        KnowledgeEntry(
            knowledge_id="kn_biz_003_working_capital",
            domain=KnowledgeDomain.BUSINESS_FINANCE,
            topic="working_capital",
            title="Working Capital & Liquidity Ratio",
            definition="Working capital represents the operating liquidity available to a business to finance day-to-day operations.",
            rules=[
                "Working Capital = Current Assets - Current Liabilities.",
                "Current Ratio = Current Assets / Current Liabilities (target benchmark 1.2 to 2.0).",
                "Accounts Receivable must factor in realistic default and aging allowances."
            ],
            required_inputs=["current_assets", "current_liabilities"],
            calculation_procedure="working_capital = current_assets - current_liabilities",
            output_fields=["working_capital", "current_ratio"],
            authority_source="Corporate Finance Institute (CFI) Working Capital Guidelines",
            verification_status=VerificationStatus.VERIFIED_CANONICAL,
            confidence_score=1.0,
            limitations="Inventory liquidity may differ from cash equivalents."
        )
    ]

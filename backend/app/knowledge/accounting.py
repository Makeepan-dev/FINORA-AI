from typing import List
from .base import KnowledgeEntry, KnowledgeDomain, VerificationStatus

def get_accounting_entries() -> List[KnowledgeEntry]:
    return [
        KnowledgeEntry(
            knowledge_id="kn_acc_001_double_entry",
            domain=KnowledgeDomain.ACCOUNTING,
            topic="double_entry_equation",
            title="Fundamental Accounting Equation & Double-Entry Principles",
            definition="The core foundation of accounting: Assets = Liabilities + Equity. Every financial event requires equal and offsetting debit and credit journal entries.",
            rules=[
                "Assets = Liabilities + Equity.",
                "Debits increase Assets and Expenses; Debits decrease Liabilities, Equity, and Revenue.",
                "Credits increase Liabilities, Equity, and Revenue; Credits decrease Assets and Expenses.",
                "Total Debits MUST equal Total Credits in every balanced journal entry."
            ],
            required_inputs=["debit_entries", "credit_entries"],
            calculation_procedure="sum(debits) == sum(credits)",
            output_fields=["trial_balance_status", "total_debits", "total_credits"],
            authority_source="US GAAP ASC 105 & IFRS Conceptual Framework for Financial Reporting",
            verification_status=VerificationStatus.REGULATORY_STANDARD,
            confidence_score=1.0,
            limitations="Single-entry transaction feeds require reconciliation rules to map to double-entry general ledger."
        ),
        KnowledgeEntry(
            knowledge_id="kn_acc_002_accrual_vs_cash",
            domain=KnowledgeDomain.ACCOUNTING,
            topic="accrual_accounting",
            title="Accrual Accounting vs. Cash Basis Accounting",
            definition="Under accrual accounting, revenues and expenses are recognized when earned or incurred, regardless of when cash changes hands.",
            rules=[
                "Revenue is recognized when performance obligations are satisfied, not upon cash receipt.",
                "Expenses are matched to the revenues they generate (Matching Principle).",
                "Unpaid issued invoices are recognized as Accounts Receivable (Assets).",
                "Unpaid received vendor bills are recognized as Accounts Payable (Liabilities)."
            ],
            required_inputs=["invoices_issued", "invoices_received", "cash_settlements"],
            calculation_procedure="accrual_revenue = sum(billed_invoices); cash_revenue = sum(settled_payments)",
            output_fields=["accrual_net_income", "cash_net_income", "timing_differences"],
            authority_source="FASB ASC 606 (Revenue from Contracts with Customers)",
            verification_status=VerificationStatus.REGULATORY_STANDARD,
            confidence_score=1.0,
            limitations="Small cash-basis sole proprietors may not maintain formal accrual ledgers."
        ),
        KnowledgeEntry(
            knowledge_id="kn_acc_003_depreciation",
            domain=KnowledgeDomain.ACCOUNTING,
            topic="depreciation_straight_line",
            title="Fixed Asset Depreciation & Cost Allocation",
            definition="The systematic allocation of the depreciable cost of a physical asset over its estimated useful economic lifespan.",
            rules=[
                "Annual Straight-Line Depreciation = (Cost - Salvage Value) / Useful Life.",
                "Depreciation is a non-cash expense that reduces taxable income.",
                "Accumulated Depreciation is a contra-asset account offsetting gross equipment book value."
            ],
            required_inputs=["asset_cost", "salvage_value", "useful_life_years"],
            calculation_procedure="calculate_depreciation_straight_line(asset_cost, salvage_value, useful_life_years)",
            output_fields=["annual_depreciation", "monthly_depreciation", "ending_book_value"],
            authority_source="IRS Publication 946 & FASB ASC 360 (Property, Plant, and Equipment)",
            verification_status=VerificationStatus.REGULATORY_STANDARD,
            confidence_score=1.0,
            limitations="Tax MACRS accelerated depreciation differs from financial statement straight-line rules."
        )
    ]

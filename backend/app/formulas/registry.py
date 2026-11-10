import inspect
from typing import Dict, Any, List, Optional, Callable
from .models import (
    FormulaDomain,
    FormulaStatus,
    FormulaEntry,
    InputVariableSpec,
    CalculationResult
)
from . import decimal_engine as eng

class FinancialFormulaRegistry:
    """
    Central Extensible Financial Formula, Algorithm & Model Registry for FINORA.
    Stores comprehensive metadata, input validation rules, and executable calculation bindings.
    """
    def __init__(self):
        self._entries: Dict[str, FormulaEntry] = {}
        self._executors: Dict[str, Callable[..., CalculationResult]] = {}
        self._populate_catalogue()

    def register(
        self,
        entry: FormulaEntry,
        executor: Optional[Callable[..., CalculationResult]] = None
    ) -> None:
        self._entries[entry.unique_id] = entry
        if executor:
            self._executors[entry.unique_id] = executor

    def get(self, formula_id: str) -> Optional[FormulaEntry]:
        return self._entries.get(formula_id)

    def list_all(
        self,
        domain: Optional[FormulaDomain] = None,
        status: Optional[FormulaStatus] = None,
        search: Optional[str] = None
    ) -> List[FormulaEntry]:
        results = list(self._entries.values())
        if domain:
            results = [e for e in results if e.domain == domain]
        if status:
            results = [e for e in results if e.status == status]
        if search:
            q = search.lower()
            results = [
                e for e in results
                if q in e.name.lower() or q in e.description.lower() or q in e.unique_id.lower() or q in e.equation_or_def.lower()
            ]
        return results

    def execute(self, formula_id: str, inputs: Dict[str, Any]) -> CalculationResult:
        entry = self.get(formula_id)
        if not entry:
            raise ValueError(f"Formula '{formula_id}' not found in registry.")
        
        executor = self._executors.get(formula_id)
        if not executor or entry.status not in [FormulaStatus.EXECUTABLE_TESTED, FormulaStatus.EXECUTABLE_UNTESTED]:
            raise NotImplementedError(
                f"Formula '{entry.name}' ({formula_id}) is marked as {entry.status.value}. "
                f"It is maintained for authoritative reference or requires live external market feeds."
            )

        # Validate required inputs
        missing = []
        for req in entry.required_inputs:
            if req.name not in inputs or inputs[req.name] is None:
                if req.default is not None:
                    inputs[req.name] = req.default
                else:
                    missing.append(req.name)
        
        if missing:
            raise ValueError(f"Missing required inputs for '{entry.name}': {', '.join(missing)}")

        # Execute bound function filtering only valid function arguments
        sig = inspect.signature(executor)
        func_kwargs = {}
        for param in sig.parameters.values():
            if param.name in inputs:
                func_kwargs[param.name] = inputs[param.name]
            elif param.default is not inspect.Parameter.empty:
                func_kwargs[param.name] = param.default

        return executor(**func_kwargs)

    def get_summary(self) -> Dict[str, Any]:
        total = len(self._entries)
        domains: Dict[str, int] = {}
        statuses: Dict[str, int] = {}
        for e in self._entries.values():
            domains[e.domain.value] = domains.get(e.domain.value, 0) + 1
            statuses[e.status.value] = statuses.get(e.status.value, 0) + 1

        return {
            "total_registered_formulas": total,
            "executable_count": len(self._executors),
            "domain_breakdown": domains,
            "status_breakdown": statuses
        }

    # =========================================================================
    # CATALOGUE POPULATION (ALL DOMAINS A TO P)
    # =========================================================================
    def _populate_catalogue(self):
        # -------------------------------------------------------------
        # DOMAIN A: CORE FINANCIAL MATHEMATICS
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_a_pct_change",
                name="Percentage Change",
                domain=FormulaDomain.CORE_MATH,
                description="Computes the relative percentage change between two financial values.",
                equation_or_def="((New - Old) / |Old|) * 100",
                required_inputs=[
                    InputVariableSpec(name="old_val", type="Decimal", unit="USD", description="Initial baseline value"),
                    InputVariableSpec(name="new_val", type="Decimal", unit="USD", description="Subsequent comparison value")
                ],
                expected_output="Percentage increase or decrease (+/- %)",
                validation_rules=["old_val must not be zero"],
                knowledge_source="Standard Financial Mathematics",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_percentage_change
        )

        self.register(
            FormulaEntry(
                unique_id="form_a_simple_interest",
                name="Simple Interest",
                domain=FormulaDomain.CORE_MATH,
                description="Calculates linear non-compounding interest over time.",
                equation_or_def="I = P * r * t",
                required_inputs=[
                    InputVariableSpec(name="principal", type="Decimal", unit="USD", description="Initial principal invested or borrowed"),
                    InputVariableSpec(name="annual_rate_pct", type="Decimal", unit="%", description="Annual interest rate percentage"),
                    InputVariableSpec(name="time_years", type="Decimal", unit="years", description="Duration in years")
                ],
                expected_output="Interest amount and total accrued value",
                knowledge_source="Consumer Finance Standards",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_simple_interest
        )

        self.register(
            FormulaEntry(
                unique_id="form_a_compound_interest",
                name="Compound Interest",
                domain=FormulaDomain.CORE_MATH,
                description="Calculates exponential interest with periodic compounding.",
                equation_or_def="A = P * (1 + r/n)^(n*t)",
                required_inputs=[
                    InputVariableSpec(name="principal", type="Decimal", unit="USD", description="Principal"),
                    InputVariableSpec(name="annual_rate_pct", type="Decimal", unit="%", description="Annual interest rate percentage"),
                    InputVariableSpec(name="time_years", type="Decimal", unit="years", description="Investment period in years")
                ],
                optional_inputs=[
                    InputVariableSpec(name="compound_freq", type="int", unit="times/year", description="Compounding frequency", default=12)
                ],
                expected_output="Future accrued value and interest earned",
                knowledge_source="Time Value of Money (TVM) Principles",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_compound_interest
        )

        self.register(
            FormulaEntry(
                unique_id="form_a_present_value",
                name="Present Value (Discounting)",
                domain=FormulaDomain.CORE_MATH,
                description="Computes the current discounted worth of a future sum.",
                equation_or_def="PV = FV / (1 + r)^t",
                required_inputs=[
                    InputVariableSpec(name="future_value", type="Decimal", unit="USD", description="Future cash sum"),
                    InputVariableSpec(name="annual_rate_pct", type="Decimal", unit="%", description="Discount rate percentage"),
                    InputVariableSpec(name="time_years", type="Decimal", unit="years", description="Years into the future")
                ],
                expected_output="Present discounted value in today's dollars",
                knowledge_source="Corporate & Personal Finance Theory",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_present_value
        )

        self.register(
            FormulaEntry(
                unique_id="form_a_effective_annual_rate",
                name="Effective Annual Rate (EAR / APY)",
                domain=FormulaDomain.CORE_MATH,
                description="Converts nominal stated interest to true annual yield accounting for compounding frequency.",
                equation_or_def="EAR = (1 + r/n)^n - 1",
                required_inputs=[
                    InputVariableSpec(name="nominal_rate_pct", type="Decimal", unit="%", description="Stated nominal annual rate")
                ],
                optional_inputs=[
                    InputVariableSpec(name="compounding_frequency", type="int", unit="times/year", description="Compounding frequency per year", default=12)
                ],
                expected_output="Effective annual percentage rate",
                knowledge_source="Truth in Lending / Truth in Savings Regulations",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_effective_annual_rate
        )

        self.register(
            FormulaEntry(
                unique_id="form_a_rule_of_72",
                name="Rule of 72",
                domain=FormulaDomain.CORE_MATH,
                description="Estimates the number of years required to double money at a fixed compound rate.",
                equation_or_def="Years = 72 / r",
                required_inputs=[
                    InputVariableSpec(name="annual_rate_pct", type="Decimal", unit="%", description="Annual return percentage")
                ],
                expected_output="Approximate years to double capital",
                knowledge_source="Empirical Financial Heuristics",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_rule_of_72
        )

        self.register(
            FormulaEntry(
                unique_id="form_a_inflation_adjustment",
                name="Inflation-Adjusted Purchasing Power",
                domain=FormulaDomain.CORE_MATH,
                description="Calculates the real purchasing power of currency over time after inflation.",
                equation_or_def="Real Value = Nominal Amount / (1 + i)^t",
                required_inputs=[
                    InputVariableSpec(name="amount", type="Decimal", unit="USD", description="Nominal money amount"),
                    InputVariableSpec(name="inflation_rate_pct", type="Decimal", unit="%", description="Annual inflation rate percentage"),
                    InputVariableSpec(name="years", type="Decimal", unit="years", description="Time elapsed in years")
                ],
                expected_output="Real purchasing power and future replacement cost",
                knowledge_source="Macroeconomic Personal Finance Models",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_inflation_adjusted_value
        )

        # -------------------------------------------------------------
        # DOMAIN B: PERSONAL INCOME AND EXPENSES
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_b_disposable_income",
                name="Disposable Income",
                domain=FormulaDomain.INCOME_EXPENSE,
                description="Calculates net take-home income remaining after taxes and statutory deductions.",
                equation_or_def="Disposable = Gross - Taxes - Mandatory Deductions",
                required_inputs=[
                    InputVariableSpec(name="gross_income", type="Decimal", unit="USD", description="Total gross income"),
                    InputVariableSpec(name="total_taxes", type="Decimal", unit="USD", description="Income and payroll taxes")
                ],
                optional_inputs=[
                    InputVariableSpec(name="mandatory_deductions", type="Decimal", unit="USD", description="Health insurance/pension deductions", default=0.0)
                ],
                expected_output="Net disposable income and take-home ratio",
                knowledge_source="National Accounting & Consumer Finance Standards",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_disposable_income
        )

        self.register(
            FormulaEntry(
                unique_id="form_b_cash_flow",
                name="Monthly Net Cash Flow",
                domain=FormulaDomain.INCOME_EXPENSE,
                description="Determines whether personal finances are in monthly surplus or deficit.",
                equation_or_def="Cash Flow = Total Monthly Income - Total Monthly Expenses",
                required_inputs=[
                    InputVariableSpec(name="monthly_income", type="Decimal", unit="USD", description="Total net income received"),
                    InputVariableSpec(name="monthly_expenses", type="Decimal", unit="USD", description="Total living expenses and obligations")
                ],
                expected_output="Net surplus/deficit dollar amount and spend ratio",
                knowledge_source="Personal Budgeting Standards",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_monthly_cash_flow
        )

        self.register(
            FormulaEntry(
                unique_id="form_b_savings_rate",
                name="Personal Savings Rate",
                domain=FormulaDomain.INCOME_EXPENSE,
                description="Measures percentage of disposable income directed into savings and investments.",
                equation_or_def="Savings Rate = (Monthly Savings / Monthly Income) * 100",
                required_inputs=[
                    InputVariableSpec(name="monthly_income", type="Decimal", unit="USD", description="Monthly net income"),
                    InputVariableSpec(name="monthly_savings", type="Decimal", unit="USD", description="Amount allocated to savings/investments")
                ],
                expected_output="Personal savings rate percentage",
                knowledge_source="Federal Reserve & Consumer Finance Guidelines",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_savings_rate
        )

        self.register(
            FormulaEntry(
                unique_id="form_b_expense_ratios",
                name="Expense Breakdown Ratios",
                domain=FormulaDomain.INCOME_EXPENSE,
                description="Computes fixed vs variable and essential vs discretionary expenditure proportions.",
                equation_or_def="Fixed Ratio = Fixed / Total, Essential Ratio = Essential / Total",
                required_inputs=[
                    InputVariableSpec(name="total_expenses", type="Decimal", unit="USD", description="Total monthly spend"),
                    InputVariableSpec(name="fixed_expenses", type="Decimal", unit="USD", description="Fixed unavoidable commitments"),
                    InputVariableSpec(name="essential_expenses", type="Decimal", unit="USD", description="Survival essential expenses")
                ],
                expected_output="Fixed%, Variable%, Essential%, and Discretionary% breakdown",
                knowledge_source="50/30/20 Budgeting Rule Architecture",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_expense_ratios
        )

        self.register(
            FormulaEntry(
                unique_id="form_b_income_volatility",
                name="Income Volatility Index",
                domain=FormulaDomain.INCOME_EXPENSE,
                description="Measures stability and unpredictability of monthly income via coefficient of variation.",
                equation_or_def="CV = (Standard Deviation / Mean) * 100",
                required_inputs=[
                    InputVariableSpec(name="monthly_incomes", type="List[Decimal]", unit="USD", description="List of historical monthly incomes")
                ],
                expected_output="Volatility percentage and baseline standard deviation",
                knowledge_source="Freelance & Gig Economy Cash Flow Research",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_income_volatility
        )

        # -------------------------------------------------------------
        # DOMAIN C: SAVINGS AND FINANCIAL GOALS
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_c_required_monthly_savings",
                name="Required Monthly Savings for Goal",
                domain=FormulaDomain.SAVINGS_GOALS,
                description="Calculates exact monthly contribution needed to reach a target sum with investment growth.",
                equation_or_def="PMT = Shortfall * r / ((1+r)^n - 1)",
                required_inputs=[
                    InputVariableSpec(name="target_amount", type="Decimal", unit="USD", description="Target financial goal amount"),
                    InputVariableSpec(name="current_savings", type="Decimal", unit="USD", description="Currently accumulated savings"),
                    InputVariableSpec(name="annual_return_pct", type="Decimal", unit="%", description="Expected annual investment return"),
                    InputVariableSpec(name="target_months", type="int", unit="months", description="Months until goal deadline")
                ],
                expected_output="Required monthly dollar contribution",
                knowledge_source="Sinking Fund Financial Theory",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_required_monthly_savings
        )

        self.register(
            FormulaEntry(
                unique_id="form_c_emergency_fund_target",
                name="Emergency Fund Target",
                domain=FormulaDomain.SAVINGS_GOALS,
                description="Calculates baseline emergency reserve capital required to survive income interruption.",
                equation_or_def="Target = Monthly Essential Expenses * Months Coverage",
                required_inputs=[
                    InputVariableSpec(name="monthly_essential_expenses", type="Decimal", unit="USD", description="Core monthly essential expenses")
                ],
                optional_inputs=[
                    InputVariableSpec(name="months_coverage", type="int", unit="months", description="Target survival buffer", default=6)
                ],
                expected_output="Total dollar emergency cushion required",
                knowledge_source="CFP Board Emergency Buffer Standards",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_emergency_fund_target
        )

        self.register(
            FormulaEntry(
                unique_id="form_c_emergency_fund_coverage",
                name="Emergency Fund Coverage Runway",
                domain=FormulaDomain.SAVINGS_GOALS,
                description="Evaluates how many months of non-discretionary survival liquid cash can sustain.",
                equation_or_def="Coverage Months = Liquid Savings / Monthly Essential Expenses",
                required_inputs=[
                    InputVariableSpec(name="current_liquid_savings", type="Decimal", unit="USD", description="Available checking and savings cash"),
                    InputVariableSpec(name="monthly_essential_expenses", type="Decimal", unit="USD", description="Baseline essential monthly spend")
                ],
                expected_output="Survival runway in months and security tier",
                knowledge_source="Financial Resilience Indicators",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_emergency_fund_coverage
        )

        # -------------------------------------------------------------
        # DOMAIN D: BANKING AND DEPOSITS
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_d_fd_maturity",
                name="Fixed Deposit (CD) Maturity Value",
                domain=FormulaDomain.BANKING_DEPOSITS,
                description="Computes maturity payout and interest on term deposits with quarterly/monthly compounding.",
                equation_or_def="Maturity = P * (1 + r/n)^(n*t)",
                required_inputs=[
                    InputVariableSpec(name="principal", type="Decimal", unit="USD", description="Deposit principal"),
                    InputVariableSpec(name="annual_rate_pct", type="Decimal", unit="%", description="Annual interest rate percentage"),
                    InputVariableSpec(name="tenure_months", type="int", unit="months", description="Deposit term in months")
                ],
                optional_inputs=[
                    InputVariableSpec(name="compound_freq", type="int", unit="times/year", description="Compounding frequency", default=4)
                ],
                expected_output="Maturity lump sum and total interest earned",
                knowledge_source="FDIC Banking Standards",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_fixed_deposit_maturity
        )

        self.register(
            FormulaEntry(
                unique_id="form_d_after_tax_yield",
                name="After-Tax Deposit Yield",
                domain=FormulaDomain.BANKING_DEPOSITS,
                description="Calculates actual take-home interest yield after deduction of marginal tax.",
                equation_or_def="Net Yield = Nominal Yield * (1 - Marginal Tax Rate)",
                required_inputs=[
                    InputVariableSpec(name="nominal_yield_pct", type="Decimal", unit="%", description="Nominal stated deposit rate"),
                    InputVariableSpec(name="marginal_tax_rate_pct", type="Decimal", unit="%", description="Investor marginal tax bracket")
                ],
                expected_output="Effective after-tax interest percentage",
                knowledge_source="Tax-Aware Banking Analysis",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_after_tax_deposit_yield
        )

        # -------------------------------------------------------------
        # DOMAIN E: LOANS AND DEBT
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_e_loan_amortization",
                name="Loan Amortization & Installment (EMI)",
                domain=FormulaDomain.LOANS_DEBT,
                description="Calculates standard monthly loan installment (PMT) and total borrowing interest.",
                equation_or_def="PMT = P * (r*(1+r)^n) / ((1+r)^n - 1)",
                required_inputs=[
                    InputVariableSpec(name="principal", type="Decimal", unit="USD", description="Loan principal amount"),
                    InputVariableSpec(name="annual_interest_rate_pct", type="Decimal", unit="%", description="Annual interest rate percentage"),
                    InputVariableSpec(name="tenure_months", type="int", unit="months", description="Repayment period in months")
                ],
                expected_output="Monthly installment payment and lifetime interest",
                knowledge_source="Consumer Financial Protection Bureau (CFPB)",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_loan_amortization_schedule
        )

        self.register(
            FormulaEntry(
                unique_id="form_e_early_repayment",
                name="Loan Early Repayment Savings",
                domain=FormulaDomain.LOANS_DEBT,
                description="Computes interest saved and tenure shortened by making extra monthly principal payments.",
                equation_or_def="Simulation iterating monthly balance reduction with extra principal contribution",
                required_inputs=[
                    InputVariableSpec(name="principal", type="Decimal", unit="USD", description="Current remaining loan balance"),
                    InputVariableSpec(name="annual_rate_pct", type="Decimal", unit="%", description="Annual interest rate percentage"),
                    InputVariableSpec(name="tenure_months", type="int", unit="months", description="Remaining term in months"),
                    InputVariableSpec(name="extra_monthly_payment", type="Decimal", unit="USD", description="Additional monthly principal payment")
                ],
                expected_output="Dollar interest saved and months cut from repayment",
                knowledge_source="Debt Optimization & Amortization Mechanics",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_loan_early_repayment_savings
        )

        self.register(
            FormulaEntry(
                unique_id="form_e_dti_ratio",
                name="Debt-to-Income (DTI) Ratio",
                domain=FormulaDomain.LOANS_DEBT,
                description="Evaluates debt service capacity by dividing total monthly debt obligations by gross income.",
                equation_or_def="DTI = (Total Monthly Debt Payments / Gross Monthly Income) * 100",
                required_inputs=[
                    InputVariableSpec(name="monthly_debt_payments", type="Decimal", unit="USD", description="Total monthly loan and card minimums"),
                    InputVariableSpec(name="monthly_gross_income", type="Decimal", unit="USD", description="Gross monthly income before tax")
                ],
                expected_output="DTI percentage and lending risk classification",
                knowledge_source="Fannie Mae / Freddie Mac Underwriting Standards",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_debt_to_income_ratio
        )

        self.register(
            FormulaEntry(
                unique_id="form_e_ltv_ratio",
                name="Loan-to-Value (LTV) Ratio",
                domain=FormulaDomain.LOANS_DEBT,
                description="Measures lending risk by comparing borrowed principal to total appraised collateral value.",
                equation_or_def="LTV = (Loan Amount / Asset Value) * 100",
                required_inputs=[
                    InputVariableSpec(name="loan_amount", type="Decimal", unit="USD", description="Loan or mortgage amount"),
                    InputVariableSpec(name="asset_value", type="Decimal", unit="USD", description="Appraised asset purchase price")
                ],
                expected_output="LTV percentage",
                knowledge_source="Secured Lending & Mortgage Guidelines",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_loan_to_value_ratio
        )

        # -------------------------------------------------------------
        # DOMAIN F: CREDIT CARDS
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_f_credit_utilization",
                name="Credit Utilization Ratio",
                domain=FormulaDomain.CREDIT_CARDS,
                description="Measures revolving debt burden as a percentage of total granted revolving credit line.",
                equation_or_def="Utilization = (Total Balance / Total Credit Limit) * 100",
                required_inputs=[
                    InputVariableSpec(name="total_credit_used", type="Decimal", unit="USD", description="Current balance owed across cards"),
                    InputVariableSpec(name="total_credit_limit", type="Decimal", unit="USD", description="Sum of credit limits on all cards")
                ],
                expected_output="Utilization percentage and credit score impact tier",
                knowledge_source="FICO & VantageScore Scoring Algorithms",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_credit_utilization
        )

        self.register(
            FormulaEntry(
                unique_id="form_f_cc_interest",
                name="Credit Card Monthly Finance Charge",
                domain=FormulaDomain.CREDIT_CARDS,
                description="Calculates monthly card interest charge based on daily balance and APR.",
                equation_or_def="Finance Charge = ADB * (APR / 365) * Days",
                required_inputs=[
                    InputVariableSpec(name="average_daily_balance", type="Decimal", unit="USD", description="Average daily revolving balance"),
                    InputVariableSpec(name="apr_pct", type="Decimal", unit="%", description="Annual Percentage Rate")
                ],
                optional_inputs=[
                    InputVariableSpec(name="billing_days", type="int", unit="days", description="Days in billing cycle", default=30)
                ],
                expected_output="Monthly interest finance charge in USD",
                knowledge_source="Credit Card Accountability Responsibility and Disclosure (CARD) Act",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_credit_card_interest_charge
        )

        # -------------------------------------------------------------
        # DOMAIN G: INVESTMENTS AND WEALTH
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_g_net_worth",
                name="Personal Net Worth",
                domain=FormulaDomain.INVESTMENTS_WEALTH,
                description="Fundamental measure of personal wealth: total assets minus total liabilities.",
                equation_or_def="Net Worth = Assets - Liabilities",
                required_inputs=[
                    InputVariableSpec(name="total_assets", type="Decimal", unit="USD", description="Sum of all bank balances, investments, property"),
                    InputVariableSpec(name="total_liabilities", type="Decimal", unit="USD", description="Sum of all mortgages, loans, card balances")
                ],
                expected_output="Net worth in USD and leverage ratio",
                knowledge_source="Standard Wealth Accounting Principles",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_net_worth
        )

        self.register(
            FormulaEntry(
                unique_id="form_g_cagr",
                name="Compound Annual Growth Rate (CAGR)",
                domain=FormulaDomain.INVESTMENTS_WEALTH,
                description="Measures smoothed annual rate of return on an investment over multiple years.",
                equation_or_def="CAGR = (Ending Value / Beginning Value)^(1/years) - 1",
                required_inputs=[
                    InputVariableSpec(name="beginning_value", type="Decimal", unit="USD", description="Initial investment value"),
                    InputVariableSpec(name="ending_value", type="Decimal", unit="USD", description="Final portfolio value"),
                    InputVariableSpec(name="years", type="Decimal", unit="years", description="Investment period in years")
                ],
                expected_output="Annualized compounded growth rate percentage",
                knowledge_source="GIPS Portfolio Performance Standards",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_cagr
        )

        self.register(
            FormulaEntry(
                unique_id="form_g_roi",
                name="Return on Investment (ROI)",
                domain=FormulaDomain.INVESTMENTS_WEALTH,
                description="Measures efficiency or profitability of an investment relative to its cost.",
                equation_or_def="ROI = ((Gain - Cost) / Cost) * 100",
                required_inputs=[
                    InputVariableSpec(name="gain_or_current_value", type="Decimal", unit="USD", description="Total revenue or terminal asset value"),
                    InputVariableSpec(name="initial_cost", type="Decimal", unit="USD", description="Total initial capital invested")
                ],
                expected_output="ROI percentage and net dollar return",
                knowledge_source="Financial Analysis Fundamentals",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_roi
        )

        # -------------------------------------------------------------
        # DOMAIN H: TAXATION
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_h_progressive_tax",
                name="Progressive Income Tax",
                domain=FormulaDomain.TAXATION,
                description="Computes exact multi-tier progressive tax liability, effective rate, and marginal rate.",
                equation_or_def="Sum(Bracket_Rate * Taxable_In_Bracket)",
                required_inputs=[
                    InputVariableSpec(name="taxable_income", type="Decimal", unit="USD", description="Taxable income after deductions")
                ],
                optional_inputs=[
                    InputVariableSpec(name="jurisdiction", type="str", unit="country_code", description="Tax authority jurisdiction", default="US_SINGLE_2024")
                ],
                expected_output="Tax liability, effective tax rate, and marginal tax bracket",
                jurisdiction="US/UK",
                knowledge_source="IRS Publication 15 & HMRC Tax Schedules",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_progressive_income_tax
        )

        # -------------------------------------------------------------
        # DOMAIN I: INSURANCE AND PROTECTION
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_i_insurance_payout",
                name="Insurance Claim Net Payout",
                domain=FormulaDomain.INSURANCE_PROTECTION,
                description="Calculates insurer reimbursement and user out-of-pocket costs after deductible and coinsurance.",
                equation_or_def="Payout = Min(PolicyLimit, (Loss - Deductible) * (1 - Coinsurance))",
                required_inputs=[
                    InputVariableSpec(name="loss_amount", type="Decimal", unit="USD", description="Total gross insured loss or damage"),
                    InputVariableSpec(name="deductible", type="Decimal", unit="USD", description="Policy deductible")
                ],
                optional_inputs=[
                    InputVariableSpec(name="coinsurance_pct", type="Decimal", unit="%", description="User coinsurance percentage", default=20),
                    InputVariableSpec(name="policy_limit", type="Decimal", unit="USD", description="Maximum policy payout limit", default=1000000)
                ],
                expected_output="Net insurance payout and user out-of-pocket share",
                knowledge_source="Insurance Underwriting Principles",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_insurance_claim_payout
        )

        # -------------------------------------------------------------
        # DOMAIN J: FOREIGN EXCHANGE AND TRANSFERS
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_j_fx_conversion",
                name="FX Transfer & Spread Cost",
                domain=FormulaDomain.FX_TRANSFERS,
                description="Calculates exact target currency received and identifies hidden exchange rate markup spreads.",
                equation_or_def="Target = (Source - Fee) * Rate * (1 - Spread)",
                required_inputs=[
                    InputVariableSpec(name="source_amount", type="Decimal", unit="USD", description="Amount sent in base currency"),
                    InputVariableSpec(name="mid_market_exchange_rate", type="Decimal", unit="ratio", description="Mid-market interbank exchange rate")
                ],
                optional_inputs=[
                    InputVariableSpec(name="spread_markup_pct", type="Decimal", unit="%", description="Bank/provider FX markup", default=1.5),
                    InputVariableSpec(name="fixed_transfer_fee", type="Decimal", unit="USD", description="Fixed wire or transaction fee", default=0.0)
                ],
                expected_output="Target currency amount received and total fees/spread",
                knowledge_source="Cross-Border Payments & Remittance Transparency Standards",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_fx_conversion
        )

        # -------------------------------------------------------------
        # DOMAIN K: SHOPPING AND COMMERCE
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_k_tco",
                name="Commerce Total Cost of Ownership",
                domain=FormulaDomain.SHOPPING_COMMERCE,
                description="Evaluates complete lifetime product cost including acquisition, taxes, setup, recurring fees and maintenance.",
                equation_or_def="TCO = Upfront + (Monthly * 12 * Years) + (Maintenance * Years)",
                required_inputs=[
                    InputVariableSpec(name="base_price", type="Decimal", unit="USD", description="Stated purchase price")
                ],
                optional_inputs=[
                    InputVariableSpec(name="shipping_cost", type="Decimal", unit="USD", description="Delivery cost", default=0.0),
                    InputVariableSpec(name="tax_rate_pct", type="Decimal", unit="%", description="Sales tax percentage", default=0.0),
                    InputVariableSpec(name="setup_fee", type="Decimal", unit="USD", description="Initial onboarding or assembly", default=0.0),
                    InputVariableSpec(name="annual_maintenance", type="Decimal", unit="USD", description="Annual service/repairs", default=0.0),
                    InputVariableSpec(name="recurring_monthly_fee", type="Decimal", unit="USD", description="Subscription or consumables", default=0.0),
                    InputVariableSpec(name="lifespan_years", type="int", unit="years", description="Expected product life", default=3)
                ],
                expected_output="Total TCO, annualized cost, and monthly equivalent",
                knowledge_source="Consumer Economics & Procurement Science",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_commerce_tco
        )

        self.register(
            FormulaEntry(
                unique_id="form_k_cost_per_use",
                name="Cost Per Use (Utilization Metric)",
                domain=FormulaDomain.SHOPPING_COMMERCE,
                description="Measures real economic value by dividing expenditure by verified utilization events.",
                equation_or_def="Cost Per Use = Total Expenditure / Total Uses",
                required_inputs=[
                    InputVariableSpec(name="total_cost", type="Decimal", unit="USD", description="Total purchase or subscription expense"),
                    InputVariableSpec(name="total_uses", type="int", unit="count", description="Number of times item or service was used")
                ],
                expected_output="Unit cost per utilization event",
                knowledge_source="Behavioral Economics & Consumption Analysis",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_cost_per_use
        )

        self.register(
            FormulaEntry(
                unique_id="form_k_unit_price",
                name="Normalized Unit Price",
                domain=FormulaDomain.SHOPPING_COMMERCE,
                description="Normalizes bulk package pricing to allow honest comparison across varying merchant sizes.",
                equation_or_def="Unit Price = Total Package Price / Quantity",
                required_inputs=[
                    InputVariableSpec(name="package_price", type="Decimal", unit="USD", description="Total shelf price"),
                    InputVariableSpec(name="quantity", type="Decimal", unit="units", description="Count, volume, or weight")
                ],
                optional_inputs=[
                    InputVariableSpec(name="unit_name", type="str", unit="text", description="Unit of measurement", default="units")
                ],
                expected_output="Price per unit of measurement",
                knowledge_source="Retail Consumer Protection Regulations",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_unit_price
        )

        self.register(
            FormulaEntry(
                unique_id="form_k_buy_vs_subscribe",
                name="Buy vs. Subscribe Break-Even Analysis",
                domain=FormulaDomain.SHOPPING_COMMERCE,
                description="Calculates how many months of subscription fees equal the outright purchase price.",
                equation_or_def="Break-Even Months = Purchase Price / Monthly Subscription",
                required_inputs=[
                    InputVariableSpec(name="purchase_price", type="Decimal", unit="USD", description="Outright one-time purchase price"),
                    InputVariableSpec(name="monthly_subscription_price", type="Decimal", unit="USD", description="Ongoing monthly fee")
                ],
                expected_output="Months and years until purchase becomes cheaper than renting/subscribing",
                knowledge_source="Consumer Finance Decision Models",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_buy_vs_subscribe_break_even
        )

        # -------------------------------------------------------------
        # DOMAIN L: PROPERTY AND VEHICLES
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_l_depreciation",
                name="Straight-Line Depreciation",
                domain=FormulaDomain.PROPERTY_VEHICLE,
                description="Computes uniform annual and monthly asset depreciation across useful lifespan.",
                equation_or_def="Depreciation = (Asset Cost - Salvage Value) / Useful Life",
                required_inputs=[
                    InputVariableSpec(name="asset_cost", type="Decimal", unit="USD", description="Initial cost of vehicle or equipment"),
                    InputVariableSpec(name="salvage_value", type="Decimal", unit="USD", description="Expected resale value at end of life"),
                    InputVariableSpec(name="useful_life_years", type="int", unit="years", description="Expected useful lifetime")
                ],
                expected_output="Annual and monthly depreciation expense",
                knowledge_source="GAAP & Asset Accounting Standards",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_straight_line_depreciation
        )

        self.register(
            FormulaEntry(
                unique_id="form_l_rental_yield",
                name="Property Gross & Net Rental Yield",
                domain=FormulaDomain.PROPERTY_VEHICLE,
                description="Evaluates property investment return comparing rental revenue against capital value.",
                equation_or_def="Gross Yield = (Rent / Price) * 100, Net Yield = ((Rent - Opex) / Price) * 100",
                required_inputs=[
                    InputVariableSpec(name="annual_rental_income", type="Decimal", unit="USD", description="Gross annual rental receipts"),
                    InputVariableSpec(name="property_price", type="Decimal", unit="USD", description="Total property purchase value")
                ],
                optional_inputs=[
                    InputVariableSpec(name="annual_operating_costs", type="Decimal", unit="USD", description="Taxes, HOA, maintenance, insurance", default=0.0)
                ],
                expected_output="Gross yield percentage and net operational yield percentage",
                knowledge_source="Real Estate Investment Analysis",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_rental_yield
        )

        # -------------------------------------------------------------
        # DOMAIN M: FREELANCE AND SELF-EMPLOYMENT
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_m_effective_hourly_rate",
                name="Freelance Effective Real Hourly Rate",
                domain=FormulaDomain.FREELANCE_SELF_EMPLOYED,
                description="Reveals true hourly earnings after factoring in unpaid administrative, marketing, and invoicing hours.",
                equation_or_def="Effective Rate = (Billable Rate * Billable Hours) / Total Hours Worked",
                required_inputs=[
                    InputVariableSpec(name="billable_rate", type="Decimal", unit="USD/hr", description="Nominal client hourly billing rate"),
                    InputVariableSpec(name="billable_hours_per_week", type="Decimal", unit="hours", description="Direct client billable hours"),
                    InputVariableSpec(name="unpaid_admin_hours_per_week", type="Decimal", unit="hours", description="Unpaid admin, pitching, email hours")
                ],
                expected_output="Real effective hourly rate and earnings dilution percentage",
                knowledge_source="Freelance Economics & Solopreneur Pricing Models",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_effective_hourly_rate
        )

        # -------------------------------------------------------------
        # DOMAIN N: FORECASTING AND STATISTICS
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_n_sma",
                name="Simple Moving Average (SMA)",
                domain=FormulaDomain.FORECASTING_STATISTICS,
                description="Calculates smoothed rolling financial baseline across recent observation periods.",
                equation_or_def="SMA = Sum(x_i) / n",
                required_inputs=[
                    InputVariableSpec(name="series", type="List[Decimal]", unit="USD", description="Historical data points")
                ],
                optional_inputs=[
                    InputVariableSpec(name="window", type="int", unit="periods", description="Rolling window size", default=3)
                ],
                expected_output="Moving average value across the specified window",
                knowledge_source="Quantitative Time Series Analysis",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_simple_moving_average
        )

        # -------------------------------------------------------------
        # DOMAIN O: ADVANCED FINANCIAL MODELS
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_o_bond_pricing",
                name="Bond Pricing (Discounted Cash Flow)",
                domain=FormulaDomain.ADVANCED_MODELS,
                description="Computes theoretical market price of fixed-rate bond by discounting coupon stream and face value.",
                equation_or_def="P = Sum(Coupon / (1+y)^t) + FaceValue / (1+y)^n",
                required_inputs=[
                    InputVariableSpec(name="face_value", type="Decimal", unit="USD", description="Par value of bond"),
                    InputVariableSpec(name="coupon_rate_pct", type="Decimal", unit="%", description="Annual coupon rate percentage"),
                    InputVariableSpec(name="years_to_maturity", type="Decimal", unit="years", description="Remaining lifespan until maturity"),
                    InputVariableSpec(name="market_yield_pct", type="Decimal", unit="%", description="Current prevailing market yield to maturity")
                ],
                optional_inputs=[
                    InputVariableSpec(name="coupon_freq", type="int", unit="times/year", description="Coupon payment frequency", default=2)
                ],
                expected_output="Bond clean price and trading status (Premium, Par, Discount)",
                knowledge_source="Fixed Income Securities Mathematics (Fabozzi)",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_bond_price
        )

        self.register(
            FormulaEntry(
                unique_id="form_o_black_scholes",
                name="Black-Scholes European Option Pricing",
                domain=FormulaDomain.ADVANCED_MODELS,
                description="Computes theoretical European call and put option prices using standard log-normal diffusion.",
                equation_or_def="C = S*N(d1) - K*e^(-rT)*N(d2), P = K*e^(-rT)*N(-d2) - S*N(-d1)",
                required_inputs=[
                    InputVariableSpec(name="spot_price", type="Decimal", unit="USD", description="Current asset spot price"),
                    InputVariableSpec(name="strike_price", type="Decimal", unit="USD", description="Option strike exercise price"),
                    InputVariableSpec(name="time_years", type="Decimal", unit="years", description="Time until expiration in years"),
                    InputVariableSpec(name="risk_free_rate_pct", type="Decimal", unit="%", description="Risk-free interest rate percentage"),
                    InputVariableSpec(name="volatility_pct", type="Decimal", unit="%", description="Annualized volatility percentage")
                ],
                expected_output="Call option price, put option price, and call Delta",
                knowledge_source="Black & Scholes (1973) / Merton (1973) Nobel Prize Model",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_black_scholes
        )

        self.register(
            FormulaEntry(
                unique_id="form_o_yield_to_maturity_ref",
                name="Yield to Maturity (Exact Multi-Period Internal Rate)",
                domain=FormulaDomain.ADVANCED_MODELS,
                description="Reference definition for exact bond YTM solved via iterative Newton-Raphson cash flow roots.",
                equation_or_def="Price = Sum(C_t / (1 + YTM)^t)",
                required_inputs=[
                    InputVariableSpec(name="bond_price", type="Decimal", unit="USD", description="Market trading price"),
                    InputVariableSpec(name="face_value", type="Decimal", unit="USD", description="Redemption par value"),
                    InputVariableSpec(name="coupon_rate_pct", type="Decimal", unit="%", description="Annual coupon rate"),
                    InputVariableSpec(name="years", type="Decimal", unit="years", description="Years to maturity")
                ],
                expected_output="Exact annualized internal yield percentage",
                knowledge_source="Fixed Income Analysis Standards",
                status=FormulaStatus.REFERENCE_ONLY
            )
        )

        self.register(
            FormulaEntry(
                unique_id="form_o_option_greeks_suite",
                name="Option Greeks Suite (Gamma, Vega, Theta, Rho)",
                domain=FormulaDomain.ADVANCED_MODELS,
                description="Comprehensive sensitivities of option contracts requiring continuous real-time market data curves.",
                equation_or_def="Vega = S*sqrt(T)*phi(d1), Theta = -S*phi(d1)*v/(2*sqrt(T)) - r*K*e^(-rT)*N(d2)",
                required_inputs=[
                    InputVariableSpec(name="spot", type="Decimal", unit="USD", description="Underlying asset price"),
                    InputVariableSpec(name="strike", type="Decimal", unit="USD", description="Option strike price")
                ],
                expected_output="Vega, Theta, and Rho sensitivity vectors",
                knowledge_source="Quantitative Derivatives Pricing Standards",
                status=FormulaStatus.REQUIRES_EXTERNAL_DATA
            )
        )

        # -------------------------------------------------------------
        # DOMAIN P: FINANCIAL DECISION METRICS
        # -------------------------------------------------------------
        self.register(
            FormulaEntry(
                unique_id="form_p_purchase_affordability",
                name="Discretionary Purchase Affordability",
                domain=FormulaDomain.DECISION_METRICS,
                description="Multi-factor decision metric evaluating whether a discretionary purchase breaches emergency reserves.",
                equation_or_def="Post Cash = Liquid Cash - Price; Verdict based on Reserve Margin",
                required_inputs=[
                    InputVariableSpec(name="purchase_price", type="Decimal", unit="USD", description="Total checkout purchase cost"),
                    InputVariableSpec(name="available_liquid_cash", type="Decimal", unit="USD", description="Current checking and liquid cash"),
                    InputVariableSpec(name="monthly_surplus", type="Decimal", unit="USD", description="Average monthly unallocated cash flow")
                ],
                optional_inputs=[
                    InputVariableSpec(name="minimum_emergency_reserve", type="Decimal", unit="USD", description="Non-negotiable cash cushion", default=1000.0)
                ],
                expected_output="Affordability verdict (AFFORDABLE, AFFORDABLE_WITH_CAUTION, NOT_RECOMMENDED)",
                knowledge_source="FINORA Personal Financial Safety Architecture",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_purchase_affordability
        )

        self.register(
            FormulaEntry(
                unique_id="form_p_financial_health_index",
                name="Composite Financial Health Index",
                domain=FormulaDomain.DECISION_METRICS,
                description="Multi-dimensional personal financial score (0-100) combining savings rate, DTI, emergency runway, and credit utilization.",
                equation_or_def="Score = Savings_Pts(25) + Debt_Pts(25) + Emergency_Pts(25) + Credit_Pts(25)",
                required_inputs=[
                    InputVariableSpec(name="savings_rate_pct", type="Decimal", unit="%", description="Personal savings rate percentage"),
                    InputVariableSpec(name="dti_ratio_pct", type="Decimal", unit="%", description="Debt-to-income percentage"),
                    InputVariableSpec(name="emergency_coverage_months", type="Decimal", unit="months", description="Emergency fund coverage months"),
                    InputVariableSpec(name="credit_utilization_pct", type="Decimal", unit="%", description="Revolving credit utilization percentage")
                ],
                expected_output="Health score out of 100 and overall financial fitness tier",
                knowledge_source="Financial Health Network Metrics",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_financial_health_index
        )

        self.register(
            FormulaEntry(
                unique_id="form_p_opportunity_cost",
                name="Opportunity Cost of Spending vs. Investing",
                domain=FormulaDomain.DECISION_METRICS,
                description="Calculates forgone future compound wealth if a sum spent was invested in a broad market index fund instead.",
                equation_or_def="Future Wealth = Amount * (1 + r)^t",
                required_inputs=[
                    InputVariableSpec(name="expenditure_amount", type="Decimal", unit="USD", description="Amount spent or about to be spent")
                ],
                optional_inputs=[
                    InputVariableSpec(name="expected_annual_return_pct", type="Decimal", unit="%", description="Expected annual index return", default=7.0),
                    InputVariableSpec(name="horizon_years", type="int", unit="years", description="Investment time horizon in years", default=10)
                ],
                expected_output="Total forgone future wealth and lost compound returns",
                knowledge_source="Behavioral Economics & Intertemporal Choice",
                status=FormulaStatus.EXECUTABLE_TESTED
            ),
            eng.calc_opportunity_cost
        )

global_formula_registry = FinancialFormulaRegistry()

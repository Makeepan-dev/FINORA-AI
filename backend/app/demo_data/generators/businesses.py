from decimal import Decimal
from typing import List
from ..models.business import SyntheticBusiness, BusinessType, EmployeeRecord

def generate_businesses() -> List[SyntheticBusiness]:
    businesses = [
        # Business 1: Aurora Cloud Technologies
        SyntheticBusiness(
            business_id="biz_aurora_tech",
            business_name="Aurora Cloud Technologies Inc.",
            business_type=BusinessType.SAAS_STARTUP,
            country="US",
            currency="USD",
            monthly_recurring_revenue=Decimal("45000.00"),
            cash_balance=Decimal("68000.00"),
            monthly_payroll=Decimal("28000.00"),
            operating_expenses_target=Decimal("12000.00"),
            suppliers=[
                {"supplier_id=" : "sup_strata_cloud", "name": "StrataVault Infrastructure", "category": "cloud_hosting"},
                {"supplier_id=": "sup_gitforge", "name": "GitForge Enterprise Cloud", "category": "devops"},
                {"supplier_id=": "sup_timber_office", "name": "Timber & Stone Hardware", "category": "office_equipment"}
            ],
            customers=[
                {"customer_id=": "cust_vertex_fin", "name": "Vertex Financial Systems", "plan": "Enterprise Annual"},
                {"customer_id=": "cust_delta_health", "name": "Delta Health Analytics", "plan": "Pro Team"},
                {"customer_id=": "cust_beacon_media", "name": "Beacon Media Digital", "plan": "Growth Tier"}
            ],
            employees=[
                EmployeeRecord(employee_id="emp_001", full_name="Elena Rostova", role="CTO & Co-founder", monthly_salary=Decimal("6000.00")),
                EmployeeRecord(employee_id="emp_002", full_name="Damon Patel", role="Lead Platform Engineer", monthly_salary=Decimal("5500.00")),
                EmployeeRecord(employee_id="emp_003", full_name="Maya Lin", role="Senior Fullstack Dev", monthly_salary=Decimal("5000.00")),
                EmployeeRecord(employee_id="emp_004", full_name="Kevin O'Connor", role="DevOps Specialist", monthly_salary=Decimal("4500.00")),
                EmployeeRecord(employee_id="emp_005", full_name="Sophie Dubois", role="Product Marketing Lead", monthly_salary=Decimal("4000.00")),
                EmployeeRecord(employee_id="emp_006", full_name="Javier Gomez", role="Customer Solutions Architect", monthly_salary=Decimal("3000.00"))
            ],
            tax_id_mask="SYNTH-TAX-84-9921"
        ),

        # Business 2: Nexus Strategic Consulting
        SyntheticBusiness(
            business_id="biz_nexus_consulting",
            business_name="Nexus Advisory Group LLC",
            business_type=BusinessType.CONSULTING_AGENCY,
            country="US",
            currency="USD",
            monthly_recurring_revenue=Decimal("32000.00"),
            cash_balance=Decimal("34000.00"),
            monthly_payroll=Decimal("18000.00"),
            operating_expenses_target=Decimal("8000.00"),
            suppliers=[
                {"supplier_id=": "sup_haven_lofts", "name": "Haven Loft Corporate Stays", "category": "travel"},
                {"supplier_id=": "sup_plancraft", "name": "PlanCraft Enterprise", "category": "software"}
            ],
            customers=[
                {"customer_id=": "cust_horizon_retail", "name": "Horizon Retail Global", "plan": "Strategic Advisory Retainer"},
                {"customer_id=": "cust_pinnacle_log", "name": "Pinnacle Logistics Corp", "plan": "Process Automation Sprint"}
            ],
            employees=[
                EmployeeRecord(employee_id="emp_101", full_name="Rachel Vance", role="Managing Partner", monthly_salary=Decimal("6500.00")),
                EmployeeRecord(employee_id="emp_102", full_name="Lucas Meyer", role="Principal Consultant", monthly_salary=Decimal("5000.00")),
                EmployeeRecord(employee_id="emp_103", full_name="Amina Al-Mansoor", role="Senior Strategy Analyst", monthly_salary=Decimal("4000.00")),
                EmployeeRecord(employee_id="emp_104", full_name="Tariq Vance", role="Operations Manager", monthly_salary=Decimal("2500.00"))
            ],
            tax_id_mask="SYNTH-TAX-72-4018"
        )
    ]
    return businesses

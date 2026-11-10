from decimal import Decimal
from typing import List
from ..models.invoice import SyntheticInvoice, InvoiceStatus, InvoiceItem

def generate_invoices() -> List[SyntheticInvoice]:
    invoices = [
        # Aurora Tech Invoices
        SyntheticInvoice(
            invoice_id="inv_aurora_2026_01",
            business_id="biz_aurora_tech",
            customer_or_vendor_id="cust_vertex_fin",
            customer_or_vendor_name="Vertex Financial Systems",
            direction="receivable",
            issue_date="2026-10-01",
            due_date="2026-10-31",
            paid_date="2026-10-28",
            subtotal=Decimal("15000.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("15000.00"),
            amount_paid=Decimal("15000.00"),
            status=InvoiceStatus.PAID,
            items=[
                InvoiceItem(item_id="item_01", description="Aurora Enterprise Cloud Platform Q4", quantity=1, unit_price=Decimal("15000.00"), total_price=Decimal("15000.00"))
            ],
            related_transaction_id="txn_biz_aurora_rev_oct"
        ),
        SyntheticInvoice(
            invoice_id="inv_aurora_2026_02",
            business_id="biz_aurora_tech",
            customer_or_vendor_id="cust_delta_health",
            customer_or_vendor_name="Delta Health Analytics",
            direction="receivable",
            issue_date="2026-10-15",
            due_date="2026-11-15",
            paid_date=None,
            subtotal=Decimal("8500.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("8500.00"),
            amount_paid=Decimal("0.00"),
            status=InvoiceStatus.UNPAID,
            items=[
                InvoiceItem(item_id="item_02", description="Aurora Pro Team License 50 seats", quantity=50, unit_price=Decimal("170.00"), total_price=Decimal("8500.00"))
            ]
        ),
        SyntheticInvoice(
            invoice_id="inv_aurora_2026_03",
            business_id="biz_aurora_tech",
            customer_or_vendor_id="cust_beacon_media",
            customer_or_vendor_name="Beacon Media Digital",
            direction="receivable",
            issue_date="2026-09-01",
            due_date="2026-10-01",
            paid_date=None,
            subtotal=Decimal("6200.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("6200.00"),
            amount_paid=Decimal("3100.00"),
            status=InvoiceStatus.OVERDUE,
            items=[
                InvoiceItem(item_id="item_03", description="Custom Data Pipeline Integration", quantity=1, unit_price=Decimal("6200.00"), total_price=Decimal("6200.00"))
            ]
        ),
        SyntheticInvoice(
            invoice_id="inv_aurora_vendor_strata",
            business_id="biz_aurora_tech",
            customer_or_vendor_id="sup_strata_cloud",
            customer_or_vendor_name="StrataVault Infrastructure",
            direction="payable",
            issue_date="2026-10-01",
            due_date="2026-10-15",
            paid_date="2026-10-14",
            subtotal=Decimal("3450.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("3450.00"),
            amount_paid=Decimal("3450.00"),
            status=InvoiceStatus.PAID,
            items=[
                InvoiceItem(item_id="item_04", description="Dedicated GPU Cluster Instances", quantity=1, unit_price=Decimal("3450.00"), total_price=Decimal("3450.00"))
            ],
            related_transaction_id="txn_biz_aurora_exp_strata"
        ),

        # Nexus Consulting Invoices
        SyntheticInvoice(
            invoice_id="inv_nexus_2026_01",
            business_id="biz_nexus_consulting",
            customer_or_vendor_id="cust_horizon_retail",
            customer_or_vendor_name="Horizon Retail Global",
            direction="receivable",
            issue_date="2026-09-15",
            due_date="2026-10-15",
            paid_date="2026-10-12",
            subtotal=Decimal("18000.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("18000.00"),
            amount_paid=Decimal("18000.00"),
            status=InvoiceStatus.PAID,
            items=[
                InvoiceItem(item_id="item_05", description="Digital Transformation Assessment Phase 1", quantity=1, unit_price=Decimal("18000.00"), total_price=Decimal("18000.00"))
            ],
            related_transaction_id="txn_biz_nexus_rev_horizon"
        ),
        SyntheticInvoice(
            invoice_id="inv_nexus_2026_02",
            business_id="biz_nexus_consulting",
            customer_or_vendor_id="cust_pinnacle_log",
            customer_or_vendor_name="Pinnacle Logistics Corp",
            direction="receivable",
            issue_date="2026-09-01",
            due_date="2026-10-01",
            paid_date=None,
            subtotal=Decimal("14000.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("14000.00"),
            amount_paid=Decimal("0.00"),
            status=InvoiceStatus.OVERDUE,
            items=[
                InvoiceItem(item_id="item_06", description="Supply Chain Optimization Advisory", quantity=1, unit_price=Decimal("14000.00"), total_price=Decimal("14000.00"))
            ]
        ),
        SyntheticInvoice(
            invoice_id="inv_nexus_vendor_cancelled",
            business_id="biz_nexus_consulting",
            customer_or_vendor_id="sup_haven_lofts",
            customer_or_vendor_name="Haven Loft Corporate Stays",
            direction="payable",
            issue_date="2026-09-20",
            due_date="2026-10-20",
            paid_date=None,
            subtotal=Decimal("1200.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("1200.00"),
            amount_paid=Decimal("0.00"),
            status=InvoiceStatus.CANCELLED,
            items=[
                InvoiceItem(item_id="item_07", description="Offsite Retreat Conference Room (Cancelled)", quantity=1, unit_price=Decimal("1200.00"), total_price=Decimal("1200.00"))
            ]
        )
    ]
    return invoices

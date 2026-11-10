from typing import List
from .base import KnowledgeEntry, KnowledgeDomain, VerificationStatus

def get_payments_commerce_entries() -> List[KnowledgeEntry]:
    return [
        KnowledgeEntry(
            knowledge_id="kn_pay_001_auth_capture",
            domain=KnowledgeDomain.PAYMENTS_COMMERCE,
            topic="payment_lifecycle",
            title="Two-Step Payment Authorization and Capture",
            definition="The standard lifecycle in card and digital wallet (PayPal) processing where funds are reserved (Authorized) and subsequently finalized/transferred (Captured).",
            rules=[
                "Authorization places a temporary hold on buyer credit/balance for up to 3-29 days.",
                "Capture transfers the authorized funds from buyer to merchant ledger.",
                "Expired authorizations must be voided or re-authorized.",
                "Duplicate capture attempts on a completed order MUST be blocked by idempotency keys."
            ],
            required_inputs=["order_id", "authorized_amount", "capture_status"],
            calculation_procedure="net_settlement = captured_amount - processing_fee",
            output_fields=["authorization_status", "capture_status", "settled_amount"],
            authority_source="PayPal REST API v2 Specifications & EMVCo Standards",
            verification_status=VerificationStatus.REGULATORY_STANDARD,
            confidence_score=1.0,
            limitations="Authorization hold windows depend on issuer card rules."
        ),
        KnowledgeEntry(
            knowledge_id="kn_pay_002_processing_fees",
            domain=KnowledgeDomain.PAYMENTS_COMMERCE,
            topic="merchant_fees",
            title="Payment Processing Fees & Net Settlement",
            definition="Standard interchange and payment gateway fees deducted from gross transaction amounts prior to merchant settlement.",
            rules=[
                "Standard US Commercial Card Fee: 2.9% + $0.30 per settled domestic transaction.",
                "Net Merchant Settlement = Gross Sale - (Gross Sale * 0.029 + 0.30).",
                "Cross-border international transactions incur an additional 1.50% currency/interchange fee."
            ],
            required_inputs=["gross_amount", "is_international"],
            calculation_procedure="fee = gross * 0.029 + 0.30; net = gross - fee",
            output_fields=["processing_fee", "net_merchant_proceeds"],
            authority_source="PayPal Merchant Rate Schedule & Visa Interchange Guidelines",
            verification_status=VerificationStatus.EMPIRICAL_RULE,
            confidence_score=0.98,
            limitations="Enterprise high-volume merchants may negotiate custom interchange-plus rate tiers."
        ),
        KnowledgeEntry(
            knowledge_id="kn_pay_003_disputes_chargebacks",
            domain=KnowledgeDomain.PAYMENTS_COMMERCE,
            topic="chargebacks_disputes",
            title="Chargeback Lifecycle & Fraud Dispute Protocol",
            definition="Formal financial reversal mechanism initiated by a cardholder or account owner via issuer due to unauthorized billing or product non-delivery.",
            rules=[
                "Chargeback filing incurs a non-refundable $15.00 to $25.00 merchant dispute fee.",
                "Legitimate repeated developer seat additions or multi-license orders must NOT be reported as duplicate fraud without checking invoice order IDs.",
                "Carrier signed delivery proof (e.g., front porch scan) provides definitive evidence resolving non-receipt disputes."
            ],
            required_inputs=["transaction_id", "evidence_source", "merchant_invoices"],
            calculation_procedure="evaluate_dispute_legitimacy(transaction_id, evidence_records)",
            output_fields=["dispute_recommendation", "evidence_confidence", "requires_chargeback"],
            authority_source="Consumer Credit Protection Act (Regulation E & Z) & PayPal Buyer Protection",
            verification_status=VerificationStatus.REGULATORY_STANDARD,
            confidence_score=1.0,
            limitations="Dispute filing deadlines vary between 60 and 120 days from transaction date."
        )
    ]

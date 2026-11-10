from typing import List
from ..models.investigation import (
    SyntheticInvestigationCase, InvestigationStatus, AnomalyClassification, RecommendedAction
)

def generate_investigations() -> List[SyntheticInvestigationCase]:
    cases = [
        # Case 1: Legitimate repeated charge (False positive for duplicate fraud)
        SyntheticInvestigationCase(
            case_id="case_inv_001_gitforge_licenses",
            user_id="usr_alex_chen",
            related_transaction_ids=["txn_alex_dup_license_1", "txn_alex_dup_license_2"],
            related_evidence_ids=[],
            status=InvestigationStatus.RESOLVED_LEGITIMATE,
            ground_truth_classification=AnomalyClassification.LEGITIMATE_REPEATED_CHARGE,
            expected_findings="Charges on October 14 are two distinct seat purchases (Order #GF-9101 and #GF-9102), not a billing duplicate error.",
            alternative_explanations=["Dual seat provisioning for project collaborator", "Accidental double-click in merchant cart"],
            confidence_score=0.96,
            recommended_action=RecommendedAction.NO_ACTION_REQUIRED,
            notes="Audit of merchant order metadata shows separate seat keys generated."
        ),
        # Case 2: Unusual spending spike (Legitimate planned hardware upgrade)
        SyntheticInvestigationCase(
            case_id="case_inv_002_standing_desk_spike",
            user_id="usr_alex_chen",
            related_transaction_ids=["txn_alex_volt_desk_sep"],
            related_evidence_ids=["evi_alex_delivery_monitor"],
            status=InvestigationStatus.RESOLVED_LEGITIMATE,
            ground_truth_classification=AnomalyClassification.SEASONAL_OR_PLANNED_SPIKE,
            expected_findings="Transaction $480.00 at Timber & Stone Hardware was 280% higher than average hardware ticket, but verified by residential delivery scan.",
            alternative_explanations=["Compromised card used for retail goods", "One-off ergonomic home office investment"],
            confidence_score=0.98,
            recommended_action=RecommendedAction.NO_ACTION_REQUIRED,
            notes="Delivery evidence matches user registered delivery address."
        ),
        # Case 3: Failed retry (Resolved benign)
        SyntheticInvestigationCase(
            case_id="case_inv_003_network_retry",
            user_id="usr_alex_chen",
            related_transaction_ids=["txn_alex_fail_retry_1", "txn_alex_fail_retry_2"],
            related_evidence_ids=[],
            status=InvestigationStatus.RESOLVED_LEGITIMATE,
            ground_truth_classification=AnomalyClassification.FAILED_RETRY,
            expected_findings="Initial $39.99 transaction timed out; subsequent retry completed successfully with only one net charge.",
            alternative_explanations=["Double debit", "Gateway timeout"],
            confidence_score=0.99,
            recommended_action=RecommendedAction.NO_ACTION_REQUIRED
        ),
        # Case 4: Delayed refund
        SyntheticInvestigationCase(
            case_id="case_inv_004_delayed_refund",
            user_id="usr_alex_chen",
            related_transaction_ids=["txn_alex_nordic_jacket", "txn_alex_nordic_refund"],
            related_evidence_ids=[],
            status=InvestigationStatus.RESOLVED_LEGITIMATE,
            ground_truth_classification=AnomalyClassification.DELAYED_REFUND,
            expected_findings="Merchant return took 23 days to post back to credit card. Refund has cleared.",
            alternative_explanations=["Lost return package in transit", "Merchant restocking review delay"],
            confidence_score=0.94,
            recommended_action=RecommendedAction.NO_ACTION_REQUIRED
        ),
        # Case 5: Contradictory travel booking (Potentially unauthorized / investigation)
        SyntheticInvestigationCase(
            case_id="case_inv_005_marcus_flight",
            user_id="usr_marcus_vance",
            related_transaction_ids=["txn_marcus_flight_disputed"],
            related_evidence_ids=["evi_marcus_travel_contradiction"],
            status=InvestigationStatus.INVESTIGATING,
            ground_truth_classification=AnomalyClassification.GENUINE_FRAUD_OR_UNAUTHORIZED,
            expected_findings="Airline booking booked under user credentials during hours when local calendar shows executive in on-site client meetings.",
            alternative_explanations=["Executive assistant booked travel for spouse/family", "Credential stuffing / compromised booking portal account"],
            confidence_score=0.78,
            recommended_action=RecommendedAction.PROMPT_USER_VERIFICATION,
            notes="Flagged for user review prior to opening formal dispute."
        )
    ]
    return cases

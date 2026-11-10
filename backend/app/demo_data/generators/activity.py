from typing import List
from ..models.activity import SyntheticActivityEvidence, EvidenceState, EvidenceType

def generate_activity_evidence() -> List[SyntheticActivityEvidence]:
    records = [
        # Alex Chen - Gym visit: Confirmed low usage
        SyntheticActivityEvidence(
            evidence_id="evi_alex_gym_visit_01",
            user_id="usr_alex_chen",
            evidence_type=EvidenceType.GYM_VISIT,
            related_merchant_id="mer_apex_fitness",
            related_subscription_id="sub_alex_apex_gym",
            related_transaction_ids=["txn_alex_gym_sub_sep"],
            event_timestamp="2026-09-14T07:22:10Z",
            evidence_source="apex_turnstile_rfid_log",
            confidence_level=1.0,
            evidence_state=EvidenceState.CONFIRMED,
            notes="Single card swipe recorded at Apex Athletic Downtown Turnstile 2 in September 2026."
        ),
        # Alex Chen - AI token subscription: Confirmed low usage
        SyntheticActivityEvidence(
            evidence_id="evi_alex_ai_telemetry",
            user_id="usr_alex_chen",
            evidence_type=EvidenceType.SUBSCRIPTION_USAGE,
            related_merchant_id="mer_ai_synth",
            related_subscription_id="sub_alex_ai_synth",
            related_transaction_ids=["txn_alex_ai_oct"],
            event_timestamp="2026-09-22T14:10:00Z",
            evidence_source="cognition_api_gateway_telemetry",
            confidence_level=0.95,
            evidence_state=EvidenceState.CONFIRMED,
            notes="Zero API query tokens consumed across the billing period ending October 2026."
        ),
        # Marcus Vance - Gym: MISSING evidence state!
        SyntheticActivityEvidence(
            evidence_id="evi_marcus_gym_telemetry_missing",
            user_id="usr_marcus_vance",
            evidence_type=EvidenceType.GYM_VISIT,
            related_merchant_id="mer_apex_fitness",
            related_subscription_id="sub_marcus_apex_gym",
            related_transaction_ids=["txn_marcus_gym_oct"],
            event_timestamp=None,
            evidence_source="apex_athletic_partner_api",
            confidence_level=0.0,
            evidence_state=EvidenceState.MISSING,
            notes="CRITICAL REASONING RULE: Merchant did not provide badge scan sync. Missing evidence MUST NOT be assumed to indicate zero attendance."
        ),
        # Delivery Confirmation for Alex Chen
        SyntheticActivityEvidence(
            evidence_id="evi_alex_delivery_monitor",
            user_id="usr_alex_chen",
            evidence_type=EvidenceType.DELIVERY_CONFIRMATION,
            related_merchant_id="mer_volt_circuits",
            related_transaction_ids=["txn_alex_volt_desk_sep"],
            event_timestamp="2026-09-18T16:45:00Z",
            evidence_source="carrier_signed_delivery",
            confidence_level=1.0,
            evidence_state=EvidenceState.CONFIRMED,
            notes="Package signed and delivered to residential front porch."
        ),
        # User reported cancellation
        SyntheticActivityEvidence(
            evidence_id="evi_sarah_cancellation_intent",
            user_id="usr_sarah_jenkins",
            evidence_type=EvidenceType.USER_CONFIRMED_CANCELLATION,
            related_merchant_id="mer_strata_cloud",
            related_subscription_id="sub_sarah_vault",
            related_transaction_ids=[],
            event_timestamp="2026-10-30T11:00:00Z",
            evidence_source="user_guardian_prompt",
            confidence_level=0.9,
            evidence_state=EvidenceState.USER_REPORTED,
            notes="User requested assistance cancelling redundant cloud backup account."
        ),
        # Contradictory evidence
        SyntheticActivityEvidence(
            evidence_id="evi_marcus_travel_contradiction",
            user_id="usr_marcus_vance",
            evidence_type=EvidenceType.TRAVEL_ACTIVITY,
            related_merchant_id="mer_aerowings",
            related_transaction_ids=["txn_marcus_flight_disputed"],
            event_timestamp="2026-10-12T19:30:00Z",
            evidence_source="airline_manifest_vs_calendar",
            confidence_level=0.5,
            evidence_state=EvidenceState.CONTRADICTORY,
            notes="Flight booking ticket issued under user name, but calendar shows attendance at local board summit."
        ),
    ]
    return records

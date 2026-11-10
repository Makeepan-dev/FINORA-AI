from typing import List
from .base import KnowledgeEntry, KnowledgeDomain, VerificationStatus

def get_consumer_commerce_entries() -> List[KnowledgeEntry]:
    return [
        KnowledgeEntry(
            knowledge_id="kn_com_001_tco",
            domain=KnowledgeDomain.CONSUMER_COMMERCE,
            topic="total_cost_of_ownership",
            title="Total Cost of Ownership (TCO) Over Useful Lifespan",
            definition="The complete economic cost of owning an asset, combining initial purchase price, shipping, taxes, setup fees, maintenance, and mandatory recurring subscriptions.",
            rules=[
                "Cheapest initial purchase price frequently masks high recurring or replacement costs.",
                "TCO = Acquisition Costs + (Monthly Recurring * 12 * Lifespan) + (Annual Maintenance * Lifespan).",
                "Product comparisons must evaluate annualized TCO rather than headline checkout price."
            ],
            required_inputs=["base_price", "shipping", "tax_rate", "setup_fee", "recurring_fee", "lifespan_years"],
            calculation_procedure="calculate_total_cost_of_ownership(price, shipping, tax, setup, maint, rec, years)",
            output_fields=["total_cost_of_ownership", "annualized_tco", "monthly_tco"],
            authority_source="Gartner IT Procurement TCO Framework & Consumer Reports Methodology",
            verification_status=VerificationStatus.VERIFIED_CANONICAL,
            confidence_score=1.0,
            limitations="Actual maintenance expenses may vary with user care and intensity of use."
        ),
        KnowledgeEntry(
            knowledge_id="kn_com_002_cost_per_use",
            domain=KnowledgeDomain.CONSUMER_COMMERCE,
            topic="cost_per_use",
            title="Cost-Per-Use (CPU) Efficiency Valuation",
            definition="The economic cost per utilization event. Used to evaluate recurring memberships (gyms, tools, streaming) and durable goods against pay-per-use alternatives.",
            rules=[
                "Cost Per Use = Total Cost / Verified Utilization Events.",
                "High recurring commitments with single-digit usage result in exorbitant cost per use (e.g. $120/mo gym with 1 visit = $120.00/workout).",
                "Missing telemetry from partner systems must NOT be assumed to indicate zero usage."
            ],
            required_inputs=["total_recurring_cost", "verified_usage_count"],
            calculation_procedure="calculate_cost_per_use(total_cost, usage_count)",
            output_fields=["cost_per_use", "efficiency_rating", "economic_alternative"],
            authority_source="Behavioral Economics Journal & FINORA Financial Guardian Core Invariants",
            verification_status=VerificationStatus.VERIFIED_CANONICAL,
            confidence_score=0.98,
            limitations="Psychological value of option availability (option value) may partially offset cost per use."
        ),
        KnowledgeEntry(
            knowledge_id="kn_com_003_value_scoring",
            domain=KnowledgeDomain.CONSUMER_COMMERCE,
            topic="value_score",
            title="Warranty, Durability & Quality Adjusted Value Scoring",
            definition="Multi-factor commerce metric that rates products on verified user ratings, manufacturer warranty duration, and expected lifespan against annualized cost.",
            rules=[
                "Never declare a product the best value solely because it has the lowest nominal price.",
                "A $300 product lasting 5 years ($60/yr) is economically superior to a $150 product failing after 1 year ($150/yr).",
                "Extended manufacturer warranties reduce unexpected replacement and repair exposure."
            ],
            required_inputs=["price", "quality_rating", "warranty_months", "expected_lifespan_years"],
            calculation_procedure="calculate_value_adjusted_score(price, rating, warranty, lifespan)",
            output_fields=["value_score", "annualized_acquisition_cost", "durability_index"],
            authority_source="ISO 9004 Quality Management & Consumer Product Safety Commission Guidelines",
            verification_status=VerificationStatus.EMPIRICAL_RULE,
            confidence_score=0.95,
            limitations="Subjective build-quality perception requires verified customer telemetry."
        )
    ]

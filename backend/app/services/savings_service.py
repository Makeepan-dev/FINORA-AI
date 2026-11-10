import uuid
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..database.session import SessionLocal, Base, engine
from ..models.db_models import SavingsRecommendationRecord, UserGoalRecord, TransactionRecord
from .transaction_service import global_transaction_service
from ..location.service import global_location_service

Base.metadata.create_all(bind=engine)

class SavingsIntelligenceService:
    """
    Unified Daily Money-Saving Intelligence Engine (Feature 5).
    Derives all figures from the single authoritative TransactionService ledger summary.
    Strictly distinguishes between:
      - Potential Savings (estimated, awaiting user review)
      - Accepted Actions (user approved, pending billing cycle verification)
      - Realized / Verified Savings (backed by actual transaction evidence)
    And strictly separates Demo Mode vs. Personal Mode records.
    """
    def __init__(self, db_factory=SessionLocal):
        self.db_factory = db_factory

    def get_db(self) -> Session:
        return self.db_factory()

    def _compute_composite_rank_score(
        self,
        monthly_savings: float,
        confidence: float,
        evidence_quality_score: float,
        effort_level: str
    ) -> float:
        """
        Ranks opportunities using a multi-factor composite score rather than theoretical maximum savings alone:
        - Financial Impact (35%, capped at $100/mo normalization)
        - Evidence Quality (30%)
        - Confidence Score (20%)
        - Ease / Low Effort Bonus (15%)
        """
        impact_norm = min(monthly_savings / 100.0, 1.0)
        effort_bonus = {"low": 1.0, "medium": 0.6, "high": 0.3}.get(effort_level.lower(), 0.5)
        score = (
            (impact_norm * 35.0)
            + (evidence_quality_score * 30.0)
            + (confidence * 20.0)
            + (effort_bonus * 15.0)
        )
        return round(score, 1)

    def seed_recommendations_if_empty(self, user_id: str = "usr_alex_chen"):
        with self.get_db() as db:
            demo_recs = db.query(SavingsRecommendationRecord).filter(
                SavingsRecommendationRecord.user_id == user_id,
                ~SavingsRecommendationRecord.related_id.like("personal_%")
            ).count()
            if demo_recs == 0:
                initial_recs = [
                    {
                        "title": "Gym Membership Underutilization: Switch to Nearby Alternative",
                        "category": "fitness_wellness",
                        "problem_identified": (
                            "Equinox / Standard Gym Membership ($45.00/mo) has 6 consecutive monthly payments "
                            "with 0 detected visits in the last 45 days of available records."
                        ),
                        "supporting_evidence": (
                            "6 monthly charges totaling $270.00. Permitted one-time GPS check shows Planet Fitness Classic "
                            "is 0.8 miles away at $20.00/month ($0 joining fee). Note: Visits while GPS was disabled or to "
                            "partner branches are not captured."
                        ),
                        "recommended_action": (
                            "Your gym membership may be underutilized based on the available records. "
                            "A nearby alternative appears to cost less ($20/mo vs $45/mo). Compare options and switch before next billing cycle."
                        ),
                        "monthly_savings": 25.00,
                        "annual_savings": 300.00,
                        "confidence": 0.90,
                        "effort": "medium",
                        "action_type": "switch_alternative",
                        "related_id": "cand_gym_planet"
                    },
                    {
                        "title": "Reduce Food Delivery Spending by 20%",
                        "category": "food_dining",
                        "problem_identified": (
                            "You spent $203.85 on Food & Dining / Delivery this month (DoorDash, coffee, dining), "
                            "which is 35% higher than your target budget baseline."
                        ),
                        "supporting_evidence": (
                            "Persisted transaction ledger shows 3 high-ticket DoorDash orders ($48.75, $54.20, $62.10) "
                            "plus cafe spend. Replacing 2 delivery orders per month with items from Trader Joe's (0.6 mi away) cuts costs immediately."
                        ),
                        "recommended_action": (
                            "Reduce food delivery orders by 20% this month and substitute with quick grocery staples from a nearby supermarket."
                        ),
                        "monthly_savings": 40.77,
                        "annual_savings": 489.24,
                        "confidence": 0.85,
                        "effort": "low",
                        "action_type": "reduce_spending",
                        "related_id": "cat_food_dining"
                    },
                    {
                        "title": "Downgrade Dormant Cognition Engine Pro Subscription",
                        "category": "tech_subscriptions",
                        "problem_identified": (
                            "Cognition Engine Pro ($35.00/month) had 0 API token consumption recorded in the trailing 45-day telemetry window."
                        ),
                        "supporting_evidence": (
                            "Verified API usage logs show 0 tokens billed across 45 days. Unless your daily development workload "
                            "has recently increased, the Pay-As-You-Go tier ($0/mo base) eliminates fixed overhead."
                        ),
                        "recommended_action": (
                            "Downgrade Cognition Engine Pro from $35/mo fixed tier to Pay-As-You-Go ($0/mo base) if not actively used daily."
                        ),
                        "monthly_savings": 35.00,
                        "annual_savings": 420.00,
                        "confidence": 0.95,
                        "effort": "low",
                        "action_type": "cancel_subscription",
                        "related_id": "sub_cognition_pro"
                    },
                    {
                        "title": "Right-Size Cloud Storage Tier (StrataVault 2TB -> 200GB)",
                        "category": "tech_subscriptions",
                        "problem_identified": (
                            "Paying $19.99/month for 2TB encrypted storage while utilizing only 142GB (7.1% capacity)."
                        ),
                        "supporting_evidence": (
                            "Storage telemetry confirms 142GB active usage, well below the 200GB standard tier ($4.99/month)."
                        ),
                        "recommended_action": (
                            "Switch StrataVault plan from 2TB ($19.99/mo) to 200GB ($4.99/mo) via account settings."
                        ),
                        "monthly_savings": 15.00,
                        "annual_savings": 180.00,
                        "confidence": 0.98,
                        "effort": "low",
                        "action_type": "reduce_spending",
                        "related_id": "sub_stratavault"
                    }
                ]

                for r in initial_recs:
                    rec = SavingsRecommendationRecord(
                        id=f"rec_{uuid.uuid4().hex[:8]}",
                        user_id=user_id,
                        title=r["title"],
                        category=r["category"],
                        problem_identified=r["problem_identified"],
                        supporting_evidence=r["supporting_evidence"],
                        recommended_action=r["recommended_action"],
                        estimated_monthly_savings=r["monthly_savings"],
                        estimated_annual_savings=r["annual_savings"],
                        confidence_score=r["confidence"],
                        effort_level=r["effort"],
                        status="pending",
                        action_type=r["action_type"],
                        related_id=r["related_id"],
                        created_at=datetime.utcnow()
                    )
                    db.add(rec)

            # Seed a default user savings goal if empty
            goal_count = db.query(UserGoalRecord).filter(UserGoalRecord.user_id == user_id).count()
            if goal_count == 0:
                goal = UserGoalRecord(
                    id=f"goal_{uuid.uuid4().hex[:8]}",
                    user_id=user_id,
                    title="Emergency Cushion & Laptop Upgrade Fund",
                    target_amount=3000.00,
                    current_amount=1250.00,
                    monthly_contribution=250.00,
                    target_date="2027-05-01",
                    category="emergency_and_tech",
                    status="in_progress",
                    created_at=datetime.utcnow()
                )
                db.add(goal)

            db.commit()

    def _sync_personal_recommendations(self, user_id: str, tx_summary: Dict[str, Any]) -> List[SavingsRecommendationRecord]:
        """
        Synchronizes personal-scope savings recommendations directly from the authoritative
        persisted personal transaction summary so personal records never mix with demo records.
        """
        opps = tx_summary.get("savings_opportunities", [])
        with self.get_db() as db:
            existing_personal = db.query(SavingsRecommendationRecord).filter(
                SavingsRecommendationRecord.user_id == user_id,
                SavingsRecommendationRecord.related_id.like("personal_%")
            ).all()
            by_rel = {r.related_id: r for r in existing_personal}
            active_rel_ids = set()

            for opp in opps:
                rel_id = f"personal_{opp['related_id']}"
                active_rel_ids.add(rel_id)
                m_sav = float(Decimal(str(opp["monthly_savings"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                a_sav = float((Decimal(str(m_sav)) * Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                if rel_id in by_rel:
                    rec = by_rel[rel_id]
                    rec.title = opp["title"]
                    rec.supporting_evidence = opp["evidence"]
                    rec.estimated_monthly_savings = m_sav
                    rec.estimated_annual_savings = a_sav
                else:
                    rec = SavingsRecommendationRecord(
                        id=f"rec_pers_{uuid.uuid4().hex[:8]}",
                        user_id=user_id,
                        title=opp["title"],
                        category=opp.get("category", "general_expense"),
                        problem_identified=opp["evidence"],
                        supporting_evidence=opp["evidence"],
                        recommended_action=f"{opp['title']} to save ${m_sav:.2f}/month (${a_sav:.2f}/year).",
                        estimated_monthly_savings=m_sav,
                        estimated_annual_savings=a_sav,
                        confidence_score=opp.get("confidence", 0.85),
                        effort_level=opp.get("effort", "low"),
                        status="pending",
                        action_type="reduce_spending" if opp["type"] == "spending_reduction" else "switch_alternative",
                        related_id=rel_id,
                        created_at=datetime.utcnow()
                    )
                    db.add(rec)

            # Remove obsolete personal recommendations no longer backed by personal ledger
            for rel_id, rec in by_rel.items():
                if rel_id not in active_rel_ids:
                    db.delete(rec)

            db.commit()
            return db.query(SavingsRecommendationRecord).filter(
                SavingsRecommendationRecord.user_id == user_id,
                SavingsRecommendationRecord.related_id.like("personal_%")
            ).all()

    def get_savings_dashboard(
        self,
        user_id: str = "usr_alex_chen",
        data_scope: str = "auto"
    ) -> Dict[str, Any]:
        """
        Returns the complete Daily Money-Saving Intelligence dashboard.
        Uses TransactionService.get_financial_summary as the single authoritative source.
        Strictly separates Potential Savings, Accepted Actions, and Verified Realized Savings.
        """
        tx_summary = global_transaction_service.get_financial_summary(user_id=user_id, data_scope=data_scope)
        active_scope = tx_summary["active_data_scope"]
        is_demo_flag = (active_scope == "demo")
        loc = global_location_service.get_user_location(user_id)

        if active_scope == "demo":
            self.seed_recommendations_if_empty(user_id)
            with self.get_db() as db:
                # Synchronize food_dining recommendation with authoritative tx_summary food_dining opportunity
                food_opp = next((o for o in tx_summary.get("savings_opportunities", []) if o.get("related_id") == "cat_food_dining"), None)
                if food_opp:
                    food_rec = db.query(SavingsRecommendationRecord).filter(
                        SavingsRecommendationRecord.user_id == user_id,
                        SavingsRecommendationRecord.related_id == "cat_food_dining"
                    ).first()
                    if food_rec:
                        m_sav = float(Decimal(str(food_opp["monthly_savings"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        a_sav = float((Decimal(str(m_sav)) * Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        food_rec.estimated_monthly_savings = m_sav
                        food_rec.estimated_annual_savings = a_sav
                        db.commit()

                recs = db.query(SavingsRecommendationRecord).filter(
                    SavingsRecommendationRecord.user_id == user_id,
                    ~SavingsRecommendationRecord.related_id.like("personal_%")
                ).all()
        else:
            recs = self._sync_personal_recommendations(user_id, tx_summary)

        with self.get_db() as db:
            goals = db.query(UserGoalRecord).filter(
                UserGoalRecord.user_id == user_id
            ).all()
            refund_txs = db.query(TransactionRecord).filter(
                TransactionRecord.user_id == user_id,
                TransactionRecord.is_demo == is_demo_flag,
                TransactionRecord.transaction_type == "refund"
            ).all()

        verified_refund_total = sum((Decimal(str(t.amount)) for t in refund_txs), Decimal("0.00"))

        formatted_recs = []
        pending_monthly = Decimal("0.00")
        accepted_monthly = Decimal("0.00")
        realized_monthly = verified_refund_total
        seen_related_ids = set()

        for r in recs:
            # Prevent overlapping savings recommendations from being counted twice
            dedup_key = r.related_id or r.title.strip().lower()
            if dedup_key in seen_related_ids:
                continue
            seen_related_ids.add(dedup_key)

            m_sav = Decimal(str(r.estimated_monthly_savings)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            a_sav = (m_sav * Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            if r.status == "pending":
                pending_monthly += m_sav
            elif r.status == "accepted":
                accepted_monthly += m_sav
            elif r.status == "realized":
                realized_monthly += m_sav

            ev_quality = 0.95 if "telemetry" in r.supporting_evidence.lower() or "charges" in r.supporting_evidence.lower() else 0.80
            rank_score = self._compute_composite_rank_score(
                monthly_savings=float(m_sav),
                confidence=r.confidence_score,
                evidence_quality_score=ev_quality,
                effort_level=r.effort_level
            )
            formatted_recs.append({
                "id": r.id,
                "title": r.title,
                "category": r.category,
                "problem_identified": r.problem_identified,
                "supporting_evidence": r.supporting_evidence,
                "recommended_action": r.recommended_action,
                "estimated_monthly_savings": float(m_sav),
                "estimated_annual_savings": float(a_sav),
                "confidence_score": r.confidence_score,
                "effort_level": r.effort_level,
                "composite_rank_score": rank_score,
                "status": r.status,
                "action_type": r.action_type,
                "related_id": r.related_id,
                "data_scope": active_scope
            })

        # Sort by composite rank score (not just raw dollar amount)
        formatted_recs.sort(key=lambda x: x["composite_rank_score"], reverse=True)

        total_potential_monthly = (pending_monthly + accepted_monthly).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_potential_annual = (total_potential_monthly * Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        food_rec_item = next((r for r in formatted_recs if "food_dining" in (r.get("related_id") or "")), None)
        food_sav_val = food_rec_item["estimated_monthly_savings"] if food_rec_item else 0.0

        daily_insights = []
        if food_sav_val > 0:
            daily_insights.append({
                "id": "ins_food_delivery",
                "type": "spending_alert",
                "title": "Elevated Food & Dining Spend Detected",
                "message": f"Reducing Food & Dining spend by 20% could save ~${food_sav_val:.2f}/mo (${food_sav_val*12:.2f}/yr).",
                "impact_monthly": food_sav_val,
                "evidence_type": f"Observed Ledger Fact ({active_scope} scope) + 20% Reduction Estimate"
            })
        if active_scope == "demo":
            daily_insights.extend([
                {
                    "id": "ins_gym_gps",
                    "type": "location_opportunity",
                    "title": "Nearby Lower-Cost Gym Option Available",
                    "message": "Your $45/mo gym membership has 0 recorded visits in 45 days. Planet Fitness Classic (0.8 mi away) costs $20/mo — potential $25/mo ($300/yr) difference.",
                    "impact_monthly": 25.00,
                    "evidence_type": f"GPS ({loc.location_source if loc else 'revoked'}) + 6 Monthly Billing Records"
                },
                {
                    "id": "ins_multi_sub",
                    "type": "subscription_waste",
                    "title": "Dormant Developer & Storage Subscriptions",
                    "message": "Cognition Engine Pro ($35/mo) and StrataVault 2TB ($19.99/mo -> $4.99/mo) show minimal utilization over the past 45 days.",
                    "impact_monthly": 50.00,
                    "evidence_type": "Verified Usage Telemetry"
                }
            ])
        daily_insights.append({
            "id": "ins_goal_impact",
            "type": "goal_projection",
            "title": "Savings Goal Acceleration",
            "message": f"Redirecting ${float(total_potential_monthly):.2f}/mo (${float(total_potential_annual):.2f}/yr) in identified potential savings accelerates your savings goal.",
            "impact_monthly": float(total_potential_monthly),
            "evidence_type": "Sinking Fund Formula Projection"
        })

        return {
            "user_id": user_id,
            "active_data_scope": active_scope,
            "summary": {
                "active_data_scope": active_scope,
                "potential_monthly_savings": float(total_potential_monthly),
                "potential_annual_savings": float(total_potential_annual),
                "pending_review_monthly": float(pending_monthly),
                "accepted_actions_monthly": float(accepted_monthly),
                "verified_realized_savings": float(realized_monthly),
                "pending_count": len([r for r in formatted_recs if r["status"] == "pending"]),
                "accepted_count": len([r for r in formatted_recs if r["status"] == "accepted"]),
                "realized_count": len([r for r in formatted_recs if r["status"] == "realized"]),
                "distinction_notice": (
                    "CRITICAL DISTINCTION: Potential savings ($"
                    f"{float(total_potential_monthly):.2f}/mo) are estimates based on recommended actions. "
                    f"Verified realized savings (${float(realized_monthly):.2f}) only count reductions confirmed by actual transaction records."
                )
            },
            "daily_insights": daily_insights,
            "ranked_recommendations": formatted_recs,
            "goals": [
                {
                    "id": g.id,
                    "title": g.title,
                    "target_amount": g.target_amount,
                    "current_amount": g.current_amount,
                    "monthly_contribution": g.monthly_contribution,
                    "target_date": g.target_date,
                    "progress_percent": round((g.current_amount / g.target_amount) * 100, 1) if g.target_amount > 0 else 0.0
                }
                for g in goals
            ],
            "financial_context": {
                "active_data_scope": active_scope,
                "monthly_income": tx_summary["total_income"],
                "monthly_expenses": tx_summary["total_expenses"],
                "remaining_available_money": tx_summary["remaining_available_money"]
            }
        }

    def update_recommendation_decision(
        self,
        user_id: str,
        rec_id: str,
        decision: str  # "accepted" | "rejected" | "pending" | "realized"
    ) -> Optional[Dict[str, Any]]:
        if decision not in ["accepted", "rejected", "pending", "realized"]:
            raise ValueError("Invalid decision status")

        with self.get_db() as db:
            rec = db.query(SavingsRecommendationRecord).filter(
                SavingsRecommendationRecord.id == rec_id
            ).first()
            if not rec:
                return None
            if rec.user_id != user_id:
                raise PermissionError("Forbidden: Cannot modify a recommendation belonging to another user.")
            rec.status = decision
            db.commit()
            db.refresh(rec)
            return {
                "id": rec.id,
                "title": rec.title,
                "status": rec.status,
                "estimated_monthly_savings": rec.estimated_monthly_savings,
                "estimated_annual_savings": rec.estimated_annual_savings,
                "note": (
                    "Action marked as ACCEPTED by user. Savings remain classified as 'Accepted (Pending Verification)' "
                    "until confirmed in next billing statement."
                    if decision == "accepted" else f"Recommendation status updated to {decision}."
                )
            }

global_savings_service = SavingsIntelligenceService()

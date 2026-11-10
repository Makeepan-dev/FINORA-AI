from decimal import Decimal
from typing import List, Dict, Any, Optional
from ..demo_data.dataset_manager import global_dataset_manager
from ..services.analytics_service import global_analytics_service
from ..algorithms.commerce_intelligence import (
    calculate_total_cost_of_ownership,
    calculate_value_adjusted_score
)
from ..algorithms.decimal_math import to_decimal

class ShoppingAgent:
    """
    Autonomous Shopping Assistant for FINORA.
    Driven by shared Commerce Intelligence algorithms:
    Evaluates multi-factor total cost of ownership (price + shipping + warranty duration),
    ranks products by durability and quality-adjusted value score, and enforces budget gates.
    """
    def __init__(self):
        self.dataset_mgr = global_dataset_manager
        self.analytics = global_analytics_service

    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        results = []
        q = query.lower() if query else ""
        cat = category.lower() if category else ""

        for p in self.dataset_mgr.products:
            if q and (q not in p.product_name.lower() and q not in p.description.lower()):
                continue
            if cat and cat != "all" and p.category.value != cat:
                continue
            if max_price is not None and float(p.total_cost) > max_price:
                continue

            # Estimate useful lifespan based on category & warranty
            lifespan_yr = 3 if p.category.value in ["electronics", "hardware"] else 2
            val_eval = calculate_value_adjusted_score(
                price=p.total_cost,
                quality_rating=p.rating,
                warranty_months=p.warranty_months,
                expected_lifespan_years=lifespan_yr
            )

            results.append({
                "product_id": p.product_id,
                "merchant_id": p.merchant_id,
                "product_name": p.product_name,
                "description": p.description,
                "category": p.category.value,
                "price": float(p.price),
                "shipping_cost": float(p.shipping_cost),
                "total_cost": float(p.total_cost),
                "currency": p.currency,
                "availability": p.availability,
                "rating": p.rating,
                "review_count": p.review_count,
                "delivery_days": p.estimated_delivery_days,
                "warranty_months": p.warranty_months,
                "expected_lifespan_years": lifespan_yr,
                "value_score": val_eval["value_score"],
                "specifications": p.specifications
            })
        return results

    def evaluate_purchase_budget(
        self,
        product_id: str,
        user_id: str = "usr_alex_chen"
    ) -> Dict[str, Any]:
        """Calculates exact total cost on backend and checks remaining monthly budget."""
        product = next((p for p in self.dataset_mgr.products if p.product_id == product_id), None)
        if not product:
            raise ValueError(f"Product {product_id} not found.")

        user_metrics = self.analytics.get_user_dashboard_metrics(user_id=user_id)
        budgets = user_metrics.get("budget_progress", [])

        # Match product category to budget category
        cat_budget = next((b for b in budgets if b["category"].lower() == product.category.value), None)

        remaining_budget = cat_budget["remaining"] if cat_budget else 500.00
        total_cost = float(product.total_cost)
        is_within_budget = total_cost <= remaining_budget
        variance = remaining_budget - total_cost

        # Calculate 3-year TCO
        tco = calculate_total_cost_of_ownership(
            base_price=product.price,
            shipping_cost=product.shipping_cost,
            lifespan_years=3
        )

        return {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "price": float(product.price),
            "shipping_cost": float(product.shipping_cost),
            "total_cost": total_cost,
            "category": product.category.value,
            "monthly_category_limit": cat_budget["limit"] if cat_budget else 500.0,
            "remaining_budget_before_purchase": remaining_budget,
            "remaining_budget_after_purchase": max(0.0, remaining_budget - total_cost),
            "is_within_budget": is_within_budget,
            "budget_variance": variance,
            "tco_analysis": tco,
            "recommendation": (
                "Approved: Purchase fits cleanly within your monthly discretionary budget."
                if is_within_budget else
                f"Caution: Total cost (${total_cost:.2f}) exceeds remaining category budget (${remaining_budget:.2f}) by ${abs(variance):.2f}. User authorization override required."
            )
        }

    def compare_products(self, product_ids: List[str], target_budget: Optional[float] = None) -> Dict[str, Any]:
        items = []
        for pid in product_ids:
            p = next((prod for prod in self.dataset_mgr.products if prod.product_id == pid), None)
            if p:
                lifespan_yr = 3 if p.category.value in ["electronics", "hardware"] else 2
                val_eval = calculate_value_adjusted_score(
                    price=p.total_cost,
                    quality_rating=p.rating,
                    warranty_months=p.warranty_months,
                    expected_lifespan_years=lifespan_yr
                )
                items.append({
                    "product_id": p.product_id,
                    "product_name": p.product_name,
                    "price": float(p.price),
                    "shipping_cost": float(p.shipping_cost),
                    "total_cost": float(p.total_cost),
                    "rating": p.rating,
                    "delivery_days": p.estimated_delivery_days,
                    "warranty_months": p.warranty_months,
                    "value_score": val_eval["value_score"],
                    "annualized_cost": val_eval["annualized_acquisition_cost"],
                    "specifications": p.specifications
                })

        # Rank by value_score (quality & warranty per dollar) rather than nominal price alone
        items_sorted = sorted(items, key=lambda x: x["value_score"], reverse=True)
        recommended = items_sorted[0] if items_sorted else None

        reasoning = ""
        if recommended:
            reasoning = (
                f"Recommended '{recommended['product_name']}' based on highest Value Score ({recommended['value_score']}/100). "
                f"Combines {recommended['warranty_months']} months warranty protection, a {recommended['rating']}/5.0 customer rating, "
                f"and an annualized acquisition cost of ${recommended['annualized_cost']:.2f}/year."
            )

        return {
            "items": items_sorted,
            "recommended_product_id": recommended["product_id"] if recommended else None,
            "reasoning": reasoning,
            "target_budget": target_budget,
            "ranking_method": "Multi-factor durability, warranty duration, and customer rating per dollar."
        }

global_shopping_agent = ShoppingAgent()

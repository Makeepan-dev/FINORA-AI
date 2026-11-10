from fastapi import APIRouter, Body, Query, Header, HTTPException
from typing import Dict, Any, List, Optional
from ..location.service import global_location_service
from ..location.discovery import global_business_discovery
from ..core.security import resolve_authorized_user

router = APIRouter(prefix="/location", tags=["Location Intelligence & Business Discovery"])

@router.get("/status")
def get_location_status(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """Returns location permission state and coordinates for active user."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    loc = global_location_service.get_user_location(auth_user)
    if not loc:
        perm_state = global_location_service.get_permission_state(auth_user)
        return {
            "user_id": auth_user,
            "is_granted": False,
            "precision_mode": "disabled",
            "access_type": "disabled",
            "latitude": None,
            "longitude": None,
            "city": perm_state.city,
            "location_source": "revoked"
        }
    return loc.model_dump()

@router.post("/permission")
def update_location_permission(
    user_id: str = Body(default="usr_alex_chen", embed=True),
    is_granted: bool = Body(..., embed=True),
    precision_mode: str = Body(default="approximate", embed=True),
    access_type: str = Body(default="one_time", embed=True),
    latitude: Optional[float] = Body(default=None, embed=True),
    longitude: Optional[float] = Body(default=None, embed=True),
    city: Optional[str] = Body(default=None, embed=True),
    postal_code: Optional[str] = Body(default=None, embed=True),
    location_source: Optional[str] = Body(default=None, embed=True),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """Updates user location permission, coordinates, and access type."""
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    perm = global_location_service.update_permission(
        user_id=auth_user,
        is_granted=is_granted,
        precision_mode=precision_mode,
        access_type=access_type,
        latitude=latitude,
        longitude=longitude,
        city=city,
        postal_code=postal_code,
        location_source=location_source
    )
    return perm.model_dump()

@router.get("/nearby")
def discover_nearby_businesses(
    category: str = Query(default="fitness"),
    user_id: str = Query(default="usr_alex_chen"),
    max_distance_miles: float = Query(default=10.0),
    current_monthly_spend: Optional[float] = Query(default=None),
    allow_demo_benchmark: bool = Query(default=False),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> List[Dict[str, Any]]:
    """
    Discovers verified local business alternatives within user's permitted perimeter.
    When GPS permission is revoked or denied, returns an empty list unless
    allow_demo_benchmark=True is explicitly requested.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    return global_business_discovery.find_nearby_alternatives(
        category=category,
        user_id=auth_user,
        max_distance_miles=max_distance_miles,
        current_monthly_spend=current_monthly_spend,
        allow_demo_benchmark=allow_demo_benchmark
    )

@router.get("/live-osm")
async def discover_live_osm_places(
    latitude: float = Query(..., description="Permitted or manual latitude"),
    longitude: float = Query(..., description="Permitted or manual longitude"),
    category: str = Query(default="groceries"),
    radius_meters: int = Query(default=3000, ge=500, le=10000),
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """
    Queries OpenStreetMap Overpass API for real-world places around the given coordinates.
    Requires active location permission or manual coordinate authorization.
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    loc = global_location_service.get_user_location(auth_user)
    if not loc or not loc.is_granted:
        raise HTTPException(
            status_code=403,
            detail="Location permission is currently revoked or denied. Grant one-time GPS or enter a manual location first."
        )
    return await global_business_discovery.discover_live_osm_places(
        latitude=latitude,
        longitude=longitude,
        category=category,
        radius_meters=radius_meters
    )

@router.get("/gym-scenario")
def get_gym_cross_module_scenario(
    user_id: str = Query(default="usr_alex_chen"),
    x_finora_session_token: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """
    Returns the complete cross-module Gym Membership demonstration scenario
    connecting Financial Records, Location Intelligence, Subscription Analysis, and AI Recommendations.
    Uses the authoritative calculate_net_switch_savings formula (4 round-trips/mo at $0.67/mile).
    """
    auth_user = resolve_authorized_user(user_id, x_finora_session_token)
    loc = global_location_service.get_user_location(auth_user)
    loc_enabled = loc is not None and loc.is_granted and loc.latitude is not None
    loc_source = loc.location_source if loc_enabled and loc else "revoked"

    net_math = global_business_discovery.calculate_net_switch_savings(
        current_monthly_spend=45.00,
        alternative_monthly_price=20.00,
        distance_miles=0.8,
        trips_per_month=4,
        transport_cost_per_mile=0.67
    )

    return {
        "scenario_title": "Cross-Module Gym Membership Underutilization & Local Alternative Analysis",
        "current_membership": {
            "name": "Equinox / Standard Gym Membership",
            "monthly_cost": 45.00,
            "annual_cost": 540.00,
            "consecutive_monthly_payments": 6,
            "total_paid_6_months": 270.00,
            "last_detected_visit_days_ago": 45,
            "detected_visits_last_45_days": 0
        },
        "nearby_alternative": {
            "name": "Planet Fitness Classic",
            "distance_miles": 0.8 if loc_enabled else None,
            "monthly_cost": 20.00,
            "annual_cost": 240.00,
            "joining_fee": 0.00,
            "price_verification": "Verified Demo Rate Card ($20/month)",
            "location_permission_required": not loc_enabled
        },
        "savings_calculation": {
            "monthly_difference": net_math["gross_monthly_savings"],
            "annual_difference": round(net_math["gross_monthly_savings"] * 12.0, 2),
            "estimated_transport_cost_monthly": net_math["estimated_monthly_transport_cost"],
            "net_monthly_savings_after_transport": net_math["net_monthly_savings"],
            "net_annual_savings_after_transport": net_math["net_annual_savings"],
            "transport_assumptions": net_math["assumptions"]
        },
        "evidence_and_caveats": {
            "classification": "POTENTIALLY_UNDERUTILIZED",
            "location_tracking_enabled": loc_enabled,
            "location_source": loc_source,
            "available_location_data": (
                f"One-time permitted location ({loc.city}, {loc.latitude:.4f}, {loc.longitude:.4f})"
                if loc_enabled and loc else "Location access currently disabled or revoked (no default coordinates used)"
            ),
            "missing_records_disclosure": "FINORA does not perform continuous background GPS tracking. Visits made while location access was off are not recorded.",
            "alternative_branches_caveat": "You may have visited partner or suburban gym branches without digital turnstile sync.",
            "other_activity_caveat": "No external wearable or Apple Health/Google Fit workout logs are connected."
        },
        "advisor_message": (
            "Your gym membership may be underutilized based on the available records. "
            "A nearby alternative appears to cost less. Would you like to compare the options?"
        ),
        "user_permission_policy": "FINORA will never automatically cancel or modify your membership. You must explicitly review and approve any action."
    }

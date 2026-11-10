from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class LocationPermissionState(BaseModel):
    user_id: str
    is_granted: bool = True
    precision_mode: str = "approximate"  # "approximate" | "precise" | "disabled"
    access_type: str = "one_time"  # "one_time" | "disabled" (never continuous background tracking)
    latitude: Optional[float] = 37.7749
    longitude: Optional[float] = -122.4194
    city: str = "San Francisco (Demo Default)"
    postal_code: str = "94103"
    location_source: str = "demo_default"  # "browser_gps" | "manual_selection" | "demo_default" | "revoked"
    last_updated: str = "2026-11-10T12:00:00Z"

class LocationIntelligenceService:
    """
    Permission-based location intelligence service.
    Enforces explicit user consent before retrieving location or discovering nearby businesses.
    Never performs continuous background tracking.
    When permission is revoked or denied, coordinates are cleared (None) and never silently
    fall back to San Francisco unless Demo Benchmark mode or manual location is explicitly selected.
    """
    def __init__(self):
        self._permissions: Dict[str, LocationPermissionState] = {
            "usr_alex_chen": LocationPermissionState(
                user_id="usr_alex_chen",
                is_granted=True,
                precision_mode="approximate",
                access_type="one_time",
                latitude=37.7749,
                longitude=-122.4194,
                city="San Francisco",
                postal_code="94103",
                location_source="demo_default"
            )
        }

    def get_user_location(self, user_id: str = "usr_alex_chen") -> Optional[LocationPermissionState]:
        perm = self._permissions.get(user_id)
        if not perm or not perm.is_granted or perm.precision_mode == "disabled" or perm.location_source == "revoked":
            return None
        return perm

    def get_permission_state(self, user_id: str = "usr_alex_chen") -> LocationPermissionState:
        perm = self._permissions.get(user_id)
        if not perm:
            return LocationPermissionState(
                user_id=user_id,
                is_granted=False,
                precision_mode="disabled",
                access_type="disabled",
                latitude=None,
                longitude=None,
                city="Permission Not Granted",
                postal_code="",
                location_source="revoked"
            )
        return perm

    def update_permission(
        self,
        user_id: str,
        is_granted: bool,
        precision_mode: str = "approximate",
        access_type: str = "one_time",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        city: Optional[str] = None,
        postal_code: Optional[str] = None,
        location_source: Optional[str] = None
    ) -> LocationPermissionState:
        # Never allow continuous tracking
        safe_access_type = "one_time" if is_granted else "disabled"
        perm = self._permissions.setdefault(user_id, LocationPermissionState(user_id=user_id))
        perm.is_granted = is_granted
        perm.precision_mode = precision_mode if is_granted else "disabled"
        perm.access_type = safe_access_type

        if not is_granted:
            # Strict Privacy Rule: Clear active coordinates when permission is revoked/denied
            perm.latitude = None
            perm.longitude = None
            perm.city = "Location Permission Revoked"
            perm.postal_code = ""
            perm.location_source = "revoked"
        else:
            if latitude is not None and longitude is not None:
                perm.latitude = float(latitude)
                perm.longitude = float(longitude)
            elif perm.latitude is None or perm.longitude is None:
                # Only restore demo benchmark coordinates when explicitly re-enabling Demo Benchmark mode
                if location_source in [None, "demo_default"]:
                    perm.latitude = 37.7749
                    perm.longitude = -122.4194
                    perm.city = city or "San Francisco (Demo Default)"
                    perm.postal_code = postal_code or "94103"
                    perm.location_source = "demo_default"
            if city:
                perm.city = city
            if postal_code is not None:
                perm.postal_code = postal_code
            if location_source:
                perm.location_source = location_source
            elif perm.location_source == "revoked":
                perm.location_source = "demo_default"

        perm.last_updated = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return perm

global_location_service = LocationIntelligenceService()

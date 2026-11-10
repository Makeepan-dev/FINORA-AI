from fastapi import APIRouter, Body
from ..core.config import settings
from ..demo_data.dataset_manager import global_dataset_manager

router = APIRouter(prefix="/settings", tags=["Application Settings"])

@router.get("/status")
def get_system_settings():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai": {
            "provider": settings.AI_PRIMARY_PROVIDER,
            "model": getattr(settings, "AI_MODEL", "gemini-flash-lite-latest"),
            "allow_paid_models": settings.ALLOW_PAID_MODELS,
            "max_spend_usd": settings.MAX_API_SPEND_USD,
            "has_gemini_key": bool(settings.GEMINI_API_KEY),
            "has_groq_key": bool(settings.GROQ_API_KEY),
            "has_openrouter_key": bool(settings.OPENROUTER_API_KEY)
        },
        "paypal": {
            "mode": settings.PAYPAL_MODE,
            "configured": bool(settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET)
        },
        "active_scenario_id": global_dataset_manager.active_scenario_id,
        "available_users": [
            {"user_id": u.user_id, "name": u.full_name, "role": u.employment_status}
            for u in global_dataset_manager.users
        ]
    }

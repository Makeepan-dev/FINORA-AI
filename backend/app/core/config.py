import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine candidate .env locations
_BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
_ROOT_DIR = _BASE_DIR.parent  # FINORA/

_ENV_FILES = [
    str(_BASE_DIR / ".env"),
    str(_ROOT_DIR / ".env"),
    ".env",
    "backend/.env"
]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        extra="ignore"
    )

    PROJECT_NAME: str = "FINORA"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # AI Configuration — Zero Cost Rules
    AI_PRIMARY_PROVIDER: str = "gemini"  # gemini, groq, openrouter, cerebras, deterministic
    AI_MODEL: str = "gemini-flash-lite-latest"
    ALLOW_PAID_MODELS: bool = False
    ALLOW_AUTO_RECHARGE: bool = False
    MAX_API_SPEND_USD: float = 0.0

    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""

    # PayPal Configuration — Sandbox & Live
    PAYPAL_MODE: str = "sandbox"
    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_CLIENT_SECRET: str = ""
    PAYPAL_API_BASE: str = "https://api.sandbox.paypal.com"
    PAYPAL_WEBHOOK_ID: str = ""
    PAYPAL_REQUIRE_WEBHOOK_VERIFICATION: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./finora.db"

settings = Settings()

def reload_settings() -> Settings:
    global settings
    settings = Settings()
    return settings

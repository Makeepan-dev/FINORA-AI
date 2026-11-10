import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine whether running as packaged Windows desktop executable
IS_FROZEN = getattr(sys, "frozen", False)
IS_DESKTOP_MODE = IS_FROZEN or os.environ.get("FINORA_DESKTOP_MODE") == "1"


def get_desktop_data_dir() -> Path:
    custom_dir = os.environ.get("FINORA_DATA_DIR")
    if custom_dir:
        data_dir = Path(custom_dir)
    else:
        appdata = os.environ.get("APPDATA")
        if appdata:
            data_dir = Path(appdata) / "FINORA"
        else:
            data_dir = Path.home() / "AppData" / "Roaming" / "FINORA"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


# Determine candidate .env locations
_BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
_ROOT_DIR = _BASE_DIR.parent  # FINORA/

if IS_DESKTOP_MODE:
    _DESKTOP_DIR = get_desktop_data_dir()
    _ENV_FILES = [str(_DESKTOP_DIR / ".env")]
    _DEFAULT_DB_URL = f"sqlite:///{(_DESKTOP_DIR / 'finora.db').as_posix()}"
else:
    _ENV_FILES = [
        str(_BASE_DIR / ".env"),
        str(_ROOT_DIR / ".env"),
        ".env",
        "backend/.env"
    ]
    _DEFAULT_DB_URL = "sqlite:///./finora.db"


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
    DATABASE_URL: str = _DEFAULT_DB_URL

settings = Settings()

def reload_settings() -> Settings:
    global settings
    settings = Settings()
    return settings

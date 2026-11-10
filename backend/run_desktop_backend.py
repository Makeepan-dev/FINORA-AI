import argparse
import os
import sys
from pathlib import Path

# Enforce desktop mode before importing application modules
os.environ.setdefault("FINORA_DESKTOP_MODE", "1")

# Explicit imports for PyInstaller static analysis
import sqlalchemy.dialects.sqlite  # noqa: F401, E402
import uvicorn  # noqa: E402
import uvicorn.lifespan.on  # noqa: F401, E402
import uvicorn.logging  # noqa: F401, E402
import uvicorn.loops.auto  # noqa: F401, E402
import uvicorn.protocols.http.auto  # noqa: F401, E402
import uvicorn.protocols.websockets.auto  # noqa: F401, E402

from app.core.config import get_desktop_data_dir  # noqa: E402
import app.models.db_models  # noqa: F401, E402
from app.main import app as fastapi_app  # noqa: E402


_ENV_TEMPLATE = """# FINORA Desktop User Configuration (%APPDATA%\\FINORA\\.env)
# Rename or copy this file to .env in this folder to configure optional live integrations.
# Never commit real credentials to version control.

AI_PRIMARY_PROVIDER=gemini
AI_MODEL=gemini-flash-lite-latest
ALLOW_PAID_MODELS=False
MAX_API_SPEND_USD=0.0
GEMINI_API_KEY=

PAYPAL_MODE=sandbox
PAYPAL_API_BASE=https://api.sandbox.paypal.com
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
PAYPAL_WEBHOOK_ID=
PAYPAL_REQUIRE_WEBHOOK_VERIFICATION=True
"""


def ensure_desktop_appdata_template() -> Path:
    data_dir = get_desktop_data_dir()
    example_file = data_dir / ".env.example"
    if not example_file.exists():
        try:
            example_file.write_text(_ENV_TEMPLATE, encoding="utf-8")
        except OSError:
            pass
    return data_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="FINORA Packaged Desktop Backend Server")
    parser.add_argument("--host", default=os.environ.get("FINORA_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("FINORA_PORT", "8000")))
    args = parser.parse_args()

    ensure_desktop_appdata_template()

    uvicorn.run(
        fastapi_app,
        host=args.host,
        port=args.port,
        interface="asgi3",
        log_level="info",
        access_log=False,
    )


if __name__ == "__main__":
    main()

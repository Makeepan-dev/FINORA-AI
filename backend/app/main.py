import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .core.config import settings, IS_DESKTOP_MODE, get_desktop_data_dir
from .database.session import engine, Base
from .api import (
    demo_data, analytics, guardian, shopping, payments,
    settings as settings_api, income, connections,
    knowledge, optimization, location, automation,
    formulas, composition, transactions, savings
)

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Financial Intelligence Network for Optimization, Reasoning & Automation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes (support both /api and /api/v1 for robust client compatibility)
all_routers = [
    demo_data.router, analytics.router, guardian.router, shopping.router,
    payments.router, settings_api.router, income.router, connections.router,
    knowledge.router, optimization.router, location.router, automation.router,
    formulas.router, composition.router, transactions.router, savings.router
]

for r in all_routers:
    app.include_router(r, prefix=settings.API_V1_STR)
    app.include_router(r, prefix="/api/v1")


def _resolve_frontend_dist() -> Path | None:
    env_dist = os.environ.get("FINORA_FRONTEND_DIST")
    if env_dist:
        candidate = Path(env_dist)
        if (candidate / "index.html").is_file():
            return candidate
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidate = Path(getattr(sys, "_MEIPASS")) / "frontend_dist"
        if (candidate / "index.html").is_file():
            return candidate
    if IS_DESKTOP_MODE:
        candidate = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
        if (candidate / "index.html").is_file():
            return candidate
    return None


@app.get("/health")
def health_check():
    return {"status": "healthy"}


_FRONTEND_DIST = _resolve_frontend_dist()

if _FRONTEND_DIST is not None:
    _ASSETS_DIR = _FRONTEND_DIST / "assets"
    if _ASSETS_DIR.is_dir():
        app.mount("/assets", StaticFiles(directory=str(_ASSETS_DIR)), name="frontend_assets")

    @app.get("/", include_in_schema=False)
    def serve_spa_root():
        return FileResponse(str(_FRONTEND_DIST / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa_fallback(full_path: str):
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "health")):
            raise HTTPException(status_code=404, detail="Not Found")
        target = (_FRONTEND_DIST / full_path).resolve()
        if target.is_file() and str(target).startswith(str(_FRONTEND_DIST.resolve())):
            return FileResponse(str(target))
        return FileResponse(str(_FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "app": "FINORA",
            "description": "Financial Intelligence Network for Optimization, Reasoning & Automation",
            "status": "online",
            "version": settings.VERSION,
            "docs": "/docs",
            "synthetic_data_bank": f"{settings.API_V1_STR}/demo-data/status"
        }

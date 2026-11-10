from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
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

@app.get("/health")
def health_check():
    return {"status": "healthy"}

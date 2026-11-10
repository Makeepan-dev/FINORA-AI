from pydantic import BaseModel, Field

class DemoDataConfig(BaseModel):
    random_seed: int = 42
    personal_users_count: int = 3
    business_count: int = 2
    history_months: int = 12
    min_merchants: int = 30
    min_products: int = 100
    primary_currency: str = "USD"
    synthetic_marker: str = "SYNTHETIC_DATA_FINORA"

DEFAULT_CONFIG = DemoDataConfig()

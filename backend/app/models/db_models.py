from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, Integer
from datetime import datetime
from ..database.session import Base

class CapturedPayment(Base):
    __tablename__ = "captured_payments"

    id = Column(String, primary_key=True, index=True)
    paypal_order_id = Column(String, index=True, nullable=False)
    paypal_capture_id = Column(String, index=True, nullable=True)
    user_id = Column(String, index=True, nullable=False)
    product_id = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, nullable=False)
    payer_email = Column(String, nullable=True)
    payer_id = Column(String, nullable=True)
    raw_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_synthetic = Column(Boolean, default=True)

class PayPalOrderRecord(Base):
    __tablename__ = "paypal_orders"

    order_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    product_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="CREATED")
    approval_url = Column(String, nullable=True)
    is_simulated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PayPalWebhookRecord(Base):
    __tablename__ = "paypal_webhooks"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, index=True, nullable=True)
    summary = Column(String, nullable=True)
    status = Column(String, default="PROCESSED")
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    institution_id = Column(String, nullable=False)
    institution_name = Column(String, nullable=False)
    provider_type = Column(String, nullable=False)  # open_banking_plaid, paypal_direct, truelayer_uk
    account_mask = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    connection_status = Column(String, default="connected")  # connected, syncing, action_required, revoked
    health_status = Column(String, default="healthy")  # healthy, degraded, disconnected
    last_sync_timestamp = Column(DateTime, default=datetime.utcnow)
    sync_frequency = Column(String, default="hourly")
    permissions_granted = Column(Text, default='["read_transactions","read_balance","read_identity"]')
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(String, primary_key=True, index=True)
    connection_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    sync_type = Column(String, default="automatic")  # automatic, manual_trigger, webhook
    status = Column(String, default="success")  # success, failed, partial
    records_ingested = Column(Integer, default=0)
    income_detected_count = Column(Integer, default=0)
    expenses_categorized_count = Column(Integer, default=0)
    duration_ms = Column(Integer, default=120)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(String, primary_key=True, index=True)
    active_scenario_id = Column(String, default="scen_01_normal_spending")
    ai_provider = Column(String, default="deterministic")
    updated_at = Column(DateTime, default=datetime.utcnow)

class TransactionRecord(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    account_id = Column(String, index=True, nullable=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    merchant = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)  # Always positive decimal float
    currency = Column(String, default="USD")
    transaction_type = Column(String, nullable=False, index=True)  # income, expense, transfer, refund
    category = Column(String, nullable=False, index=True)
    is_recurring = Column(Boolean, default=False)
    is_demo = Column(Boolean, default=False)
    source = Column(String, default="manual")  # manual, csv_import, demo_seed, paypal
    import_batch_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SubscriptionRecord(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    merchant = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    frequency = Column(String, default="monthly")  # monthly, annual, weekly
    category = Column(String, default="services")
    billing_day = Column(Integer, nullable=True)
    last_payment_date = Column(String, nullable=True)
    status = Column(String, default="active")  # active, canceled, paused
    usage_days_dormant = Column(Integer, default=0)
    is_underutilized = Column(Boolean, default=False)
    detection_confidence = Column(Float, default=1.0)
    alternative_name = Column(String, nullable=True)
    alternative_amount = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserGoalRecord(Base):
    __tablename__ = "user_goals"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    monthly_contribution = Column(Float, default=0.0)
    target_date = Column(String, nullable=True)  # YYYY-MM-DD
    category = Column(String, default="general")
    status = Column(String, default="in_progress")
    created_at = Column(DateTime, default=datetime.utcnow)

class SavingsRecommendationRecord(Base):
    __tablename__ = "savings_recommendations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    problem_identified = Column(Text, nullable=False)
    supporting_evidence = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    estimated_monthly_savings = Column(Float, default=0.0)
    estimated_annual_savings = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.9)
    effort_level = Column(String, default="low")  # low, medium, high
    status = Column(String, default="pending")  # pending, accepted, rejected, realized
    action_type = Column(String, default="review")  # cancel_subscription, switch_alternative, reduce_spending
    related_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


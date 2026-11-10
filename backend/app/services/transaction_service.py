import csv
import io
import uuid
import re
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.db_models import TransactionRecord, SubscriptionRecord
from ..database.session import SessionLocal, Base, engine

# Ensure tables are created
Base.metadata.create_all(bind=engine)

# Strict CSV Upload Protection Limits
MAX_CSV_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB (2,097,152 bytes)
MAX_CSV_ROWS = 5000

# Categorization dictionary mapping keywords to FINORA categories
CATEGORY_KEYWORDS = {
    "food_dining": [
        "restaurant", "cafe", "coffee", "starbucks", "doordash", "uber eats", "grubhub", 
        "mcdonald", "burger", "pizza", "dining", "bakery", "subway", "chipotle", "diner"
    ],
    "groceries": [
        "grocery", "supermarket", "walmart", "whole foods", "trader joe", "safeway", 
        "kroger", "costco", "aldi", "target", "market", "food store"
    ],
    "tech_subscriptions": [
        "netflix", "spotify", "apple", "google", "aws", "github", "chatgpt", "openai", 
        "adobe", "dropbox", "hulu", "disney", "prime", "youtube", "microsoft", "claude", 
        "cognition", "anthropic", "software", "api", "stratavault", "cloud"
    ],
    "fitness_wellness": [
        "gym", "fitness", "equinox", "planet fitness", "crossfit", "yoga", "pilates", 
        "workout", "anytime fitness", "gold's gym"
    ],
    "utilities_housing": [
        "electric", "water", "gas", "power", "internet", "comcast", "verizon", "att", 
        "at&t", "rent", "mortgage", "hoa", "utility", "trash"
    ],
    "transportation": [
        "uber", "lyft", "gas station", "chevron", "shell", "exxon", "mobil", "bp", 
        "metro", "subway", "transit", "parking", "toll", "airline", "delta", "united"
    ],
    "shopping": [
        "amazon", "ebay", "best buy", "clothing", "apparel", "zara", "nike", "store", 
        "retail", "nordstrom", "macys"
    ],
    "salary_income": [
        "payroll", "salary", "employer", "direct deposit", "stripe payout", "paycheck", 
        "freelance", "client payment", "dividend", "interest"
    ],
    "transfers": [
        "transfer", "wire", "venmo", "zelle", "cash app", "internal transfer", "savings transfer"
    ]
}

def infer_category_and_type(description: str, merchant: str, raw_amount: float) -> Tuple[str, str, bool]:
    """Infers category, transaction type, and whether it is a transfer/recurring."""
    text = f"{merchant} {description}".lower()
    
    # Check for transfer first
    for kw in CATEGORY_KEYWORDS["transfers"]:
        if kw in text:
            return "transfer", "transfer", False

    # Check for income
    for kw in CATEGORY_KEYWORDS["salary_income"]:
        if kw in text:
            return "salary_income", "income", False
            
    # Check expense categories
    for cat, kws in CATEGORY_KEYWORDS.items():
        if cat in ["transfers", "salary_income"]:
            continue
        for kw in kws:
            if kw in text:
                is_rec = cat in ["tech_subscriptions", "fitness_wellness", "utilities_housing"]
                return cat, "expense", is_rec

    # Fallback based on amount sign
    if raw_amount < 0:
        return "salary_income", "income", False
    return "general_expense", "expense", False


class TransactionService:
    def __init__(self, db_factory=SessionLocal):
        self.db_factory = db_factory

    def get_db(self) -> Session:
        return self.db_factory()

    def has_personal_records(self, user_id: str) -> bool:
        """Checks whether the user has any non-demo (personal) transactions persisted."""
        with self.get_db() as db:
            personal_count = db.query(TransactionRecord).filter(
                TransactionRecord.user_id == user_id,
                TransactionRecord.is_demo == False
            ).count()
            return personal_count > 0

    def resolve_data_scope(self, user_id: str, requested_scope: str = "auto") -> str:
        """
        Determines the active data scope ('personal' vs 'demo') so demo records
        NEVER silently mix with or contaminate personal financial records.
        - 'personal': strictly is_demo == False
        - 'demo': strictly is_demo == True
        - 'auto': if the user has any personal (is_demo == False) records, use 'personal';
                  otherwise use 'demo'.
        """
        scope = (requested_scope or "auto").lower().strip()
        if scope in ["personal", "demo"]:
            return scope
        return "personal" if self.has_personal_records(user_id) else "demo"

    def seed_initial_demo_if_empty(self, user_id: str = "usr_alex_chen"):
        """Seeds demo data into SQLite if demo records do not yet exist for user."""
        with self.get_db() as db:
            demo_tx_count = db.query(TransactionRecord).filter(
                TransactionRecord.user_id == user_id,
                TransactionRecord.is_demo == True
            ).count()

            if demo_tx_count == 0:
                demo_records = [
                    # Incomes ($7,050.00)
                    {"date": "2026-10-01", "merchant": "TechCorp Global", "description": "Bi-weekly Payroll Direct Deposit", "amount": 3200.00, "type": "income", "cat": "salary_income", "rec": True},
                    {"date": "2026-10-15", "merchant": "TechCorp Global", "description": "Bi-weekly Payroll Direct Deposit", "amount": 3200.00, "type": "income", "cat": "salary_income", "rec": True},
                    {"date": "2026-10-22", "merchant": "Upwork Escrow", "description": "Freelance Backend API Milestone", "amount": 650.00, "type": "income", "cat": "salary_income", "rec": False},
                    
                    # Recurring Subscriptions & Fixed Expenses
                    {"date": "2026-10-02", "merchant": "Equinox Fitness", "description": "Monthly Club All-Access Membership", "amount": 45.00, "type": "expense", "cat": "fitness_wellness", "rec": True},
                    {"date": "2026-10-03", "merchant": "Cognition Engine Pro", "description": "Monthly Developer AI Engine License", "amount": 35.00, "type": "expense", "cat": "tech_subscriptions", "rec": True},
                    {"date": "2026-10-05", "merchant": "Netflix Standard", "description": "HD 2-Screens Streaming Subscription", "amount": 15.49, "type": "expense", "cat": "tech_subscriptions", "rec": True},
                    {"date": "2026-10-06", "merchant": "Spotify Premium", "description": "Individual Music Streaming", "amount": 10.99, "type": "expense", "cat": "tech_subscriptions", "rec": True},
                    {"date": "2026-10-08", "merchant": "Amazon Prime", "description": "Monthly Delivery & Video Membership", "amount": 14.99, "type": "expense", "cat": "tech_subscriptions", "rec": True},
                    {"date": "2026-10-12", "merchant": "Pacific Gas & Electric", "description": "Residential Power and Gas Bill", "amount": 112.40, "type": "expense", "cat": "utilities_housing", "rec": True},
                    {"date": "2026-10-14", "merchant": "Sonic Fiber Internet", "description": "Gigabit Home Internet Service", "amount": 60.00, "type": "expense", "cat": "utilities_housing", "rec": True},

                    # Variable Expenses - Dining & Food ($203.85 total -> 20% = $40.77)
                    {"date": "2026-10-04", "merchant": "DoorDash", "description": "Sushi Dinner Delivery + Tip", "amount": 48.75, "type": "expense", "cat": "food_dining", "rec": False},
                    {"date": "2026-10-07", "merchant": "Blue Bottle Coffee", "description": "Single Origin Pour Over & Pastry", "amount": 12.50, "type": "expense", "cat": "food_dining", "rec": False},
                    {"date": "2026-10-10", "merchant": "DoorDash", "description": "Thai Curry & Appetizers Delivery", "amount": 54.20, "type": "expense", "cat": "food_dining", "rec": False},
                    {"date": "2026-10-16", "merchant": "Chipotle Mexican Grill", "description": "Burrito Bowl & Chips", "amount": 16.85, "type": "expense", "cat": "food_dining", "rec": False},
                    {"date": "2026-10-19", "merchant": "DoorDash", "description": "Late Night Italian Pasta & Gelato", "amount": 62.10, "type": "expense", "cat": "food_dining", "rec": False},
                    {"date": "2026-10-25", "merchant": "Starbucks Coffee", "description": "Cold Brew & Sandwich", "amount": 9.45, "type": "expense", "cat": "food_dining", "rec": False},

                    # Groceries
                    {"date": "2026-10-06", "merchant": "Trader Joe's", "description": "Weekly Pantry and Fresh Produce", "amount": 84.60, "type": "expense", "cat": "groceries", "rec": False},
                    {"date": "2026-10-13", "merchant": "Whole Foods Market", "description": "Organic Meat, Fish & Dairy", "amount": 142.30, "type": "expense", "cat": "groceries", "rec": False},
                    {"date": "2026-10-20", "merchant": "Trader Joe's", "description": "Weekly Groceries & Snacks", "amount": 91.20, "type": "expense", "cat": "groceries", "rec": False},
                    {"date": "2026-10-27", "merchant": "Costco Wholesale", "description": "Bulk Household Supplies & Drinks", "amount": 178.50, "type": "expense", "cat": "groceries", "rec": False},

                    # Transportation & Shopping
                    {"date": "2026-10-09", "merchant": "Uber", "description": "Ride to Downtown Office", "amount": 24.50, "type": "expense", "cat": "transportation", "rec": False},
                    {"date": "2026-10-11", "merchant": "Chevron", "description": "Regular Unleaded Fuel 12 Gallons", "amount": 52.80, "type": "expense", "cat": "transportation", "rec": False},
                    {"date": "2026-10-18", "merchant": "Uber", "description": "Ride from Airport", "amount": 38.90, "type": "expense", "cat": "transportation", "rec": False},
                    {"date": "2026-10-21", "merchant": "Amazon.com", "description": "Ergonomic Desk Keyboard & Cable", "amount": 89.99, "type": "expense", "cat": "shopping", "rec": False},
                    
                    # Internal Transfer (Must NOT be counted in income or expense!)
                    {"date": "2026-10-15", "merchant": "Internal Transfer", "description": "Automatic Savings Transfer to HYSA", "amount": 500.00, "type": "transfer", "cat": "transfers", "rec": True}
                ]

                for d in demo_records:
                    tx = TransactionRecord(
                        id=f"tx_demo_{uuid.uuid4().hex[:8]}",
                        user_id=user_id,
                        account_id="acc_chase_checking",
                        date=d["date"],
                        merchant=d["merchant"],
                        description=d["description"],
                        amount=float(d["amount"]),
                        currency="USD",
                        transaction_type=d["type"],
                        category=d["cat"],
                        is_recurring=d["rec"],
                        is_demo=True,
                        source="demo_seed",
                        created_at=datetime.utcnow()
                    )
                    db.add(tx)

            # Ensure all 5 canonical demo subscriptions exist in SubscriptionRecord
            existing_subs = db.query(SubscriptionRecord).filter(
                SubscriptionRecord.user_id == user_id,
                SubscriptionRecord.is_demo == True
            ).all()
            existing_sub_names = {s.name for s in existing_subs}

            demo_subs = [
                {
                    "name": "Equinox All-Access Fitness",
                    "merchant": "Equinox Fitness",
                    "amount": 45.00,
                    "freq": "monthly",
                    "cat": "fitness_wellness",
                    "dormant": 45,
                    "underutilized": True,
                    "alt_name": "Planet Fitness Classic",
                    "alt_amount": 20.00,
                    "notes": "No detected check-in or gym visit within 45 days. Local alternative available 0.8 miles away."
                },
                {
                    "name": "Cognition Engine Pro",
                    "merchant": "Cognition Engine Pro",
                    "amount": 35.00,
                    "freq": "monthly",
                    "cat": "tech_subscriptions",
                    "dormant": 45,
                    "underutilized": True,
                    "alt_name": "Open-Source / Pay-As-You-Go Tier",
                    "alt_amount": 0.00,
                    "notes": "0 API tokens consumed across trailing 45-day telemetry window."
                },
                {
                    "name": "StrataVault Cloud 2TB",
                    "merchant": "StrataVault Storage",
                    "amount": 19.99,
                    "freq": "monthly",
                    "cat": "tech_subscriptions",
                    "dormant": 30,
                    "underutilized": True,
                    "alt_name": "StrataVault 200GB Standard",
                    "alt_amount": 4.99,
                    "notes": "Utilizing only 142GB (7.1% of 2TB encrypted storage capacity)."
                },
                {
                    "name": "Netflix Standard",
                    "merchant": "Netflix Standard",
                    "amount": 15.49,
                    "freq": "monthly",
                    "cat": "tech_subscriptions",
                    "dormant": 5,
                    "underutilized": False,
                    "alt_name": None,
                    "alt_amount": None,
                    "notes": "Active streaming detected."
                },
                {
                    "name": "Spotify Premium",
                    "merchant": "Spotify Premium",
                    "amount": 10.99,
                    "freq": "monthly",
                    "cat": "tech_subscriptions",
                    "dormant": 2,
                    "underutilized": False,
                    "alt_name": None,
                    "alt_amount": None,
                    "notes": "Daily music listening."
                }
            ]
            for s in demo_subs:
                if s["name"] not in existing_sub_names:
                    sr = SubscriptionRecord(
                        id=f"sub_{uuid.uuid4().hex[:8]}",
                        user_id=user_id,
                        name=s["name"],
                        merchant=s["merchant"],
                        amount=s["amount"],
                        currency="USD",
                        frequency=s["freq"],
                        category=s["cat"],
                        billing_day=2,
                        last_payment_date="2026-10-02",
                        status="active",
                        usage_days_dormant=s["dormant"],
                        is_underutilized=s["underutilized"],
                        detection_confidence=0.95,
                        alternative_name=s["alt_name"],
                        alternative_amount=s["alt_amount"],
                        notes=s["notes"],
                        is_demo=True,
                        created_at=datetime.utcnow()
                    )
                    db.add(sr)

            db.commit()

    def get_transactions(
        self, 
        user_id: str, 
        limit: int = 100, 
        offset: int = 0,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        search: Optional[str] = None,
        data_scope: str = "auto"
    ) -> List[Dict[str, Any]]:
        """
        Retrieves persisted transactions strictly isolated by data_scope ('personal' vs 'demo').
        Demo records never silently mix with personal records.
        """
        active_scope = self.resolve_data_scope(user_id, data_scope)
        if active_scope == "demo":
            self.seed_initial_demo_if_empty(user_id)

        with self.get_db() as db:
            query = db.query(TransactionRecord).filter(
                TransactionRecord.user_id == user_id,
                TransactionRecord.is_demo == (active_scope == "demo")
            )
            if category:
                query = query.filter(TransactionRecord.category == category)
            if transaction_type:
                query = query.filter(TransactionRecord.transaction_type == transaction_type)
            if search:
                term = f"%{search}%"
                query = query.filter(
                    (TransactionRecord.merchant.ilike(term)) | 
                    (TransactionRecord.description.ilike(term))
                )
            
            records = query.order_by(TransactionRecord.date.desc(), TransactionRecord.created_at.desc()).offset(offset).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "date": r.date,
                    "merchant": r.merchant,
                    "description": r.description,
                    "amount": r.amount,
                    "currency": r.currency,
                    "transaction_type": r.transaction_type,
                    "category": r.category,
                    "is_recurring": r.is_recurring,
                    "is_demo": r.is_demo,
                    "data_scope": active_scope,
                    "source": r.source,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                }
                for r in records
            ]

    def add_transaction(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adds a single manual personal transaction (is_demo=False) with strict validation."""
        date_str = data.get("date") or date.today().isoformat()
        merchant = (data.get("merchant") or "Manual Entry").strip()
        description = (data.get("description") or merchant).strip()
        raw_amt = float(data.get("amount", 0.0))
        amt = abs(raw_amt)
        currency = data.get("currency", "USD").upper()
        
        explicit_type = data.get("transaction_type")
        explicit_cat = data.get("category")
        
        inferred_cat, inferred_type, is_rec = infer_category_and_type(description, merchant, raw_amt)
        tx_type = explicit_type if explicit_type in ["income", "expense", "transfer", "refund"] else inferred_type
        cat = explicit_cat or inferred_cat

        tx_id = f"tx_{uuid.uuid4().hex[:10]}"
        with self.get_db() as db:
            tx = TransactionRecord(
                id=tx_id,
                user_id=user_id,
                account_id=data.get("account_id", "acc_manual"),
                date=date_str,
                merchant=merchant,
                description=description,
                amount=amt,
                currency=currency,
                transaction_type=tx_type,
                category=cat,
                is_recurring=bool(data.get("is_recurring", is_rec)),
                is_demo=False,
                source="manual",
                created_at=datetime.utcnow()
            )
            db.add(tx)
            db.commit()
            db.refresh(tx)
            return {
                "id": tx.id,
                "user_id": tx.user_id,
                "date": tx.date,
                "merchant": tx.merchant,
                "description": tx.description,
                "amount": tx.amount,
                "currency": tx.currency,
                "transaction_type": tx.transaction_type,
                "category": tx.category,
                "is_recurring": tx.is_recurring,
                "is_demo": tx.is_demo,
                "source": tx.source
            }

    def delete_transaction(self, user_id: str, tx_id: str) -> bool:
        """Deletes a transaction after verifying server-side ownership."""
        with self.get_db() as db:
            tx = db.query(TransactionRecord).filter(TransactionRecord.id == tx_id).first()
            if not tx:
                return False
            if tx.user_id != user_id:
                raise PermissionError("Forbidden: Cannot delete a transaction belonging to another user.")
            db.delete(tx)
            db.commit()
            return True

    def preview_csv_import(self, user_id: str, csv_content: str) -> Dict[str, Any]:
        """
        Parses CSV and returns preview with validation errors and duplicate flags.
        Enforces strict 2 MB size limit, 5,000 row limit, null-byte check, and malformed CSV safety.
        """
        if not isinstance(csv_content, str):
            raise ValueError("CSV content must be a valid UTF-8 text string.")
        if "\x00" in csv_content:
            raise ValueError("Malformed binary content detected (null bytes not permitted in CSV).")
        if len(csv_content.encode("utf-8", errors="replace")) > MAX_CSV_SIZE_BYTES:
            raise ValueError(f"CSV content exceeds maximum allowed size of 2 MB ({MAX_CSV_SIZE_BYTES:,} bytes).")

        stripped = csv_content.strip()
        if not stripped:
            return {"valid_count": 0, "invalid_count": 0, "duplicate_count": 0, "total_rows": 0, "records": []}

        try:
            reader = csv.reader(io.StringIO(stripped))
            rows = []
            for idx, r in enumerate(reader):
                if idx > MAX_CSV_ROWS:  # 1 header row + up to 5,000 data rows
                    raise ValueError(f"CSV exceeds maximum allowed limit of {MAX_CSV_ROWS:,} rows.")
                rows.append(r)
        except csv.Error as ce:
            raise ValueError(f"Malformed CSV structure could not be parsed safely: {ce}")

        if not rows:
            return {"valid_count": 0, "invalid_count": 0, "duplicate_count": 0, "total_rows": 0, "records": []}

        header = [h.strip().lower() for h in rows[0]]
        
        # Find column indices
        date_idx = -1
        merchant_idx = -1
        desc_idx = -1
        amount_idx = -1
        cat_idx = -1
        type_idx = -1

        for i, col in enumerate(header):
            if any(k in col for k in ["date", "timestamp", "time"]):
                date_idx = i
            elif any(k in col for k in ["merchant", "payee", "vendor"]):
                merchant_idx = i
            elif any(k in col for k in ["description", "memo", "details", "name"]):
                desc_idx = i
            elif any(k in col for k in ["amount", "value", "cost", "price"]):
                amount_idx = i
            elif any(k in col for k in ["category", "cat"]):
                cat_idx = i
            elif any(k in col for k in ["type", "trans_type"]):
                type_idx = i

        # Fallbacks for headerless or standard bank CSV formats
        if amount_idx == -1 and len(header) >= 3:
            amount_idx = len(header) - 1
        if date_idx == -1:
            date_idx = 0
        if desc_idx == -1 and len(header) >= 2:
            desc_idx = 1

        parsed_records = []
        valid_count = 0
        invalid_count = 0
        dup_count = 0

        # Query existing personal user transactions to flag duplicates (never compare against demo seed)
        with self.get_db() as db:
            existing = db.query(TransactionRecord.date, TransactionRecord.merchant, TransactionRecord.amount).filter(
                TransactionRecord.user_id == user_id,
                TransactionRecord.is_demo == False
            ).all()
            existing_set = {(e[0], e[1].strip().lower(), round(float(e[2]), 2)) for e in existing}

        for row_num, row in enumerate(rows[1:], start=2):
            if not row or all(not cell.strip() for cell in row):
                continue
            
            errors = []
            
            # Parse date
            raw_date = row[date_idx].strip() if date_idx < len(row) else ""
            parsed_date = ""
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%m-%d-%Y", "%b %d, %Y"]:
                try:
                    dt = datetime.strptime(raw_date, fmt)
                    parsed_date = dt.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    pass
            if not parsed_date:
                errors.append(f"Invalid date format: '{raw_date}'")

            # Parse merchant and description
            desc = row[desc_idx].strip() if desc_idx != -1 and desc_idx < len(row) else "Expense"
            merchant = row[merchant_idx].strip() if merchant_idx != -1 and merchant_idx < len(row) else desc
            if not merchant:
                merchant = desc or "Unknown Merchant"

            # Parse amount
            raw_amount_str = row[amount_idx].strip() if amount_idx != -1 and amount_idx < len(row) else "0"
            clean_amt = re.sub(r"[^\d.-]", "", raw_amount_str)
            try:
                raw_amt = float(clean_amt)
                amt = abs(raw_amt)
                if amt == 0.0:
                    errors.append("Amount cannot be zero")
            except ValueError:
                raw_amt = 0.0
                amt = 0.0
                errors.append(f"Invalid monetary amount: '{raw_amount_str}'")

            # Inferred or explicit category/type
            explicit_cat = row[cat_idx].strip().lower().replace(" ", "_") if cat_idx != -1 and cat_idx < len(row) else None
            explicit_type = row[type_idx].strip().lower() if type_idx != -1 and type_idx < len(row) else None

            inferred_cat, inferred_type, is_rec = infer_category_and_type(desc, merchant, raw_amt)
            tx_type = explicit_type if explicit_type in ["income", "expense", "transfer", "refund"] else inferred_type
            cat = explicit_cat or inferred_cat

            # Check duplicate
            is_dup = (parsed_date, merchant.lower(), round(amt, 2)) in existing_set

            if is_dup:
                dup_count += 1
            if errors:
                invalid_count += 1
            else:
                valid_count += 1

            parsed_records.append({
                "row_number": row_num,
                "date": parsed_date or raw_date,
                "merchant": merchant,
                "description": desc,
                "amount": round(amt, 2),
                "transaction_type": tx_type,
                "category": cat,
                "is_recurring": is_rec,
                "is_duplicate": is_dup,
                "is_valid": len(errors) == 0,
                "validation_errors": errors
            })

        return {
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "duplicate_count": dup_count,
            "total_rows": len(parsed_records),
            "records": parsed_records
        }

    def confirm_csv_import(self, user_id: str, records: List[Dict[str, Any]], skip_duplicates: bool = True) -> Dict[str, Any]:
        """Imports valid records into SQLite as personal data (is_demo=False) with strict deduplication."""
        if len(records) > MAX_CSV_ROWS:
            raise ValueError(f"Import batch exceeds maximum allowed limit of {MAX_CSV_ROWS:,} rows.")

        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        imported_count = 0
        skipped_count = 0

        with self.get_db() as db:
            # Re-fetch existing personal records for race safety
            existing = db.query(TransactionRecord.date, TransactionRecord.merchant, TransactionRecord.amount).filter(
                TransactionRecord.user_id == user_id,
                TransactionRecord.is_demo == False
            ).all()
            existing_set = {(e[0], e[1].strip().lower(), round(float(e[2]), 2)) for e in existing}

            for r in records:
                if not r.get("is_valid", True):
                    skipped_count += 1
                    continue

                d = str(r.get("date", "")).strip()
                m = str(r.get("merchant", "")).strip()
                amt = round(float(r.get("amount", 0.0)), 2)
                if not d or not m or amt <= 0:
                    skipped_count += 1
                    continue

                if skip_duplicates and (d, m.lower(), amt) in existing_set:
                    skipped_count += 1
                    continue

                tx = TransactionRecord(
                    id=f"tx_csv_{uuid.uuid4().hex[:10]}",
                    user_id=user_id,
                    account_id="acc_csv_import",
                    date=d,
                    merchant=m,
                    description=r.get("description", m),
                    amount=amt,
                    currency="USD",
                    transaction_type=r.get("transaction_type", "expense"),
                    category=r.get("category", "general_expense"),
                    is_recurring=bool(r.get("is_recurring", False)),
                    is_demo=False,
                    source="csv_import",
                    import_batch_id=batch_id,
                    created_at=datetime.utcnow()
                )
                db.add(tx)
                existing_set.add((d, m.lower(), amt))
                imported_count += 1

            db.commit()

        return {
            "status": "success",
            "batch_id": batch_id,
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "active_data_scope": "personal"
        }

    def get_financial_summary(
        self,
        user_id: str,
        month_str: Optional[str] = None,
        data_scope: str = "auto"
    ) -> Dict[str, Any]:
        """
        Computes authoritative financial summaries with Decimal precision.
        Critical Rules:
        1. Demo records and personal records are strictly separated by active_scope.
        2. Transfers are strictly excluded from income and expenses!
        3. Remaining Available Money = Total Income - Total Expenses.
        4. Potential savings opportunities are computed deterministically without double-counting.
        """
        active_scope = self.resolve_data_scope(user_id, data_scope)
        if active_scope == "demo":
            self.seed_initial_demo_if_empty(user_id)
        
        is_demo_flag = (active_scope == "demo")
        with self.get_db() as db:
            all_txs = db.query(TransactionRecord).filter(
                TransactionRecord.user_id == user_id,
                TransactionRecord.is_demo == is_demo_flag
            ).all()
            subs = db.query(SubscriptionRecord).filter(
                SubscriptionRecord.user_id == user_id,
                SubscriptionRecord.is_demo == is_demo_flag
            ).all()

        # Select target month or default to latest month in dataset (e.g. 2026-10)
        target_month = month_str
        if not target_month and all_txs:
            months = sorted(list(set(t.date[:7] for t in all_txs if t.date)), reverse=True)
            target_month = months[0] if months else datetime.now().strftime("%Y-%m")
        elif not target_month:
            target_month = datetime.now().strftime("%Y-%m")

        total_income = Decimal("0.00")
        total_expense = Decimal("0.00")
        category_spending: Dict[str, Decimal] = {}
        daily_spending: Dict[str, Decimal] = {}
        recurring_monthly_total = Decimal("0.00")

        for s in subs:
            if s.status == "active":
                freq = s.frequency or "monthly"
                amt = Decimal(str(s.amount))
                if freq == "monthly":
                    recurring_monthly_total += amt
                elif freq == "annual":
                    recurring_monthly_total += (amt / Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                elif freq == "weekly":
                    recurring_monthly_total += (amt * Decimal("4.33")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        for t in all_txs:
            if t.date.startswith(target_month):
                amt = Decimal(str(t.amount))
                # Rule: Transfers are excluded!
                if t.transaction_type == "transfer":
                    continue
                elif t.transaction_type == "income":
                    total_income += amt
                elif t.transaction_type == "expense":
                    total_expense += amt
                    category_spending[t.category] = category_spending.get(t.category, Decimal("0.00")) + amt
                    daily_spending[t.date] = daily_spending.get(t.date, Decimal("0.00")) + amt
                elif t.transaction_type == "refund":
                    total_expense -= amt
                    category_spending[t.category] = category_spending.get(t.category, Decimal("0.00")) - amt

        # If personal subscriptions table is empty in personal mode, derive recurring total from recurring expense txs
        if active_scope == "personal" and not subs:
            for t in all_txs:
                if t.date.startswith(target_month) and t.transaction_type == "expense" and t.is_recurring:
                    recurring_monthly_total += Decimal(str(t.amount))

        remaining_available = total_income - total_expense

        # Category Breakdown
        spending_breakdown = []
        for cat, amt in sorted(category_spending.items(), key=lambda x: x[1], reverse=True):
            pct = float((amt / total_expense * Decimal("100")).quantize(Decimal("0.1"))) if total_expense > 0 else 0.0
            spending_breakdown.append({
                "category": cat.replace("_", " ").title(),
                "category_raw": cat,
                "amount": float(amt),
                "percentage": pct
            })

        # Authoritative Non-Overlapping Savings Opportunities Calculation
        potential_savings = Decimal("0.00")
        savings_opportunities = []
        seen_opportunity_keys = set()

        for s in subs:
            if s.is_underutilized and s.alternative_amount is not None:
                opp_key = f"sub_{s.name.strip().lower()}"
                if opp_key in seen_opportunity_keys:
                    continue
                seen_opportunity_keys.add(opp_key)
                diff = (Decimal(str(s.amount)) - Decimal(str(s.alternative_amount))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                if diff > Decimal("0.00"):
                    potential_savings += diff
                    annual_diff = (diff * Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    savings_opportunities.append({
                        "related_id": opp_key,
                        "type": "subscription_alternative",
                        "category": s.category,
                        "title": f"Switch {s.name} to {s.alternative_name}",
                        "monthly_savings": float(diff),
                        "annual_savings": float(annual_diff),
                        "confidence": float(s.detection_confidence or 0.90),
                        "effort": "medium" if s.category == "fitness_wellness" else "low",
                        "evidence": s.notes or f"Underutilized for {s.usage_days_dormant} days"
                    })

        # In personal mode without SubscriptionRecord rows, check for personal underutilized recurring expenses
        if active_scope == "personal" and not subs:
            for t in all_txs:
                if t.date.startswith(target_month) and t.transaction_type == "expense":
                    if t.category == "fitness_wellness" and Decimal(str(t.amount)) > Decimal("20.00"):
                        opp_key = "sub_personal_gym"
                        if opp_key not in seen_opportunity_keys:
                            seen_opportunity_keys.add(opp_key)
                            diff = (Decimal(str(t.amount)) - Decimal("20.00")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                            potential_savings += diff
                            savings_opportunities.append({
                                "related_id": opp_key,
                                "type": "subscription_alternative",
                                "category": "fitness_wellness",
                                "title": f"Switch {t.merchant} (${float(t.amount):.2f}/mo) to Planet Fitness Classic ($20.00/mo)",
                                "monthly_savings": float(diff),
                                "annual_savings": float((diff * Decimal('12.0')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                                "confidence": 0.90,
                                "effort": "medium",
                                "evidence": f"Recurring fitness expense of ${float(t.amount):.2f}/mo detected in personal ledger."
                            })

        food_delivery_spend = category_spending.get("food_dining", Decimal("0.00"))
        if food_delivery_spend > Decimal("0.00") and "cat_food_dining" not in seen_opportunity_keys:
            seen_opportunity_keys.add("cat_food_dining")
            sav = (food_delivery_spend * Decimal("0.20")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if sav > Decimal("0.00"):
                potential_savings += sav
                annual_sav = (sav * Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                savings_opportunities.append({
                    "related_id": "cat_food_dining",
                    "type": "spending_reduction",
                    "category": "food_dining",
                    "title": "Reduce Food Delivery & Dining by 20%",
                    "monthly_savings": float(sav),
                    "annual_savings": float(annual_sav),
                    "confidence": 0.85,
                    "effort": "low",
                    "evidence": f"Spent ${float(food_delivery_spend):.2f} on Food & Dining in {target_month} ({active_scope} scope)."
                })

        annual_potential_total = (potential_savings * Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "user_id": user_id,
            "active_data_scope": active_scope,
            "has_personal_records": self.has_personal_records(user_id),
            "month": target_month,
            "total_income": float(total_income),
            "total_expenses": float(total_expense),
            "remaining_available_money": float(remaining_available),
            "net_cash_flow": float(remaining_available),
            "recurring_monthly_expenses": float(recurring_monthly_total),
            "potential_monthly_savings": float(potential_savings),
            "potential_annual_savings": float(annual_potential_total),
            "category_breakdown": spending_breakdown,
            "savings_opportunities": savings_opportunities,
            "transaction_count": len([t for t in all_txs if t.date.startswith(target_month)]),
            "calculation_formula": "Remaining Available = Total Income ($) - Total Expenses ($) [Transfers Strictly Excluded]"
        }


global_transaction_service = TransactionService()

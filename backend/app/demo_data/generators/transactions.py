import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple
from ..models.transaction import (
    SyntheticTransaction, TransactionType, TransactionStatus, PaymentMethod
)
from ..models.account import SyntheticAccount

def generate_transactions(
    seed: int = 42,
    history_months: int = 12,
    accounts: List[SyntheticAccount] = None
) -> Tuple[List[SyntheticTransaction], Dict[str, Decimal]]:
    """
    Generates 12+ months of coherent, reconciled synthetic transactions.
    Returns: (list_of_transactions, account_balance_map)
    where account_balance_map has the final reconciled current_balance for each account.
    """
    rng = random.Random(seed)
    transactions: List[SyntheticTransaction] = []

    # Map opening balances
    account_balances: Dict[str, Decimal] = {}
    if accounts:
        for acc in accounts:
            account_balances[acc.account_id] = acc.opening_balance

    # Base reference date: November 2026
    end_date = datetime(2026, 11, 8, 12, 0, 0)
    start_date = end_date - timedelta(days=history_months * 30)

    # 1. USER 1: Alex Chen (usr_alex_chen)
    # Recurring income: Bi-weekly salary $4,250 on 1st & 15th
    cur_date = start_date
    tx_counter = 1

    while cur_date <= end_date:
        year_str = cur_date.strftime("%Y-%m")
        day = cur_date.day

        # Bi-weekly salary
        if day in [1, 15]:
            tx_id = f"txn_alex_sal_{cur_date.strftime('%Y%m%d')}"
            amt = Decimal("4250.00")
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_checking",
                    amount=amt,
                    currency="USD",
                    transaction_type=TransactionType.INCOME,
                    category="income",
                    timestamp=cur_date.replace(hour=8, minute=30).isoformat() + "Z",
                    description="Payroll Direct Deposit — Nexus Cloud Systems",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.BANK_TRANSFER,
                    is_recurring=True
                )
            )
            account_balances["acc_alex_checking"] = account_balances.get("acc_alex_checking", Decimal("0.00")) + amt

        # Housing: Rent $2,400 on 1st of month
        if day == 1:
            tx_id = f"txn_alex_rent_{cur_date.strftime('%Y%m%d')}"
            amt = Decimal("2400.00")
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_checking",
                    amount=amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="housing",
                    timestamp=cur_date.replace(hour=9, minute=0).isoformat() + "Z",
                    description="Metropolitan Lofts — Monthly Residential Lease",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.BANK_TRANSFER,
                    is_recurring=True
                )
            )
            account_balances["acc_alex_checking"] -= amt

            # Savings automated transfer: $800 to high yield savings on 2nd
            tx_out_id = f"txn_alex_trf_out_{cur_date.strftime('%Y%m%d')}"
            tx_in_id = f"txn_alex_trf_in_{cur_date.strftime('%Y%m%d')}"
            trf_amt = Decimal("800.00")
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_out_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_checking",
                    amount=trf_amt,
                    currency="USD",
                    transaction_type=TransactionType.TRANSFER,
                    category="savings",
                    timestamp=cur_date.replace(hour=10, minute=0).isoformat() + "Z",
                    description="Transfer to High-Yield Vault Savings",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.BANK_TRANSFER,
                    related_transaction_id=tx_in_id
                )
            )
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_in_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_savings",
                    amount=trf_amt,
                    currency="USD",
                    transaction_type=TransactionType.TRANSFER,
                    category="savings",
                    timestamp=cur_date.replace(hour=10, minute=1).isoformat() + "Z",
                    description="Transfer from Premier Checking",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.BANK_TRANSFER,
                    related_transaction_id=tx_out_id
                )
            )
            account_balances["acc_alex_checking"] -= trf_amt
            account_balances["acc_alex_savings"] = account_balances.get("acc_alex_savings", Decimal("0.00")) + trf_amt

        # Subscriptions on designated days:
        # Apex Gym $120 on 1st
        if day == 1:
            tx_id = f"txn_alex_gym_{cur_date.strftime('%Y%m%d')}"
            amt = Decimal("120.00")
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_credit",
                    merchant_id="mer_apex_fitness",
                    amount=amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="fitness",
                    timestamp=cur_date.replace(hour=4, minute=15).isoformat() + "Z",
                    description="Apex Athletic All-Access Pass Monthly",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.CREDIT_CARD,
                    is_recurring=True
                )
            )
            account_balances["acc_alex_credit"] = account_balances.get("acc_alex_credit", Decimal("0.00")) - amt

        # Fiber internet $70 on 5th
        if day == 5:
            tx_id = f"txn_alex_fiber_{cur_date.strftime('%Y%m%d')}"
            amt = Decimal("70.00")
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_checking",
                    merchant_id="mer_fiber_link",
                    amount=amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="utilities",
                    timestamp=cur_date.replace(hour=5, minute=0).isoformat() + "Z",
                    description="OpticSpeed 1Gbps Fiber Internet",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.BANK_TRANSFER,
                    is_recurring=True
                )
            )
            account_balances["acc_alex_checking"] -= amt

        # Cloud storage $9.99 on 15th
        if day == 15:
            tx_id = f"txn_alex_strata_{cur_date.strftime('%Y%m%d')}"
            amt = Decimal("9.99")
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_paypal",
                    merchant_id="mer_strata_cloud",
                    amount=amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="digital_services",
                    timestamp=cur_date.replace(hour=6, minute=12).isoformat() + "Z",
                    description="StrataVault 2TB Encrypted Storage Subscription",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.PAYPAL,
                    is_recurring=True
                )
            )
            account_balances["acc_alex_paypal"] = account_balances.get("acc_alex_paypal", Decimal("0.00")) - amt

        # StreamPulse $22.99 on 20th
        if day == 20:
            tx_id = f"txn_alex_stream_{cur_date.strftime('%Y%m%d')}"
            amt = Decimal("22.99")
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_paypal",
                    merchant_id="mer_stream_pulse",
                    amount=amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="entertainment",
                    timestamp=cur_date.replace(hour=7, minute=45).isoformat() + "Z",
                    description="StreamPulse Prime 4K Family Tier",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.PAYPAL,
                    is_recurring=True
                )
            )
            account_balances["acc_alex_paypal"] = account_balances.get("acc_alex_paypal", Decimal("0.00")) - amt

        # SonicWave $14.99 on 25th
        if day == 25:
            tx_id = f"txn_alex_sonic_{cur_date.strftime('%Y%m%d')}"
            amt = Decimal("14.99")
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_paypal",
                    merchant_id="mer_sonic_cloud",
                    amount=amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="entertainment",
                    timestamp=cur_date.replace(hour=7, minute=45).isoformat() + "Z",
                    description="SonicWave HiFi Audio Spatial",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.PAYPAL,
                    is_recurring=True
                )
            )
            account_balances["acc_alex_paypal"] = account_balances.get("acc_alex_paypal", Decimal("0.00")) - amt

        # GitForge $19.00 on 28th
        if day == 28:
            tx_id = f"txn_alex_git_{cur_date.strftime('%Y%m%d')}"
            amt = Decimal("19.00")
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_credit",
                    merchant_id="mer_git_forge",
                    amount=amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="software",
                    timestamp=cur_date.replace(hour=8, minute=0).isoformat() + "Z",
                    description="GitForge Pro Developer Subscription",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.CREDIT_CARD,
                    is_recurring=True
                )
            )
            account_balances["acc_alex_credit"] = account_balances.get("acc_alex_credit", Decimal("0.00")) - amt

        # Regular discretionary expenses:
        # Weekly groceries (approx every 6-7 days)
        if day in [3, 10, 17, 24]:
            g_amt = Decimal(str(rng.randint(110, 165))) + Decimal(".45")
            tx_id = f"txn_alex_groc_{cur_date.strftime('%Y%m%d')}"
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_credit",
                    merchant_id="mer_fresh_harvest",
                    amount=g_amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="groceries",
                    timestamp=cur_date.replace(hour=17, minute=rng.randint(10, 50)).isoformat() + "Z",
                    description="Fresh Harvest Organic Market — Weekly Essentials",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.CREDIT_CARD
                )
            )
            account_balances["acc_alex_credit"] = account_balances.get("acc_alex_credit", Decimal("0.00")) - g_amt

        # Occasional dining/coffee
        if day in [6, 13, 21, 27]:
            r_amt = Decimal(str(rng.randint(28, 85))) + Decimal(".00")
            tx_id = f"txn_alex_rest_{cur_date.strftime('%Y%m%d')}"
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_credit",
                    merchant_id="mer_tokyo_ramen",
                    amount=r_amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="restaurants",
                    timestamp=cur_date.replace(hour=19, minute=rng.randint(10, 50)).isoformat() + "Z",
                    description="Shibuya Umami Noodle Bar — Dinner",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.CREDIT_CARD
                )
            )
            account_balances["acc_alex_credit"] = account_balances.get("acc_alex_credit", Decimal("0.00")) - r_amt

        # Occasional transit
        if day in [8, 22]:
            t_amt = Decimal(str(rng.randint(15, 35))) + Decimal(".50")
            tx_id = f"txn_alex_trf_{cur_date.strftime('%Y%m%d')}"
            transactions.append(
                SyntheticTransaction(
                    transaction_id=tx_id,
                    user_id="usr_alex_chen",
                    account_id="acc_alex_checking",
                    merchant_id="mer_city_commute",
                    amount=t_amt,
                    currency="USD",
                    transaction_type=TransactionType.EXPENSE,
                    category="transportation",
                    timestamp=cur_date.replace(hour=8, minute=45).isoformat() + "Z",
                    description="SwiftRide Mobility Urban Transit",
                    status=TransactionStatus.COMPLETED,
                    payment_method=PaymentMethod.DEBIT_CARD
                )
            )
            account_balances["acc_alex_checking"] -= t_amt

        cur_date += timedelta(days=1)

    # 2. Add SPECIFIC SCENARIO TRANSACTIONS for Alex Chen:
    # A) Unusual spike / purchase: VoltDesk standing desk setup in September
    spike_tx_id = "txn_alex_volt_desk_sep"
    spike_amt = Decimal("480.00")
    transactions.append(
        SyntheticTransaction(
            transaction_id=spike_tx_id,
            user_id="usr_alex_chen",
            account_id="acc_alex_credit",
            merchant_id="mer_craft_timber",
            amount=spike_amt,
            currency="USD",
            transaction_type=TransactionType.EXPENSE,
            category="electronics",
            timestamp="2026-09-15T15:20:00Z",
            description="Timber & Stone Hardware — Standing Desk Upgrade Component",
            status=TransactionStatus.COMPLETED,
            payment_method=PaymentMethod.CREDIT_CARD,
            anomaly_flag=True
        )
    )
    account_balances["acc_alex_credit"] = account_balances.get("acc_alex_credit", Decimal("0.00")) - spike_amt

    # B) Failed transaction followed by retry on October 10:
    fail_id = "txn_alex_fail_retry_1"
    retry_id = "txn_alex_fail_retry_2"
    retry_amt = Decimal("39.99")
    transactions.append(
        SyntheticTransaction(
            transaction_id=fail_id,
            user_id="usr_alex_chen",
            account_id="acc_alex_paypal",
            merchant_id="mer_micro_gear",
            amount=retry_amt,
            currency="USD",
            transaction_type=TransactionType.EXPENSE,
            category="electronics",
            timestamp="2026-10-10T11:00:00Z",
            description="Silicon Bay Electronics — Clean Duster (Network Timeout)",
            status=TransactionStatus.FAILED,
            payment_method=PaymentMethod.PAYPAL
        )
    )
    # The retry succeeded 3 minutes later:
    transactions.append(
        SyntheticTransaction(
            transaction_id=retry_id,
            user_id="usr_alex_chen",
            account_id="acc_alex_paypal",
            merchant_id="mer_micro_gear",
            amount=retry_amt,
            currency="USD",
            transaction_type=TransactionType.EXPENSE,
            category="electronics",
            timestamp="2026-10-10T11:03:00Z",
            description="Silicon Bay Electronics — Clean Duster (Retry Successful)",
            status=TransactionStatus.COMPLETED,
            payment_method=PaymentMethod.PAYPAL,
            related_transaction_id=fail_id
        )
    )
    account_balances["acc_alex_paypal"] = account_balances.get("acc_alex_paypal", Decimal("0.00")) - retry_amt

    # C) Delayed refund scenario in October:
    orig_tx_id = "txn_alex_nordic_jacket"
    refund_tx_id = "txn_alex_nordic_refund"
    ret_amt = Decimal("145.00")
    transactions.append(
        SyntheticTransaction(
            transaction_id=orig_tx_id,
            user_id="usr_alex_chen",
            account_id="acc_alex_credit",
            merchant_id="mer_nordic_threads",
            amount=ret_amt,
            currency="USD",
            transaction_type=TransactionType.EXPENSE,
            category="clothing",
            timestamp="2026-10-02T14:00:00Z",
            description="Nordic Weave Apparel — All-Weather Merino Coat",
            status=TransactionStatus.REFUNDED,
            payment_method=PaymentMethod.CREDIT_CARD
        )
    )
    # The refund posted on October 25 (delayed 23 days):
    transactions.append(
        SyntheticTransaction(
            transaction_id=refund_tx_id,
            user_id="usr_alex_chen",
            account_id="acc_alex_credit",
            merchant_id="mer_nordic_threads",
            amount=ret_amt,
            currency="USD",
            transaction_type=TransactionType.REFUND,
            category="clothing",
            timestamp="2026-10-25T16:30:00Z",
            description="Nordic Weave Apparel — Return Refund Processed",
            status=TransactionStatus.COMPLETED,
            payment_method=PaymentMethod.CREDIT_CARD,
            related_transaction_id=orig_tx_id
        )
    )
    # Balance effect: original expense (-145), refund (+145) = net 0

    # D) Duplicate-looking transaction scenario (Legitimate repeated charge):
    # Two identical charges on the same day for two distinct team licenses:
    dup1_id = "txn_alex_dup_license_1"
    dup2_id = "txn_alex_dup_license_2"
    lic_amt = Decimal("49.00")
    transactions.append(
        SyntheticTransaction(
            transaction_id=dup1_id,
            user_id="usr_alex_chen",
            account_id="acc_alex_credit",
            merchant_id="mer_git_forge",
            amount=lic_amt,
            currency="USD",
            transaction_type=TransactionType.EXPENSE,
            category="software",
            timestamp="2026-10-14T09:15:00Z",
            description="GitForge — Developer Tool Plugin Seat A (Order #GF-9101)",
            status=TransactionStatus.COMPLETED,
            payment_method=PaymentMethod.CREDIT_CARD,
            anomaly_flag=True
        )
    )
    transactions.append(
        SyntheticTransaction(
            transaction_id=dup2_id,
            user_id="usr_alex_chen",
            account_id="acc_alex_credit",
            merchant_id="mer_git_forge",
            amount=lic_amt,
            currency="USD",
            transaction_type=TransactionType.EXPENSE,
            category="software",
            timestamp="2026-10-14T09:16:00Z",
            description="GitForge — Developer Tool Plugin Seat B (Order #GF-9102)",
            status=TransactionStatus.COMPLETED,
            payment_method=PaymentMethod.CREDIT_CARD,
            anomaly_flag=True
        )
    )
    account_balances["acc_alex_credit"] -= (lic_amt * 2)

    # 3. USER 2: Sarah Jenkins (usr_sarah_jenkins)
    # Freelance variable income deposits + overspending on groceries
    for m in range(1, 12):
        s_date = datetime(2025, 11, 1) + timedelta(days=m * 30)
        # Monthly client retainer
        c_amt = Decimal("5200.00")
        transactions.append(
            SyntheticTransaction(
                transaction_id=f"txn_sarah_retainer_{m}",
                user_id="usr_sarah_jenkins",
                account_id="acc_sarah_checking",
                amount=c_amt,
                currency="USD",
                transaction_type=TransactionType.INCOME,
                category="income",
                timestamp=s_date.replace(day=3, hour=10).isoformat() + "Z",
                description="Client Retainer Deposit — Jenkins Design",
                status=TransactionStatus.COMPLETED,
                payment_method=PaymentMethod.BANK_TRANSFER,
                is_recurring=True
            )
        )
        account_balances["acc_sarah_checking"] = account_balances.get("acc_sarah_checking", Decimal("0.00")) + c_amt

        # Rent $1,700
        transactions.append(
            SyntheticTransaction(
                transaction_id=f"txn_sarah_rent_{m}",
                user_id="usr_sarah_jenkins",
                account_id="acc_sarah_checking",
                amount=Decimal("1700.00"),
                currency="USD",
                transaction_type=TransactionType.EXPENSE,
                category="housing",
                timestamp=s_date.replace(day=1, hour=9).isoformat() + "Z",
                description="Canyon Creek Apartments — Monthly Rent",
                status=TransactionStatus.COMPLETED,
                payment_method=PaymentMethod.BANK_TRANSFER,
                is_recurring=True
            )
        )
        account_balances["acc_sarah_checking"] -= Decimal("1700.00")

        # Heavy grocery spending (exceeds $450 budget in recent months, e.g. $580-$620)
        g_amt = Decimal("590.00") if m >= 8 else Decimal("420.00")
        transactions.append(
            SyntheticTransaction(
                transaction_id=f"txn_sarah_groc_{m}",
                user_id="usr_sarah_jenkins",
                account_id="acc_sarah_checking",
                merchant_id="mer_fresh_harvest",
                amount=g_amt,
                currency="USD",
                transaction_type=TransactionType.EXPENSE,
                category="groceries",
                timestamp=s_date.replace(day=18, hour=18).isoformat() + "Z",
                description="Fresh Harvest Organic Market — Monthly Specialty Grocery Total",
                status=TransactionStatus.COMPLETED,
                payment_method=PaymentMethod.DEBIT_CARD
            )
        )
        account_balances["acc_sarah_checking"] -= g_amt

    # 4. USER 3: Marcus Vance (usr_marcus_vance)
    # High salary $11,500, luxury travel, gym sub with missing telemetry
    for m in range(1, 12):
        v_date = datetime(2025, 11, 1) + timedelta(days=m * 30)
        # Salary
        transactions.append(
            SyntheticTransaction(
                transaction_id=f"txn_marcus_sal_{m}",
                user_id="usr_marcus_vance",
                account_id="acc_marcus_checking",
                amount=Decimal("11500.00"),
                currency="USD",
                transaction_type=TransactionType.INCOME,
                category="income",
                timestamp=v_date.replace(day=1, hour=9).isoformat() + "Z",
                description="Executive Payroll Deposit — Vanguard Scale Partners",
                status=TransactionStatus.COMPLETED,
                payment_method=PaymentMethod.BANK_TRANSFER,
                is_recurring=True
            )
        )
        account_balances["acc_marcus_checking"] = account_balances.get("acc_marcus_checking", Decimal("0.00")) + Decimal("11500.00")

        # Mortgage $3,400
        transactions.append(
            SyntheticTransaction(
                transaction_id=f"txn_marcus_mort_{m}",
                user_id="usr_marcus_vance",
                account_id="acc_marcus_checking",
                amount=Decimal("3400.00"),
                currency="USD",
                transaction_type=TransactionType.EXPENSE,
                category="housing",
                timestamp=v_date.replace(day=1, hour=10).isoformat() + "Z",
                description="Pacific Summit Bancorp — Mortgage Payment",
                status=TransactionStatus.COMPLETED,
                payment_method=PaymentMethod.BANK_TRANSFER,
                is_recurring=True
            )
        )
        account_balances["acc_marcus_checking"] -= Decimal("3400.00")

        # Diamond gym $180
        transactions.append(
            SyntheticTransaction(
                transaction_id=f"txn_marcus_gym_{m}",
                user_id="usr_marcus_vance",
                account_id="acc_marcus_checking",
                merchant_id="mer_apex_fitness",
                amount=Decimal("180.00"),
                currency="USD",
                transaction_type=TransactionType.EXPENSE,
                category="fitness",
                timestamp=v_date.replace(day=1, hour=4).isoformat() + "Z",
                description="Apex Athletic Diamond Membership",
                status=TransactionStatus.COMPLETED,
                payment_method=PaymentMethod.BANK_TRANSFER,
                is_recurring=True
            )
        )
        account_balances["acc_marcus_checking"] -= Decimal("180.00")

    # 5. BUSINESS TRANSACTIONS (Aurora Tech & Nexus Consulting)
    # Aurora Tech Monthly SaaS Revenues & Cloud Costs
    for m in range(1, 12):
        b_date = datetime(2025, 11, 1) + timedelta(days=m * 30)
        # SaaS Subscriptions collected
        rev_amt = Decimal("45000.00")
        transactions.append(
            SyntheticTransaction(
                transaction_id=f"txn_biz_aurora_rev_{m}",
                business_id="biz_aurora_tech",
                account_id="acc_aurora_operating",
                amount=rev_amt,
                currency="USD",
                transaction_type=TransactionType.INCOME,
                category="saas_revenue",
                timestamp=b_date.replace(day=10, hour=12).isoformat() + "Z",
                description="Recurring Enterprise Customer Subscriptions",
                status=TransactionStatus.COMPLETED,
                payment_method=PaymentMethod.BANK_TRANSFER,
                is_recurring=True
            )
        )
        account_balances["acc_aurora_operating"] = account_balances.get("acc_aurora_operating", Decimal("0.00")) + rev_amt

        # Payroll expense $28,000
        pay_amt = Decimal("28000.00")
        transactions.append(
            SyntheticTransaction(
                transaction_id=f"txn_biz_aurora_pay_{m}",
                business_id="biz_aurora_tech",
                account_id="acc_aurora_operating",
                amount=pay_amt,
                currency="USD",
                transaction_type=TransactionType.EXPENSE,
                category="payroll",
                timestamp=b_date.replace(day=25, hour=9).isoformat() + "Z",
                description="Monthly Employee Payroll Batch",
                status=TransactionStatus.COMPLETED,
                payment_method=PaymentMethod.BANK_TRANSFER,
                is_recurring=True
            )
        )
        account_balances["acc_aurora_operating"] -= pay_amt

    # Nexus Consulting: Fluctuating cash flow
    # Month with cash flow shortage (delayed payment):
    short_date = datetime(2026, 9, 15)
    transactions.append(
        SyntheticTransaction(
            transaction_id="txn_biz_nexus_payroll_sep",
            business_id="biz_nexus_consulting",
            account_id="acc_nexus_operating",
            amount=Decimal("18000.00"),
            currency="USD",
            transaction_type=TransactionType.EXPENSE,
            category="payroll",
            timestamp=short_date.replace(day=28).isoformat() + "Z",
            description="Nexus Advisory Monthly Payroll",
            status=TransactionStatus.COMPLETED,
            payment_method=PaymentMethod.BANK_TRANSFER,
            is_recurring=True
        )
    )
    account_balances["acc_nexus_operating"] = account_balances.get("acc_nexus_operating", Decimal("0.00")) - Decimal("18000.00")

    # Sort transactions chronologically
    transactions.sort(key=lambda t: t.timestamp)

    return transactions, account_balances

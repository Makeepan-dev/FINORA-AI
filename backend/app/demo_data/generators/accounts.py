from decimal import Decimal
from typing import List, Dict
from ..models.account import SyntheticAccount, AccountType, AccountStatus

def generate_accounts(users_list=None, businesses_list=None) -> List[SyntheticAccount]:
    accounts: List[SyntheticAccount] = []

    # Accounts for Alex Chen (usr_alex_chen)
    accounts.extend([
        SyntheticAccount(
            account_id="acc_alex_checking",
            owner_id="usr_alex_chen",
            owner_type="user",
            account_name="Primary Premier Checking",
            account_type=AccountType.CHECKING,
            currency="USD",
            opening_balance=Decimal("4200.00"),
            current_balance=Decimal("4200.00"),  # will be updated by transaction generator
            creation_date="2025-01-01",
            account_number_mask="SYNTH-CHK-****-8812"
        ),
        SyntheticAccount(
            account_id="acc_alex_savings",
            owner_id="usr_alex_chen",
            owner_type="user",
            account_name="High-Yield Vault Savings",
            account_type=AccountType.SAVINGS,
            currency="USD",
            opening_balance=Decimal("18000.00"),
            current_balance=Decimal("18000.00"),
            creation_date="2025-01-01",
            account_number_mask="SYNTH-SAV-****-3319"
        ),
        SyntheticAccount(
            account_id="acc_alex_credit",
            owner_id="usr_alex_chen",
            owner_type="user",
            account_name="Apex Sapphire Cash Rewards",
            account_type=AccountType.CREDIT_CARD,
            currency="USD",
            opening_balance=Decimal("0.00"),
            current_balance=Decimal("0.00"),
            credit_limit=Decimal("12000.00"),
            creation_date="2025-01-15",
            account_number_mask="SYNTH-CC-****-4091"
        ),
        SyntheticAccount(
            account_id="acc_alex_paypal",
            owner_id="usr_alex_chen",
            owner_type="user",
            account_name="PayPal Digital Wallet",
            account_type=AccountType.PAYPAL_WALLET,
            currency="USD",
            opening_balance=Decimal("350.00"),
            current_balance=Decimal("350.00"),
            creation_date="2025-02-01",
            account_number_mask="SYNTH-PP-****-7210"
        ),
    ])

    # Accounts for Sarah Jenkins (usr_sarah_jenkins)
    accounts.extend([
        SyntheticAccount(
            account_id="acc_sarah_checking",
            owner_id="usr_sarah_jenkins",
            owner_type="user",
            account_name="Creative Studio Checking",
            account_type=AccountType.CHECKING,
            currency="USD",
            opening_balance=Decimal("2800.00"),
            current_balance=Decimal("2800.00"),
            creation_date="2025-01-01",
            account_number_mask="SYNTH-CHK-****-1194"
        ),
        SyntheticAccount(
            account_id="acc_sarah_savings",
            owner_id="usr_sarah_jenkins",
            owner_type="user",
            account_name="Tax & Safety Buffer Savings",
            account_type=AccountType.SAVINGS,
            currency="USD",
            opening_balance=Decimal("5000.00"),
            current_balance=Decimal("5000.00"),
            creation_date="2025-01-01",
            account_number_mask="SYNTH-SAV-****-5521"
        ),
        SyntheticAccount(
            account_id="acc_sarah_paypal",
            owner_id="usr_sarah_jenkins",
            owner_type="user",
            account_name="PayPal Designer Commerce",
            account_type=AccountType.PAYPAL_WALLET,
            currency="USD",
            opening_balance=Decimal("180.00"),
            current_balance=Decimal("180.00"),
            creation_date="2025-01-20",
            account_number_mask="SYNTH-PP-****-9402"
        ),
    ])

    # Accounts for Marcus Vance (usr_marcus_vance)
    accounts.extend([
        SyntheticAccount(
            account_id="acc_marcus_checking",
            owner_id="usr_marcus_vance",
            owner_type="user",
            account_name="Executive Private Client Checking",
            account_type=AccountType.CHECKING,
            currency="USD",
            opening_balance=Decimal("9500.00"),
            current_balance=Decimal("9500.00"),
            creation_date="2025-01-01",
            account_number_mask="SYNTH-CHK-****-6632"
        ),
        SyntheticAccount(
            account_id="acc_marcus_savings",
            owner_id="usr_marcus_vance",
            owner_type="user",
            account_name="Strategic Growth Reserves",
            account_type=AccountType.SAVINGS,
            currency="USD",
            opening_balance=Decimal("45000.00"),
            current_balance=Decimal("45000.00"),
            creation_date="2025-01-01",
            account_number_mask="SYNTH-SAV-****-7789"
        ),
        SyntheticAccount(
            account_id="acc_marcus_paypal",
            owner_id="usr_marcus_vance",
            owner_type="user",
            account_name="PayPal Executive Wallet",
            account_type=AccountType.PAYPAL_WALLET,
            currency="USD",
            opening_balance=Decimal("750.00"),
            current_balance=Decimal("750.00"),
            creation_date="2025-01-10",
            account_number_mask="SYNTH-PP-****-2201"
        ),
    ])

    # Accounts for Business 1 (biz_aurora_tech)
    accounts.extend([
        SyntheticAccount(
            account_id="acc_aurora_operating",
            owner_id="biz_aurora_tech",
            owner_type="business",
            account_name="Aurora Operating Treasury",
            account_type=AccountType.CHECKING,
            currency="USD",
            opening_balance=Decimal("68000.00"),
            current_balance=Decimal("68000.00"),
            creation_date="2025-01-01",
            account_number_mask="SYNTH-BIZ-****-4100"
        ),
        SyntheticAccount(
            account_id="acc_aurora_paypal",
            owner_id="biz_aurora_tech",
            owner_type="business",
            account_name="Aurora SaaS Checkout Gateway",
            account_type=AccountType.PAYPAL_WALLET,
            currency="USD",
            opening_balance=Decimal("12400.00"),
            current_balance=Decimal("12400.00"),
            creation_date="2025-01-01",
            account_number_mask="SYNTH-PP-****-8833"
        ),
    ])

    # Accounts for Business 2 (biz_nexus_consulting)
    accounts.extend([
        SyntheticAccount(
            account_id="acc_nexus_operating",
            owner_id="biz_nexus_consulting",
            owner_type="business",
            account_name="Nexus Advisory Operating",
            account_type=AccountType.CHECKING,
            currency="USD",
            opening_balance=Decimal("34000.00"),
            current_balance=Decimal("34000.00"),
            creation_date="2025-01-01",
            account_number_mask="SYNTH-BIZ-****-9150"
        ),
    ])

    return accounts

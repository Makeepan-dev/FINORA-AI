import json
import csv
import io
import os
from decimal import Decimal
from typing import Dict, Any, List, Optional
from .configuration import DemoDataConfig, DEFAULT_CONFIG
from .generators.merchants import generate_merchants
from .generators.products import generate_products
from .generators.users import generate_users
from .generators.accounts import generate_accounts
from .generators.subscriptions import generate_subscriptions
from .generators.transactions import generate_transactions
from .generators.businesses import generate_businesses
from .generators.invoices import generate_invoices
from .generators.activity import generate_activity_evidence
from .generators.payments import generate_payment_records
from .generators.investigation import generate_investigations
from .validators import validate_dataset, ValidationReport
from .scenarios.catalogue import get_predefined_scenarios, TestScenario

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

class DatasetManager:
    def __init__(self, config: Optional[DemoDataConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.users = []
        self.accounts = []
        self.transactions = []
        self.merchants = []
        self.subscriptions = []
        self.products = []
        self.businesses = []
        self.invoices = []
        self.activity_evidence = []
        self.payment_requests = []
        self.payment_auths = []
        self.payment_captures = []
        self.authorization_policies = []
        self.investigation_cases = []
        self.active_scenario_id = "scen_01_normal_spending"
        self.last_validation_report: Optional[ValidationReport] = None
        self.generate_complete_dataset()

    def generate_complete_dataset(self, seed: Optional[int] = None):
        """Generates the full deterministic synthetic financial data bank."""
        active_seed = seed if seed is not None else self.config.random_seed
        self.config.random_seed = active_seed

        # 1. Base static entities
        self.merchants = generate_merchants()
        self.products = generate_products()
        self.users = generate_users()
        self.businesses = generate_businesses()
        self.subscriptions = generate_subscriptions()
        self.invoices = generate_invoices()
        self.activity_evidence = generate_activity_evidence()
        self.investigation_cases = generate_investigations()

        pay_reqs, pay_auths, pay_caps, policies = generate_payment_records()
        self.payment_requests = pay_reqs
        self.payment_auths = pay_auths
        self.payment_captures = pay_caps
        self.authorization_policies = policies

        # 2. Accounts & transactions with reconciled balance propagation
        raw_accounts = generate_accounts(self.users, self.businesses)
        tx_list, reconciled_balances = generate_transactions(
            seed=active_seed,
            history_months=self.config.history_months,
            accounts=raw_accounts
        )
        self.transactions = tx_list

        # Update accounts with exact reconciled current_balance
        for acc in raw_accounts:
            if acc.account_id in reconciled_balances:
                acc.current_balance = reconciled_balances[acc.account_id]
        self.accounts = raw_accounts

        # Run automated validation
        self.last_validation_report = self.validate()
        return self.get_statistics()

    def reset_dataset(self):
        """Safely resets the dataset back to initial seeded state."""
        return self.generate_complete_dataset(seed=42)

    def validate(self) -> ValidationReport:
        """Runs full financial data integrity audit."""
        report = validate_dataset(
            users=self.users,
            accounts=self.accounts,
            transactions=self.transactions,
            merchants=self.merchants,
            subscriptions=self.subscriptions,
            products=self.products,
            businesses=self.businesses,
            invoices=self.invoices,
            evidence=self.activity_evidence,
            payments=self.payment_requests
        )
        self.last_validation_report = report
        return report

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "status": "active",
            "seed": self.config.random_seed,
            "currency": self.config.primary_currency,
            "counts": {
                "users": len(self.users),
                "accounts": len(self.accounts),
                "transactions": len(self.transactions),
                "merchants": len(self.merchants),
                "products": len(self.products),
                "subscriptions": len(self.subscriptions),
                "businesses": len(self.businesses),
                "invoices": len(self.invoices),
                "activity_records": len(self.activity_evidence),
                "payment_records": len(self.payment_requests),
                "investigation_cases": len(self.investigation_cases),
                "predefined_scenarios": len(get_predefined_scenarios())
            },
            "validation_status": self.last_validation_report.overall_status if self.last_validation_report else "UNCHECKED",
            "synthetic_marker": self.config.synthetic_marker
        }

    def list_scenarios(self) -> List[TestScenario]:
        return get_predefined_scenarios()

    def load_scenario(self, scenario_id: str) -> Optional[TestScenario]:
        scenarios = {s.scenario_id: s for s in get_predefined_scenarios()}
        if scenario_id in scenarios:
            self.active_scenario_id = scenario_id
            return scenarios[scenario_id]
        return None

    def export_to_json(self) -> str:
        """Serializes full dataset into JSON format."""
        dataset = {
            "metadata": {
                "generated_with_seed": self.config.random_seed,
                "history_months": self.config.history_months,
                "is_synthetic": True,
                "synthetic_marker": self.config.synthetic_marker
            },
            "users": [u.model_dump() for u in self.users],
            "accounts": [a.model_dump() for a in self.accounts],
            "transactions": [t.model_dump() for t in self.transactions],
            "merchants": [m.model_dump() for m in self.merchants],
            "products": [p.model_dump() for p in self.products],
            "subscriptions": [s.model_dump() for s in self.subscriptions],
            "businesses": [b.model_dump() for b in self.businesses],
            "invoices": [i.model_dump() for i in self.invoices],
            "activity_evidence": [e.model_dump() for e in self.activity_evidence],
            "investigation_cases": [c.model_dump() for c in self.investigation_cases],
        }
        return json.dumps(dataset, cls=DecimalEncoder, indent=2)

    def export_transactions_to_csv(self) -> str:
        """Exports transactions to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "transaction_id", "user_id", "business_id", "account_id", "merchant_id",
            "amount", "currency", "transaction_type", "category", "timestamp",
            "description", "status", "payment_method", "is_synthetic"
        ])
        for t in self.transactions:
            writer.writerow([
                t.transaction_id, t.user_id or "", t.business_id or "", t.account_id,
                t.merchant_id or "", str(t.amount), t.currency, t.transaction_type.value,
                t.category, t.timestamp, t.description, t.status.value,
                t.payment_method.value, "true"
            ])
        return output.getvalue()

    def import_from_json(self, json_content: str) -> Dict[str, Any]:
        """Imports and validates a JSON dataset."""
        data = json.loads(json_content)
        if "metadata" not in data or not data["metadata"].get("is_synthetic"):
            raise ValueError("Dataset rejected: Must be verified synthetic FINORA data.")

        # Re-initialize models
        self.users = [SyntheticUser(**u) for u in data.get("users", [])]
        self.accounts = [SyntheticAccount(**a) for a in data.get("accounts", [])]
        self.transactions = [SyntheticTransaction(**t) for t in data.get("transactions", [])]
        self.merchants = [SyntheticMerchant(**m) for m in data.get("merchants", [])]
        self.products = [SyntheticProduct(**p) for p in data.get("products", [])]
        self.subscriptions = [SyntheticSubscription(**s) for s in data.get("subscriptions", [])]
        self.businesses = [SyntheticBusiness(**b) for b in data.get("businesses", [])]
        self.invoices = [SyntheticInvoice(**i) for i in data.get("invoices", [])]
        self.activity_evidence = [SyntheticActivityEvidence(**e) for e in data.get("activity_evidence", [])]

        # Run validation
        val_report = self.validate()
        return {
            "imported_records": len(self.transactions) + len(self.users) + len(self.accounts),
            "validation_status": val_report.overall_status,
            "errors": val_report.balance_errors + val_report.referential_errors
        }

# Global singleton for backend demo data bank
global_dataset_manager = DatasetManager()

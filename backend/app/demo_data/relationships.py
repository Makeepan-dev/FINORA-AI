from typing import Dict, List, Any
from .models.user import SyntheticUser
from .models.account import SyntheticAccount
from .models.transaction import SyntheticTransaction
from .models.merchant import SyntheticMerchant
from .models.subscription import SyntheticSubscription

class EntityRelationshipGraph:
    """Provides fast indexed lookup of interconnected entities in the financial data bank."""
    def __init__(self, users: List[SyntheticUser], accounts: List[SyntheticAccount],
                 transactions: List[SyntheticTransaction], merchants: List[SyntheticMerchant],
                 subscriptions: List[SyntheticSubscription]):
        self.users_by_id = {u.user_id: u for u in users}
        self.accounts_by_id = {a.account_id: a for a in accounts}
        self.merchants_by_id = {m.merchant_id: m for m in merchants}

        self.accounts_by_owner: Dict[str, List[SyntheticAccount]] = {}
        for acc in accounts:
            self.accounts_by_owner.setdefault(acc.owner_id, []).append(acc)

        self.transactions_by_user: Dict[str, List[SyntheticTransaction]] = {}
        self.transactions_by_account: Dict[str, List[SyntheticTransaction]] = {}
        for tx in transactions:
            if tx.user_id:
                self.transactions_by_user.setdefault(tx.user_id, []).append(tx)
            self.transactions_by_account.setdefault(tx.account_id, []).append(tx)

        self.subscriptions_by_user: Dict[str, List[SyntheticSubscription]] = {}
        for sub in subscriptions:
            self.subscriptions_by_user.setdefault(sub.user_id, []).append(sub)

    def get_user_full_context(self, user_id: str) -> Dict[str, Any]:
        user = self.users_by_id.get(user_id)
        if not user:
            return {}
        accounts = self.accounts_by_owner.get(user_id, [])
        txs = self.transactions_by_user.get(user_id, [])
        subs = self.subscriptions_by_user.get(user_id, [])
        return {
            "user": user,
            "accounts": accounts,
            "transaction_count": len(txs),
            "recent_transactions": txs[-20:],
            "subscriptions": subs
        }

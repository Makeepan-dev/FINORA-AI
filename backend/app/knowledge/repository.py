from typing import List, Dict, Optional, Any
from .base import KnowledgeEntry, KnowledgeDomain, KnowledgeSufficiency
from .personal_finance import get_personal_finance_entries
from .business_finance import get_business_finance_entries
from .accounting import get_accounting_entries
from .payments_commerce import get_payments_commerce_entries
from .consumer_commerce import get_consumer_commerce_entries

class KnowledgeRepository:
    """
    Central, high-performance structured knowledge repository for FINORA.
    Stores authoritative financial, business, accounting, payment, and commerce knowledge.
    Enables internal-first reasoning without relying on external AI API dependencies.
    """
    def __init__(self):
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._domain_index: Dict[KnowledgeDomain, List[KnowledgeEntry]] = {}
        self._topic_index: Dict[str, KnowledgeEntry] = {}
        self._initialize_knowledge()

    def _initialize_knowledge(self):
        all_entries: List[KnowledgeEntry] = []
        all_entries.extend(get_personal_finance_entries())
        all_entries.extend(get_business_finance_entries())
        all_entries.extend(get_accounting_entries())
        all_entries.extend(get_payments_commerce_entries())
        all_entries.extend(get_consumer_commerce_entries())

        for entry in all_entries:
            self._entries[entry.knowledge_id] = entry
            self._domain_index.setdefault(entry.domain, []).append(entry)
            self._topic_index[entry.topic.lower()] = entry

    def get_by_id(self, knowledge_id: str) -> Optional[KnowledgeEntry]:
        return self._entries.get(knowledge_id)

    def get_by_topic(self, topic: str) -> Optional[KnowledgeEntry]:
        return self._topic_index.get(topic.lower())

    def get_by_domain(self, domain: KnowledgeDomain) -> List[KnowledgeEntry]:
        return self._domain_index.get(domain, [])

    def search(self, query: str, limit: int = 5) -> List[KnowledgeEntry]:
        """
        Retrieves relevant structured knowledge entries matching query keywords.
        """
        q = query.lower()
        scored_entries = []

        for entry in self._entries.values():
            score = 0
            if entry.topic.lower() in q:
                score += 10
            for rule in entry.rules:
                if any(w in rule.lower() for w in q.split() if len(w) > 3):
                    score += 2
            if any(w in entry.definition.lower() for w in q.split() if len(w) > 3):
                score += 3
            if any(w in entry.title.lower() for w in q.split() if len(w) > 3):
                score += 5

            if score > 0:
                scored_entries.append((score, entry))

        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_entries[:limit]]

    def get_all_entries(self) -> List[KnowledgeEntry]:
        return list(self._entries.values())

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Returns structured inventory of the knowledge base across domains."""
        summary = {}
        for domain, entries in self._domain_index.items():
            summary[domain.value] = {
                "count": len(entries),
                "topics": [e.topic for e in entries]
            }
        return {
            "total_knowledge_entries": len(self._entries),
            "domains": summary
        }

global_knowledge_repository = KnowledgeRepository()

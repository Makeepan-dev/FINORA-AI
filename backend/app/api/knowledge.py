from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, List, Optional
from ..knowledge.repository import global_knowledge_repository

router = APIRouter(prefix="/knowledge", tags=["Structured Financial & Commerce Knowledge"])

@router.get("/inventory")
def get_knowledge_inventory() -> Dict[str, Any]:
    """Returns complete inventory of structured knowledge domains and topics."""
    return global_knowledge_repository.get_inventory_summary()

@router.get("/search")
def search_knowledge(q: str = Query(..., min_length=2), limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves relevant structured knowledge entries matching query."""
    entries = global_knowledge_repository.search(query=q, limit=limit)
    return [e.model_dump() for e in entries]

@router.get("/{topic}")
def get_knowledge_by_topic(topic: str) -> Dict[str, Any]:
    """Retrieves specific knowledge entry by topic identifier."""
    entry = global_knowledge_repository.get_by_topic(topic)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Knowledge topic '{topic}' not found.")
    return entry.model_dump()

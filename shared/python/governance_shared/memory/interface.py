"""
ICGL Memory Interface
======================

Defines the abstract contract for Vector Stores.
Enforces P-CORE-01 (Strategic Optionality) by ensuring the system depends on this 
abstraction, not on specific vendors (Qdrant/Chroma).
"""

from typing import List, Dict, Any, Protocol, Optional
from dataclasses import dataclass

@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None

@dataclass
class SearchResult:
    document: Document
    score: float

class VectorStore(Protocol):
    """
    Protocol for Semantic Memory storage.
    """
    
    async def initialize(self) -> None:
        """Bootstraps the storage (create collections, load indices)."""
        ...
        
    async def add_document(self, doc: Document) -> None:
        """Upserts a document to the store."""
        ...
        
    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Semantically searches for documents relevant to the query."""
        ...
        
    async def save(self) -> None:
        """Persists the state to disk (if applicable)."""
        ...

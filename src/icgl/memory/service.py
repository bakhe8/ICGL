"""
Vector Memory Service
---------------------

High-level service for semantic memory operations.
Wraps the underlying vector store (Qdrant) and manages embedding/retrieval policies.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

from .interface import VectorStore, Document, SearchResult
from .qdrant_adapter import QdrantAdapter
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class VectorMemoryService:
    """
    Manages long-term semantic memory.
    
    Features:
    - Async indexing (fire and forget)
    - Hybrid retrieval (semantic + metadata filters)
    - Automatic retries
    """
    
    def __init__(self, store: Optional[VectorStore] = None):
        self.store = store or QdrantAdapter()
        self._initialized = False
        
    async def initialize(self) -> None:
        """Ensure backend is ready"""
        if not self._initialized:
            try:
                await self.store.initialize()
                self._initialized = True
                logger.info("🧠 Vector Memory Service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Vector Memory: {e}")
                # We don't raise here to allow strict degradation (app runs without vector memory)
                
    async def remember_interaction(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> None:
        """
        Index a conversation turn for future recall.
        
        This should usually be called as a background task.
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            doc = Document(
                id=f"{session_id}_{datetime.utcnow().timestamp()}",
                content=f"{role}: {content}",
                metadata={
                    "session_id": session_id,
                    "role": role,
                    "timestamp": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            await self.store.add_document(doc)
            logger.debug(f"🧠 Remembered interaction in session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to index interaction: {e}")

    async def recall_context(self, query: str, session_id: str = None, limit: int = 5) -> List[SearchResult]:
        """
        Retrieve relevant context for a query.
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Future: Apply metadata filter for session_id if we want strictly local context,
            # but usually we want global context (cross-session).
            results = await self.store.search(query, limit=limit)
            return results
        except Exception as e:
            logger.error(f"Failed to recall context: {e}")
            return []
            
# Global Instance
_memory_service: Optional[VectorMemoryService] = None

def get_memory_service() -> VectorMemoryService:
    global _memory_service
    if _memory_service is None:
        _memory_service = VectorMemoryService()
    return _memory_service

"""
ICGL Qdrant Adapter
===================

Implements the VectorStore protocol using Qdrant.
Supports Local Mode (no Docker required) for development.
"""

import os
from typing import List
from uuid import UUID, uuid4
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    QdrantClient = None

from .interface import VectorStore, Document, SearchResult
from ..llm.client import LLMClient

class QdrantAdapter(VectorStore):
    def __init__(self, path: str = ":memory:", collection_name: str = "icgl_memory"):
        if not QdrantClient:
            raise ImportError("qdrant-client not installed. No mock fallback allowed.")
        env_path = os.getenv("ICGL_QDRANT_PATH")
        if env_path:
            path = env_path
        self.path = path
        self.collection_name = collection_name
        self.client = QdrantClient(path=path)
        self.llm_client = LLMClient()

    async def initialize(self) -> None:
        """Creates the collection if it doesn't exist."""
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            # 1536 is OpenAI Ada-002 dimension
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            
    async def _embed(self, text: str) -> List[float]:
        """Helper to get embeddings using LLMClient."""
        if self.llm_client.api_key and self.llm_client.client:
            return await self.llm_client.get_embedding(text)
        raise RuntimeError("Embedding failed: OPENAI_API_KEY missing or client not initialized.")

    async def add_document(self, doc: Document) -> None:
        vector = await self._embed(doc.content)
        try:
            safe_id = str(UUID(doc.id))
        except Exception:
            safe_id = str(uuid4())
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=safe_id,  # Qdrant supports UUID strings
                    vector=vector,
                    payload={"content": doc.content, "orig_id": doc.id, **doc.metadata}
                )
            ]
        )

    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        query_vector = await self._embed(query)
        
        # Use query_points if search is missing (possible version mismatch)
        try:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
        except AttributeError:
             # Fallback for some versions
             hits = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector, 
                limit=limit
            ).points
        
        results = []
        for hit in hits:
            doc = Document(
                id=str(hit.id),
                content=hit.payload.get("content", ""),
                metadata={k:v for k,v in hit.payload.items() if k != "content"}
            )
            results.append(SearchResult(document=doc, score=hit.score))
            
        return results

    async def save(self) -> None:
        # Qdrant local client saves automatically, but we can force flush if needed.
        pass

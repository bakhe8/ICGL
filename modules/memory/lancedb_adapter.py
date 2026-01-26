"""
ICGL LanceDB Adapter
====================

Implements the VectorStore protocol using LanceDB.
LanceDB is serverless and stores data in local files.
"""

import os
from typing import List

try:
    import lancedb  # type: ignore[import]
except Exception:  # pragma: no cover - optional dependency in dev
    lancedb = None

try:
    import pyarrow as pa  # type: ignore[import]
except Exception:  # pragma: no cover - optional dependency in dev
    pa = None

from modules.llm.client import LLMClient
from .interface import Document, SearchResult, VectorStore


class LanceDBAdapter(VectorStore):
    def __init__(self, uri: str = "data/lancedb", table_name: str = "icgl_memory"):
        env_uri = os.getenv("ICGL_LANCEDB_URI")
        if env_uri:
            uri = env_uri
        self.uri = uri
        self.table_name = table_name
        self.db = lancedb.connect(uri) if lancedb is not None else None
        self.llm_client = LLMClient()
        self.table = None

    async def initialize(self) -> None:
        """Bootstraps the table if it doesn't exist."""
        if self.db is None or pa is None:
            # LanceDB or pyarrow is unavailable in this environment.
            self.table = None
            return

        if self.table_name not in self.db.table_names():
            # Initial schema for the table
            # 1536 is OpenAI Ada-002 dimension
            schema = pa.schema(
                [
                    pa.field("vector", pa.list_(pa.float32(), 1536)),
                    pa.field("id", pa.string()),
                    pa.field("content", pa.string()),
                    pa.field(
                        "metadata", pa.string()
                    ),  # Store as JSON string for flexibility
                ]
            )
            self.table = self.db.create_table(self.table_name, schema=schema)
        else:
            self.table = self.db.open_table(self.table_name)

    async def _embed(self, text: str) -> List[float]:
        """Helper to get embeddings using LLMClient."""
        if self.llm_client.api_key and self.llm_client.client:
            return await self.llm_client.get_embedding(text)
        raise RuntimeError(
            "Embedding failed: OPENAI_API_KEY missing or client not initialized."
        )

    async def add_document(self, doc: Document) -> None:
        import json

        # Gracefully skip if LanceDB not available
        if self.table is None:
            return  # Silent skip - memory disabled

        vector = await self._embed(doc.content)

        data = [
            {
                "vector": vector,
                "id": str(doc.id),
                "content": doc.content,
                "metadata": json.dumps(doc.metadata),
            }
        ]

        # Use table.add when available
        add = getattr(self.table, "add", None)
        if callable(add):
            add(data)
        else:
            return  # Silent skip if method missing

    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        import json

        # Gracefully return empty if LanceDB not available
        if self.table is None:
            return []  # No results when memory disabled

        query_vector = await self._embed(query)

        search = getattr(self.table, "search", None)
        if not callable(search):
            return []  # No results if method missing

        hits = self.table.search(query_vector).limit(limit).to_list()

        results = []
        for hit in hits:
            doc = Document(
                id=hit["id"],
                content=hit["content"],
                metadata=json.loads(hit["metadata"]),
            )
            results.append(
                SearchResult(document=doc, score=1.0 - hit.get("_distance", 0))
            )  # LanceDB uses L2/Cosine distance

        return results

    async def save(self) -> None:
        # LanceDB is ACID and saves on write.
        pass

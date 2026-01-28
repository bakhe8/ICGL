from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any] = None


class QdrantAdapter:
    def __init__(self, path: str = None):
        pass

    async def initialize(self):
        pass

    async def add_document(self, doc: Document):
        pass

    async def search(self, query: str, limit: int = 4):
        return []

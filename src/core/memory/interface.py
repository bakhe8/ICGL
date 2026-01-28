from abc import ABC, abstractmethod
from typing import Any, List


class VectorStore(ABC):
    """Abstract interface for Vector Stores."""

    @abstractmethod
    async def search(self, query: str, limit: int = 4) -> List[Any]:
        """Search for similar documents."""
        pass

    @abstractmethod
    async def add_document(self, document: Any) -> None:
        """Add a document to the store."""
        pass

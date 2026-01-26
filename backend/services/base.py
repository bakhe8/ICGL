from typing import TypeVar

from modules.kb.storage import StorageBackend

T = TypeVar("T")


class BaseService:
    """
    Base class for all business logic services.
    Ensures consistent access to storage and common utilities.
    """

    def __init__(self, storage: StorageBackend):
        self.storage = storage

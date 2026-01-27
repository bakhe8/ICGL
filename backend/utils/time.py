from datetime import datetime


def now() -> str:
    """Returns current ISO timestamp."""
    return datetime.now().isoformat()

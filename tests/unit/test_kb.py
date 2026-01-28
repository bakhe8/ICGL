import sqlite3

import pytest

from src.core.kb.schemas import ADR, uid
from src.core.kb.storage import StorageBackend


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_kb.db"
    return str(db_file)


def test_kb_storage_init(temp_db):
    StorageBackend(temp_db)
    # Check if tables were created
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='adrs'")
    assert cursor.fetchone() is not None
    conn.close()


def test_add_get_adr(temp_db):
    storage = StorageBackend(temp_db)
    adr = ADR(
        id=uid(),
        title="Test ADR",
        status="DRAFT",
        context="Testing context",
        decision="Testing decision",
        consequences=[],
        related_policies=[],
        sentinel_signals=[],
        human_decision_id=None,
    )
    storage.save_adr(adr)

    all_adrs = storage.load_all_adrs()
    assert adr.id in all_adrs
    retrieved = all_adrs[adr.id]
    assert retrieved.title == "Test ADR"
    assert retrieved.id == adr.id

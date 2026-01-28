import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    path = Path("tests/data")
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def mock_env():
    os.environ["OPENAI_API_KEY"] = "sk-test-key-for-unit-testing"
    yield
    # No cleanup needed as it's process-wide env

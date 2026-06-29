import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def pikachu_payload() -> dict:
    return json.loads((FIXTURES / "pikachu.json").read_text())


@pytest.fixture(autouse=True)
def _isolate_cache(tmp_path, monkeypatch):
    monkeypatch.setattr("pokedex.client.DEFAULT_CACHE_DIR", tmp_path / "cache")

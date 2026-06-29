import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def pikachu_payload() -> dict:
    return json.loads((FIXTURES / "pikachu.json").read_text())

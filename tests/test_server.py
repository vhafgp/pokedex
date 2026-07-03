import pytest

from pokedex import server
from pokedex.models import Pokemon, PokemonRecord
from pokedex.snapshot import build_snapshot


def _p(id_: int, name: str, types: tuple[str, ...]) -> Pokemon:
    return Pokemon(
        id=id_, name=name, height=1, weight=1, types=types, abilities=("static",), stats={"hp": 1}
    )


@pytest.fixture
def dex(tmp_path, monkeypatch):
    db = tmp_path / "dex.sqlite"
    build_snapshot(db, [_p(7, "squirtle", ("water",)), _p(25, "pikachu", ("electric",))])
    monkeypatch.setenv("POKEDEX_DB", str(db))
    return db


def test_get_pokemon_tool(dex):
    result = server.get_pokemon("pikachu")
    assert result["id"] == 25
    assert result["types"] == ["electric"]


def test_get_pokemon_missing(dex):
    assert "error" in server.get_pokemon("missingno")


def test_search_by_type_tool(dex):
    assert [r["name"] for r in server.search_by_type("water")] == ["squirtle"]


def test_semantic_search_tool_formats_scores(dex, monkeypatch):
    record = PokemonRecord(
        id=25, name="pikachu", height=1, weight=1,
        types=("electric",), abilities=("static",), stats={},
    )
    monkeypatch.setattr("pokedex.search.semantic_search", lambda db, q, k: [(record, 0.9123)])
    out = server.semantic_search("electric mouse")
    assert out[0]["name"] == "pikachu"
    assert out[0]["score"] == 0.9123


def test_require_db_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("POKEDEX_DB", str(tmp_path / "nope.sqlite"))
    with pytest.raises(FileNotFoundError):
        server.get_pokemon("pikachu")

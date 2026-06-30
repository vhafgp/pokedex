from pokedex.models import Pokemon
from pokedex.snapshot import build_snapshot
from pokedex.store import get, search_by_type


def _p(id_: int, name: str, types: tuple[str, ...]) -> Pokemon:
    return Pokemon(
        id=id_, name=name, height=1, weight=1, types=types, abilities=("x",), stats={"hp": 1}
    )


def _build(tmp_path):
    db = tmp_path / "dex.sqlite"
    build_snapshot(
        db,
        [
            _p(7, "squirtle", ("water",)),
            _p(54, "psyduck", ("water",)),
            _p(25, "pikachu", ("electric",)),
        ],
    )
    return db


def test_get_by_name_and_id(tmp_path):
    db = _build(tmp_path)
    assert get(db, "pikachu").id == 25
    assert get(db, 25).name == "pikachu"
    assert get(db, "Pikachu").id == 25  # case-insensitive


def test_get_missing_returns_none(tmp_path):
    db = _build(tmp_path)
    assert get(db, "missingno") is None


def test_search_by_type_ordered(tmp_path):
    db = _build(tmp_path)
    water = search_by_type(db, "water")
    assert [p.name for p in water] == ["squirtle", "psyduck"]

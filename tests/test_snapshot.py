from pokedex.models import Pokemon
from pokedex.snapshot import build_snapshot
from pokedex.store import get


def _pokemon(**kw) -> Pokemon:
    base = dict(
        id=25,
        name="pikachu",
        height=4,
        weight=60,
        types=("electric",),
        abilities=("static", "lightning-rod"),
        stats={"hp": 35, "speed": 90},
    )
    base.update(kw)
    return Pokemon(**base)


def test_snapshot_round_trip(tmp_path):
    db = tmp_path / "dex.sqlite"
    build_snapshot(db, [_pokemon()])

    record = get(db, "pikachu")
    assert record is not None
    assert record.id == 25
    assert record.types == ("electric",)
    assert record.abilities == ("static", "lightning-rod")
    assert record.stats["speed"] == 90


def test_build_is_idempotent(tmp_path):
    db = tmp_path / "dex.sqlite"
    build_snapshot(db, [_pokemon()])
    build_snapshot(db, [_pokemon()])  # rebuild wipes first; no UNIQUE violation
    assert get(db, "pikachu") is not None

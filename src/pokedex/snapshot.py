"""Build the local SQLite snapshot from fetched Pokémon (the L3→L4 ETL sink)."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from pokedex.models import Pokemon

_SCHEMA = """
CREATE TABLE pokemon (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    height INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    stats TEXT NOT NULL
);
CREATE TABLE pokemon_type (
    pokemon_id INTEGER NOT NULL REFERENCES pokemon(id),
    type TEXT NOT NULL
);
CREATE TABLE pokemon_ability (
    pokemon_id INTEGER NOT NULL REFERENCES pokemon(id),
    ability TEXT NOT NULL
);
CREATE INDEX idx_pokemon_type ON pokemon_type(type);
"""


def build_snapshot(db_path: Path, pokemon: list[Pokemon]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.unlink(missing_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        conn.executescript(_SCHEMA)
        for p in pokemon:
            conn.execute(
                "INSERT INTO pokemon (id, name, height, weight, stats) VALUES (?, ?, ?, ?, ?)",
                (p.id, p.name, p.height, p.weight, json.dumps(p.stats)),
            )
            conn.executemany(
                "INSERT INTO pokemon_type (pokemon_id, type) VALUES (?, ?)",
                [(p.id, t) for t in p.types],
            )
            conn.executemany(
                "INSERT INTO pokemon_ability (pokemon_id, ability) VALUES (?, ?)",
                [(p.id, a) for a in p.abilities],
            )
        conn.commit()

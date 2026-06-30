"""Read layer over the local snapshot. Reconstructs trusted PokemonRecord rows (no Pydantic)."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from pokedex.models import PokemonRecord


def _record(conn: sqlite3.Connection, row: tuple) -> PokemonRecord:
    pid, name, height, weight, stats = row
    types = tuple(
        t for (t,) in conn.execute(
            "SELECT type FROM pokemon_type WHERE pokemon_id = ? ORDER BY rowid", (pid,)
        )
    )
    abilities = tuple(
        a for (a,) in conn.execute(
            "SELECT ability FROM pokemon_ability WHERE pokemon_id = ? ORDER BY rowid", (pid,)
        )
    )
    return PokemonRecord(
        id=pid,
        name=name,
        height=height,
        weight=weight,
        types=types,
        abilities=abilities,
        stats=json.loads(stats),
    )


def get(db_path: Path, name_or_id: str | int) -> PokemonRecord | None:
    key = str(name_or_id).lower()
    id_key = int(key) if key.isdigit() else -1
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute(
            "SELECT id, name, height, weight, stats FROM pokemon WHERE name = ? OR id = ?",
            (key, id_key),
        ).fetchone()
        return _record(conn, row) if row else None


def search_by_type(db_path: Path, type_name: str) -> list[PokemonRecord]:
    with closing(sqlite3.connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT p.id, p.name, p.height, p.weight, p.stats "
            "FROM pokemon p JOIN pokemon_type t ON t.pokemon_id = p.id "
            "WHERE t.type = ? ORDER BY p.id",
            (type_name.lower(),),
        ).fetchall()
        return [_record(conn, row) for row in rows]

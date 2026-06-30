"""Typed models: Pydantic validates API JSON at the ingest edge; a plain dataclass carries the
trusted snapshot read path (no re-validation)."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict


class Pokemon(BaseModel):
    """A Pokémon flattened from the PokéAPI `/pokemon/{id}` response."""

    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    height: int  # decimetres, per PokéAPI
    weight: int  # hectograms, per PokéAPI
    types: tuple[str, ...]
    abilities: tuple[str, ...]
    stats: dict[str, int]

    @classmethod
    def from_api(cls, raw: dict) -> Pokemon:
        return cls(
            id=raw["id"],
            name=raw["name"],
            height=raw["height"],
            weight=raw["weight"],
            types=tuple(t["type"]["name"] for t in raw["types"]),
            abilities=tuple(a["ability"]["name"] for a in raw["abilities"]),
            stats={s["stat"]["name"]: s["base_stat"] for s in raw["stats"]},
        )


@dataclass(frozen=True, slots=True)
class PokemonRecord:
    """A Pokémon read back from the local snapshot (trusted data, no validation)."""

    id: int
    name: str
    height: int
    weight: int
    types: tuple[str, ...]
    abilities: tuple[str, ...]
    stats: dict[str, int]

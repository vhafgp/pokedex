"""Typed ingest models. Pydantic validation runs here, at the API boundary, and nowhere else."""

from __future__ import annotations

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

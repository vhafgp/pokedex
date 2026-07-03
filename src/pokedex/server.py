"""Pokédex MCP server: exposes the snapshot as Claude tools over stdio, for Claude Code/Desktop on
a subscription (no API key). Snapshot path comes from POKEDEX_DB or the store default."""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from pokedex import search, store
from pokedex.models import PokemonRecord
from pokedex.store import DEFAULT_DB

mcp = FastMCP("pokedex")


def _require_db() -> Path:
    db = Path(os.environ.get("POKEDEX_DB") or DEFAULT_DB)
    if not db.exists():
        raise FileNotFoundError(f"Snapshot not found at {db}. Run `pokedex build` first.")
    return db


def _as_dict(record: PokemonRecord) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "types": list(record.types),
        "abilities": list(record.abilities),
        "stats": record.stats,
    }


@mcp.tool()
def get_pokemon(name_or_id: str) -> dict:
    """Look up one Pokémon by name or Pokédex id."""
    record = store.get(_require_db(), name_or_id)
    return _as_dict(record) if record else {"error": f"No Pokémon found: {name_or_id}"}


@mcp.tool()
def search_by_type(type_name: str) -> list[dict]:
    """List every Pokémon of a given type (water, electric, fire, ...)."""
    return [_as_dict(r) for r in store.search_by_type(_require_db(), type_name)]


@mcp.tool()
def semantic_search(query: str, k: int = 5) -> list[dict]:
    """Rank Pokémon by natural-language similarity to their type/ability profile."""
    hits = search.semantic_search(_require_db(), query, k)
    return [_as_dict(r) | {"score": round(score, 4)} for r, score in hits]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

"""Typer CLI over the library-core: build the snapshot, then query it offline."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from pokedex.client import make_async_client
from pokedex.fetch import fetch_all, list_pokemon_names
from pokedex.snapshot import build_snapshot
from pokedex.store import DEFAULT_DB, search_by_type
from pokedex.store import get as store_get

app = typer.Typer(no_args_is_help=True, add_completion=False)

DbOption = Annotated[Path, typer.Option(help="Snapshot path.")]


@app.command()
def build(
    limit: Annotated[int, typer.Option(help="Max Pokémon to fetch.")] = 100_000,
    concurrency: Annotated[int, typer.Option(help="Concurrent requests.")] = 10,
    db: DbOption = DEFAULT_DB,
) -> None:
    """Fetch the dex from PokéAPI and build the local SQLite snapshot."""

    async def _fetch() -> list:
        async with make_async_client() as client:
            names = await list_pokemon_names(client, limit=limit)
            return await fetch_all(names, client=client, concurrency=concurrency)

    pokemon = asyncio.run(_fetch())
    build_snapshot(db, pokemon)
    typer.echo(f"Built snapshot: {len(pokemon)} Pokémon -> {db}")


@app.command()
def embed(db: DbOption = DEFAULT_DB) -> None:
    """Embed the snapshot for semantic search (fastembed; downloads the model once)."""
    from pokedex.search import build_embeddings

    count = build_embeddings(db)
    typer.echo(f"Embedded {count} Pokémon -> {db}")


@app.command()
def get(name: str, db: DbOption = DEFAULT_DB) -> None:
    """Look up one Pokémon in the snapshot."""
    record = store_get(db, name)
    if record is None:
        typer.echo(f"Not found: {name}")
        raise typer.Exit(1)
    typer.echo(f"#{record.id} {record.name}")
    typer.echo(f"  types: {', '.join(record.types)}")
    typer.echo(f"  abilities: {', '.join(record.abilities)}")
    typer.echo(f"  stats: {record.stats}")


@app.command()
def search(
    type_: Annotated[str, typer.Option("--type", help="Filter by type.")],
    db: DbOption = DEFAULT_DB,
) -> None:
    """List Pokémon of a given type from the snapshot."""
    matches = search_by_type(db, type_)
    for record in matches:
        typer.echo(f"#{record.id} {record.name}")
    typer.echo(f"({len(matches)} match{'es' if len(matches) != 1 else ''})")

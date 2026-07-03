# pokedex

A study project I built to practice consuming a public REST API with discipline, then layering a
small retrieval and tooling stack on top. Structured as a five-step ladder (L1 to L5), each step
adding one technique on top of the last.

## What it does

- Fetches Pokémon from the public PokeAPI, validated into typed models (Pydantic)
- Caches responses to disk (RFC-9111 via Hishel) so repeat lookups skip the network
- Batch-fetches the full dex concurrently, with bounded concurrency and retries
- Snapshots everything into a local SQLite database for fast, offline queries
- Adds semantic search over the dex (sentence embeddings + NumPy cosine top-k)
- Exposes it all as an MCP server (Model Context Protocol) so the data can be queried as tools

## The ladder

| Step | Focus |
|------|-------|
| L1 | Typed fetch core (httpx + Pydantic) |
| L2 | RFC-9111 disk caching (Hishel) |
| L3 | Async batch fetch (asyncio, bounded concurrency, tenacity retries) |
| L4 | SQLite snapshot + Typer CLI |
| L5 | Semantic search + MCP server |

## Quickstart

```bash
uv venv
uv pip install -e ".[dev]"
pytest                # offline, no network

pokedex build         # fetch the dex into a local SQLite snapshot
pokedex embed         # build embeddings for semantic search
pokedex get pikachu
pokedex search --type water
```

## About

Not a product, just me learning by building. Each rung is a self-contained exercise in one
technique, from typed HTTP clients through async batch ETL to embeddings and a tool server.

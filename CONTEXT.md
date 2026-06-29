# CONTEXT — pokedex

The *why* behind this project, the domain language, and the locked design decisions. Read this
before extending the ladder; it grounds the `/grill-with-docs` workflow.

## What this is

A study/portfolio project for the QA→SWE→AI-Eng transition. The headline artifact is a **Claude
tool-using agent** that answers natural-language questions about Pokémon; the typed, cached,
resilient data layer beneath it exists to give that agent something real to stand on. Built
foundation-first as a graded **L1→L5 ladder**, one new hard technique per rung.

## Domain glossary

- **PokéAPI** — the public REST API (`pokeapi.co/api/v2/`); source of truth for Pokémon data.
- **Ingest edge** — the boundary where untrusted API JSON enters; the only place Pydantic
  validation runs.
- **Snapshot** — a local SQLite copy of the dex, built once from the live API (L4); what the agent
  reads at inference, for offline determinism.
- **Ladder (Lx)** — the staged build: L1 fetch → L2 cache → L3 async batch → L4 snapshot+CLI →
  L5 agent.
- **type / ability / stat** — the three sub-resources flattened out of the nested `/pokemon`
  response.

## Locked decisions

| # | Decision | Choice |
|---|----------|--------|
| 1 | North star | AI agent is the point; foundation serves it (ends at L5) |
| 2 | Agent reads | Local SQLite snapshot built once from the live API; not the veekun CSVs (frozen ~Gen 8) |
| 3 | HTTP stack | httpx + Hishel + respx, sync-first, async only at L3 |
| 4 | Typed models | Pydantic v2 at the ingest edge; dataclasses/TypedDict for the snapshot read path |
| 5 | Interface | Thin Typer CLI (`get` / `search` / `ask`) over a library-core |
| 6 | Format | Graded ladder L1→L5 |
| 7 | First slice | L1 tracer bullet, one rung per commit |
| 8 | L5 RAG | Tool-use agent + minimal cosine RAG (embeddings + NumPy/sqlite top-k), no vector DB |

**Hard constraint:** PokéAPI fair-use mandates local caching (IP-ban risk). L2 lands before any
bulk fetch (L3).

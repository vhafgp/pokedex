# pokedex

A study Pokédex built as a graded **L1→L5 ladder**: a typed, cached, resilient PokéAPI client that
culminates in a **Claude tool-using agent** over a local snapshot — exposed as an MCP server, so it
runs on a Claude Pro/Max subscription with **no API key**.

The agent is the point; the data foundation exists to feed it. See [CONTEXT.md](CONTEXT.md) for the
domain glossary and the locked design decisions.

## Status

- **L1 — typed fetch core** — fetch one Pokémon, validated into a Pydantic model.
- **L2 — RFC-9111 caching** — transparent Hishel disk cache; repeat lookups skip the network.
- **L3 — async batch ETL** — bounded-concurrency fetch of the full dex with tenacity retry/backoff.
- **L4 — SQLite snapshot + Typer CLI** — `build` the dex into SQLite, then `get`/`search` offline.
- **L5 — MCP server + semantic search** — fastembed + NumPy cosine RAG, exposed as Claude tools
  (`get_pokemon`, `search_by_type`, `semantic_search`) over stdio. Keyless.

## Quickstart

```bash
uv venv
uv pip install -e ".[dev]"
pytest                        # 26 tests, fully mocked, no network, no key

pokedex build                 # fetch the full dex into a local SQLite snapshot
pokedex embed                 # embed it for semantic search (downloads the model once)
pokedex get pikachu           # query the snapshot, offline
pokedex search --type water
```

## The agent (keyless)

The L5 capstone is an **MCP server** consumed by Claude Code / Claude Desktop, which supply auth
from your subscription — no `ANTHROPIC_API_KEY` required.

```bash
claude mcp add pokedex --scope user -- "$(pwd)/.venv/bin/pokedex-mcp"
```

Then, in a new Claude Code session, ask in natural language ("which poison snakes are there?",
"find a fire-breathing dragon") and Claude calls the `pokedex` tools. `src/pokedex/agent.py` models
the raw `tool_use`→`tool_result` loop directly (tested with a fake client) for reference.

# pokedex

A study Pokédex built as a graded **L1→L5 ladder**: a typed, cached, resilient PokéAPI client
that culminates in a Claude tool-using agent over a local snapshot.

The agent is the point; the data foundation exists to feed it. See [CONTEXT.md](CONTEXT.md) for the
domain glossary and the locked design decisions.

## Status

- **L1 — typed fetch core** — fetch one Pokémon, validated into a Pydantic model.
- **L2 — RFC-9111 caching** — transparent Hishel disk cache; repeat lookups skip the network.
- L3 — async batch ETL · L4 — SQLite snapshot + Typer CLI · L5 — agent.

## Quickstart

```bash
uv venv
uv pip install -e ".[dev]"
pytest          # fully mocked, no network
python -c "from pokedex.fetch import get_pokemon; print(get_pokemon('pikachu'))"
```

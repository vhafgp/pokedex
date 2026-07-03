"""Semantic search over the snapshot: fastembed vectors + NumPy cosine top-k. The embedder is
injectable so tests run offline; the default lazy-loads fastembed only when actually called."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from contextlib import closing
from pathlib import Path

import numpy as np

from pokedex import store
from pokedex.models import PokemonRecord

Embedder = Callable[[list[str]], np.ndarray]

_model = None


def _fastembed(texts: list[str]) -> np.ndarray:
    global _model
    if _model is None:
        from fastembed import TextEmbedding

        _model = TextEmbedding()
    return np.asarray(list(_model.embed(texts)), dtype=np.float32)


def _document(record: PokemonRecord) -> str:
    return (
        f"{record.name}, a {'/'.join(record.types)}-type Pokémon. "
        f"Abilities: {', '.join(record.abilities)}."
    )


def cosine_top_k(
    query: np.ndarray, matrix: np.ndarray, ids: list[int], k: int = 5
) -> list[tuple[int, float]]:
    q = query / (np.linalg.norm(query) + 1e-12)
    m = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12)
    scores = m @ q
    order = np.argsort(scores)[::-1][:k]
    return [(int(ids[i]), float(scores[i])) for i in order]


def build_embeddings(db_path: Path, embedder: Embedder | None = None) -> int:
    embed = embedder or _fastembed
    records = store.all_records(db_path)
    vectors = embed([_document(r) for r in records])
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS pokemon_embedding "
            "(pokemon_id INTEGER PRIMARY KEY, vector BLOB NOT NULL)"
        )
        conn.execute("DELETE FROM pokemon_embedding")
        conn.executemany(
            "INSERT INTO pokemon_embedding (pokemon_id, vector) VALUES (?, ?)",
            [(r.id, v.astype(np.float32).tobytes()) for r, v in zip(records, vectors, strict=True)],
        )
        conn.commit()
    return len(records)


def _load_embeddings(db_path: Path) -> tuple[list[int], np.ndarray]:
    with closing(sqlite3.connect(db_path)) as conn:
        try:
            rows = conn.execute(
                "SELECT pokemon_id, vector FROM pokemon_embedding ORDER BY pokemon_id"
            ).fetchall()
        except sqlite3.OperationalError:
            return [], np.empty((0, 0), dtype=np.float32)
    if not rows:
        return [], np.empty((0, 0), dtype=np.float32)
    ids = [pid for pid, _ in rows]
    matrix = np.stack([np.frombuffer(v, dtype=np.float32) for _, v in rows])
    return ids, matrix


def semantic_search(
    db_path: Path, query: str, k: int = 5, embedder: Embedder | None = None
) -> list[tuple[PokemonRecord, float]]:
    embed = embedder or _fastembed
    ids, matrix = _load_embeddings(db_path)
    if not ids:
        return []
    ranked = cosine_top_k(embed([query])[0], matrix, ids, k)
    return [(store.get(db_path, pid), score) for pid, score in ranked]

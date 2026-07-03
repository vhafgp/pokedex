import numpy as np

from pokedex.models import Pokemon
from pokedex.search import build_embeddings, cosine_top_k, semantic_search
from pokedex.snapshot import build_snapshot


def _p(id_: int, name: str, types: tuple[str, ...]) -> Pokemon:
    return Pokemon(
        id=id_, name=name, height=1, weight=1, types=types, abilities=("x",), stats={"hp": 1}
    )


def _keyword_embed(texts: list[str]) -> np.ndarray:
    vocab = ("water", "electric", "fire")
    return np.asarray([[float(w in t.lower()) for w in vocab] for t in texts], dtype=np.float32)


def _dex(tmp_path):
    db = tmp_path / "dex.sqlite"
    build_snapshot(
        db,
        [
            _p(7, "squirtle", ("water",)),
            _p(25, "pikachu", ("electric",)),
            _p(4, "charmander", ("fire",)),
        ],
    )
    return db


def test_cosine_top_k_ranks_by_similarity():
    matrix = np.array([[1, 0], [0, 1], [1, 1]], dtype=np.float32)
    ranked = cosine_top_k(np.array([1, 0], dtype=np.float32), matrix, [10, 20, 30], k=2)
    assert [pid for pid, _ in ranked] == [10, 30]
    assert ranked[0][1] > ranked[1][1]


def test_build_embeddings_persists_and_rebuilds(tmp_path):
    db = _dex(tmp_path)
    assert build_embeddings(db, embedder=_keyword_embed) == 3
    assert build_embeddings(db, embedder=_keyword_embed) == 3


def test_semantic_search_ranks_relevant_first(tmp_path):
    db = _dex(tmp_path)
    build_embeddings(db, embedder=_keyword_embed)
    results = semantic_search(db, "an electric type", k=1, embedder=_keyword_embed)
    assert results[0][0].name == "pikachu"


def test_semantic_search_empty_without_embeddings(tmp_path):
    db = _dex(tmp_path)
    assert semantic_search(db, "water", embedder=_keyword_embed) == []

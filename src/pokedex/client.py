"""PokéAPI HTTP client with transparent RFC-9111 caching (Hishel over httpx).

Caching is a PokéAPI fair-use requirement (uncached bulk traffic risks an IP ban), not an
optimization. Pinned to hishel<1.0 for its httpx-native CacheClient (1.x dropped it).
"""

from __future__ import annotations

from pathlib import Path

import hishel
import httpx

BASE_URL = "https://pokeapi.co/api/v2/"
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "pokedex"


def make_client(cache_dir: Path | None = None) -> httpx.Client:
    storage = hishel.FileStorage(base_path=cache_dir or DEFAULT_CACHE_DIR)
    controller = hishel.Controller(cacheable_methods=["GET"])
    return hishel.CacheClient(
        base_url=BASE_URL,
        timeout=10.0,
        storage=storage,
        controller=controller,
    )

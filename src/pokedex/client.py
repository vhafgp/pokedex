"""HTTP client for the PokéAPI. L2 will wrap this factory with a Hishel cache."""

from __future__ import annotations

import httpx

BASE_URL = "https://pokeapi.co/api/v2/"


def make_client() -> httpx.Client:
    return httpx.Client(base_url=BASE_URL, timeout=10.0)

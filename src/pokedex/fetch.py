"""Fetch PokéAPI resources and normalize them into typed models."""

from __future__ import annotations

import httpx

from pokedex.client import make_client
from pokedex.models import Pokemon


def get_pokemon(name_or_id: str | int, *, client: httpx.Client | None = None) -> Pokemon:
    owns_client = client is None
    client = client or make_client()
    try:
        response = client.get(f"pokemon/{str(name_or_id).lower()}")
        response.raise_for_status()
        return Pokemon.from_api(response.json())
    finally:
        if owns_client:
            client.close()

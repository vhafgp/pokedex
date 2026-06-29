"""Fetch PokéAPI resources and normalize them into typed models."""

from __future__ import annotations

from pokedex.client import make_client
from pokedex.models import Pokemon


def get_pokemon(name_or_id: str | int) -> Pokemon:
    with make_client() as client:
        response = client.get(f"pokemon/{str(name_or_id).lower()}")
        response.raise_for_status()
        return Pokemon.from_api(response.json())

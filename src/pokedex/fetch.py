"""Fetch PokéAPI resources and normalize them into typed models."""

from __future__ import annotations

import asyncio

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

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


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code >= 500


@retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.2, max=2),
    reraise=True,
)
async def _fetch_one(client: httpx.AsyncClient, name: str) -> Pokemon:
    response = await client.get(f"pokemon/{name}")
    response.raise_for_status()
    return Pokemon.from_api(response.json())


async def list_pokemon_names(client: httpx.AsyncClient, *, limit: int = 100_000) -> list[str]:
    response = await client.get(f"pokemon?limit={limit}")
    response.raise_for_status()
    return [entry["name"] for entry in response.json()["results"]]


async def fetch_all(
    names: list[str], *, client: httpx.AsyncClient, concurrency: int = 10
) -> list[Pokemon]:
    semaphore = asyncio.Semaphore(concurrency)

    async def _bounded(name: str) -> Pokemon:
        async with semaphore:
            return await _fetch_one(client, name)

    return await asyncio.gather(*(_bounded(name) for name in names))

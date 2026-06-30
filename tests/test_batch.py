import asyncio
from email.utils import formatdate

import httpx
import respx

from pokedex.client import make_async_client
from pokedex.fetch import fetch_all

NAMES = [f"poke{i}" for i in range(20)]


async def test_concurrency_is_bounded(pikachu_payload):
    in_flight = 0
    peak = 0

    async def handler(request):
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)
        in_flight -= 1
        return httpx.Response(200, json=pikachu_payload)

    with respx.mock() as mock:
        mock.route(method="GET", url__regex=r"https://pokeapi\.co/api/v2/pokemon/poke\d+").mock(
            side_effect=handler
        )
        async with httpx.AsyncClient(base_url="https://pokeapi.co/api/v2/") as client:
            results = await fetch_all(NAMES, client=client, concurrency=5)

    assert len(results) == len(NAMES)
    assert 1 < peak <= 5


async def test_5xx_retried_then_succeeds(tmp_path, pikachu_payload):
    with respx.mock(base_url="https://pokeapi.co/api/v2") as mock:
        route = mock.get("/pokemon/pikachu").mock(
            side_effect=[httpx.Response(500), httpx.Response(200, json=pikachu_payload)]
        )
        client = make_async_client(cache_dir=tmp_path)
        results = await fetch_all(["pikachu"], client=client, concurrency=1)
        await client.aclose()

    assert route.call_count == 2
    assert results[0].name == "pikachu"


async def test_rerun_served_from_cache(tmp_path, pikachu_payload):
    headers = {"Cache-Control": "public, max-age=86400", "Date": formatdate(usegmt=True)}
    with respx.mock(base_url="https://pokeapi.co/api/v2") as mock:
        route = mock.get("/pokemon/pikachu").mock(
            return_value=httpx.Response(200, json=pikachu_payload, headers=headers)
        )
        client = make_async_client(cache_dir=tmp_path)
        await fetch_all(["pikachu"], client=client, concurrency=1)
        await fetch_all(["pikachu"], client=client, concurrency=1)
        await client.aclose()

    assert route.call_count == 1

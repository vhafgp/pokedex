from email.utils import formatdate

import httpx
import respx

from pokedex.client import make_client
from pokedex.fetch import get_pokemon


def _cacheable_response(payload: dict) -> httpx.Response:
    return httpx.Response(
        200,
        json=payload,
        headers={"Cache-Control": "public, max-age=86400", "Date": formatdate(usegmt=True)},
    )


def test_repeat_lookup_served_from_cache(pikachu_payload, tmp_path):
    with respx.mock(base_url="https://pokeapi.co/api/v2") as mock:
        route = mock.get("/pokemon/pikachu").mock(return_value=_cacheable_response(pikachu_payload))
        client = make_client(cache_dir=tmp_path)
        get_pokemon("pikachu", client=client)
        get_pokemon("pikachu", client=client)
        client.close()

    assert route.call_count == 1


def test_cache_survives_new_client(pikachu_payload, tmp_path):
    with respx.mock(base_url="https://pokeapi.co/api/v2") as mock:
        route = mock.get("/pokemon/pikachu").mock(return_value=_cacheable_response(pikachu_payload))
        warm = make_client(cache_dir=tmp_path)
        get_pokemon("pikachu", client=warm)
        warm.close()

        restarted = make_client(cache_dir=tmp_path)  # new instance, same on-disk store
        get_pokemon("pikachu", client=restarted)
        restarted.close()

    assert route.call_count == 1

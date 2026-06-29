import httpx
import respx

from pokedex.fetch import get_pokemon


def test_get_pokemon_parses_api_response(pikachu_payload):
    with respx.mock(base_url="https://pokeapi.co/api/v2") as mock:
        route = mock.get("/pokemon/pikachu").mock(
            return_value=httpx.Response(200, json=pikachu_payload)
        )
        pokemon = get_pokemon("pikachu")

    assert route.called
    assert pokemon.id == 25
    assert pokemon.name == "pikachu"
    assert pokemon.types == ("electric",)
    assert "static" in pokemon.abilities
    assert "lightning-rod" in pokemon.abilities
    assert pokemon.stats["hp"] == 35
    assert pokemon.stats["speed"] == 90


def test_get_pokemon_lowercases_lookup(pikachu_payload):
    with respx.mock(base_url="https://pokeapi.co/api/v2") as mock:
        route = mock.get("/pokemon/pikachu").mock(
            return_value=httpx.Response(200, json=pikachu_payload)
        )
        get_pokemon("Pikachu")

    assert route.called

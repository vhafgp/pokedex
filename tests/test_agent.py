from dataclasses import dataclass, field

from pokedex.agent import run


@dataclass
class FakeResponse:
    stop_reason: str
    content: list[dict] = field(default_factory=list)


class ScriptedClient:
    """Turn 1 asks to call get_pokemon; turn 2 answers, citing the tool_result fed back in."""

    def __init__(self) -> None:
        self.calls = 0

    def create(self, messages: list[dict]) -> FakeResponse:
        self.calls += 1
        if self.calls == 1:
            return FakeResponse(
                "tool_use",
                [{"type": "tool_use", "id": "t1", "name": "get_pokemon",
                  "input": {"name_or_id": "pikachu"}}],
            )
        fed_back = messages[-1]["content"][0]["content"]
        return FakeResponse("end_turn", [{"type": "text", "text": f"Answer: {fed_back}"}])


def test_agent_runs_tool_then_answers():
    client = ScriptedClient()
    tools = {"get_pokemon": lambda args: f"{args['name_or_id']} is electric"}
    assert run(client, tools, "what type is pikachu?") == "Answer: pikachu is electric"
    assert client.calls == 2


def test_agent_no_tool_use_returns_text():
    class Immediate:
        def create(self, messages):
            return FakeResponse("end_turn", [{"type": "text", "text": "hello"}])

    assert run(Immediate(), {}, "hi") == "hello"

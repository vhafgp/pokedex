"""Raw tool-use agent loop, modelled without an SDK so it runs offline and is tested with a fake
client. Mirrors the contract: stop_reason 'tool_use' -> run tools -> tool_result -> repeat."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol


class Response(Protocol):
    stop_reason: str
    content: list[dict]


class Client(Protocol):
    def create(self, messages: list[dict]) -> Response: ...


ToolFn = Callable[[dict], Any]


def run(client: Client, tools: dict[str, ToolFn], question: str, max_turns: int = 10) -> str:
    messages: list[dict] = [{"role": "user", "content": question}]
    for _ in range(max_turns):
        response = client.create(messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return _text(response.content)
        results = []
        for block in response.content:
            if block.get("type") != "tool_use":
                continue
            output = tools[block["name"]](block.get("input", {}))
            results.append(
                {"type": "tool_result", "tool_use_id": block["id"], "content": str(output)}
            )
        messages.append({"role": "user", "content": results})
    raise RuntimeError("tool-use loop did not terminate")


def _text(content: list[dict]) -> str:
    return "".join(b.get("text", "") for b in content if b.get("type") == "text")

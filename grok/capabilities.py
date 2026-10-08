"""What each xAI model is known to accept.

Unknown models keep the grok-4.7 attempt profile. A 400 from the Responses
API still drops the rejected parameter or tool and retries once.
"""

from __future__ import annotations

from dataclasses import dataclass

from grok.models import REASONING_EFFORTS

SERVER_TOOLS = frozenset(
    {"web_search", "x_search", "code_interpreter", "image_generation"}
)


@dataclass(frozen=True)
class ModelCapabilities:
    efforts: frozenset[str]
    server_tools: frozenset[str]
    vision: bool
    structured_outputs: bool
    reasoning: bool


def _flagship() -> ModelCapabilities:
    return ModelCapabilities(
        efforts=frozenset(REASONING_EFFORTS),
        server_tools=SERVER_TOOLS,
        vision=True,
        structured_outputs=True,
        reasoning=True,
    )


# grok-build-0.1 documents function calling, structured outputs, and reasoning.
# Server tools and vision are not on its model page, so they are omitted
# until a 400-fallback would be the only signal.
def _code_model() -> ModelCapabilities:
    return ModelCapabilities(
        efforts=frozenset(REASONING_EFFORTS),
        server_tools=frozenset(),
        vision=False,
        structured_outputs=True,
        reasoning=True,
    )


_MODELS = {
    "grok-4.7": _flagship(),
    "grok-4.6": _flagship(),
    "grok-build-0.1": _code_model(),
}

_ALIASES = {
    "grok-code-fast-1": "grok-build-0.1",
    "grok-code-fast": "grok-build-0.1",
    "grok-code-fast-1-0825": "grok-build-0.1",
}


def capabilities_for(model: str) -> ModelCapabilities:
    canonical = _ALIASES.get(model, model)
    return _MODELS.get(canonical, _flagship())

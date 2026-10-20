"""Versioned interfaces for pluggable research environments and agents."""
from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence
import random

PROTOCOL_VERSION = "1.1"


class Environment(Protocol):
    environment_id: str
    version: str
    configuration: Mapping[str, Any]

    def reset(self, seed: int) -> Any: ...
    def legal_actions(self, state: Any) -> Sequence[Any]: ...
    def current_player(self, state: Any) -> int: ...
    def step(self, state: Any, action: Any) -> Any: ...
    def is_terminal(self, state: Any) -> bool: ...
    def result(self, state: Any) -> Mapping[str, Any]: ...
    def serialize(self, state: Any) -> Any: ...


class Agent(Protocol):
    agent_id: str
    version: str
    configuration: Mapping[str, Any]

    def select_action(
        self,
        observation: Any,
        legal_actions: Sequence[Any],
        rng: random.Random,
    ) -> Any: ...

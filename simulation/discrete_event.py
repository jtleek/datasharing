"""Simplified discrete event simulation skeleton."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(order=True)
class Event:
    time: float
    description: str


@dataclass
class DiscreteEventSimulator:
    events: List[Event] = field(default_factory=list)

    def schedule(self, event: Event) -> None:
        self.events.append(event)
        self.events.sort()

    def run(self) -> List[Event]:
        executed: List[Event] = []
        while self.events:
            executed.append(self.events.pop(0))
        return executed

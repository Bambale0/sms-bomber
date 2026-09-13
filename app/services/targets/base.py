from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import aiohttp


@dataclass(frozen=True, slots=True)
class TargetResult:
    name: str
    ok: bool
    status_code: int | None = None
    error: str | None = None


class Target(Protocol):
    name: str

    async def send(self, session: aiohttp.ClientSession, identifier: str) -> TargetResult:
        """Send one authorized test request and return a normalized result."""
        ...

from __future__ import annotations

from urllib.parse import urlparse

import aiohttp

from app.services.targets.base import TargetResult


class SandboxTarget:
    """HTTP target restricted to an explicitly allowlisted host."""

    name = "sandbox"

    def __init__(self, url: str, allowed_hosts: frozenset[str]) -> None:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Target URL must use http or https")
        if not host or host not in allowed_hosts:
            raise ValueError(f"Target host is not allowlisted: {host or '<missing>'}")

        self._url = url

    async def send(self, session: aiohttp.ClientSession, identifier: str) -> TargetResult:
        try:
            async with session.post(
                self._url,
                json={"test_identifier": identifier, "authorized_test": True},
            ) as response:
                ok = 200 <= response.status < 300
                return TargetResult(name=self.name, ok=ok, status_code=response.status)
        except (aiohttp.ClientError, TimeoutError) as exc:
            return TargetResult(name=self.name, ok=False, error=type(exc).__name__)

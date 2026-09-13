from __future__ import annotations

import aiohttp


class HttpClient:
    """Owns the application's single long-lived aiohttp session."""

    def __init__(self, timeout_seconds: float) -> None:
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
            self._session = aiohttp.ClientSession(timeout=self._timeout, connector=connector)

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError("HTTP client has not been started")
        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

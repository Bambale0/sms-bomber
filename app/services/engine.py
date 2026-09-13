from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from uuid import uuid4

import aiohttp

from app.services.targets.base import Target, TargetResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class BatchResult:
    request_id: str
    results: tuple[TargetResult, ...]

    @property
    def success_count(self) -> int:
        return sum(result.ok for result in self.results)

    @property
    def failure_count(self) -> int:
        return len(self.results) - self.success_count


class RequestEngine:
    """Runs authorized target calls concurrently while bounding resource usage."""

    def __init__(
        self,
        *,
        session: aiohttp.ClientSession,
        targets: tuple[Target, ...],
        max_concurrency: int,
        max_retries: int,
        retry_base_delay_seconds: float,
    ) -> None:
        self._session = session
        self._targets = targets
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._max_retries = max_retries
        self._retry_base_delay_seconds = retry_base_delay_seconds

    async def run(self, identifier: str) -> BatchResult:
        request_id = uuid4().hex
        logger.info("request_started request_id=%s target_count=%d", request_id, len(self._targets))

        results = await asyncio.gather(
            *(self._run_target(target, identifier, request_id) for target in self._targets),
            return_exceptions=False,
        )
        batch = BatchResult(request_id=request_id, results=tuple(results))

        logger.info(
            "request_finished request_id=%s success=%d failure=%d",
            request_id,
            batch.success_count,
            batch.failure_count,
        )
        return batch

    async def _run_target(
        self,
        target: Target,
        identifier: str,
        request_id: str,
    ) -> TargetResult:
        async with self._semaphore:
            last_result: TargetResult | None = None

            for attempt in range(self._max_retries + 1):
                try:
                    result = await target.send(self._session, identifier)
                except Exception:
                    logger.exception(
                        "target_unhandled_error request_id=%s target=%s attempt=%d",
                        request_id,
                        target.name,
                        attempt + 1,
                    )
                    return TargetResult(
                        name=target.name,
                        ok=False,
                        error="UnhandledTargetError",
                    )

                last_result = result
                if result.ok or not self._is_transient(result):
                    return result

                if attempt < self._max_retries:
                    delay = self._retry_base_delay_seconds * (2**attempt)
                    logger.warning(
                        "target_retry request_id=%s target=%s attempt=%d delay=%.2f status=%s",
                        request_id,
                        target.name,
                        attempt + 1,
                        delay,
                        result.status_code,
                    )
                    await asyncio.sleep(delay)

            assert last_result is not None
            return last_result

    @staticmethod
    def _is_transient(result: TargetResult) -> bool:
        if result.status_code is None:
            return result.error is not None
        return result.status_code == 429 or result.status_code >= 500

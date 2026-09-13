from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.services.engine import RequestEngine
from app.services.targets.base import TargetResult


@dataclass
class FakeTarget:
    name: str
    results: list[TargetResult]

    async def send(self, session, identifier: str) -> TargetResult:  # noqa: ANN001
        assert identifier == "79991112233"
        return self.results.pop(0)


@pytest.mark.asyncio
async def test_engine_counts_success_and_failure() -> None:
    engine = RequestEngine(
        session=object(),  # type: ignore[arg-type]
        targets=(
            FakeTarget("ok", [TargetResult("ok", True, 200)]),
            FakeTarget("bad", [TargetResult("bad", False, 400)]),
        ),
        max_concurrency=2,
        max_retries=0,
        retry_base_delay_seconds=0,
    )

    result = await engine.run("79991112233")

    assert result.success_count == 1
    assert result.failure_count == 1
    assert len(result.request_id) == 32


@pytest.mark.asyncio
async def test_engine_retries_transient_status() -> None:
    target = FakeTarget(
        "retry",
        [
            TargetResult("retry", False, 503),
            TargetResult("retry", True, 204),
        ],
    )
    engine = RequestEngine(
        session=object(),  # type: ignore[arg-type]
        targets=(target,),
        max_concurrency=1,
        max_retries=1,
        retry_base_delay_seconds=0,
    )

    result = await engine.run("79991112233")

    assert result.success_count == 1
    assert result.results[0].status_code == 204

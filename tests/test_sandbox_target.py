import pytest

from app.services.targets.sandbox import SandboxTarget


def test_target_rejects_non_allowlisted_host() -> None:
    with pytest.raises(ValueError, match="not allowlisted"):
        SandboxTarget("https://example.com/send", frozenset({"localhost"}))


def test_target_accepts_allowlisted_host() -> None:
    target = SandboxTarget("http://localhost:8080/test", frozenset({"localhost"}))
    assert target.name == "sandbox"

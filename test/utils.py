import pytest
from typing import Any

def approx_val(expected: float, *, rel: float = 1e-6) -> Any:
    """Return pytest.approx wrapped as Any so static type checkers don't complain."""
    return pytest.approx(expected, rel=rel)

def assert_approx(actual: float, expected: float, *, rel: float = 1e-6, msg: str | None = None) -> None:
    """Convenience assertion that uses approx_val internally."""
    assert actual == approx_val(expected, rel=rel), msg or f"got
import pytest
from typing import Any, Union

Number = Union[int, float]


def approx_val(expected: Number, *, rel: float = 1e-6, abs: float | None = None) -> Any:
    """Return pytest.approx wrapped as Any so static type checkers don't complain.

    Accepts ints or floats and an optional relative or absolute tolerance.
    """
    if abs is not None:
        return pytest.approx(expected, abs=abs)
    return pytest.approx(expected, rel=rel)


def assert_approx(actual: Number, expected: Number, *, rel: float = 1e-6, abs: float | None = None) -> None:
    """Assert that `actual` approximately equals `expected` within tolerance.

    This keeps the assertion at the top-level in tests simple and avoids
    needing complex message handling in the helper.
    """
    approx = approx_val(expected, rel=rel, abs=abs)
    assert actual == approx
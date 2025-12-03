
import pytest

from frist._util import verify_start_end  # type: Callable[[Any], Callable[..., Any]]

def test_verify_start_end_raises_valueerror():
    """
    Test that verify_start_end raises ValueError when start >= end.
    """
    @verify_start_end
    def dummy(self, start: int = 0, end: int | None = None) -> None:
        return None

    class Dummy:
        pass

    d = Dummy()
    with pytest.raises(ValueError, match="must not be greater than end"):
        dummy(d, 2, 1)
    with pytest.raises(ValueError, match="must not be greater than end"):
        dummy(d, 0, 0)
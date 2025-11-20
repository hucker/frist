import functools
from typing import Any, Callable


def verify_start_end(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for calendar window methods to validate input ranges.

    Ensures that the 'start' argument is less than or equal to 'end'.
    If 'end' is None, it is set to 'start' (single-value window).
    If 'start' > 'end', raises ValueError with the function name and values.

    Usage:
        @verify_start_end
        def in_days(self, start=0, end=None):
            ...

    Exception message format:
        '<function>: start (<start>) must not be greater than end (<end>)'
    """
    @functools.wraps(func)
    def wrapper(self: Any, start: int = 0, end: int | None = None, *args: Any, **kwargs: Any) -> bool:
        if end is None:
            end = start
        if start > end:
            func_name = getattr(func, "__name__", repr(func))
            raise ValueError(f"{func_name}: start ({start}) must not be greater than end ({end})")
        return func(self, start, end, *args, **kwargs)
    return wrapper
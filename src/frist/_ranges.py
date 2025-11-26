from __future__ import annotations
from typing import Callable, Optional

__all__ = ["UnitNamespace"]


class UnitNamespace:
    """Compact unit namespace that delegates to a Cal `in_*` method.

    Usage examples (compact):
      cal.mon.in_(-2, 0)     # half-open (default)
      cal.mon(-2, 0)         # maps to in_
      cal.mon.thru(-2, 0)    # inclusive end
            # slice syntax is not supported
    """

    def __init__(self, cal: object, fn: Callable[[int, Optional[int]], bool]) -> None:
        self._cal = cal
        self._fn = fn

    def in_(self, start: int = 0, end: Optional[int] = None) -> bool:
        """Half-open membership: start <= target < end.

        Single-arg (end omitted) -> single-unit window [start, start+1).
        """
        if end is None:
            end = start + 1
        return self._fn(start, end)

    between = in_

    def __call__(self, start: int = 0, end: Optional[int] = None) -> bool:
        return self.in_(start, end)


    def _thru_impl(self, start: int = 0, end: Optional[int] = None) -> bool:
        # single-arg -> same single unit; convert inclusive -> half-open by +1
        if end is None:
            end = start
        return self.in_(start, end + 1)

    @property
    def thru(self):
        """Return a callable object supporting call syntax for inclusive "through" semantics.

        Example: `cal.mon.thru(-2, 0)`.
        """

        parent = self

        class _Thru:
            def __call__(self, s: int = 0, e: Optional[int] = None) -> bool:
                return parent._thru_impl(s, e)

        return _Thru()

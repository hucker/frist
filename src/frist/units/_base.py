from __future__ import annotations

import datetime as dt
from typing import Generic, Protocol, TypeVar


class CalProtocol(Protocol):
    @property
    def ref_dt(self) -> dt.datetime: ...

    @property
    def target_dt(self) -> dt.datetime: ...


class BizProtocol(CalProtocol, Protocol):
    def in_business_days(self, start: int, end: int) -> bool: ...
    def in_working_days(self, start: int, end: int) -> bool: ...
    def in_fiscal_quarters(self, start: int, end: int) -> bool: ...
    def in_fiscal_years(self, start: int, end: int) -> bool: ...

    @property
    def fiscal_year(self) -> int: ...

    @property
    def fiscal_quarter(self) -> int: ...


TCal = TypeVar("TCal", bound=CalProtocol)


class UnitNamespace(Generic[TCal]):
    """Base namespace for time unit operations with half-open semantics."""

    def __init__(self, cal: TCal) -> None:
        self._cal = cal

    def in_(self, start: int = 0, end: int | None = None) -> bool:
        if end is None:
            end = start + 1
        if start >= end:
            raise ValueError(f"{self.__class__.__name__}.in_: {start=} must not be > than {end=}")
        return self._in_impl(start, end)

    def _in_impl(self, start: int, end: int) -> bool:
        raise NotImplementedError("implement _in_impl in subclass")

    def between(self, start: int = 0, end: int | None = None, inclusive: str = "both") -> bool:
        if end is None:
            return self.in_(start, start + 1)

        start_offsets = {"both": 0, "left": 0, "right": 1, "neither": 1}
        end_offsets = {"both": 1, "left": 0, "right": 1, "neither": 0}

        if inclusive not in start_offsets:
            raise ValueError(f"Invalid inclusive value: {inclusive!r}")

        adj_start = start + start_offsets[inclusive]
        adj_end = end + end_offsets[inclusive]
        return self.in_(adj_start, adj_end)

    def _thru_impl(self, start: int = 0, end: int | None = None) -> bool:
        if end is None:
            end = start
        return self.in_(start, end + 1)

    @property
    def thru(self):
        parent = self

        class _Thru:
            def __call__(self, s: int = 0, e: int | None = None) -> bool:
                return parent._thru_impl(s, e)

        return _Thru()

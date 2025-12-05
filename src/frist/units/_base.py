"""
Base types and protocols for units.

Defines `UnitName` and protocol aliases used by calendar (`Cal`) and
business (`Biz`) adapters. `UnitName` provide ergonomic helpers (.in_()) that
delegate to the canonical methods on their parent objects without owning core
logic.
"""
from __future__ import annotations

import datetime as dt
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Generic, Literal, Protocol, TypeVar


class CalProtocol(Protocol):
    """Protocol for calendar-like parents.

    Exposes only the reference and target datetimes required by unit adapters.
    Implementations should ensure timezone consistency elsewhere (see `time_pair`).
    """

    @property
    def ref_dt(self) -> dt.datetime:
        """Reference datetime used as the zero point for unit offsets."""
        ...

    @property
    def target_dt(self) -> dt.datetime:
        """Target datetime to evaluate against unit windows relative to `ref_dt`."""
        ...


class BizProtocol(CalProtocol, Protocol):
    """Protocol for business-calendar parents.

    Extends `CalProtocol` with business-aware membership checks and fiscal context.
    Methods use unit-offset semantics compatible with `UnitName` helpers.
    """

    def in_business_days(self, start: int, end: int) -> bool:
        """Return True if `target_dt` falls within `[start, end)` business days."""
        ...

    def in_working_days(self, start: int, end: int) -> bool:
        """Return True if `target_dt` falls within `[start, end)` working days."""
        ...

    def in_fiscal_quarters(self, start: int, end: int) -> bool:
        """Return True if `target_dt` falls within `[start, end)` fiscal quarters."""
        ...

    def in_fiscal_years(self, start: int, end: int) -> bool:
        """Return True if `target_dt` falls within `[start, end)` fiscal years."""
        ...

    @property
    def fiscal_year(self) -> int:
        """Current fiscal year derived from `target_dt` under the configured policy."""
        ...

    @property
    def fiscal_quarter(self) -> int:
        """Current fiscal quarter (1–4) derived from `target_dt` under policy."""
        ...


# Generic parent type for unit names.
# Bound to `CalProtocol` so `UnitName[TCal]` is type-safe:
# - Calendar unit names accept `Cal`-like parents (must expose `ref_dt`/`target_dt`).
# - Business unit names can use richer `Biz` parents while staying compatible.
# This improves IDE hints and catches misuse (e.g., calling biz-only methods on Cal).
TCal = TypeVar("TCal", bound=CalProtocol)

# Constrained literal type for boundary inclusivity in `between()`
Inclusive = Literal["both", "left", "right", "neither"]


class UnitName(Generic[TCal], ABC):
    """Base unit name for time unit operations with half-open semantics.

    This adapter is intentionally minimal: functionality relies only on the
    parent object's `target_dt` and `ref_dt` (as required by `CalProtocol`).
    Concrete units implement `_in_impl(start, end)` using those two
    datetimes; no other parent state is required.
    """

    def __init__(self, cal: TCal) -> None:
        self._cal = cal

    def in_(self, start: int = 0, end: int | None = None) -> bool:
        """Half-open window membership for this unit.

        Semantics:
        - Offsets are in this unit (e.g., hours for Hours).
        - `end=None` represents a single-unit window `[start, start+1)`.
        - Uses half-open intervals: `[start, end)`.
        - Validates `start < end` after normalization.
        """
        if end is None:
            end = start + 1
        if start >= end:
            raise ValueError(f"{self.__class__.__name__}.in_: {start=} must not be > than {end=}")
        return self._in_impl(start, end)

    @abstractmethod
    def _in_impl(self, start: int, end: int) -> bool:
        """Subclass must implement concrete range check for the unit."""

    def between(
        self,
        start: int = 0,
        end: int | None = None,
        inclusive: Inclusive = "both",
    ) -> bool:
        """Window membership with configurable boundary inclusivity.

        Args:
        - `start`, `end`: unit offsets relative to the reference.
        - `inclusive`: Literal of {"both", "left", "right", "neither"} describing
          which boundaries to include before conversion to half-open form.

                Details:
                - `inclusive` is applied by adjusting offsets, then delegating to `in_`, which
                    uses half-open semantics `[adj_start, adj_end)`.
                - When `end is None`, it returns a single-unit window shifted by inclusivity:
                    `adj_start = start + start_offsets[inclusive]` and `adj_end = adj_start + 1`.
        """
        if end is None:
            adj_start = start + {"both": 0, "left": 0, "right": 1, "neither": 1}[inclusive]
            return self.in_(adj_start, adj_start + 1)

        start_offsets: Mapping[Inclusive, int] = {"both": 0, "left": 0, "right": 1, "neither": 1}
        end_offsets: Mapping[Inclusive, int] = {"both": 1, "left": 0, "right": 1, "neither": 0}

        if inclusive not in start_offsets:
            raise ValueError(f"Invalid inclusive value: {inclusive!r}")

        adj_start = start + start_offsets[inclusive]
        adj_end = end + end_offsets[inclusive]
        return self.in_(adj_start, adj_end)

    def thru(self, start: int = 0, end: int | None = None) -> bool:
        """Inclusive end semantics (thru) for this unit.

        Meaning:
        - Treats `end` as inclusive by delegating to `in_` with `end+1`.
        - When `end is None`, interprets as a single-unit window `[start, start+1)`.
        - Result uses half-open comparison under the hood for consistency.
        """
        if end is None:
            end = start
        return self.in_(start, end + 1)

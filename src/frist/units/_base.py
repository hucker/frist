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
from enum import Enum
from typing import Generic, Protocol, TypeVar


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


## Note: Business-specific logic is implemented within business unit classes,
## which accept a `CalProtocol` parent and a `BizPolicy`. A separate BizProtocol
## is not required.


# Generic parent type for unit names.
# Bound to `CalProtocol` so `UnitName[TCal]` is type-safe:
# - Calendar unit names accept `Cal`-like parents (must expose `ref_dt`/`target_dt`).
# - Business unit names can use richer `Biz` parents while staying compatible.
# This improves IDE hints and catches misuse (e.g., calling biz-only methods on Cal).
TCal = TypeVar("TCal", bound=CalProtocol)


# Runtime enum for boundary inclusivity in `between()`.
class Inclusive(str, Enum):
    """Literal-like enum for window boundary inclusivity.

    Values: "both", "left", "right", "neither".
    """

    BOTH = "both"
    LEFT = "left"
    RIGHT = "right"
    NEITHER = "neither"


# Runtime tuple of allowed values (useful for error messages/validation)
INCLUSIVE_VALUES: tuple[str, ...] = tuple(m.value for m in Inclusive)


def coerce_inclusive(value: Inclusive | str) -> Inclusive:
    """Coerce a string or Inclusive into an `Inclusive` enum.

    Raises ValueError for invalid inputs.
    """
    if isinstance(value, Inclusive):
        return value
    try:
        return Inclusive(value)
    except ValueError as exc:
        raise ValueError(f"Invalid inclusive value: {value!r}. Valid: {INCLUSIVE_VALUES}") from exc


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
        inclusive: Inclusive | str = Inclusive.BOTH,
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
        inc = coerce_inclusive(inclusive)

        start_offsets: dict[Inclusive, int] = {
            Inclusive.BOTH: 0,
            Inclusive.LEFT: 0,
            Inclusive.RIGHT: 1,
            Inclusive.NEITHER: 1,
        }
        end_offsets: dict[Inclusive, int] = {
            Inclusive.BOTH: 1,
            Inclusive.LEFT: 0,
            Inclusive.RIGHT: 1,
            Inclusive.NEITHER: 0,
        }

        if end is None:
            adj_start = start + start_offsets[inc]
            return self.in_(adj_start, adj_start + 1)

        adj_start = start + start_offsets[inc]
        adj_end = end + end_offsets[inc]
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

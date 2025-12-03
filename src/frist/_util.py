"""
Utility functions and decorators for calendar and business date logic.

This module provides:
  - Decorators for normalizing and validating calendar window arguments
  - Half-open interval membership checks for ints, datetimes, and dates
  - Helpers to enforce consistent interval semantics across the codebase

All functions follow PEP 8 and Google-style docstrings.
"""

import datetime as dt
import functools
from collections.abc import Callable
from typing import Any

from ._constants import WEEKDAY_INDEX


def normalize_weekday(day_spec: str) -> int:
    """Normalize various day-of-week specifications to Python weekday numbers.

    Args:
        day_spec: Day specification as a string

    Returns:
        int: Python weekday number (0=Monday, 1=Tuesday, ..., 6=Sunday)

    Accepts:
        - Full names: 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
          'saturday', 'sunday'
        - 3-letter abbrev: 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
        - 2-letter abbrev: 'mo', 'tu', 'we', 'th', 'fr', 'sa', 'su'
        - Pandas style: 'w-mon', 'w-tue', etc.
        - All case insensitive

    Examples:
        normalize_weekday('monday') -> 0
        normalize_weekday('MON') -> 0
        normalize_weekday('w-sun') -> 6
        normalize_weekday('thu') -> 3
    """
    day_spec = str(day_spec).lower().strip()

    # Remove pandas-style prefix
    if day_spec.startswith("w-"):
        day_spec = day_spec[2:]

    if day_spec in WEEKDAY_INDEX:
        return WEEKDAY_INDEX[day_spec]

    # Generate helpful error message
    valid_examples = [
        "Full: 'monday', 'sunday'",
        "3-letter: 'mon', 'sun', 'tue', 'wed', 'thu', 'fri', 'sat'",
        "2-letter: 'mo', 'su', 'tu', 'we', 'th', 'fr', 'sa'",
        "Pandas: 'w-mon', 'w-sun'",
    ]
    raise ValueError(
        f"Invalid day specification: '{day_spec}'. Valid formats:\n"
        + "\n".join(f"  • {ex}" for ex in valid_examples)
    )


def verify_start_end(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for calendar window methods to validate and normalize start/end.

    Behavior:
      - If `end` is None it is normalized to `start + 1` so a single-arg call
        like `in_days(n)` represents the half-open interval [n, n+1).
      - The decorator enforces that start < end (strict). If start >= end an
        error is raised because the half-open interval would be empty.
    """

    @functools.wraps(func)
    def wrapper(
        self: Any, start: int = 0, end: int | None = None, *args: Any, **kwargs: Any
    ) -> Any:
        # Normalize end: single-arg convenience -> one-unit half-open interval
        end_fixed: int = start + 1 if end is None else end

        # Enforce non-empty half-open interval: start must be strictly less than end
        if start >= end_fixed:
            func_name = getattr(func, "__name__", repr(func))
            # Match existing test expectations which look for the phrase
            # 'must not be greater than end'. Keep the function name prefix
            # for clarity.
            raise ValueError(
                f"{func_name}: start ({start}) must not be > than end ({end_fixed})"
            )

        # Call wrapped function with normalized end
        return func(self, start, end_fixed, *args, **kwargs)

    return wrapper


def in_half_open(start: int, value: int, end: int) -> bool:
    """
    Return True when value is in the half-open interval [start, end).

    The use of ANY here might be painful to look at but in the codebase open ended
    intervals are used for integers, tuples, and datetimes.
    """
    return start <= value < end


def in_half_open_dt(start: dt.datetime, value: dt.datetime, end: dt.datetime) -> bool:
    """
    Return True when value is in the half-open interval [start, end).

    Note: this seems like possible overkill, but I made the mistake of making the end
          comparison <= instead of < in a few cases, so this utility function should
          help avoid that mistake and it makes half_open semantics explicit.
    """
    return start <= value < end


def in_half_open_date(start: dt.date, value: dt.date, end: dt.date) -> bool:
    """
    Return True when value is in the half-open interval [start, end).

    Note: this seems like possible overkill, but I made the mistake of making the end
          comparison <= instead of < in a few cases, so this utility function should
          help avoid that mistake and it makes half_open semantics explicit.
    """
    return start <= value < end

"""
Shared types and conversion utilities for frist package.

Contains type aliases and functions used across multiple modules to avoid circular imports.
"""

import datetime as dt
from typing import TypeAlias

from ._constants import CHRONO_DATETIME_FORMATS

# Alias for inputs accepted by Frist time utilities (datetime, date, POSIX ts, or string)
# Note: explicit optionality (`| None`) should be expressed at the call site.
TimeLike: TypeAlias = dt.datetime | dt.date | float | int | str


def to_datetime(val: TimeLike, formats: list[str] | None = None) -> dt.datetime:
    """
    Convert a TimeLike value to a datetime object.

    Args:
        val: Value to convert (datetime, date, float, int, or str)
        formats: Optional list of datetime formats to use for string parsing.
                If None, uses default CHRONO_DATETIME_FORMATS.

    Returns:
        datetime: Converted datetime object

    Raises:
        TypeError: If value is not a supported type or unrecognized string format
    """
    # In order of expected frequency of use
    if isinstance(val, dt.datetime):
        if val.tzinfo is not None:
            raise TypeError("Timezones are not supported")
        return val
    elif isinstance(val, dt.date):
        return dt.datetime.combine(val, dt.time(0, 0, 0))
    elif isinstance(val, (float, int)):
        return dt.datetime.fromtimestamp(val)
    elif isinstance(val, str):  # type: ignore # Run time type checker
        format_list = formats or CHRONO_DATETIME_FORMATS
        for format in format_list:
            try:
                return dt.datetime.strptime(val, format)
            except ValueError:
                continue
        raise TypeError(f"Unrecognized datetime string format: {val}")
    else:
        raise TypeError("Value must be datetime, date, float, int, or str")


def time_pair(
    *,
    start_time: TimeLike | None = None,
    end_time: TimeLike | None = None,
    formats__: list[str] | None = None,
) -> tuple[dt.datetime, dt.datetime]:
    """
    Normalize and validate a pair of time values.

    Accepts start_time and end_time as keyword arguments, which may be datetime objects,
    POSIX timestamps (float or int), strings in allowed formats, or None.
    Converts timestamps and strings to datetime objects.
    If end_time is None, defaults to the current time. If start_time is None, raises TypeError.
    The allowed string formats are defined in _constants.py and can be overridden.

    Args:
        start_time (datetime | float | int | str | None): The start time. Must not be None.
        end_time (datetime | float | int | str | None): The end time. If None, defaults to now.
        formats__ (list[str], optional): List of datetime formats to use for string parsing.

    Returns:
        tuple[datetime, datetime]: Normalized (start_time, end_time) as datetime objects.

    Raises:
        TypeError: If start_time is None or either value is not a supported type.

    Example:
        time_pair(start_time=dt.datetime(2020, 1, 1))
        time_pair(end_time=dt.datetime(2024, 1, 1))
        time_pair(start_time=1700000000.0)  # POSIX timestamp
        time_pair(start_time="2023-12-25 14:30:00")  # String format
        time_pair(start_time="2023-12-25")  # String format
    """
    formats: list[str] = formats__ or CHRONO_DATETIME_FORMATS

    if start_time is None:
        raise TypeError("start_time cannot be None")
    normalized_start_time: dt.datetime = to_datetime(start_time, formats)

    # Keep mypy happy, this code is does not "run"
    normalized_end_time: dt.datetime

    if end_time is None:
        normalized_end_time = dt.datetime.now()
    else:
        normalized_end_time = to_datetime(end_time, formats)

    return normalized_start_time, normalized_end_time
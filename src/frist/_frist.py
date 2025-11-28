"""
Chrono - Comprehensive datetime utility class.

Handles age calculations, calendar windows, and datetime parsing for any datetime operations.
Designed to be reusable beyond file operations.
"""

import datetime as dt
from typing import TypeAlias

from ._age import Age
from ._cal import Cal
from ._biz import Biz
from ._biz_policy import BizPolicy
from ._constants import CHRONO_DATETIME_FORMATS

# Alias for inputs accepted by Frist time utilities (datetime, date, POSIX ts, or string)
# Note: explicit optionality (`| None`) should be expressed at the call site.
TimeLike: TypeAlias = dt.datetime | dt.date | float | int | str


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
    formats:list[str] = formats__ or CHRONO_DATETIME_FORMATS

    def to_datetime(val: TimeLike) -> dt.datetime:
        
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
            for format in formats:
                try:
                    return dt.datetime.strptime(val,format)
                except ValueError:
                    continue
            raise TypeError(f"Unrecognized datetime string format: {val}")
        else:
            raise TypeError("Value must be datetime, date, float, int, or str")

    if start_time is None:
        raise TypeError("start_time cannot be None")
    normalized_start_time: dt.datetime = to_datetime(start_time)

    # Keep mypy happy, this code is does not "run"
    normalized_end_time: dt.datetime
    
    if end_time is None:
        normalized_end_time = dt.datetime.now()
    else:
        normalized_end_time = to_datetime(end_time)

    return normalized_start_time, normalized_end_time


class Chrono:
    """
    Comprehensive datetime utility with age and window calculations.

    Provides age calculations, calendar windows, and datetime parsing that can be used
    for any datetime operations, not just file timestamps.

    Examples:
        # Standalone datetime operations
        meeting = Chrono(datetime(2024, 12, 1, 14, 0))
        if meeting.age.hours < 2:
            print("Meeting was recent")

        # Custom reference time
        project = Chrono(start_date, reference_time=deadline)
        if project.age.days > 30:
            print("Project overdue")

        # Calendar windows
        if meeting.cal.in_days(0):
            print("Meeting was today")
    """

    def __init__(
        self,
        *,
        target_time: TimeLike,
        reference_time: TimeLike | None = None,
        policy: BizPolicy | None = None,
    ):
        """
        Initialize Chrono with target and reference times and an optional BizPolicy.

        Args:
            target_time (datetime): The datetime to analyze (e.g., file timestamp, event time).
            reference_time (datetime, optional): The reference datetime for calculations (defaults to now).
            policy (BizPolicy, optional): BizPolicy object for business rules (defaults to fiscal year Jan, 9-5, no holidays).

        Raises:
            ValueError: If target_time is not a datetime instance.

        Examples:
            >>> Chrono(target_time=datetime(2024, 5, 1))
            >>> Chrono(target_time=datetime(2024, 5, 1), reference_time=datetime(2025, 5, 1))
            >>> Chrono(target_time=datetime(2024, 5, 1), policy=BizPolicy(fiscal_year_start_month=4))
        """
        
        # Normalize target and reference so we get clean  datetime objects
        target,ref = time_pair(start_time=target_time,end_time=reference_time) 

        # This keeps the typechecker happy
        self.target_time:dt.datetime = target
        self.reference_time:dt.datetime = ref

        # Forward the policy to both objects
        self.policy: BizPolicy = policy or BizPolicy()

        # Now we have synchronized reference times with no possibility of the reference time being different
        # in the case that now() is used in both cases.  If you didn't do this it would be up to you
        # to ensure the same reference time.  This could make VERY hard to find bugs if the reference time
        # for the two objects occurred across a hour/day/month/quarter/year boundary.
        self._age: Age = Age(self.target_time, self.reference_time)
        self._cal: Cal = Cal(self.target_time, self.reference_time)

        # Biz gets the policy since that is how it figures things out.
        self._biz: Biz = Biz(self.target_time, self.reference_time, self.policy)
        

    @property
    def age(self) -> Age:
        """Return the Age object for this Chrono."""
        return self._age

    @property
    def cal(self) -> Cal:
        """Return the Cal object for this Chrono."""
        return self._cal

    @property
    def biz(self) -> Biz:
        """Return the Biz object for this Chrono."""
        return self._biz
    
    @property
    def timestamp(self) -> float:
        """Get the raw timestamp for target_time."""
        return self.target_time.timestamp()

    @staticmethod
    def parse(time_str: str, reference_time: TimeLike | None = None, policy: BizPolicy | None = None):
        """
        Parse a time string and return a Chrono object.

        Args:
            time_str: Time string to parse
            reference_time: Optional reference time for age calculations
            policy: Optional BizPolicy for business rules

        Returns:
            Chrono object for the parsed time

        Examples:
            "2023-12-25" -> Chrono for Dec 25, 2023
            "2023-12-25 14:30" -> Chrono for Dec 25, 2023 2:30 PM
            "2023-12-25T14:30:00" -> ISO format datetime
            "1640995200" -> Chrono from Unix timestamp
        """
        time_str = time_str.strip()

        # Handle Unix timestamp (all digits)
        if time_str.isdigit():
            target_time = dt.datetime.fromtimestamp(float(time_str))
            return Chrono(target_time=target_time, reference_time=reference_time, policy=policy)

        # Try common datetime formats
        formats = [
            "%Y-%m-%d",  # 2023-12-25
            "%Y-%m-%d %H:%M",  # 2023-12-25 14:30
            "%Y-%m-%d %H:%M:%S",  # 2023-12-25 14:30:00
            "%Y-%m-%dT%H:%M:%S",  # 2023-12-25T14:30:00 (ISO)
            "%Y-%m-%dT%H:%M:%SZ",  # 2023-12-25T14:30:00Z (ISO with Z)
            "%Y/%m/%d",  # 2023/12/25
            "%Y/%m/%d %H:%M",  # 2023/12/25 14:30
            "%m/%d/%Y",  # 12/25/2023
            "%m/%d/%Y %H:%M",  # 12/25/2023 14:30
        ]

        for fmt in formats:
            try:
                target_time = dt.datetime.strptime(time_str, fmt)
                return Chrono(target_time=target_time, reference_time=reference_time, policy=policy)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse time string: {time_str}")

    def with_reference_time(self, reference_time: dt.datetime):
        """
        Create a new Chrono object with a different reference time.

        Args:
            reference_time: New reference time for calculations

        Returns:
            New Chrono object with same target_time but different reference_time
        """
        return Chrono(target_time=self.target_time, reference_time=reference_time, policy=self.policy)

    def __repr__(self) -> str:
        """String representation of Chrono object."""
        return f"Chrono(target={self.target_time.isoformat()}, reference={self.reference_time.isoformat()})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Chrono for {self.target_time.strftime('%Y-%m-%d %H:%M:%S')}"

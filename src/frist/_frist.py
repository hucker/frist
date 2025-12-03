"""
Chrono - Comprehensive datetime utility class.

Handles age calculations, calendar windows, and datetime parsing for any datetime operations.
Designed to be reusable beyond file operations.
"""

import datetime as dt

from ._age import Age
from ._biz import Biz
from ._biz_policy import BizPolicy
from ._cal import Cal
from ._types import TimeLike, time_pair


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
        formats: list[str] | None = None,
    ):
        """
        Initialize Chrono with target and reference times and an optional BizPolicy.

        Args:
            target_time (TimeLike): The datetime to analyze (e.g., file timestamp, event time).
            reference_time (TimeLike, optional): The reference datetime for calculations (defaults to now).
            policy (BizPolicy, optional): BizPolicy object for business rules (defaults to fiscal year Jan, 9-5, no holidays).
            formats (list[str], optional): Custom datetime formats for string parsing.

        Raises:
            ValueError: If target_time is not a datetime instance.

        Examples:
            >>> Chrono(target_time=datetime(2024, 5, 1))
            >>> Chrono(target_time=datetime(2024, 5, 1), reference_time=datetime(2025, 5, 1))
            >>> Chrono(target_time=datetime(2024, 5, 1), policy=BizPolicy(fiscal_year_start_month=4))
            >>> Chrono(target_time="2024-05-01", formats=["%Y-%m-%d"])
        """
        
        # Normalize target and reference so we get clean  datetime objects
        target,ref = time_pair(start_time=target_time, 
                                                   end_time=reference_time, 
                                                   formats__=formats) 

        # This keeps the typechecker happy
        self.target_time:dt.datetime = target
        self.reference_time:dt.datetime = ref

        # Forward the policy to both objects
        self.policy: BizPolicy = policy or BizPolicy()

        # Now we have synchronized reference times with no possibility of the reference time being 
        # different in the case that now() is used in both cases.  If you didn't do this it would 
        # be up to you to ensure the same reference time.  This could make VERY hard to find bugs 
        # if the reference time for the two objects occurred across a hour/day/month/quarter/year 
        # boundary.
        self._age: Age = Age(self.target_time, self.reference_time)
        self._cal: Cal = Cal(self.target_time, self.reference_time)

        # Biz gets the policy since that is how it figures things out.
        self._biz: Biz = Biz(target_dt=self.target_time, 
                             ref_dt=self.reference_time, 
                             policy=self.policy)
        

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

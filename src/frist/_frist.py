"""
Frist - Comprehensive datetime utility class.

Handles age calculations, calendar windows, and datetime parsing for any datetime operations.
Designed to be reusable beyond file operations.
"""

import datetime as dt

from ._age import Age
from ._cal import Cal


class Frist:
    """
    Comprehensive datetime utility with age and window calculations.

    Provides age calculations, calendar windows, and datetime parsing that can be used
    for any datetime operations, not just file timestamps.

    Examples:
        # Standalone datetime operations
        meeting = Frist(datetime(2024, 12, 1, 14, 0))
        if meeting.age.hours < 2:
            print("Meeting was recent")

        # Custom reference time
        project = Frist(start_date, reference_time=deadline)
        if project.age.days > 30:
            print("Project overdue")

        # Calendar windows
    if meeting.cal.in_days(0):
            print("Meeting was today")
    """

    def __init__(
        self,
        *,
        target_time: dt.datetime,
        reference_time: dt.datetime | None = None,
        fy_start_month: int = 1,
        holidays: set[str] | None = None,
    ):
        """
        Initialize Frist with target and reference times.

        Args:
            target_time: The datetime to analyze (e.g., file timestamp, meeting time)
            reference_time: Reference time for calculations (defaults to now)
            fy_start_month: Fiscal year start month (1=Jan, 2=Feb, ... 12=Dec)
            holidays: Set of date strings (YYYY-MM-DD) that are holidays

        Raises:
            ValueError: If fy_start_month is not between 1 and 12
        """
        if not (1 <= fy_start_month <= 12):
            raise ValueError(f"fy_start_month must be between 1 and 12, got {fy_start_month}")
        if not isinstance(target_time, dt.datetime):
            raise ValueError(f"target_time must be a datetime instance, got {type(target_time)}")
        self.target_time:dt.datetime = target_time
        self.reference_time :dt.datetime= reference_time or dt.datetime.now()
        self.fy_start_month:int = fy_start_month
        self.holidays :set[str]= holidays if holidays is not None else set()


    @property
    def age(self) -> Age:
        """
        Get age of target_time relative to reference_time.

        Returns Age object with properties like .seconds, .minutes, .hours, .days, etc.
        """
        # Convert datetime objects to timestamps for Age class
        target_timestamp = self.target_time.timestamp()

        # Age expects (path, timestamp, base_time) - we pass None for path since standalone
        return Age(None, target_timestamp, self.reference_time)  # type: ignore

    @property
    def cal(self):

        """
        Get calendar window functionality for target_time.

        Returns Cal object for checking if target_time falls within calendar windows.
        """
        # Cal can work directly with Frist since we have .target_dt and .ref_dt properties
        return Cal(self, fy_start_month=self.fy_start_month, holidays=self.holidays)

    @property
    def timestamp(self) -> float:
        """Get the raw timestamp for target_time."""
        return self.target_time.timestamp()

    @property
    def target_dt(self) -> dt.datetime:
        """Get the target datetime for TimeSpan compatibility."""
        return self.target_time

    @property
    def ref_dt(self) -> dt.datetime:
        """Get the reference datetime for TimeSpan compatibility."""
        return self.reference_time


    @staticmethod
    def parse(time_str: str, reference_time: dt.datetime | None = None):
        """
        Parse a time string and return a Frist object.

        Args:
            time_str: Time string to parse
            reference_time: Optional reference time for age calculations

        Returns:
            Frist object for the parsed time

        Examples:
            "2023-12-25" -> Frist for Dec 25, 2023
            "2023-12-25 14:30" -> Frist for Dec 25, 2023 2:30 PM
            "2023-12-25T14:30:00" -> ISO format datetime
            "1640995200" -> Frist from Unix timestamp
        """
        time_str = time_str.strip()

        # Handle Unix timestamp (all digits)
        if time_str.isdigit():
            target_time = dt.datetime.fromtimestamp(float(time_str))
            return Frist(target_time=target_time, reference_time=reference_time)

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
                return Frist(target_time=target_time, reference_time=reference_time)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse time string: {time_str}")

    def with_reference_time(self, reference_time: dt.datetime):
        """
        Create a new Frist object with a different reference time.

        Args:
            reference_time: New reference time for calculations

        Returns:
            New Frist object with same target_time but different reference_time
        """
        return Frist(target_time=self.target_time, reference_time=reference_time)


    def __repr__(self) -> str:
        """String representation of Frist object."""
        return f"Frist(target={self.target_time.isoformat()}, reference={self.reference_time.isoformat()})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Frist for {self.target_time.strftime('%Y-%m-%d %H:%M:%S')}"


__all__ = ["Frist"]

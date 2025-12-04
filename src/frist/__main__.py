"""
CLI tool for frist: Print age, calendar, and business info for one or two dates.

Usage:
    python -m frist <date> [<date>]
If only one date is provided, the second is assumed to be None (now).

AAA Pattern:
- Arrange: Parse arguments, set up BizPolicy and Chrono objects.
- Act: Query Chrono for age, calendar, and business info.
- Assert: Print results to console (for demonstration).

Follows frist CODESTYLE.md: 
- Uses docstrings for module and functions.
- Section headers for output.
- Consistent formatting and alignment.
"""

import sys
from frist import Chrono, BizPolicy


def main() -> None:
    """
    Main entry point for the frist CLI tool.

    Parses command-line arguments, sets up BizPolicy and Chrono objects,
    and prints age, calendar, and business info for the provided dates.
    """

    if len(sys.argv) not in (2, 3):
        print("Usage: python -m frist <date> [<date>]")
        print("Example: python -m frist 2023-01-01 2023-02-15T12:00:00")
        sys.exit(1)

    # Create a BizPolicy
    biz_policy = BizPolicy(
        fiscal_year_start_month=4, holidays={"2025-1-1", "2025-07-04", "2025-12-25"}
    )

    date1 = sys.argv[1]
    date2 = sys.argv[2] if len(sys.argv) == 3 else None
    chrono = Chrono(target_time=date1, reference_time=date2, policy=biz_policy)

    print("\n=== frist CLI demo ===")
    print(f"{'target_time:':<18} {chrono.target_time}")
    print(f"{'reference_time:':<18} {chrono.reference_time}\n")

    print("=== Age Properties ===")
    print(f"{'seconds:':<18} {chrono.age.seconds:.2f}")
    print(f"{'minutes:':<18} {chrono.age.minutes:.2f}")
    print(f"{'hours:':<18} {chrono.age.hours:.2f}")
    print(f"{'days:':<18} {chrono.age.days:.2f}")
    print(f"{'months:':<18} {chrono.age.months:.2f}")
    print(f"{'years:':<18} {chrono.age.years:.2f}")
    print(f"{'months_precise:':<18} {chrono.age.months_precise:.2f}")
    print(f"{'years_precise:':<18} {chrono.age.years_precise:.2f}\n")

    print("=== Calendar Aligned Window Checks (Cal) ===")
    print(f"{'Minute in_(-5,0):':<20} {chrono.cal.minute.in_(-5, 0):<6}  # Is target 5 min ago to ref_time?")
    print(f"{'Hour in_(-1,0):':<20} {chrono.cal.hour.in_(-1, 0):<6}  # Is target 1 hr ago to ref_time?")
    print(f"{'Day in_(-1,1):':<20} {chrono.cal.day.in_(-1, 1):<6}  # Is target day before to day after ref_time?")
    print(f"{'Week in_(-2,0):':<20} {chrono.cal.week.in_(-2, 0):<6}  # Is target 2 weeks ago to ref_time?")
    print(f"{'Month in_(-6,0):':<20} {chrono.cal.month.in_(-6, 0):<6}  # Is target 6 months ago to ref_time?")
    print(f"{'Quarter in_(-1,1):':<20} {chrono.cal.qtr.in_(-1, 1):<6}  # Is target 1 qtr ago to qtr after ref_time?")
    print(f"{'Year in_(-3,0):':<20} {chrono.cal.year.in_(-3, 0):<6}  # Is target 3 yrs ago to ref_time?\n")

    print("=== Calendar Shortcuts (Cal) ===")
    print(f"{'is_today:':<18} {chrono.cal.is_today}")
    print(f"{'is_yesterday:':<18} {chrono.cal.is_yesterday}")
    print(f"{'is_tomorrow:':<18} {chrono.cal.is_tomorrow}")
    print(f"{'is_this_week:':<18} {chrono.cal.is_this_week}")
    print(f"{'is_this_month:':<18} {chrono.cal.is_this_month}")
    print(f"{'is_this_quarter:':<18} {chrono.cal.is_this_quarter}")
    print(f"{'is_this_year:':<18} {chrono.cal.is_this_year}")
    print(f"{'is_last_month:':<18} {chrono.cal.is_last_month}")
    print(f"{'is_last_year:':<18} {chrono.cal.is_last_year}\n")

    print("=== Calendar Info ===")
    print(f"{'Minute:':<18} {chrono.cal.minute.val}")
    print(f"{'Hour:':<18} {chrono.cal.hour.val}")
    print(f"{'Day:':<18} {chrono.cal.day.val} ({chrono.cal.day.name})")
    print(f"{'Week:':<18} {chrono.cal.week.val} (Day: {chrono.cal.week.day})")
    print(f"{'Month:':<18} {chrono.cal.month.val} (Day: {chrono.cal.month.day})")
    print(f"{'Quarter:':<18} {chrono.cal.qtr.val} ({chrono.cal.qtr.name})")
    print(f"{'Year:':<18} {chrono.cal.year.val} (Day: {chrono.cal.year.day})\n")

    print("=== Biz Info ===")
    print(f"{'Is Business Day:':<18} {chrono.biz.is_business_day}")
    print(f"{'Is Working Day:':<18} {chrono.biz.is_workday}")
    print(f"{'Work days:':<18} {chrono.biz.working_days:.2f}")
    print(f"{'Business days:':<18} {chrono.biz.business_days:.2f}")
    print(f"{'Fiscal Quarter:':<18} {chrono.biz.fis_qtr.val} ({chrono.biz.fis_qtr.name})")
    print(f"{'Fiscal Year:':<18} {chrono.biz.fiscal_year}")


if __name__ == "__main__":
    main()

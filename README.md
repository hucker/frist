# `Frist`: Unified Age and Calendar Logic

`Frist` is a modern Python library designed to make working with time, dates, intervals and business calendars easy using a simple, expressive property-based API. `Frist` provides property-based APIs for `Age`, `Cal` and `Biz`. The `Age` object answers “How old is this?” for two datetimes (often defaulting the second datetime to “now”), making it useful for file aging, log analysis, or event tracking. The `Cal` object lets you ask “Is this date in a specific window?”—such as today, yesterday, this month, this quarter, or this fiscal year—using intuitive properties for calendar logic. Calendar ranges are aligned to calendar units (minute, hour, day, business day, week, month, quarter, year). Finally, the `Biz` class lets you establish a business policy for workdays, business hours, holidays and fiscal years so you can perform business-calendar-aware queries.

`Frist` is not a [replacement](https://imgs.xkcd.com/comics/standards_2x.png) for `datetime` or `timedelta`. If the standard library meets your needs, keep using it.

Frist does more than shorten expressions: it reduces many common calendar and business-date queries to a single, expressive property (for example, `Cal(...).is_this_quarter`, `Age(...).days`, or `Biz(...).bday.in_(0)`). That one-property approach makes intent explicit, avoids repeating low-level date math across projects, and centralizes tricky edge cases such as half-open intervals, fiscal boundaries, and business-hour fractions.

Here are some examples of a dataset with a bunch of datetimes.

``` python
from frist import Age, Cal, Biz, BizPolicy

# In these examples a second datetime is not provided; when omitted the constructors use the reference time (now).
#
# If you omit the reference time, Frist uses the current time (`now`) as the reference. This makes
# one-property expressions (for example, `Age(date).days` or `Cal(date).is_today`) convenient for
# interactive use; pass an explicit reference when you need deterministic, reproducible comparisons
# (for tests or batch processing against a fixed point in time).

dates = large_list_of_date_times()

# Policy only required if you want business date info
policy = BizPolicy(fiscal_year_start_month=4, holidays={"2026-01-01"})

# If no second date provided then now() assumed.

last_four_and_half_minutes = [date for date in dates if Age(date).minutes <= 4.5]

last_three_years = [date for date in dates if Age(date).years < 3.0]

dates_today = [date for date in dates if Cal(date).day.in_(0)]

last_two_months = [date for date in dates if Cal(date).mon.in_(-2, 0)]

last_three_cal_years = [date for date in dates if Cal(date).year.in_(-3, 0)]

last_five_business_days = [date for date in dates if Biz(date).bday.in_(-5, 0)]

this_fiscal_year = [date for date in dates if Biz(date, policy).fyear.in_(0)]

last_3_fiscal_years = [date for date in dates if Biz(date, policy).fyear.in_(-2, 0)]

ignore_holidays = [date for date in dates if not Biz(date, policy).is_holiday]

# Shortcut examples where intent is very clear
dates_today_shortcut = [date for date in dates if Cal(date).is_today]
dates_this_quarter = [date for date in dates if Cal(date).is_this_quarter]
dates_last_year = [date for date in dates if Cal(date).is_last_year]
```

## Caveats

- **Fixed-length business days:** Calculations assume standard day lengths; DST transitions 
  are ignored. Fractional-day values always use these standard lengths.

- **No timezone support:** All datetimes are treated as naive; timezones are not considered.

- **Fiscal-year and fiscal-quarter logic:** You can set the fiscal year to start on any 
  month. Each fiscal year has four quarters, each 3 months long, with Q1 starting on the 
  first day of the chosen month.

- **Precomputed Holidays** The business holiday set is a precomputed list of holidays provided by the business.  It is assumed this list will take care of ALL "movable" holiday calculations and provide a list of days (that should land on working days) that are considered days off.  THere is NO calculation involved.  If New Years on a Sunday and you are closed Monday then you need to add the 2nd as a holiday.  These calendars are usually provided by HR or accounting.

## Age

The `Age` object answers "How old is X?" for two datetimes (start and end). It exposes common elapsed-time metrics as properties so you can write intent‑revealing one‑liners.

- Purpose: elapsed / duration properties (seconds, minutes, hours, days, weeks, months, years).
- Special: `months_precise` and `years_precise` compute calendar-accurate values; `parse()` converts human-friendly duration strings to seconds.
- Default behavior: if `end_time` is omitted it defaults to set to `datetime.now()`.

Example:

```python
>>> from frist import Age
>>> import datetime as dt
>>> a = Age(start_time=dt.datetime(2025,9,1), end_time=dt.datetime(2025,11,20))
>>> a.days
80.0
>>> a.years     # number of days in "average" years thus 80/365.25 days
0.2190280629705681
>>> a.years_precise # number of days in 2025  thus 80/366
0.2191780821917808

```

---

## Cal

The `Cal` object provides calendar-aligned window queries (minute/hour/day/week/month/quarter/year and fiscal variants) using half-open semantics. Use `in_*` methods to ask whether a target falls in a calendar window relative to a reference date.

- Purpose: calendar-window membership (in_days, in_months, in_quarters, in_fiscal_years, ...).
- Behavior: calendar-aligned, half-open intervals; supports custom week starts and fiscal start month via Chrono/BizPolicy composition.
- Use-case: one-liners for "was this date in the last two months?" or "is this in the current fiscal quarter?"

Practical note on half-open intervals:

It is normal English to define time spans as half-open intervals. For example, when you say "from 1:00 PM to 2:00 PM" you mean a meeting that starts at 1:00 PM and ends at 2:00 PM (one hour long). You do not mean "any time whose hour is 1 or 2" or that the instant at 2:00 PM is included in the 1:00–2:00 meeting. In half-open semantics the start is inclusive and the end is exclusive — i.e. the interval contains times t where 1:00 PM <= t < 2:00 PM. This convention avoids overlapping windows (e.g., an event that ends exactly at 2:00 PM belongs to the next interval, not the previous one) and makes unit-based queries like `in_hours(1)` intuitive.

Example:

```python
>>> from frist import Cal
>>> import datetime as dt
>>> target = dt.datetime(2025,9,15)
>>> ref = dt.datetime(2025,11,20)
>>> c = Cal(target_dt=target, ref_dt=ref)
>>> c.mon.in_(-2, 0)
True    # target was in Sept/Oct (the two full months before Nov)
>>> c.day.in_(-7, -1)
False   # not in the 7..1 days before ref
```

### Inclusive `thru` helper

Frist also provides a  helper available on the compact `UnitNamespace` properties (for example `cal.mon`, `cal.day`, `biz.bday`) named `thru`. The `thru` method uses inclusive end semantics which is convenient for human-readable ranges such as "Mon thru Fri" where the end is part of the range.

- `*.in_` methods and the main API use half-open intervals: `start <= value < end`. - `*.thru(start, end)` is inclusive on the end: it returns True when `start <= value <= end`.

Implementation note: `thru` is implemented as a thin ergonomic adapter that forwards to the canonical half-open `in_*` methods by advancing the exclusive end by one unit. For example `cal.mon.thru(-2, 0)` is equivalent to `cal.mon.in_(-2, 1)` (the inclusive end `0` becomes exclusive `1`). This keeps the core API canonical while offering a more natural English-style `thru` surface for consumers.

Examples:

```pycon
>>> from frist import Cal
>>> import datetime as dt
>>> ref = dt.datetime(2025,11,20)
>>> # "last Monday thru Friday" style checks
>>> Cal(dt.datetime(2025,11,17), ref).day.thru(-3, -1)   # Mon thru Wed
True
>>> # Equivalent half-open call
>>> Cal(dt.datetime(2025,11,17), ref).day.in_(-3, 0)
True
```

---

## Biz

The `Biz` object performs policy-aware business calendar calculations. It relies on `BizPolicy` to determine workdays, holidays, business hours, and fiscal rules.

- Purpose: business/working-day arithmetic (fractional day spans, range membership, fiscal helpers).
- Key differences: `working_days` counts weekdays per policy (ignores holidays); `business_days` excludes holidays. Fractional days computed using policy business hours.
- Common methods: `working_days`, `business_days`, `in_working_days`, `in_business_days`, `get_fiscal_year`, `get_fiscal_quarter`.

Example:

```pycon
>>> from frist import Biz, BizPolicy
>>> import datetime as dt
>>> policy = BizPolicy(workdays={0,1,2,3,4}, holidays={"2025-12-25"})
>>> start = dt.datetime(2025,12,24,9,0)
>>> end   = dt.datetime(2025,12,26,17,0)
>>> b = Biz(start, end, policy)
>>> b.working_days
3.0      # counts Wed/Thu/Fri as workdays (holidays ignored)
>>> b.business_days
2.0      # Dec 25 removed from business-day total
>>> b.bday.in_(0)
False    # target is a holiday -> not a business day
>>> b.wday.in_(0)
True     # still a weekday per policy

The `BizPolicy` object lets you customize business logic for calendar calculations using half-open intervals You can define:

- **Workdays:** Any combination of weekdays (e.g., Mon, Wed, Fri, Sun)
- **Holidays:** Any set of dates to exclude from working day calculations
- **Business hours:** Custom start/end times for each day
- **Fiscal year start:** Set the starting month for fiscal calculations

**Default Policy:**

If you do not provide a `BizPolicy`, Frist uses a default policy:

- Workdays: Monday–Friday (0–4)
>>> c.day.in_(-1)
- Holidays: none

This is suitable for most standard business use cases. You only need to provide a custom `BizPolicy` if your calendar logic requires non-standard workweeks, holidays, or business hours.

Example (custom policy):

```python
>>> from frist import BizPolicy
>>> policy = BizPolicy(
...     workdays=[0, 1, 2, 3, 4],
...     holidays={"2025-01-10"},
...     start_of_business=dt.time(9, 0),
...     end_of_business=dt.time(17, 0),
...     fiscal_year_start_month=4,
... )
>>> date = dt.datetime(2025, 5, 15)
>>> policy.get_fiscal_year(date)
2025
>>> policy.get_fiscal_quarter(date)
1
>>> policy.is_holiday(dt.datetime(year=2025, month=1, day=1))
False
```

---

## API Reference

Here is a brief overview of the various classes that make up `Frist`.

### Age Object

`Age(start_time: datetime, end_time: datetime = None, biz_policy: BizPolicy = None)`

| Property         | Description                                               |
| ---------------- | --------------------------------------------------------- |
| `seconds`        | Age in seconds                                            |
| `minutes`        | Age in minutes                                            |
| `hours`          | Age in hours                                              |
| `days`           | Age in days                                               |
| `weeks`          | Age in weeks                                              |
| `months`         | Age in months (approximate, 30.44 days)                   |
| `months_precise` | Age in months (precise, calendar-based)                   |
| `years`          | Age in years (approximate, 365.25 days)                   |
| `years_precise`  | Age in years (precise, calendar-based)                    |
| `working_days`   | Fractional working days between start and end, per policy |
| `fiscal_year`    | Fiscal year for start_time                                |
| `fiscal_quarter` | Fiscal quarter for start_time                             |
| `start_time`     | Start datetime                                            |
| `end_time`       | End datetime                                              |
| `biz_policy`     | BizPolicy used for business logic                    |

| Method                                      | Description                 |
| ------------------------------------------- | --------------------------- |
| `set_times(start_time=None, end_time=None)` | Update start/end times      |
| `parse(age_str)`                            | Parse age string to seconds |

The `months_precise` and `years_precise` properties calculate the `exact` number of calendar months or years between two dates, accounting for the actual length of each month and year. Unlike the approximate versions (which use averages like 30.44 days/month or 365.25 days/year), these properties provide results that match real-world calendar boundaries. They are more intuitively correct but are slower to compute since the first and last month/year need to be handled differently.  Basically, Feb 1 to Feb 28 (non leap year) is 1.0 precise months long, while Jan 1 to Jan31 is also 1 precise month long. And Jan 1 to Feb 14 is 1.5 precise months.  For years it is similar but the effect is smaller.  The 365 days in 2021 is 1 precise year as are the 366 days in 2024.

---

### Cal Object

The Cal object provides a family of `in_*` methods (e.g., `in_days`, `in_months`, `in_years` etc) to check if the target date falls within a calendar window relative to the reference date. These methods use calendar units (not elapsed time) using half-open intervals. The start is inclusive, the end is exclusive. This makes it easy to check if a date is in a specific calendar range (e.g., last week, next month, fiscal quarter) using intuitive, unit-based logic.

 `day.in_(-1)`: Is the target date yesterday?
 `day.in_(-1, 1)`: Is the target date within ±1 calendar day of the reference?

`Cal(target_dt: datetime, ref_dt: datetime, fy_start_month: int = 1, holidays: set[str] = None)`

| Property         | Description                   | Return |
| ---------------- | ----------------------------- | ------ |
| `dt_val`         | Target datetime               | `datetime` |
| `base_time`      | Reference datetime            | `datetime` |
| `fiscal_year`    | Fiscal year for `dt_val`      | `int` |
| `fiscal_quarter` | Fiscal quarter for `dt_val`   | `int` |
| `holiday`        | True if `dt_val` is a holiday | `bool` |

| Unit accessor                                      | Description                 | Return |
| -------------------------------------------------- | --------------------------- | ------ |
| `cal.min.in_(start=0, end=None)`                   | Is target in minute window  | `bool` |
| `cal.hr.in_(start=0, end=None)`                    | Is target in hour window    | `bool` |
| `cal.day.in_(start=0, end=None)`                   | Is target in day window     | `bool` |
| `cal.wk.in_(start=0, end=None, week_start="monday")` | Is target in week window    | `bool` |
| `cal.mon.in_(start=0, end=None)`                   | Is target in month window   | `bool` |
| `cal.qtr.in_(start=0, end=None)`                   | Is target in quarter window | `bool` |
| `cal.year.in_(start=0, end=None)`                   | Is target in year window    | `bool` |

Shortcuts (convenience boolean properties):

| Shortcut | Equivalent |
| -------- | ---------------------- |
| `is_today`       | `cal.day.in_(0)`        |
| `is_yesterday`   | `cal.day.in_(-1)`       |
| `is_tomorrow`    | `cal.day.in_(1)`        |
| `is_last_week`   | `cal.wk.in_(-1)`        |
| `is_this_week`   | `cal.wk.in_(0)`         |
| `is_next_week`   | `cal.wk.in_(1)`         |
| `is_last_month`  | `cal.mon.in_(-1)`       |
| `is_this_month`  | `cal.mon.in_(0)`        |
| `is_next_month`  | `cal.mon.in_(1)`        |
| `is_last_quarter`| `cal.qtr.in_(-1)`       |
| `is_this_quarter`| `cal.qtr.in_(0)`        |
| `is_next_quarter`| `cal.qtr.in_(1)`        |
| `is_last_year`   | `cal.year.in_(-1)`        |
| `is_this_year`   | `cal.year.in_(0)`         |
| `is_next_year`   | `cal.year.in_(1)`         |

---

### Biz Object

The `Biz` object performs business-aware calculations using a `BizPolicy`. It counts
working days (defined by the policy's workday set) and business days (working days that are not holidays).
It also computes fractional day contributions using the policy's business hours.

***Business days and workdays are tricky to calculate and involve iteration because no/few assumptions can be made about the way the days fall. Normally this isn't a huge deal because the time spans are a few days, not 1000's of days.***

`Biz(target_time: datetime, ref_time: datetime | None, policy: BizPolicy | None)`

| Property / Attribute | Description                                                         | Return |
| -------------------- | ------------------------------------------------------------------- | ------ |
| `cal_policy`         | `BizPolicy` instance used by this Biz                          | `BizPolicy` |
| `target_time`        | Target datetime                                                     | `datetime` |
| `ref_time`           | Reference datetime                                                  | `datetime` |
| `holiday`            | True if `target_time` is a holiday                                  | `bool` |
| `is_workday`         | True if `target_time` falls on a workday                            | `bool` |
| `is_business_day`    | True if `target_time` is a business day (workday and not holiday)   | `bool` |
| `working_days`       | Fractional working days between target and ref (ignores holidays)   | `float` |
| `business_days`      | Fractional business days between target and ref (excludes holidays) | `float` |

| Method                                   | Description                                           | Return |
| ---------------------------------------- | ----------------------------------------------------- | ------ |
| `in_working_days(start=0, end=0)`        | Range membership by working days (ignores holidays)   | `bool` |
| `in_business_days(start=0, end=0)`       | Range membership by business days (excludes holidays) | `bool` |
| `get_fiscal_year(dt, fy_start_month)`    | Static helper to compute fiscal year for a datetime   | `int`  |
| `get_fiscal_quarter(dt, fy_start_month)` | Static helper to compute fiscal quarter               | `int`  |

Shortcuts (convenience boolean properties):

| Shortcut | Equivalent `in_*` call |
| -------- | --------------------- |
| `is_business_last_day` | `bday.in_(-1)` (observes holidays) |
| `is_business_this_day` | `bday.in_(0)` (observes holidays) |
| `is_business_next_day` | `bday.in_(1)` (observes holidays) |
| `is_workday_last_day` | `wday.in_(-1)` |
| `is_workday_this_day` | `wday.in_(0)` |
| `is_workday_next_day` | `wday.in_(1)` |
| `is_last_fiscal_quarter` | `in_fiscal_quarters(-1)` |
| `is_this_fiscal_quarter` | `in_fiscal_quarters(0)` |
| `is_next_fiscal_quarter` | `in_fiscal_quarters(1)` |
| `is_last_fiscal_year` | `in_fiscal_years(-1)` |
| `is_this_fiscal_year` | `in_fiscal_years(0)` |
| `is_next_fiscal_year` | `in_fiscal_years(1)` |

### Chrono Object

In some situations you will need to have all three of these classes together because the filtering you are doing is related to the multiple classes.  The best way to handle this is with the chrono object.  The `Chrono` class initializes all three so you have access to each of the classes, with no race conditions when setting the reference time.

```python
# Brief Chrono example: create a Chrono and print Age / Cal / Biz properties
>>> from frist import Chrono, BizPolicy
>>> import datetime as dt
>>> target = dt.datetime(2025, 4, 25, 15, 0)
>>> ref = dt.datetime(2025, 4, 30, 12, 0)
>>> policy = BizPolicy(workdays={0,1,2,3,4}, holidays={"2025-04-28"})
>>> z = Chrono(target_time=target, reference_time=ref, policy=policy)

# Age (elapsed-time properties)
>>> z.age.days                # elapsed days (float)
3.875
>>> z.age.years_precise       # calendar-accurate years
0.0106

# Cal (calendar-window queries)
>>> z.cal.day.in_(-5)         # was target 5 days before reference?
True
>>> z.cal.mon.in_(0)        # same calendar month as reference?
True

# Biz (policy-aware business logic — properties are floats)
>>> z.biz.working_days        # fractional working days (counts workdays per policy)
1.0
>>> z.biz.business_days       # fractional business days (excludes holidays from policy)
0.0
>>> z.biz.wday.in_(0)  # range-membership helper (bool)
True
>>> z.biz.bday.in_(0) # range-membership helper (bool)
False
```

`Chrono(target_time: datetime, reference_time: datetime = None, biz_policy:BizPolicy|None)`

| Property | Description                                           |
| -------- | ----------------------------------------------------- |
| `age`    | Age object for span calculations (see Age above)      |
| `cal`    | Cal object for calendar window logic (see Cal above)  |
| `biz`    | Biz  object for calendar window logic (see Cal above) |

### Status

[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue?logo=python&logoColor=white)](https://www.python.org/) [![Coverage](https://img.shields.io/badge/coverage-100%25-green)](https://github.com/hucker/frist/actions) [![Pytest](https://img.shields.io/badge/pytest-100%25%20pass%20%7C%20368%20tests-green?logo=pytest&logoColor=white)](https://docs.pytest.org/en/stable/) [![Ruff](https://img.shields.io/badge/ruff-100%25-green?logo=ruff&logoColor=white)](https://github.com/charliermarsh/ruff) [![Tox](https://img.shields.io/static/v1?label=tox&message=3.10-3.14&color=green&logo=tox&logoColor=white)](https://tox.readthedocs.io/) [![Mypy](https://img.shields.io/static/v1?label=mypy&message=0%20issues&color=green&logo=mypy&logoColor=white)](https://mypy-lang.org/)

### Pytest (100% pass/100% coverage)

```text
Name                                      Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------------------------
src\frist\__init__.py                          8      0      0      0   100%
src\frist\_age.py                            119      0     34      0   100%
src\frist\_biz.py                            186      0     28      0   100%
src\frist\_biz_policy.py                      79      0     38      0   100%
src\frist\_cal.py                            160      0     12      0   100%
src\frist\_constants.py                       15      0      0      0   100%
src\frist\_frist.py                           73      0     18      0   100%
src\frist\_ranges.py                          25      0      4      0   100%
src\frist\_util.py                            18      0      2      0   100%
```

### Tox

```text
main> tox
  py310: OK (5.11=setup[3.24]+cmd[1.87] seconds)
  py311: OK (6.46=setup[3.89]+cmd[2.57] seconds)
  py312: OK (7.01=setup[4.65]+cmd[2.36] seconds)
  py313: OK (6.67=setup[4.37]+cmd[2.30] seconds)
  py314: OK (6.04=setup[4.27]+cmd[1.77] seconds)
  congratulations :) (32.91 seconds)
```

### Mypy

```text
main> mypy src/frist
Success: no issues found in 8 source files
```

### Notes

This project was developed iteratively using agentic AI thus most of the code was generated from prompts rather that writing code.  It was tricky getting tests implemented correctly. Generally I write a test case and then ask the AI to parameterize it and then I review.  I discovered that I had some code that had a bug in one case and the AI changed the test inputs (added 1) to make the test pass. I find with agentic AI that I spend more time on my testing than on coding, even to the point that I will happily delete a test file and start over if I don't like it. With manually written code I would be far less inclined to do that.

I also noted that certain types of refactoring humans are much better at.  I change the naming convention of some methods and asked the AI to fix it, after messing around with constant tab issues and bad assumptions I rolled it back and did a search and replace and change the names manually in a fraction of the time.

Contributions are welcome. Please prefer small, reviewable pull requests and include tests that exercise expected behavior and edge cases.

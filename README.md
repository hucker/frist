# `Frist`: Unified Age and Calendar Logic

`Frist`is a modern Python library designed to make working with time, dates, and intervals simple and expressive—whether you’re analyzing file ages, tracking events, or handling business calendars. `Frist` provides two core property-based APIs: `Age` and `Cal`. The `Age` object lets you answer “How old is this?” for two datetimes (often defaulting one to “now”), making it perfect for file aging, log analysis, or event tracking. The `Cal` object lets you ask “Is this date in a specific window?”—such as today, yesterday, this month, this quarter, or this fiscal year—using intuitive properties for calendar logic. Calendar ranges are always aligned to a calendar time scale, day, business day, month, year, quarter, hour.  `Frist` is not a [replacement](https://imgs.xkcd.com/comics/standards_2x.png) for `datetime` or `timedelta`.  

It is meant for usecases where you are doing lots of datetime math and find your self writing lots of small tricky functions. Frist lets you write code that is human readable with edge cases handled for you.

``` pycon
from frist import Age, Cal, Biz, CalendarPolicy
dates = large_list_of_dates()

last_four_and_half_minutes = [date for date in dates if Age(date).minutes <= 4.5]

last_three_years = [date for date in dates if Age(date).years < 3]

dates_today = [date for date in dates if Cal(date).in_days(0)]

last_two_months = [date for date in dates if Cal(date).in_months(-2,0)]

# Business day math requires business date setup in as a CalendarPolicy object.
policy = CalendaPolicy(fiscal_year_start_month=4,holidays={"2026-1-1"})

last_five_business_days = [date for date in dates if Biz(date,cal_policy=policy).in_business_days(-5,0)]

this_fiscal_year = [date for date in dates if Biz(date,cal_policy=policy).in_fiscal_years(0)]
```

## Age

The `Age` object answers "How old is X?" for two datetimes (start and end). It exposes common elapsed-time metrics as properties so you can write intent‑revealing one‑liners.

- Purpose: elapsed / duration properties (seconds, minutes, hours, days, weeks, months, years).
- Special: `months_precise` and `years_precise` compute calendar-accurate values; `parse()` converts human-friendly duration strings to seconds.
- Default behaviour: if `end_time` is omitted it defaults to now.

Example:

```pycon
>>> from frist import Age
>>> import datetime as dt
>>> a = Age(start_time=dt.datetime(2025,9,1), end_time=dt.datetime(2025,11,20))
>>> a.days
80.125
>>> a.years
0.21

```

---

## Cal

The `Cal` object provides calendar-aligned window queries (minute/hour/day/week/month/quarter/year and fiscal variants) using half-open semantics. Use `in_*` methods to ask whether a target falls in a calendar window relative to a reference date.

- Purpose: calendar-window membership (in_days, in_months, in_quarters, in_fiscal_years, ...).
- Behaviour: calendar-aligned, half-open intervals; supports custom week starts and fiscal start month via Chrono/CalendarPolicy composition.
- Use-case: one-liners for "was this date in the last two months?" or "is this in the current fiscal quarter?"

Example:

```pycon
>>> from frist import Cal
>>> import datetime as dt
>>> target = dt.datetime(2025,9,15)
>>> ref = dt.datetime(2025,11,20)
>>> c = Cal(target_dt=target, ref_dt=ref)
>>> c.in_months(-2, -1)
True    # target was in Sept/Oct (the two full months before Nov)
>>> c.in_days(-7, -1)
False   # not in the 7..1 days before ref
```

---

## Biz

The `Biz` object performs policy-aware business calendar calculations. It relies on `CalendarPolicy` to determine workdays, holidays, business hours, and fiscal rules.

- Purpose: business/working-day arithmetic (fractional day spans, range membership, fiscal helpers).
- Key differences: `working_days` counts weekdays per policy (ignores holidays); `business_days` excludes holidays. Fractional days computed using policy business hours.
- Common methods: `working_days`, `business_days`, `in_working_days`, `in_business_days`, `get_fiscal_year`, `get_fiscal_quarter`.

Example:

```pycon
>>> from frist import Biz, CalendarPolicy
>>> import datetime as dt
>>> policy = CalendarPolicy(workdays={0,1,2,3,4}, holidays={"2025-12-25"})
>>> start = dt.datetime(2025,12,24,9,0)
>>> end   = dt.datetime(2025,12,26,17,0)
>>> b = Biz(start, end, policy)
>>> b.working_days
3.0      # counts Wed/Thu/Fri as workdays (holidays ignored)
>>> b.business_days
2.0      # Dec 25 removed from business-day total
>>> b.in_business_days(0)
False    # target is a holiday -> not a business day
>>> b.in_working_days(0)
True     # still a weekday per policy
```

## CalendarPolicy

The `CalendarPolicy` object lets you customize business logic for calendar calculations using half open intervals You can define:

- **Workdays:** Any combination of weekdays (e.g., Mon, Wed, Fri, Sun)
- **Holidays:** Any set of dates to exclude from working day calculations
- **Business hours:** Custom start/end times for each day
- **Fiscal year start:** Set the starting month for fiscal calculations

**Default Policy:**

If you do not provide a `CalendarPolicy`, Frist uses a default policy:

- Workdays: Monday–Friday (0–4)
- Work hours: 9AM–5PM
- Holidays: none

This is suitable for most standard business use cases. You only need to provide a custom `CalendarPolicy` if your calendar logic requires non-standard workweeks, holidays, or business hours.

Example (custom policy):

```pycon
>>> from frist import CalendarPolicy
>>> import datetime as dt
>>> policy = CalendarPolicy(workdays={0,1,2,3,4}, holidays={"2025-1-1"}, work_hours=(9,17), fy_start_month=4)
>>> date = dt.datetime(2025, 5, 15)
>>> policy.get_fiscal_year(date)
2026
>>> policy.get_fiscal_quarter(date)
1
>>> policy.is_holiday(dt.datetime(year=2025,month=1,day=1))
True
```

---

## API Reference

Here is a brief overview of the various classes that makeup `Frist`.

### Age Object

`Age(start_time: datetime, end_time: datetime = None, cal_policy: CalendarPolicy = None)`

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
| `cal_policy`     | CalendarPolicy used for business logic                    |

| Method                                      | Description                 |
| ------------------------------------------- | --------------------------- |
| `set_times(start_time=None, end_time=None)` | Update start/end times      |
| `parse(age_str)`                            | Parse age string to seconds |

The `months_precise` and `years_precise` properties calculate the exact number of calendar months or years between two dates, accounting for the actual length of each month and year. Unlike the approximate versions (which use averages like 30.44 days/month or 365.25 days/year), these properties provide results that match real-world calendar boundaries. They are more intuitively correct but may be slower to compute, especially for long time spans.

---

### Cal Object

The Cal object provides a family of `in_*` methods (e.g., `in_days`, `in_months`, `in_years` etc) to check if the target date falls within a calendar window relative to the reference date. These methods use calendar units (not elapsed time) using half-open intervals. The start is inclusive, the end is exclusive. This makes it easy to check if a date is in a specific calendar range (e.g., last week, next month, fiscal quarter) using intuitive, unit-based logic.

- `in_days(-1)`: Is the target date yesterday?
- `in_days(-1, 1)`: Is the target date within ±1 calendar day of the reference?

`Cal(target_dt: datetime, ref_dt: datetime, fy_start_month: int = 1, holidays: set[str] = None)`

| Property         | Description                   |
| ---------------- | ----------------------------- |
| `dt_val`         | Target datetime               |
| `base_time`      | Reference datetime            |
| `fiscal_year`    | Fiscal year for `dt_val`      |
| `fiscal_quarter` | Fiscal quarter for `dt_val`   |
| `holiday`        | True if `dt_val` is a holiday |

| Interval Method                                    | Description                 |
| -------------------------------------------------- | --------------------------- |
| `in_minutes(start=0, end=None)`                    | Is target in minute window  |
| `in_hours(start=0, end=None)`                      | Is target in hour window    |
| `in_days(start=0, end=None)`                       | Is target in day window     |
| `in_weeks(start=0, end=None, week_start="monday")` | Is target in week window    |
| `in_months(start=0, end=None)`                     | Is target in month window   |
| `in_quarters(start=0, end=None)`                   | Is target in quarter window |
| `in_years(start=0, end=None)`                      | Is target in year window    |

---

### Biz Object

The `Biz` object performs business-aware calculations using a `CalendarPolicy`. It counts
working days (defined by the policy's workday set) and business days (working days that are not holidays).
It also computes fractional day contributions using the policy's business hours.

***Business days and work days are tricky to calculate an involve iteration because no/few assumptions can be made about the way the days fall. Normally this isn't a huge deal becase the time spans are a few days, not 1000's of days.***

`Biz(target_time: datetime, ref_time: datetime | None, policy: CalendarPolicy | None)`

| Property / Attribute | Description                                                         |
| -------------------- | ------------------------------------------------------------------- |
| `cal_policy`         | `CalendarPolicy` instance used by this Biz                          |
| `target_time`        | Target datetime                                                     |
| `ref_time`           | Reference datetime                                                  |
| `holiday`            | True if `target_time` is a holiday                                  |
| `is_workday`         | True if `target_time` falls on a workday                            |
| `is_business_day`    | True if `target_time` is a business day (workday and not holiday)   |
| `working_days`       | Fractional working days between target and ref (ignores holidays)   |
| `business_days`      | Fractional business days between target and ref (excludes holidays) |

| Method                                   | Description                                           |
| ---------------------------------------- | ----------------------------------------------------- |
| `in_working_days(start=0, end=0)`        | Range membership by working days (ignores holidays)   |
| `in_business_days(start=0, end=0)`       | Range membership by business days (excludes holidays) |
| `get_fiscal_year(dt, fy_start_month)`    | Static helper to compute fiscal year for a datetime   |
| `get_fiscal_quarter(dt, fy_start_month)` | Static helper to compute fiscal quarter               |

### Chrono Object

In some situations you will need to have all three of these classes together because the filtering you are doing is related
to the multiple classes.  The best way to handle this is with the chrono object.  The `Chrono` class initiaizlizes all three so you have access to each of the classes, with no race conditions when setting the reference time.

```pycon
# Brief Chrono example: create a Chrono and print Age / Cal / Biz properties
>>> from frist import Chrono, CalendarPolicy
>>> import datetime as dt
>>> target = dt.datetime(2025, 4, 25, 15, 0)
>>> ref = dt.datetime(2025, 4, 30, 12, 0)
>>> policy = CalendarPolicy(workdays={0,1,2,3,4}, holidays={"2025-04-28"})
>>> z = Chrono(target_time=target, reference_time=ref, policy=policy)

# Age (elapsed-time properties)
>>> z.age.days                # elapsed days (float)
3.875
>>> z.age.years_precise       # calendar-accurate years
0.0106

# Cal (calendar-window queries)
>>> z.cal.in_days(-5)         # was target 5 days before reference?
True
>>> z.cal.in_months(0)        # same calendar month as reference?
True

# Biz (policy-aware business logic — properties are floats)
>>> z.biz.working_days        # fractional working days (counts workdays per policy)
1.0
>>> z.biz.business_days       # fractional business days (excludes holidays from policy)
0.0
>>> z.biz.in_working_days(0)  # range-membership helper (bool)
True
>>> z.biz.in_business_days(0) # range-membership helper (bool)
False
```

`Chrono(target_time: datetime, reference_time: datetime = None, cal_policy:CalendarPolicy|None)`

| Property | Description                                           |
| -------- | ----------------------------------------------------- |
| `age`    | Age object for span calculations (see Age above)      |
| `cal`    | Cal object for calendar window logic (see Cal above)  |
| `biz`    | Biz  object for calendar window logic (see Cal above) |

### Status

[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue?logo=python&logoColor=white)](https://www.python.org/) [![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/hucker/frist/actions) [![Pytest](https://img.shields.io/badge/pytest-100%25%20pass%20%7C%20341%20tests-blue?logo=pytest&logoColor=white)](https://docs.pytest.org/en/stable/) [![Ruff](https://img.shields.io/badge/ruff-100%25-brightgreen?logo=ruff&logoColor=white)](https://github.com/charliermarsh/ruff) [![Tox](https://img.shields.io/badge/tox-tested%20%7C%20multi%20envs-green?logo=tox&logoColor=white)](https://tox.readthedocs.io/)

### Pytest

```text
src\frist\__init__.py                         8      0      0      0   100%
src\frist\_age.py                           149      0     46      0   100%
src\frist\_biz.py                           138      0     28      0   100%
src\frist\_cal.py                           114      0     20      0   100%
src\frist\_cal_policy.py                     79      0     38      0   100%
src\frist\_constants.py                      15      0      0      0   100%
src\frist\_frist.py                          71      0     18      0   100%
src\frist\_util.py                           12      0      4      0   100%
```

### Tox

```text
  py310: OK (15.17=setup[12.99]+cmd[2.18] seconds)
  py311: OK (10.57=setup[7.96]+cmd[2.61] seconds)
  py312: OK (11.98=setup[9.45]+cmd[2.53] seconds)
  py313: OK (10.74=setup[8.46]+cmd[2.29] seconds)
  py314: OK (11.04=setup[8.61]+cmd[2.43] seconds)
  congratulations :) (59.61 seconds)
```

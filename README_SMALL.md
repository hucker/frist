# Frist — Quick Start (5 minutes)

Frist removes user math from datetime work. It provides:
- Explicit windows you can read at a glance.
- Clear unit values (`val`/`name`) without conversions.
- Policy-aware business/working day logic with signed counts.

## Install

```bash
pip install frist
```

## 1) Ages — durations without math

Why: Answer “how old?” in seconds/minutes/hours/days/months/years with properties.

```python
from frist import Age
import datetime as dt

# Example span: Jan 1, 2025 00:00 -> Jan 4, 2025 12:00
age = Age(dt.datetime(2025, 1, 1), dt.datetime(2025, 1, 4, 12))

# Common properties
assert age.days == 3.5           # 3 days + 12 hours
assert age.hours == 84.0         # 3.5 * 24
assert age.minutes == 5040.0     # 84 * 60
assert age.seconds == 302_400.0  # 5040 * 60

# Calendar-aware options
assert age.weeks == 0.5 + 2.5/7  # illustrative (fractional weeks)
assert age.months_precise > 0    # uses actual month lengths
assert age.years_precise > 0     # uses actual year length
```

- Properties: `seconds`, `minutes`, `hours`, `days`, `weeks`, `months`, `years`.
- Calendar-accurate: `months_precise` and `years_precise` use real month/year lengths.
- Tip: omit the end-time to use “now”.

## 2) Windows — half-open ranges you can trust

Why: Ask “is target in this window relative to ref?” with start-inclusive/end-exclusive semantics.

```python
from frist import Cal
import datetime as dt

c = Cal(target_dt=dt.datetime(2025, 1, 2, 12), ref_dt=dt.datetime(2025, 1, 4, 12))
assert c.day.in_(-2, 0) is True  # Jan 2 within [Jan 2, Jan 4)

# Multiple time scales
assert c.second.in_(0) in (True, False)   # second-level window
assert c.minute.in_(0) in (True, False)   # minute-level window
assert c.hour.in_(0)   in (True, False)   # hour-level window
assert c.day.in_(0)    in (True, False)   # day-level window
assert c.week.in_(0)   in (True, False)   # week-level window
assert c.month.in_(0)  in (True, False)   # month-level window
assert c.quarter.in_(0) in (True, False)  # quarter-level window
assert c.year.in_(0)   in (True, False)   # year-level window

# Unit values and names (at target: 2025-01-02 12:00)
assert c.second.val == 0          # second is 00
assert c.minute.val == 0          # minute is 00
assert c.hour.val == 12           # hour is 12

assert c.day.val == 4             # ISO weekday: Thursday = 4
assert c.day.name == "Thursday"

assert c.month.val == 1           # January = 1
assert c.month.name == "January"

assert c.quarter.val == 1         # Q1
assert c.quarter.name == "Q1"

assert c.year.val == 2025
```

- Readable: `in_(start, end)` clearly states the range.
- Predictable: half-open prevents boundary overlap.
- Unit values: `cal.day.val` (ISO weekday 1..7), `cal.day.name` (e.g., "Thursday").

## 3) Business vs Working — signed fractional counts

Why: Get policy-aware fractional days with direction. Reverse order returns the negative.

```python
from frist import Biz, BizPolicy
import datetime as dt

pol = BizPolicy(holidays={"2025-01-03"})  # Thu holiday
fwd = Biz(dt.datetime(2025, 1, 1, 12), dt.datetime(2025, 1, 4, 15), pol)
assert round(fwd.working_days, 3) == round(0.625 + 1.0 + 1.0 + 0.75, 3)
assert round(fwd.business_days, 3) == round(0.625 + 1.0 + 0.0 + 0.75, 3)

rev = Biz(dt.datetime(2025, 1, 4, 15), dt.datetime(2025, 1, 1, 12), pol)
assert rev.business_days == -fwd.business_days
assert rev.working_days == -fwd.working_days
```

- Signed: positive if `target <= ref`, negative if `target > ref`.
- Holidays: contribute `0.0` to `business_days`; `working_days` counts weekday fractions.
- Shortcuts: `is_today` only; use `in_(-1, 0)` or `in_(1, 2)` for yesterday/tomorrow.

## Common Inputs (TimeLike)

- Accepts: `datetime`, `date`, `int/float` timestamps, and ISO strings.
- Naive datetimes: no timezone handling (keep both values in the same zone).
- Hint: fractional seconds on timestamps are handled as microseconds.

## Recap — what to remember

- Windows: `in_(start, end)` are half-open and unit-aligned.
- Units: `val`/`name` give you readable values for the target.
- Business/Working: signed fractional days; reversing order flips the sign.
- Holidays: affect `business_days` only.

## Learn More

- See `README.md` for deeper examples, design notes, comparisons, and API details.

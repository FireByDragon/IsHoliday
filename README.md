# IsHoliday

**Define the rule once. Calculate holidays forever.**

IsHoliday is a rule-based holiday engine for Python. Holidays are defined as human-readable rules in TOML configuration files — not hardcoded in Python classes, not stored in year-by-year lookup tables, and not dependent on third-party packages. Define "Christmas is December 25th" or "Thanksgiving is the 4th Thursday in November" once, and IsHoliday computes the correct observed date for any year — past, present, or future — with zero maintenance.

```python
from datetime import date
from isholiday import is_holiday, get_holiday, is_business_day

is_holiday(date(2025, 12, 25))      # True
get_holiday(date(2025, 12, 25))     # "Christmas Day"
is_business_day(date(2025, 12, 25)) # False

is_holiday(date(2050, 12, 25))      # True — no tables to update
```

## Installation

```bash
pip install holiday-engine
```

Python 3.11+ required. Zero external dependencies — pure stdlib.

---

## How It Works

IsHoliday's core architecture separates **data** from **computation** from **API**:

```
TOML Calendar File          →  Rule Engine (calendar.py)  →  Public API (__init__.py)
 ├─ Holiday definitions          ├─ DOM: fixed-date math        ├─ is_holiday()
 ├─ Rule types (DOM/NOW)         ├─ NOW: nth-weekday math       ├─ get_holiday()
 └─ Observed-date flags          ├─ Observed-date shifting      ├─ get_holidays()
                                 └─ Boundary-month handling     └─ is_business_day()
```

### The Two Rule Types

Every holiday in any calendar reduces to one of two rule types:

**DOM (Day of Month)** — A fixed calendar date that occurs on the same month and day every year. The engine constructs `date(year, month, day)` and applies observed-date shifting when the date falls on a weekend.

```
Christmas Day  →  DOM  →  month=12, day=25
Independence Day  →  DOM  →  month=7, day=4
```

**NOW (Nth Weekday of Month)** — A relative date defined as the Nth occurrence of a specific weekday within a month. The engine starts at the 1st of the month, calculates the offset to the target weekday, then advances by `(N-1) × 7` days. A special sentinel value (`week=10`) means "last occurrence," which the engine resolves by walking backward from month-end.

```
Thanksgiving  →  NOW  →  4th Thursday in November
Memorial Day  →  NOW  →  Last Monday in May (week=10)
Labor Day     →  NOW  →  1st Monday in September
```

### Observed-Date Shifting

When a fixed-date holiday lands on a weekend, federal and market conventions shift the observed date to the nearest weekday. IsHoliday makes this configurable per holiday:

- `saturday_to_friday = true` — Saturday holidays shift to the preceding Friday
- `sunday_to_monday = true` — Sunday holidays shift to the following Monday

This correctly handles edge cases like New Year's Day 2028 (Saturday), which shifts its observed date to **December 31, 2027** — across a year boundary. The engine checks adjacent years automatically.

### Caching

TOML files are parsed once and cached for the lifetime of the process. Subsequent calls to any API function incur only lightweight date arithmetic — no file I/O, no network calls, no database queries.

---

## How IsHoliday Compares

| Feature | **IsHoliday** | `holidays` (vacanza) | `workalendar` | `business_calendar` |
|---|---|---|---|---|
| **Configuration** | TOML files (human-editable) | Python class subclassing | Python class inheritance | Hardcoded date lists |
| **Custom calendars** | Drop in a `.toml` file | Write a Python class | Subclass + override methods | Pass date strings |
| **Dependencies** | None (pure stdlib) | `python-dateutil` | `python-dateutil`, `lunardate`, `convertdate` | None |
| **Who can edit calendars** | Anyone (config file) | Python developers only | Python developers only | Python developers only |
| **Country coverage** | US, UK, Canada, Japan | 249 country codes | ~80 countries | None built-in |
| **API surface** | 4 functions | Dict-like class interface | Class methods | Class methods |
| **Python requirement** | 3.11+ | 3.10+ | 3.7+ | 2.7+ |

### When to use IsHoliday

IsHoliday is designed for teams that need **configurable, maintainable holiday logic** without writing Python code to define or modify calendars. Its sweet spot is:

- Applications where **non-developers** (operations, HR, compliance) need to manage holiday calendars
- Projects that require **multiple calendar types** (banking, market, company, regional) switchable at runtime
- Environments where **zero dependencies** matters (containers, embedded, air-gapped systems)
- Codebases where **simplicity** is valued — 4 functions, one import, no classes to instantiate

### When to use something else

If you need holiday data for **dozens of countries** out of the box, [`holidays`](https://pypi.org/project/holidays/) (vacanza) covers 249 country codes with active maintenance. If you need **business-day arithmetic** (add N working days, count business days between dates), [`workalendar`](https://pypi.org/project/workalendar/) includes that functionality natively.

---

## Use Cases

### Financial Services — Stock Market

Determine whether the NYSE or NASDAQ is open on a given date. The built-in `"market"` calendar covers all 9 exchange holidays. Integrate with trading systems, portfolio dashboards, or automated order schedulers.

```python
from datetime import date
from isholiday import is_business_day, get_holiday

# Is the market open today?
if not is_business_day(date.today(), calendar="market"):
    holiday = get_holiday(date.today(), calendar="market")
    if holiday:
        print(f"Market closed — {holiday}")
    else:
        print("Market closed — weekend")

# Count trading days in a date range
from datetime import timedelta
start = date(2025, 1, 1)
trading_days = sum(
    1 for i in range(365)
    if is_business_day(start + timedelta(days=i), calendar="market")
)
print(f"Trading days in 2025: {trading_days}")  # 251
```

### Financial Services — Banking

Determine settlement dates, ACH processing windows, and wire transfer availability. The built-in `"banking"` calendar includes all 11 Federal Reserve holidays — two more than the market calendar (Columbus Day and Veterans Day).

```python
from datetime import date, timedelta
from isholiday import is_business_day

def next_settlement_date(from_date: date) -> date:
    """Find the next valid banking settlement date (T+1)."""
    candidate = from_date + timedelta(days=1)
    while not is_business_day(candidate, calendar="banking"):
        candidate += timedelta(days=1)
    return candidate

# Trade on Friday before a Monday holiday
trade_date = date(2025, 5, 23)    # Friday before Memorial Day
settlement = next_settlement_date(trade_date)
print(f"Settlement: {settlement}")  # 2025-05-27 (Tuesday — skips weekend + holiday)
```

### Human Resources — Payroll and PTO

Build a company holiday calendar that HR can maintain without developer involvement. Define company-specific holidays (floating holidays, office closures) alongside federal holidays in a single TOML file.

```toml
# company_holidays.toml
[calendar]
name        = "acme-corp"
description = "ACME Corporation holiday calendar"

[types]
DOM = "Calendar Day of Month"
NOW = "Nth Weekday of Month"

[[holidays]]
name               = "New Year's Day"
type               = "DOM"
month              = 1
day                = 1
saturday_to_friday = true
sunday_to_monday   = true
year_added         = 2020
enabled            = true

[[holidays]]
name               = "Company Founder's Day"
type               = "DOM"
month              = 3
day                = 15
saturday_to_friday = true
sunday_to_monday   = true
year_added         = 2020
enabled            = true

[[holidays]]
name               = "Day After Thanksgiving"
type               = "NOW"
month              = 11
week               = 4
weekday            = 6          # Friday (day after 4th Thursday)
saturday_to_friday = false
sunday_to_monday   = false
year_added         = 2020
enabled            = true
```

```python
from isholiday import get_holidays

# HR can update the TOML file — no code changes needed
for holiday_date, name in get_holidays(2025, calendar="company_holidays.toml"):
    print(f"  {holiday_date}  {name}")
```

### Accounting — Fiscal Calendars and Reporting Deadlines

Calculate business days for invoice due dates, reporting deadlines, and fiscal period boundaries. Ensure financial close processes account for holidays.

```python
from datetime import date, timedelta
from isholiday import is_business_day

def add_business_days(start: date, days: int, calendar: str = "banking") -> date:
    """Add N business days to a start date, skipping weekends and holidays."""
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if is_business_day(current, calendar=calendar):
            added += 1
    return current

# Net-30 invoice due date (30 business days, not calendar days)
invoice_date = date(2025, 11, 1)
due_date = add_business_days(invoice_date, 30, calendar="banking")
print(f"Invoice due: {due_date}")  # Skips Thanksgiving, Veterans Day, weekends

# Quarterly close — last business day of Q4
from isholiday import is_holiday
q4_end = date(2025, 12, 31)
while not is_business_day(q4_end, calendar="banking"):
    q4_end -= timedelta(days=1)
print(f"Q4 close date: {q4_end}")
```

### Education — School Calendars

Define academic calendar holidays in a TOML file that school administrators can update each year. Track instructional days, plan around breaks, and generate academic calendars.

```toml
# school_holidays.toml
[calendar]
name        = "lincoln-elementary"
description = "Lincoln Elementary 2025-2026 academic calendar"

[types]
DOM = "Calendar Day of Month"
NOW = "Nth Weekday of Month"

[[holidays]]
name               = "Thanksgiving Break"
type               = "NOW"
month              = 11
week               = 4
weekday            = 5          # Thursday
saturday_to_friday = false
sunday_to_monday   = false
year_added         = 2025
enabled            = true

[[holidays]]
name               = "Winter Break Start"
type               = "DOM"
month              = 12
day                = 22
saturday_to_friday = false
sunday_to_monday   = false
year_added         = 2025
enabled            = true

[[holidays]]
name               = "Martin Luther King Jr. Day"
type               = "NOW"
month              = 1
week               = 3
weekday            = 2
saturday_to_friday = false
sunday_to_monday   = false
year_added         = 2025
enabled            = true
```

```python
from datetime import date, timedelta
from isholiday import is_business_day

# Count instructional days in a semester
semester_start = date(2025, 8, 25)
semester_end = date(2025, 12, 19)
instructional_days = sum(
    1 for i in range((semester_end - semester_start).days + 1)
    if is_business_day(semester_start + timedelta(days=i),
                       calendar="school_holidays.toml")
)
print(f"Instructional days: {instructional_days}")
```

---

## Built-in Calendars

### Market Calendar (default) — 9 Holidays

The NYSE and NASDAQ observe these holidays. The exchanges are **closed** on these dates:

| Holiday | Rule | Observed Shift |
|---------|------|----------------|
| New Year's Day | January 1 | Sat→Fri, Sun→Mon |
| Martin Luther King Jr. Day | 3rd Monday in January | — |
| Presidents' Day | 3rd Monday in February | — |
| Memorial Day | Last Monday in May | — |
| Juneteenth | June 19 | Sat→Fri, Sun→Mon |
| Independence Day | July 4 | Sat→Fri, Sun→Mon |
| Labor Day | 1st Monday in September | — |
| Thanksgiving Day | 4th Thursday in November | — |
| Christmas Day | December 25 | Sat→Fri, Sun→Mon |

### Banking Calendar — 11 Holidays

All market holidays plus:

| Holiday | Rule | Observed Shift |
|---------|------|----------------|
| Columbus Day | 2nd Monday in October | — |
| Veterans Day | November 11 | Sat→Fri, Sun→Mon |

```python
# Columbus Day: banks closed, markets open
from datetime import date
from isholiday import is_holiday

is_holiday(date(2025, 10, 13), calendar="banking")   # True
is_holiday(date(2025, 10, 13), calendar="market")    # False
```

### United Kingdom Calendar — 6 Holidays

England and Wales bank holidays under the Banking and Financial Dealings Act 1971. Covers all holidays that fit the DOM/NOW rule pattern. Easter-dependent holidays (Good Friday, Easter Monday) require a future `EASTER` rule type.

| Holiday | Rule | Observed Shift |
|---------|------|----------------|
| New Year's Day | January 1 | Sun→Mon |
| Early May Bank Holiday | 1st Monday in May | — |
| Spring Bank Holiday | Last Monday in May | — |
| Summer Bank Holiday | Last Monday in August | — |
| Christmas Day | December 25 | Sun→Mon |
| Boxing Day | December 26 | Sun→Mon |

```python
from datetime import date
from isholiday import get_holidays

for holiday_date, name in get_holidays(2025, calendar="uk"):
    print(f"  {holiday_date}  {name}")
```

### Canada Calendar — 9 Holidays

Federal statutory holidays under the Canada Labour Code. Excludes Easter-dependent holidays and Victoria Day (which uses a "Monday on or before May 24" rule not yet supported). Provincial holidays vary — create province-specific TOML files for full coverage.

| Holiday | Rule | Observed Shift |
|---------|------|----------------|
| New Year's Day | January 1 | Sun→Mon |
| Family Day | 3rd Monday in February | — |
| Canada Day | July 1 | Sun→Mon |
| Labour Day | 1st Monday in September | — |
| National Day for Truth and Reconciliation | September 30 | Sun→Mon |
| Thanksgiving Day | 2nd Monday in October | — |
| Remembrance Day | November 11 | Sun→Mon |
| Christmas Day | December 25 | Sun→Mon |
| Boxing Day | December 26 | Sun→Mon |

```python
from datetime import date
from isholiday import is_holiday

# Canadian Thanksgiving is the 2nd Monday in October (not the 4th Thursday)
is_holiday(date(2025, 10, 13), calendar="canada")    # True  — Thanksgiving
is_holiday(date(2025, 11, 27), calendar="canada")    # False — US Thanksgiving
```

### Japan Calendar — 14 Holidays

National holidays defined by Japan's Act on National Holidays (国民の祝日に関する法律). Covers 14 of 16 holidays — excludes Vernal Equinox Day and Autumnal Equinox Day, which require astronomical calculation. Japan uses the *furikae kyūjitsu* (振替休日) substitute holiday system: Sunday holidays shift to the following Monday.

| Holiday | Rule | Observed Shift |
|---------|------|----------------|
| New Year's Day (元日) | January 1 | Sun→Mon |
| Coming of Age Day (成人の日) | 2nd Monday in January | — |
| National Foundation Day (建国記念の日) | February 11 | Sun→Mon |
| Emperor's Birthday (天皇誕生日) | February 23 | Sun→Mon |
| Shōwa Day (昭和の日) | April 29 | Sun→Mon |
| Constitution Memorial Day (憲法記念日) | May 3 | Sun→Mon |
| Greenery Day (みどりの日) | May 4 | Sun→Mon |
| Children's Day (こどもの日) | May 5 | Sun→Mon |
| Marine Day (海の日) | 3rd Monday in July | — |
| Mountain Day (山の日) | August 11 | Sun→Mon |
| Respect for the Aged Day (敬老の日) | 3rd Monday in September | — |
| Sports Day (スポーツの日) | 2nd Monday in October | — |
| Culture Day (文化の日) | November 3 | Sun→Mon |
| Labour Thanksgiving Day (勤労感謝の日) | November 23 | Sun→Mon |

```python
from datetime import date
from isholiday import get_holiday

# Golden Week
get_holiday(date(2025, 5, 3), calendar="japan")   # "Constitution Memorial Day (憲法記念日)"
get_holiday(date(2025, 5, 5), calendar="japan")   # "Children's Day (こどもの日)"

# Marine Day — 3rd Monday in July
get_holiday(date(2025, 7, 21), calendar="japan")  # "Marine Day (海の日)"
```

---

## International Coverage Analysis

IsHoliday's DOM/NOW rule engine covers a significant percentage of holidays worldwide. The two rule types handle any holiday that falls on either a fixed calendar date or an nth weekday of a month — which accounts for the majority of secular and civic holidays across countries.

| Pattern | Coverage | Examples |
|---------|----------|----------|
| **DOM** (fixed date) | ~40% of world holidays | New Year's, Christmas, national independence days, fixed civic holidays |
| **NOW** (nth weekday) | ~20–30% of world holidays | Thanksgiving variants, bank holidays, labour days, memorial days |
| **Easter-dependent** | ~15–20% | Good Friday, Easter Monday, Ascension, Whit Monday (future `EASTER` rule type) |
| **Astronomical / lunar** | ~10–15% | Chinese New Year, Eid, Diwali, equinox days (require lookup tables) |

The built-in UK, Canada, and Japan calendars demonstrate that most holidays in developed economies fit the DOM/NOW pattern. Countries with primarily fixed-date and nth-weekday holidays — including Australia, Germany, France, the Netherlands, and most of the Americas — can be fully modeled with custom TOML files today.

---

## Custom Calendars

Create a TOML file with your holiday definitions and pass the file path to any API function:

```python
from isholiday import is_holiday, get_holidays

is_holiday(date(2025, 3, 15), calendar="./my_holidays.toml")
get_holidays(2025, calendar="/etc/company/holidays.toml")
```

### TOML Structure

```toml
[calendar]
name        = "my-calendar"
description = "Description of this calendar"

[types]
DOM = "Calendar Day of Month"
NOW = "Nth Weekday of Month"

[[holidays]]
name               = "Holiday Name"
type               = "DOM"          # or "NOW"
month              = 1              # 1-12
day                = 1              # DOM only: day of month
week               = 0              # NOW only: occurrence (1-5, or 10 for last)
weekday            = 0              # NOW only: 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri, 7=Sat
saturday_to_friday = true           # shift Saturday holidays to Friday
sunday_to_monday   = true           # shift Sunday holidays to Monday
year_added         = 1900           # holiday is active starting this year
enabled            = true           # set false to disable without deleting
```

The `enabled` flag lets you temporarily disable a holiday without removing it from the file — useful for one-time schedule changes or phased rollouts.

---

## API Reference

### `is_holiday(target_date, calendar="market") -> bool`

Returns `True` if the date is a holiday on the specified calendar.

### `get_holiday(target_date, calendar="market") -> Optional[str]`

Returns the holiday name if the date is a holiday, or `None`.

### `get_holidays(year, calendar="market") -> list[tuple[date, str]]`

Returns all `(date, name)` pairs for the given year, sorted chronologically. Includes boundary-shifted holidays (e.g., New Year's 2028 observed on Dec 31, 2027 appears in the 2027 results).

### `is_business_day(target_date, calendar="market") -> bool`

Returns `True` if the date is a weekday (Monday–Friday) **and** not a holiday on the specified calendar.

All four functions accept `calendar` as:
- `"market"` — NYSE/NASDAQ holidays (default)
- `"banking"` — Federal Reserve banking holidays
- `"uk"` — United Kingdom bank holidays (England & Wales)
- `"canada"` — Canada federal statutory holidays
- `"japan"` — Japan national holidays (国民の祝日)
- A file path — any custom TOML calendar file

---

## Requirements

- **Python 3.11+** (uses `tomllib` from the standard library)
- **Zero external dependencies** — no `pip install` chain, no version conflicts
- **No network access required** — works offline, in CI/CD, in air-gapped environments

## Unicode Support

Holiday names support the full Unicode character set — including CJK ideographs, accented Latin characters, Arabic script, and any other UTF-8 encoded text. The TOML specification mandates UTF-8, and Python 3's `tomllib` parser enforces it. Holiday names are stored and returned exactly as written in the TOML file.

```python
from isholiday import get_holiday
from datetime import date

get_holiday(date(2025, 7, 21), calendar="japan")   # "Marine Day (海の日)"
get_holiday(date(2025, 10, 13), calendar="japan")   # "Sports Day (スポーツの日)"
```

This means custom calendars can use native-language holiday names without any additional configuration:

```toml
[[holidays]]
name = "Día de la Independencia"    # Spanish — México
type = "DOM"
month = 9
day = 16
# ...

[[holidays]]
name = "Fête nationale (Saint-Jean-Baptiste)"   # French — Québec
type = "DOM"
month = 6
day = 24
# ...

[[holidays]]
name = "Tag der Deutschen Einheit"   # German — Germany
type = "DOM"
month = 10
day = 3
# ...
```

No encoding flags, no locale settings, no special imports — UTF-8 throughout the entire pipeline.

## License

MIT — see [LICENSE](LICENSE) for details.

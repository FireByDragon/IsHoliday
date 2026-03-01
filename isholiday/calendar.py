"""
Holiday calendar engine.

Loads holiday definitions from TOML files, computes actual and observed
dates for each holiday, and provides lookup functions used by the public API.

Supports four holiday types:
  DOM    — Calendar Day of Month (fixed date like January 1st)
  NOW    — Nth Weekday of Month (relative date like 3rd Monday in January)
  EASTER — Offset from Easter Sunday (e.g., Good Friday = Easter − 2)
  BEFORE — Weekday on or before a date (e.g., Victoria Day = Monday ≤ May 24)

Weekday values in TOML use the SQL Server convention:
  1=Sunday, 2=Monday, 3=Tuesday, 4=Wednesday, 5=Thursday, 6=Friday, 7=Saturday

All functions are pure — no I/O, no side effects beyond module-level caching.
"""

import calendar as cal
import importlib.resources
import tomllib
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class HolidayDefinition:
    """A single holiday rule parsed from a TOML calendar file."""

    name: str
    holiday_type: str           # "DOM", "NOW", "EASTER", or "BEFORE"
    month: int
    day: int                    # DOM: calendar day; BEFORE: anchor day; others: 0
    week: int                   # NOW: occurrence (1–5, or 10 = last); others: 0
    weekday_sql: int            # NOW/BEFORE: SQL weekday (1=Sun..7=Sat); others: 0
    saturday_to_friday: bool
    sunday_to_monday: bool
    year_added: int
    enabled: bool
    offset: int                 # EASTER: days from Easter Sunday (e.g., -2, +1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# SQL Server DATEPART(WEEKDAY) → Python isoweekday (1=Mon..7=Sun)
_SQL_TO_ISO = {1: 7, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}

# Built-in calendar short names → data file names
_BUILTIN_CALENDARS = {
    "banking": "holidays_banking.toml",
    "market":  "holidays_market.toml",
    "uk":      "holidays_uk.toml",
    "canada":  "holidays_canada.toml",
    "japan":   "holidays_japan.toml",
}

# Module-level cache: calendar_key → list[HolidayDefinition]
_calendar_cache: dict[str, list[HolidayDefinition]] = {}


# ---------------------------------------------------------------------------
# TOML loading
# ---------------------------------------------------------------------------

def _load_builtin_toml(filename: str) -> dict:
    """Read a TOML file bundled inside isholiday/data/."""
    ref = importlib.resources.files("isholiday.data") / filename
    with ref.open("rb") as file_handle:
        return tomllib.load(file_handle)


def _load_external_toml(path: Path) -> dict:
    """Read a user-supplied TOML calendar file from disk."""
    if not path.exists():
        raise FileNotFoundError(f"Calendar file not found: {path}")
    with open(path, "rb") as file_handle:
        return tomllib.load(file_handle)


def _parse_holiday_entry(entry: dict) -> HolidayDefinition:
    """Convert a single [[holidays]] TOML table into a HolidayDefinition."""
    return HolidayDefinition(
        name=entry["name"],
        holiday_type=entry["type"],
        month=entry.get("month", 0),
        day=entry.get("day", 0),
        week=entry.get("week", 0),
        weekday_sql=entry.get("weekday", 0),
        saturday_to_friday=entry.get("saturday_to_friday", False),
        sunday_to_monday=entry.get("sunday_to_monday", False),
        year_added=entry.get("year_added", 0),
        enabled=entry.get("enabled", True),
        offset=entry.get("offset", 0),
    )


def load_calendar(calendar: str) -> list[HolidayDefinition]:
    """Load holiday definitions for a named or file-path calendar.

    Parameters
    ----------
    calendar : str
        ``"banking"``, ``"market"``, or an absolute/relative file path
        to a custom TOML calendar file.

    Returns
    -------
    list[HolidayDefinition]
        Enabled holiday definitions, cached after first load.
    """
    if calendar in _calendar_cache:
        return _calendar_cache[calendar]

    if calendar in _BUILTIN_CALENDARS:
        parsed = _load_builtin_toml(_BUILTIN_CALENDARS[calendar])
    else:
        parsed = _load_external_toml(Path(calendar))

    definitions = [
        _parse_holiday_entry(entry)
        for entry in parsed.get("holidays", [])
        if entry.get("enabled", True)
    ]

    _calendar_cache[calendar] = definitions
    return definitions


# ---------------------------------------------------------------------------
# Date computation — DOM (fixed calendar day)
# ---------------------------------------------------------------------------

def _compute_fixed_date(year: int, month: int, day: int) -> date:
    """Build a date from year, month, and day of month."""
    return date(year, month, day)


# ---------------------------------------------------------------------------
# Date computation — NOW (nth weekday of month)
# ---------------------------------------------------------------------------

def _compute_nth_weekday(year: int, month: int, week: int, weekday_sql: int) -> date:
    """Find the nth occurrence of a weekday in a given month.

    Replicates the SQL Server ``IsBankingHoliday`` cursor logic:
      1. Start at the 1st of the month.
      2. Calculate the offset to the first occurrence of the target weekday.
      3. Jump forward by ``(week - 1) * 7`` days.
      4. If the result exceeds the month, walk back by 7 until it fits.

    The ``week = 10`` sentinel means *last occurrence* of that weekday in the
    month (e.g., Memorial Day = last Monday in May).

    Parameters
    ----------
    year : int
    month : int
    week : int
        Occurrence number (1–5), or 10 for "last".
    weekday_sql : int
        Target weekday in SQL convention (1=Sun, 2=Mon, ..., 7=Sat).

    Returns
    -------
    date
    """
    target_iso = _SQL_TO_ISO[weekday_sql]
    first_of_month = date(year, month, 1)
    first_iso = first_of_month.isoweekday()

    days_to_first_occurrence = (target_iso - first_iso) % 7
    day_of_month = 1 + days_to_first_occurrence + (week - 1) * 7

    _, last_day = cal.monthrange(year, month)
    while day_of_month > last_day:
        day_of_month -= 7

    return date(year, month, day_of_month)


# ---------------------------------------------------------------------------
# Date computation — EASTER (offset from Easter Sunday)
# ---------------------------------------------------------------------------

def _compute_easter_sunday(year: int) -> date:
    """Compute Easter Sunday for a given year.

    Uses the Anonymous Gregorian algorithm (Meeus/Jones/Butcher), valid for
    any year in the Gregorian calendar.  Easter Sunday always falls between
    March 22 and April 25.

    Parameters
    ----------
    year : int

    Returns
    -------
    date
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    el = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * el) // 451
    month = (h + el - 7 * m + 114) // 31
    day = ((h + el - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _compute_easter_offset(year: int, offset: int) -> date:
    """Compute a date relative to Easter Sunday.

    Parameters
    ----------
    year : int
    offset : int
        Days from Easter Sunday (e.g., -2 for Good Friday, +1 for Easter Monday).

    Returns
    -------
    date
    """
    return _compute_easter_sunday(year) + timedelta(days=offset)


# ---------------------------------------------------------------------------
# Date computation — BEFORE (weekday on or before a date)
# ---------------------------------------------------------------------------

def _compute_weekday_on_or_before(
    year: int, month: int, day: int, weekday_sql: int,
) -> date:
    """Find the target weekday on or before the given anchor date.

    For example, Victoria Day = Monday on or before May 24:
    ``_compute_weekday_on_or_before(2025, 5, 24, 2)`` → May 19 (Monday).

    Parameters
    ----------
    year : int
    month : int
    day : int
        Anchor day of month (inclusive upper bound).
    weekday_sql : int
        Target weekday in SQL convention (1=Sun, 2=Mon, ..., 7=Sat).

    Returns
    -------
    date
    """
    target_iso = _SQL_TO_ISO[weekday_sql]
    anchor = date(year, month, day)
    days_back = (anchor.isoweekday() - target_iso) % 7
    return anchor - timedelta(days=days_back)


# ---------------------------------------------------------------------------
# Actual → observed date shifting
# ---------------------------------------------------------------------------

def _apply_observed_shift(actual_date: date, definition: HolidayDefinition) -> date:
    """Shift a holiday's actual date to its observed date.

    If the actual date falls on Saturday and ``saturday_to_friday`` is set,
    the observed date moves to the preceding Friday.

    If the actual date falls on Sunday and ``sunday_to_monday`` is set,
    the observed date moves to the following Monday.

    Parameters
    ----------
    actual_date : date
    definition : HolidayDefinition

    Returns
    -------
    date
        The observed (possibly shifted) date.
    """
    iso_weekday = actual_date.isoweekday()

    if iso_weekday == 6 and definition.saturday_to_friday:
        return actual_date - timedelta(days=1)

    if iso_weekday == 7 and definition.sunday_to_monday:
        return actual_date + timedelta(days=1)

    return actual_date


# ---------------------------------------------------------------------------
# Single-holiday date resolution
# ---------------------------------------------------------------------------

def _resolve_holiday_date(definition: HolidayDefinition, year: int) -> Optional[date]:
    """Compute the observed date for a holiday definition in a given year.

    Returns ``None`` if the holiday was not yet enacted (``year < year_added``).
    """
    if year < definition.year_added:
        return None

    if definition.holiday_type == "DOM":
        actual = _compute_fixed_date(year, definition.month, definition.day)
    elif definition.holiday_type == "NOW":
        actual = _compute_nth_weekday(
            year, definition.month, definition.week, definition.weekday_sql,
        )
    elif definition.holiday_type == "EASTER":
        actual = _compute_easter_offset(year, definition.offset)
    elif definition.holiday_type == "BEFORE":
        actual = _compute_weekday_on_or_before(
            year, definition.month, definition.day, definition.weekday_sql,
        )
    else:
        return None

    return _apply_observed_shift(actual, definition)


# ---------------------------------------------------------------------------
# Public engine functions (called by __init__.py)
# ---------------------------------------------------------------------------

def lookup_holiday(target_date: date, calendar: str) -> Optional[str]:
    """Check whether *target_date* is a holiday on the given calendar.

    Handles year-boundary edge cases:
      - A December holiday whose observed date shifts into January.
      - A January holiday whose observed date shifts back into December.

    Returns the holiday name, or ``None`` if the date is not a holiday.
    """
    definitions = load_calendar(calendar)

    for definition in definitions:
        # Same-year check
        observed = _resolve_holiday_date(definition, target_date.year)
        if observed == target_date:
            return definition.name

        # Boundary: previous year's December → this year's January
        if target_date.month == 1 and definition.month == 12:
            observed = _resolve_holiday_date(definition, target_date.year - 1)
            if observed == target_date:
                return definition.name

        # Boundary: next year's January → this year's December
        if target_date.month == 12 and definition.month == 1:
            observed = _resolve_holiday_date(definition, target_date.year + 1)
            if observed == target_date:
                return definition.name

    return None


def holidays_for_year(year: int, calendar: str) -> list[tuple[date, str]]:
    """Compute all observed holiday dates for a given year, sorted by date.

    Includes boundary-month holidays that shift into or out of the year.
    """
    definitions = load_calendar(calendar)
    results: list[tuple[date, str]] = []

    for definition in definitions:
        # Holidays defined in this year
        observed = _resolve_holiday_date(definition, year)
        if observed is not None and observed.year == year:
            results.append((observed, definition.name))

        # Previous year's December holidays that shift into January of this year
        if definition.month == 12:
            observed = _resolve_holiday_date(definition, year - 1)
            if observed is not None and observed.year == year:
                results.append((observed, definition.name))

        # Next year's January holidays that shift back into December of this year
        if definition.month == 1:
            observed = _resolve_holiday_date(definition, year + 1)
            if observed is not None and observed.year == year:
                results.append((observed, definition.name))

    results.sort(key=lambda pair: pair[0])
    return results

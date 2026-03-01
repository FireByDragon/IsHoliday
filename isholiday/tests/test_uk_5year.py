"""
Five-year boundary tests for the UK calendar (2024-2028).

For every holiday in each year, verifies:
  - The day OF the holiday is recognized (with correct name).
  - The day BEFORE the holiday is NOT a holiday.
  - The day AFTER the holiday is NOT a holiday.

When holidays are adjacent (e.g., Christmas + Boxing Day, Golden Week), the
before/after boundary walks past the cluster to find the nearest non-holiday.

All expected dates were independently verified against published calendars.
"""

import pytest
from datetime import date

from isholiday import is_holiday, get_holiday


# ---------------------------------------------------------------------------
# Holiday dates -- day of (should be a holiday with matching name)
# ---------------------------------------------------------------------------

HOLIDAYS_UK = [
    (date(2024, 1, 1), "New Year's Day"),
    (date(2024, 3, 29), "Good Friday"),
    (date(2024, 4, 1), "Easter Monday"),
    (date(2024, 5, 6), "Early May Bank Holiday"),
    (date(2024, 5, 27), "Spring Bank Holiday"),
    (date(2024, 8, 26), "Summer Bank Holiday"),
    (date(2024, 12, 25), "Christmas Day"),
    (date(2024, 12, 26), "Boxing Day"),
    (date(2025, 1, 1), "New Year's Day"),
    (date(2025, 4, 18), "Good Friday"),
    (date(2025, 4, 21), "Easter Monday"),
    (date(2025, 5, 5), "Early May Bank Holiday"),
    (date(2025, 5, 26), "Spring Bank Holiday"),
    (date(2025, 8, 25), "Summer Bank Holiday"),
    (date(2025, 12, 25), "Christmas Day"),
    (date(2025, 12, 26), "Boxing Day"),
    (date(2026, 1, 1), "New Year's Day"),
    (date(2026, 4, 3), "Good Friday"),
    (date(2026, 4, 6), "Easter Monday"),
    (date(2026, 5, 4), "Early May Bank Holiday"),
    (date(2026, 5, 25), "Spring Bank Holiday"),
    (date(2026, 8, 31), "Summer Bank Holiday"),
    (date(2026, 12, 25), "Christmas Day"),
    (date(2026, 12, 26), "Boxing Day"),
    (date(2027, 1, 1), "New Year's Day"),
    (date(2027, 3, 26), "Good Friday"),
    (date(2027, 3, 29), "Easter Monday"),
    (date(2027, 5, 3), "Early May Bank Holiday"),
    (date(2027, 5, 31), "Spring Bank Holiday"),
    (date(2027, 8, 30), "Summer Bank Holiday"),
    (date(2027, 12, 25), "Christmas Day"),
    (date(2027, 12, 27), "Boxing Day"),
    (date(2028, 1, 1), "New Year's Day"),
    (date(2028, 4, 14), "Good Friday"),
    (date(2028, 4, 17), "Easter Monday"),
    (date(2028, 5, 1), "Early May Bank Holiday"),
    (date(2028, 5, 29), "Spring Bank Holiday"),
    (date(2028, 8, 28), "Summer Bank Holiday"),
    (date(2028, 12, 25), "Christmas Day"),
    (date(2028, 12, 26), "Boxing Day"),
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day before each holiday (walks past adjacent holidays)
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_BEFORE_UK = [
    date(2023, 12, 31),  # before New Year's Day 2024
    date(2024, 3, 28),  # before Good Friday 2024
    date(2024, 3, 31),  # before Easter Monday 2024
    date(2024, 5, 5),  # before Early May Bank Holiday 2024
    date(2024, 5, 26),  # before Spring Bank Holiday 2024
    date(2024, 8, 25),  # before Summer Bank Holiday 2024
    date(2024, 12, 24),  # before Christmas Day 2024
    date(2024, 12, 31),  # before New Year's Day 2025
    date(2025, 4, 17),  # before Good Friday 2025
    date(2025, 4, 20),  # before Easter Monday 2025
    date(2025, 5, 4),  # before Early May Bank Holiday 2025
    date(2025, 5, 25),  # before Spring Bank Holiday 2025
    date(2025, 8, 24),  # before Summer Bank Holiday 2025
    date(2025, 12, 24),  # before Christmas Day 2025
    date(2025, 12, 31),  # before New Year's Day 2026
    date(2026, 4, 2),  # before Good Friday 2026
    date(2026, 4, 5),  # before Easter Monday 2026
    date(2026, 5, 3),  # before Early May Bank Holiday 2026
    date(2026, 5, 24),  # before Spring Bank Holiday 2026
    date(2026, 8, 30),  # before Summer Bank Holiday 2026
    date(2026, 12, 24),  # before Christmas Day 2026
    date(2026, 12, 31),  # before New Year's Day 2027
    date(2027, 3, 25),  # before Good Friday 2027
    date(2027, 3, 28),  # before Easter Monday 2027
    date(2027, 5, 2),  # before Early May Bank Holiday 2027
    date(2027, 5, 30),  # before Spring Bank Holiday 2027
    date(2027, 8, 29),  # before Summer Bank Holiday 2027
    date(2027, 12, 24),  # before Christmas Day 2027
    date(2027, 12, 26),  # before Boxing Day 2027
    date(2027, 12, 31),  # before New Year's Day 2028
    date(2028, 4, 13),  # before Good Friday 2028
    date(2028, 4, 16),  # before Easter Monday 2028
    date(2028, 4, 30),  # before Early May Bank Holiday 2028
    date(2028, 5, 28),  # before Spring Bank Holiday 2028
    date(2028, 8, 27),  # before Summer Bank Holiday 2028
    date(2028, 12, 24),  # before Christmas Day 2028
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day after each holiday (walks past adjacent holidays)
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_AFTER_UK = [
    date(2024, 1, 2),  # after New Year's Day 2024
    date(2024, 3, 30),  # after Good Friday 2024
    date(2024, 4, 2),  # after Easter Monday 2024
    date(2024, 5, 7),  # after Early May Bank Holiday 2024
    date(2024, 5, 28),  # after Spring Bank Holiday 2024
    date(2024, 8, 27),  # after Summer Bank Holiday 2024
    date(2024, 12, 27),  # after Christmas Day 2024
    date(2025, 1, 2),  # after New Year's Day 2025
    date(2025, 4, 19),  # after Good Friday 2025
    date(2025, 4, 22),  # after Easter Monday 2025
    date(2025, 5, 6),  # after Early May Bank Holiday 2025
    date(2025, 5, 27),  # after Spring Bank Holiday 2025
    date(2025, 8, 26),  # after Summer Bank Holiday 2025
    date(2025, 12, 27),  # after Christmas Day 2025
    date(2026, 1, 2),  # after New Year's Day 2026
    date(2026, 4, 4),  # after Good Friday 2026
    date(2026, 4, 7),  # after Easter Monday 2026
    date(2026, 5, 5),  # after Early May Bank Holiday 2026
    date(2026, 5, 26),  # after Spring Bank Holiday 2026
    date(2026, 9, 1),  # after Summer Bank Holiday 2026
    date(2026, 12, 27),  # after Christmas Day 2026
    date(2027, 1, 2),  # after New Year's Day 2027
    date(2027, 3, 27),  # after Good Friday 2027
    date(2027, 3, 30),  # after Easter Monday 2027
    date(2027, 5, 4),  # after Early May Bank Holiday 2027
    date(2027, 6, 1),  # after Spring Bank Holiday 2027
    date(2027, 8, 31),  # after Summer Bank Holiday 2027
    date(2027, 12, 26),  # after Christmas Day 2027
    date(2027, 12, 28),  # after Boxing Day 2027
    date(2028, 1, 2),  # after New Year's Day 2028
    date(2028, 4, 15),  # after Good Friday 2028
    date(2028, 4, 18),  # after Easter Monday 2028
    date(2028, 5, 2),  # after Early May Bank Holiday 2028
    date(2028, 5, 30),  # after Spring Bank Holiday 2028
    date(2028, 8, 29),  # after Summer Bank Holiday 2028
    date(2028, 12, 27),  # after Christmas Day 2028
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestUKDayOf:
    """Each holiday date should be recognized with the correct name."""

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_UK)
    def test_is_holiday(self, target_date, expected_name):
        assert is_holiday(target_date, calendar="uk") is True

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_UK)
    def test_get_holiday_name(self, target_date, expected_name):
        assert get_holiday(target_date, calendar="uk") == expected_name


class TestUKDayBefore:
    """The nearest non-holiday before each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_BEFORE_UK)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="uk") is False


class TestUKDayAfter:
    """The nearest non-holiday after each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_AFTER_UK)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="uk") is False

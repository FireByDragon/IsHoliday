"""
Five-year boundary tests for the Banking calendar (2024-2028).

For every holiday in each year, verifies:
  - The day OF the holiday is recognized (with correct name).
  - The day BEFORE the holiday is NOT a holiday.
  - The day AFTER the holiday is NOT a holiday.

Adjacent-holiday pairs (e.g., Christmas + Boxing Day) are excluded from the
before/after lists because the neighbouring day is itself a holiday.

All expected dates were independently verified against published calendars.
"""

import pytest
from datetime import date

from isholiday import is_holiday, get_holiday


# ---------------------------------------------------------------------------
# Holiday dates -- day of (should be a holiday with matching name)
# ---------------------------------------------------------------------------

HOLIDAYS_BANKING = [
    (date(2024, 1, 1), "New Year's Day"),
    (date(2024, 1, 15), "Martin Luther King Jr. Day"),
    (date(2024, 2, 19), "Presidents' Day"),
    (date(2024, 3, 29), "Good Friday"),
    (date(2024, 4, 1), "Easter Monday"),
    (date(2024, 5, 27), "Memorial Day"),
    (date(2024, 6, 19), "Juneteenth National Independence Day"),
    (date(2024, 7, 4), "Independence Day"),
    (date(2024, 9, 2), "Labor Day"),
    (date(2024, 10, 14), "Columbus Day"),
    (date(2024, 11, 11), "Veterans Day"),
    (date(2024, 11, 28), "Thanksgiving Day"),
    (date(2024, 12, 25), "Christmas Day"),
    (date(2025, 1, 1), "New Year's Day"),
    (date(2025, 1, 20), "Martin Luther King Jr. Day"),
    (date(2025, 2, 17), "Presidents' Day"),
    (date(2025, 4, 18), "Good Friday"),
    (date(2025, 4, 21), "Easter Monday"),
    (date(2025, 5, 26), "Memorial Day"),
    (date(2025, 6, 19), "Juneteenth National Independence Day"),
    (date(2025, 7, 4), "Independence Day"),
    (date(2025, 9, 1), "Labor Day"),
    (date(2025, 10, 13), "Columbus Day"),
    (date(2025, 11, 11), "Veterans Day"),
    (date(2025, 11, 27), "Thanksgiving Day"),
    (date(2025, 12, 25), "Christmas Day"),
    (date(2026, 1, 1), "New Year's Day"),
    (date(2026, 1, 19), "Martin Luther King Jr. Day"),
    (date(2026, 2, 16), "Presidents' Day"),
    (date(2026, 4, 3), "Good Friday"),
    (date(2026, 4, 6), "Easter Monday"),
    (date(2026, 5, 25), "Memorial Day"),
    (date(2026, 6, 19), "Juneteenth National Independence Day"),
    (date(2026, 7, 3), "Independence Day"),
    (date(2026, 9, 7), "Labor Day"),
    (date(2026, 10, 12), "Columbus Day"),
    (date(2026, 11, 11), "Veterans Day"),
    (date(2026, 11, 26), "Thanksgiving Day"),
    (date(2026, 12, 25), "Christmas Day"),
    (date(2027, 1, 1), "New Year's Day"),
    (date(2027, 1, 18), "Martin Luther King Jr. Day"),
    (date(2027, 2, 15), "Presidents' Day"),
    (date(2027, 3, 26), "Good Friday"),
    (date(2027, 3, 29), "Easter Monday"),
    (date(2027, 5, 31), "Memorial Day"),
    (date(2027, 6, 18), "Juneteenth National Independence Day"),
    (date(2027, 7, 5), "Independence Day"),
    (date(2027, 9, 6), "Labor Day"),
    (date(2027, 10, 11), "Columbus Day"),
    (date(2027, 11, 11), "Veterans Day"),
    (date(2027, 11, 25), "Thanksgiving Day"),
    (date(2027, 12, 24), "Christmas Day"),
    (date(2027, 12, 31), "New Year's Day"),
    (date(2028, 1, 17), "Martin Luther King Jr. Day"),
    (date(2028, 2, 21), "Presidents' Day"),
    (date(2028, 4, 14), "Good Friday"),
    (date(2028, 4, 17), "Easter Monday"),
    (date(2028, 5, 29), "Memorial Day"),
    (date(2028, 6, 19), "Juneteenth National Independence Day"),
    (date(2028, 7, 4), "Independence Day"),
    (date(2028, 9, 4), "Labor Day"),
    (date(2028, 10, 9), "Columbus Day"),
    (date(2028, 11, 10), "Veterans Day"),
    (date(2028, 11, 23), "Thanksgiving Day"),
    (date(2028, 12, 25), "Christmas Day"),
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day before each holiday
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_BEFORE_BANKING = [
    date(2023, 12, 31),  # before New Year's Day 2024
    date(2024, 1, 14),  # before Martin Luther King Jr. Day 2024
    date(2024, 2, 18),  # before Presidents' Day 2024
    date(2024, 3, 28),  # before Good Friday 2024
    date(2024, 3, 31),  # before Easter Monday 2024
    date(2024, 5, 26),  # before Memorial Day 2024
    date(2024, 6, 18),  # before Juneteenth National Independence Day 2024
    date(2024, 7, 3),  # before Independence Day 2024
    date(2024, 9, 1),  # before Labor Day 2024
    date(2024, 10, 13),  # before Columbus Day 2024
    date(2024, 11, 10),  # before Veterans Day 2024
    date(2024, 11, 27),  # before Thanksgiving Day 2024
    date(2024, 12, 24),  # before Christmas Day 2024
    date(2024, 12, 31),  # before New Year's Day 2025
    date(2025, 1, 19),  # before Martin Luther King Jr. Day 2025
    date(2025, 2, 16),  # before Presidents' Day 2025
    date(2025, 4, 17),  # before Good Friday 2025
    date(2025, 4, 20),  # before Easter Monday 2025
    date(2025, 5, 25),  # before Memorial Day 2025
    date(2025, 6, 18),  # before Juneteenth National Independence Day 2025
    date(2025, 7, 3),  # before Independence Day 2025
    date(2025, 8, 31),  # before Labor Day 2025
    date(2025, 10, 12),  # before Columbus Day 2025
    date(2025, 11, 10),  # before Veterans Day 2025
    date(2025, 11, 26),  # before Thanksgiving Day 2025
    date(2025, 12, 24),  # before Christmas Day 2025
    date(2025, 12, 31),  # before New Year's Day 2026
    date(2026, 1, 18),  # before Martin Luther King Jr. Day 2026
    date(2026, 2, 15),  # before Presidents' Day 2026
    date(2026, 4, 2),  # before Good Friday 2026
    date(2026, 4, 5),  # before Easter Monday 2026
    date(2026, 5, 24),  # before Memorial Day 2026
    date(2026, 6, 18),  # before Juneteenth National Independence Day 2026
    date(2026, 7, 2),  # before Independence Day 2026
    date(2026, 9, 6),  # before Labor Day 2026
    date(2026, 10, 11),  # before Columbus Day 2026
    date(2026, 11, 10),  # before Veterans Day 2026
    date(2026, 11, 25),  # before Thanksgiving Day 2026
    date(2026, 12, 24),  # before Christmas Day 2026
    date(2026, 12, 31),  # before New Year's Day 2027
    date(2027, 1, 17),  # before Martin Luther King Jr. Day 2027
    date(2027, 2, 14),  # before Presidents' Day 2027
    date(2027, 3, 25),  # before Good Friday 2027
    date(2027, 3, 28),  # before Easter Monday 2027
    date(2027, 5, 30),  # before Memorial Day 2027
    date(2027, 6, 17),  # before Juneteenth National Independence Day 2027
    date(2027, 7, 4),  # before Independence Day 2027
    date(2027, 9, 5),  # before Labor Day 2027
    date(2027, 10, 10),  # before Columbus Day 2027
    date(2027, 11, 10),  # before Veterans Day 2027
    date(2027, 11, 24),  # before Thanksgiving Day 2027
    date(2027, 12, 23),  # before Christmas Day 2027
    date(2027, 12, 30),  # before New Year's Day 2027
    date(2028, 1, 16),  # before Martin Luther King Jr. Day 2028
    date(2028, 2, 20),  # before Presidents' Day 2028
    date(2028, 4, 13),  # before Good Friday 2028
    date(2028, 4, 16),  # before Easter Monday 2028
    date(2028, 5, 28),  # before Memorial Day 2028
    date(2028, 6, 18),  # before Juneteenth National Independence Day 2028
    date(2028, 7, 3),  # before Independence Day 2028
    date(2028, 9, 3),  # before Labor Day 2028
    date(2028, 10, 8),  # before Columbus Day 2028
    date(2028, 11, 9),  # before Veterans Day 2028
    date(2028, 11, 22),  # before Thanksgiving Day 2028
    date(2028, 12, 24),  # before Christmas Day 2028
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day after each holiday
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_AFTER_BANKING = [
    date(2024, 1, 2),  # after New Year's Day 2024
    date(2024, 1, 16),  # after Martin Luther King Jr. Day 2024
    date(2024, 2, 20),  # after Presidents' Day 2024
    date(2024, 3, 30),  # after Good Friday 2024
    date(2024, 4, 2),  # after Easter Monday 2024
    date(2024, 5, 28),  # after Memorial Day 2024
    date(2024, 6, 20),  # after Juneteenth National Independence Day 2024
    date(2024, 7, 5),  # after Independence Day 2024
    date(2024, 9, 3),  # after Labor Day 2024
    date(2024, 10, 15),  # after Columbus Day 2024
    date(2024, 11, 12),  # after Veterans Day 2024
    date(2024, 11, 29),  # after Thanksgiving Day 2024
    date(2024, 12, 26),  # after Christmas Day 2024
    date(2025, 1, 2),  # after New Year's Day 2025
    date(2025, 1, 21),  # after Martin Luther King Jr. Day 2025
    date(2025, 2, 18),  # after Presidents' Day 2025
    date(2025, 4, 19),  # after Good Friday 2025
    date(2025, 4, 22),  # after Easter Monday 2025
    date(2025, 5, 27),  # after Memorial Day 2025
    date(2025, 6, 20),  # after Juneteenth National Independence Day 2025
    date(2025, 7, 5),  # after Independence Day 2025
    date(2025, 9, 2),  # after Labor Day 2025
    date(2025, 10, 14),  # after Columbus Day 2025
    date(2025, 11, 12),  # after Veterans Day 2025
    date(2025, 11, 28),  # after Thanksgiving Day 2025
    date(2025, 12, 26),  # after Christmas Day 2025
    date(2026, 1, 2),  # after New Year's Day 2026
    date(2026, 1, 20),  # after Martin Luther King Jr. Day 2026
    date(2026, 2, 17),  # after Presidents' Day 2026
    date(2026, 4, 4),  # after Good Friday 2026
    date(2026, 4, 7),  # after Easter Monday 2026
    date(2026, 5, 26),  # after Memorial Day 2026
    date(2026, 6, 20),  # after Juneteenth National Independence Day 2026
    date(2026, 7, 4),  # after Independence Day 2026
    date(2026, 9, 8),  # after Labor Day 2026
    date(2026, 10, 13),  # after Columbus Day 2026
    date(2026, 11, 12),  # after Veterans Day 2026
    date(2026, 11, 27),  # after Thanksgiving Day 2026
    date(2026, 12, 26),  # after Christmas Day 2026
    date(2027, 1, 2),  # after New Year's Day 2027
    date(2027, 1, 19),  # after Martin Luther King Jr. Day 2027
    date(2027, 2, 16),  # after Presidents' Day 2027
    date(2027, 3, 27),  # after Good Friday 2027
    date(2027, 3, 30),  # after Easter Monday 2027
    date(2027, 6, 1),  # after Memorial Day 2027
    date(2027, 6, 19),  # after Juneteenth National Independence Day 2027
    date(2027, 7, 6),  # after Independence Day 2027
    date(2027, 9, 7),  # after Labor Day 2027
    date(2027, 10, 12),  # after Columbus Day 2027
    date(2027, 11, 12),  # after Veterans Day 2027
    date(2027, 11, 26),  # after Thanksgiving Day 2027
    date(2027, 12, 25),  # after Christmas Day 2027
    date(2028, 1, 1),  # after New Year's Day 2027
    date(2028, 1, 18),  # after Martin Luther King Jr. Day 2028
    date(2028, 2, 22),  # after Presidents' Day 2028
    date(2028, 4, 15),  # after Good Friday 2028
    date(2028, 4, 18),  # after Easter Monday 2028
    date(2028, 5, 30),  # after Memorial Day 2028
    date(2028, 6, 20),  # after Juneteenth National Independence Day 2028
    date(2028, 7, 5),  # after Independence Day 2028
    date(2028, 9, 5),  # after Labor Day 2028
    date(2028, 10, 10),  # after Columbus Day 2028
    date(2028, 11, 11),  # after Veterans Day 2028
    date(2028, 11, 24),  # after Thanksgiving Day 2028
    date(2028, 12, 26),  # after Christmas Day 2028
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBankingDayOf:
    """Each holiday date should be recognized with the correct name."""

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_BANKING)
    def test_is_holiday(self, target_date, expected_name):
        assert is_holiday(target_date, calendar="banking") is True

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_BANKING)
    def test_get_holiday_name(self, target_date, expected_name):
        assert get_holiday(target_date, calendar="banking") == expected_name


class TestBankingDayBefore:
    """The day before each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_BEFORE_BANKING)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="banking") is False


class TestBankingDayAfter:
    """The day after each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_AFTER_BANKING)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="banking") is False

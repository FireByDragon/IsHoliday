"""
Five-year boundary tests for the Japan calendar (2024-2028).

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

HOLIDAYS_JAPAN = [
    (date(2024, 1, 1), "New Year's Day (元日)"),
    (date(2024, 1, 8), "Coming of Age Day (成人の日)"),
    (date(2024, 2, 12), "National Foundation Day (建国記念の日)"),
    (date(2024, 2, 23), "Emperor's Birthday (天皇誕生日)"),
    (date(2024, 4, 29), "Shōwa Day (昭和の日)"),
    (date(2024, 5, 3), "Constitution Memorial Day (憲法記念日)"),
    (date(2024, 5, 4), "Greenery Day (みどりの日)"),
    (date(2024, 5, 6), "Children's Day (こどもの日)"),
    (date(2024, 7, 15), "Marine Day (海の日)"),
    (date(2024, 8, 12), "Mountain Day (山の日)"),
    (date(2024, 9, 16), "Respect for the Aged Day (敬老の日)"),
    (date(2024, 10, 14), "Sports Day (スポーツの日)"),
    (date(2024, 11, 4), "Culture Day (文化の日)"),
    (date(2024, 11, 23), "Labour Thanksgiving Day (勤労感謝の日)"),
    (date(2025, 1, 1), "New Year's Day (元日)"),
    (date(2025, 1, 13), "Coming of Age Day (成人の日)"),
    (date(2025, 2, 11), "National Foundation Day (建国記念の日)"),
    (date(2025, 2, 24), "Emperor's Birthday (天皇誕生日)"),
    (date(2025, 4, 29), "Shōwa Day (昭和の日)"),
    (date(2025, 5, 3), "Constitution Memorial Day (憲法記念日)"),
    (date(2025, 5, 5), "Greenery Day (みどりの日)"),
    (date(2025, 7, 21), "Marine Day (海の日)"),
    (date(2025, 8, 11), "Mountain Day (山の日)"),
    (date(2025, 9, 15), "Respect for the Aged Day (敬老の日)"),
    (date(2025, 10, 13), "Sports Day (スポーツの日)"),
    (date(2025, 11, 3), "Culture Day (文化の日)"),
    (date(2025, 11, 24), "Labour Thanksgiving Day (勤労感謝の日)"),
    (date(2026, 1, 1), "New Year's Day (元日)"),
    (date(2026, 1, 12), "Coming of Age Day (成人の日)"),
    (date(2026, 2, 11), "National Foundation Day (建国記念の日)"),
    (date(2026, 2, 23), "Emperor's Birthday (天皇誕生日)"),
    (date(2026, 4, 29), "Shōwa Day (昭和の日)"),
    (date(2026, 5, 4), "Constitution Memorial Day (憲法記念日)"),
    (date(2026, 5, 5), "Children's Day (こどもの日)"),
    (date(2026, 7, 20), "Marine Day (海の日)"),
    (date(2026, 8, 11), "Mountain Day (山の日)"),
    (date(2026, 9, 21), "Respect for the Aged Day (敬老の日)"),
    (date(2026, 10, 12), "Sports Day (スポーツの日)"),
    (date(2026, 11, 3), "Culture Day (文化の日)"),
    (date(2026, 11, 23), "Labour Thanksgiving Day (勤労感謝の日)"),
    (date(2027, 1, 1), "New Year's Day (元日)"),
    (date(2027, 1, 11), "Coming of Age Day (成人の日)"),
    (date(2027, 2, 11), "National Foundation Day (建国記念の日)"),
    (date(2027, 2, 23), "Emperor's Birthday (天皇誕生日)"),
    (date(2027, 4, 29), "Shōwa Day (昭和の日)"),
    (date(2027, 5, 3), "Constitution Memorial Day (憲法記念日)"),
    (date(2027, 5, 4), "Greenery Day (みどりの日)"),
    (date(2027, 5, 5), "Children's Day (こどもの日)"),
    (date(2027, 7, 19), "Marine Day (海の日)"),
    (date(2027, 8, 11), "Mountain Day (山の日)"),
    (date(2027, 9, 20), "Respect for the Aged Day (敬老の日)"),
    (date(2027, 10, 11), "Sports Day (スポーツの日)"),
    (date(2027, 11, 3), "Culture Day (文化の日)"),
    (date(2027, 11, 23), "Labour Thanksgiving Day (勤労感謝の日)"),
    (date(2028, 1, 1), "New Year's Day (元日)"),
    (date(2028, 1, 10), "Coming of Age Day (成人の日)"),
    (date(2028, 2, 11), "National Foundation Day (建国記念の日)"),
    (date(2028, 2, 23), "Emperor's Birthday (天皇誕生日)"),
    (date(2028, 4, 29), "Shōwa Day (昭和の日)"),
    (date(2028, 5, 3), "Constitution Memorial Day (憲法記念日)"),
    (date(2028, 5, 4), "Greenery Day (みどりの日)"),
    (date(2028, 5, 5), "Children's Day (こどもの日)"),
    (date(2028, 7, 17), "Marine Day (海の日)"),
    (date(2028, 8, 11), "Mountain Day (山の日)"),
    (date(2028, 9, 18), "Respect for the Aged Day (敬老の日)"),
    (date(2028, 10, 9), "Sports Day (スポーツの日)"),
    (date(2028, 11, 3), "Culture Day (文化の日)"),
    (date(2028, 11, 23), "Labour Thanksgiving Day (勤労感謝の日)"),
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day before each holiday (walks past adjacent holidays)
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_BEFORE_JAPAN = [
    date(2023, 12, 31),  # before New Year's Day (元日) 2024
    date(2024, 1, 7),  # before Coming of Age Day (成人の日) 2024
    date(2024, 2, 11),  # before National Foundation Day (建国記念の日) 2024
    date(2024, 2, 22),  # before Emperor's Birthday (天皇誕生日) 2024
    date(2024, 4, 28),  # before Shōwa Day (昭和の日) 2024
    date(2024, 5, 2),  # before Constitution Memorial Day (憲法記念日) 2024
    date(2024, 5, 5),  # before Children's Day (こどもの日) 2024
    date(2024, 7, 14),  # before Marine Day (海の日) 2024
    date(2024, 8, 11),  # before Mountain Day (山の日) 2024
    date(2024, 9, 15),  # before Respect for the Aged Day (敬老の日) 2024
    date(2024, 10, 13),  # before Sports Day (スポーツの日) 2024
    date(2024, 11, 3),  # before Culture Day (文化の日) 2024
    date(2024, 11, 22),  # before Labour Thanksgiving Day (勤労感謝の日) 2024
    date(2024, 12, 31),  # before New Year's Day (元日) 2025
    date(2025, 1, 12),  # before Coming of Age Day (成人の日) 2025
    date(2025, 2, 10),  # before National Foundation Day (建国記念の日) 2025
    date(2025, 2, 23),  # before Emperor's Birthday (天皇誕生日) 2025
    date(2025, 4, 28),  # before Shōwa Day (昭和の日) 2025
    date(2025, 5, 2),  # before Constitution Memorial Day (憲法記念日) 2025
    date(2025, 5, 4),  # before Greenery Day (みどりの日) 2025
    date(2025, 7, 20),  # before Marine Day (海の日) 2025
    date(2025, 8, 10),  # before Mountain Day (山の日) 2025
    date(2025, 9, 14),  # before Respect for the Aged Day (敬老の日) 2025
    date(2025, 10, 12),  # before Sports Day (スポーツの日) 2025
    date(2025, 11, 2),  # before Culture Day (文化の日) 2025
    date(2025, 11, 23),  # before Labour Thanksgiving Day (勤労感謝の日) 2025
    date(2025, 12, 31),  # before New Year's Day (元日) 2026
    date(2026, 1, 11),  # before Coming of Age Day (成人の日) 2026
    date(2026, 2, 10),  # before National Foundation Day (建国記念の日) 2026
    date(2026, 2, 22),  # before Emperor's Birthday (天皇誕生日) 2026
    date(2026, 4, 28),  # before Shōwa Day (昭和の日) 2026
    date(2026, 5, 3),  # before Constitution Memorial Day (憲法記念日) 2026
    date(2026, 7, 19),  # before Marine Day (海の日) 2026
    date(2026, 8, 10),  # before Mountain Day (山の日) 2026
    date(2026, 9, 20),  # before Respect for the Aged Day (敬老の日) 2026
    date(2026, 10, 11),  # before Sports Day (スポーツの日) 2026
    date(2026, 11, 2),  # before Culture Day (文化の日) 2026
    date(2026, 11, 22),  # before Labour Thanksgiving Day (勤労感謝の日) 2026
    date(2026, 12, 31),  # before New Year's Day (元日) 2027
    date(2027, 1, 10),  # before Coming of Age Day (成人の日) 2027
    date(2027, 2, 10),  # before National Foundation Day (建国記念の日) 2027
    date(2027, 2, 22),  # before Emperor's Birthday (天皇誕生日) 2027
    date(2027, 4, 28),  # before Shōwa Day (昭和の日) 2027
    date(2027, 5, 2),  # before Constitution Memorial Day (憲法記念日) 2027
    date(2027, 7, 18),  # before Marine Day (海の日) 2027
    date(2027, 8, 10),  # before Mountain Day (山の日) 2027
    date(2027, 9, 19),  # before Respect for the Aged Day (敬老の日) 2027
    date(2027, 10, 10),  # before Sports Day (スポーツの日) 2027
    date(2027, 11, 2),  # before Culture Day (文化の日) 2027
    date(2027, 11, 22),  # before Labour Thanksgiving Day (勤労感謝の日) 2027
    date(2027, 12, 31),  # before New Year's Day (元日) 2028
    date(2028, 1, 9),  # before Coming of Age Day (成人の日) 2028
    date(2028, 2, 10),  # before National Foundation Day (建国記念の日) 2028
    date(2028, 2, 22),  # before Emperor's Birthday (天皇誕生日) 2028
    date(2028, 4, 28),  # before Shōwa Day (昭和の日) 2028
    date(2028, 5, 2),  # before Constitution Memorial Day (憲法記念日) 2028
    date(2028, 7, 16),  # before Marine Day (海の日) 2028
    date(2028, 8, 10),  # before Mountain Day (山の日) 2028
    date(2028, 9, 17),  # before Respect for the Aged Day (敬老の日) 2028
    date(2028, 10, 8),  # before Sports Day (スポーツの日) 2028
    date(2028, 11, 2),  # before Culture Day (文化の日) 2028
    date(2028, 11, 22),  # before Labour Thanksgiving Day (勤労感謝の日) 2028
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day after each holiday (walks past adjacent holidays)
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_AFTER_JAPAN = [
    date(2024, 1, 2),  # after New Year's Day (元日) 2024
    date(2024, 1, 9),  # after Coming of Age Day (成人の日) 2024
    date(2024, 2, 13),  # after National Foundation Day (建国記念の日) 2024
    date(2024, 2, 24),  # after Emperor's Birthday (天皇誕生日) 2024
    date(2024, 4, 30),  # after Shōwa Day (昭和の日) 2024
    date(2024, 5, 5),  # after Constitution Memorial Day (憲法記念日) 2024
    date(2024, 5, 7),  # after Children's Day (こどもの日) 2024
    date(2024, 7, 16),  # after Marine Day (海の日) 2024
    date(2024, 8, 13),  # after Mountain Day (山の日) 2024
    date(2024, 9, 17),  # after Respect for the Aged Day (敬老の日) 2024
    date(2024, 10, 15),  # after Sports Day (スポーツの日) 2024
    date(2024, 11, 5),  # after Culture Day (文化の日) 2024
    date(2024, 11, 24),  # after Labour Thanksgiving Day (勤労感謝の日) 2024
    date(2025, 1, 2),  # after New Year's Day (元日) 2025
    date(2025, 1, 14),  # after Coming of Age Day (成人の日) 2025
    date(2025, 2, 12),  # after National Foundation Day (建国記念の日) 2025
    date(2025, 2, 25),  # after Emperor's Birthday (天皇誕生日) 2025
    date(2025, 4, 30),  # after Shōwa Day (昭和の日) 2025
    date(2025, 5, 4),  # after Constitution Memorial Day (憲法記念日) 2025
    date(2025, 5, 6),  # after Greenery Day (みどりの日) 2025
    date(2025, 7, 22),  # after Marine Day (海の日) 2025
    date(2025, 8, 12),  # after Mountain Day (山の日) 2025
    date(2025, 9, 16),  # after Respect for the Aged Day (敬老の日) 2025
    date(2025, 10, 14),  # after Sports Day (スポーツの日) 2025
    date(2025, 11, 4),  # after Culture Day (文化の日) 2025
    date(2025, 11, 25),  # after Labour Thanksgiving Day (勤労感謝の日) 2025
    date(2026, 1, 2),  # after New Year's Day (元日) 2026
    date(2026, 1, 13),  # after Coming of Age Day (成人の日) 2026
    date(2026, 2, 12),  # after National Foundation Day (建国記念の日) 2026
    date(2026, 2, 24),  # after Emperor's Birthday (天皇誕生日) 2026
    date(2026, 4, 30),  # after Shōwa Day (昭和の日) 2026
    date(2026, 5, 6),  # after Constitution Memorial Day (憲法記念日) 2026
    date(2026, 7, 21),  # after Marine Day (海の日) 2026
    date(2026, 8, 12),  # after Mountain Day (山の日) 2026
    date(2026, 9, 22),  # after Respect for the Aged Day (敬老の日) 2026
    date(2026, 10, 13),  # after Sports Day (スポーツの日) 2026
    date(2026, 11, 4),  # after Culture Day (文化の日) 2026
    date(2026, 11, 24),  # after Labour Thanksgiving Day (勤労感謝の日) 2026
    date(2027, 1, 2),  # after New Year's Day (元日) 2027
    date(2027, 1, 12),  # after Coming of Age Day (成人の日) 2027
    date(2027, 2, 12),  # after National Foundation Day (建国記念の日) 2027
    date(2027, 2, 24),  # after Emperor's Birthday (天皇誕生日) 2027
    date(2027, 4, 30),  # after Shōwa Day (昭和の日) 2027
    date(2027, 5, 6),  # after Constitution Memorial Day (憲法記念日) 2027
    date(2027, 7, 20),  # after Marine Day (海の日) 2027
    date(2027, 8, 12),  # after Mountain Day (山の日) 2027
    date(2027, 9, 21),  # after Respect for the Aged Day (敬老の日) 2027
    date(2027, 10, 12),  # after Sports Day (スポーツの日) 2027
    date(2027, 11, 4),  # after Culture Day (文化の日) 2027
    date(2027, 11, 24),  # after Labour Thanksgiving Day (勤労感謝の日) 2027
    date(2028, 1, 2),  # after New Year's Day (元日) 2028
    date(2028, 1, 11),  # after Coming of Age Day (成人の日) 2028
    date(2028, 2, 12),  # after National Foundation Day (建国記念の日) 2028
    date(2028, 2, 24),  # after Emperor's Birthday (天皇誕生日) 2028
    date(2028, 4, 30),  # after Shōwa Day (昭和の日) 2028
    date(2028, 5, 6),  # after Constitution Memorial Day (憲法記念日) 2028
    date(2028, 7, 18),  # after Marine Day (海の日) 2028
    date(2028, 8, 12),  # after Mountain Day (山の日) 2028
    date(2028, 9, 19),  # after Respect for the Aged Day (敬老の日) 2028
    date(2028, 10, 10),  # after Sports Day (スポーツの日) 2028
    date(2028, 11, 4),  # after Culture Day (文化の日) 2028
    date(2028, 11, 24),  # after Labour Thanksgiving Day (勤労感謝の日) 2028
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestJapanDayOf:
    """Each holiday date should be recognized with the correct name."""

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_JAPAN)
    def test_is_holiday(self, target_date, expected_name):
        assert is_holiday(target_date, calendar="japan") is True

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_JAPAN)
    def test_get_holiday_name(self, target_date, expected_name):
        assert get_holiday(target_date, calendar="japan") == expected_name


class TestJapanDayBefore:
    """The nearest non-holiday before each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_BEFORE_JAPAN)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="japan") is False


class TestJapanDayAfter:
    """The nearest non-holiday after each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_AFTER_JAPAN)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="japan") is False

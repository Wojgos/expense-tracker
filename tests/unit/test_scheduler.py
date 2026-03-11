import os
import sys
from datetime import date
from unittest.mock import MagicMock


os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_unit_tests")

for _mod in [
    "asyncpg",
    "app.db.session",
    "app.services.notification_manager",
]:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

if "app.db.session" not in sys.modules or not hasattr(sys.modules.get("app.db.session"), "async_session_factory"):
    mock_session = MagicMock()
    mock_session.async_session_factory = MagicMock()
    sys.modules["app.db.session"] = mock_session

mock_nm = MagicMock()
mock_nm.manager = MagicMock()
sys.modules["app.services.notification_manager"] = mock_nm

from app.services.scheduler import _compute_next_run
from app.db.models.recurring_expense import RecurrenceInterval


class TestComputeNextRunWeekly:

    def test_weekly_adds_7_days(self):
        """Standardowy tydzień od poniedziałku."""
        result = _compute_next_run(date(2025, 1, 6), RecurrenceInterval.WEEKLY)
        assert result == date(2025, 1, 13)

    def test_weekly_crosses_month_boundary(self):
        """Tydzień przekraczający granicę miesiąca (31 stycznia → 7 lutego)."""
        result = _compute_next_run(date(2025, 1, 31), RecurrenceInterval.WEEKLY)
        assert result == date(2025, 2, 7)

    def test_weekly_crosses_year_boundary(self):
        """Tydzień przekraczający granicę roku (29 grudnia → 5 stycznia)."""
        result = _compute_next_run(date(2024, 12, 29), RecurrenceInterval.WEEKLY)
        assert result == date(2025, 1, 5)

    def test_weekly_leap_year_boundary(self):
        """Tydzień z 26 lutego na 4 marca w roku przestępnym 2024."""
        result = _compute_next_run(date(2024, 2, 26), RecurrenceInterval.WEEKLY)
        assert result == date(2024, 3, 4)

    def test_weekly_non_leap_year_boundary(self):
        """Tydzień z 22 lutego na 1 marca w roku nieprzestępnym 2025."""
        result = _compute_next_run(date(2025, 2, 22), RecurrenceInterval.WEEKLY)
        assert result == date(2025, 3, 1)

    def test_weekly_result_is_date_object(self):
        """Zwracany typ powinien być datetime.date."""
        result = _compute_next_run(date(2025, 6, 1), RecurrenceInterval.WEEKLY)
        assert isinstance(result, date)

    def test_weekly_multiple_iterations(self):
        """Trzykrotne zastosowanie WEEKLY daje wynik +21 dni."""
        current = date(2025, 3, 1)
        for _ in range(3):
            current = _compute_next_run(current, RecurrenceInterval.WEEKLY)
        assert current == date(2025, 3, 22)


class TestComputeNextRunMonthly:

    def test_monthly_standard(self):
        """Standardowy miesiąc: 15 marca → 15 kwietnia."""
        result = _compute_next_run(date(2025, 3, 15), RecurrenceInterval.MONTHLY)
        assert result == date(2025, 4, 15)

    def test_monthly_crosses_year_boundary(self):
        """Miesiąc przekraczający granicę roku: grudzień → styczeń."""
        result = _compute_next_run(date(2025, 12, 10), RecurrenceInterval.MONTHLY)
        assert result == date(2026, 1, 10)

    def test_monthly_end_of_month_31_to_30(self):
        """31 stycznia → relativedelta przenosi na 28 lub 29 lutego."""
        result = _compute_next_run(date(2025, 1, 31), RecurrenceInterval.MONTHLY)
        # relativedelta ucina do ostatniego dnia lutego (28 w 2025)
        assert result == date(2025, 2, 28)

    def test_monthly_end_of_month_31_to_30_days_month(self):
        """31 marca → 30 kwietnia (kwiecień ma 30 dni)."""
        result = _compute_next_run(date(2025, 3, 31), RecurrenceInterval.MONTHLY)
        assert result == date(2025, 4, 30)

    def test_monthly_leap_year_february(self):
        """31 stycznia 2024 → 29 lutego 2024 (rok przestępny)."""
        result = _compute_next_run(date(2024, 1, 31), RecurrenceInterval.MONTHLY)
        assert result == date(2024, 2, 29)

    def test_monthly_preserves_day_when_possible(self):
        """Miesiąc z 1 na 1: dzień miesiąca nie zmienia się."""
        result = _compute_next_run(date(2025, 5, 1), RecurrenceInterval.MONTHLY)
        assert result.day == 1

    def test_monthly_result_is_date_object(self):
        """Zwracany typ powinien być datetime.date."""
        result = _compute_next_run(date(2025, 6, 15), RecurrenceInterval.MONTHLY)
        assert isinstance(result, date)

    def test_monthly_multiple_iterations_equals_one_year(self):
        """12 razy MONTHLY od 1 stycznia 2025 = 1 stycznia 2026."""
        current = date(2025, 1, 1)
        for _ in range(12):
            current = _compute_next_run(current, RecurrenceInterval.MONTHLY)
        assert current == date(2026, 1, 1)


class TestComputeNextRunYearly:

    def test_yearly_standard(self):
        """Standardowy rok: 15 marca 2025 → 15 marca 2026."""
        result = _compute_next_run(date(2025, 3, 15), RecurrenceInterval.YEARLY)
        assert result == date(2026, 3, 15)

    def test_yearly_leap_day_to_non_leap_year(self):
        """29 lutego 2024 (rok przestępny) → 28 lutego 2025 (nie-przestępny)."""
        result = _compute_next_run(date(2024, 2, 29), RecurrenceInterval.YEARLY)
        assert result == date(2025, 2, 28)

    def test_yearly_crosses_century(self):
        """Rok na granicy stulecia: 1 stycznia 2099 → 1 stycznia 2100."""
        result = _compute_next_run(date(2099, 1, 1), RecurrenceInterval.YEARLY)
        assert result == date(2100, 1, 1)

    def test_yearly_result_is_date_object(self):
        """Zwracany typ powinien być datetime.date."""
        result = _compute_next_run(date(2025, 7, 4), RecurrenceInterval.YEARLY)
        assert isinstance(result, date)

    def test_yearly_multiple_iterations(self):
        """Trzykrotne zastosowanie YEARLY od 2025 daje 2028."""
        current = date(2025, 6, 1)
        for _ in range(3):
            current = _compute_next_run(current, RecurrenceInterval.YEARLY)
        assert current == date(2028, 6, 1)

    def test_yearly_to_leap_year(self):
        """28 lutego 2027 → 28 lutego 2028 (rok przestępny — dzień się nie zmienia)."""
        result = _compute_next_run(date(2027, 2, 28), RecurrenceInterval.YEARLY)
        assert result == date(2028, 2, 28)



class TestComputeNextRunComparisons:

    def test_weekly_shorter_than_monthly(self):
        """WEEKLY zawsze daje wcześniejszą datę niż MONTHLY."""
        current = date(2025, 4, 1)
        weekly = _compute_next_run(current, RecurrenceInterval.WEEKLY)
        monthly = _compute_next_run(current, RecurrenceInterval.MONTHLY)
        assert weekly < monthly

    def test_monthly_shorter_than_yearly(self):
        """MONTHLY zawsze daje wcześniejszą datę niż YEARLY."""
        current = date(2025, 4, 1)
        monthly = _compute_next_run(current, RecurrenceInterval.MONTHLY)
        yearly = _compute_next_run(current, RecurrenceInterval.YEARLY)
        assert monthly < yearly

    def test_all_intervals_return_future_date(self):
        """Każdy interwał zwraca datę późniejszą niż data wejściowa."""
        current = date(2025, 6, 15)
        for interval in RecurrenceInterval:
            result = _compute_next_run(current, interval)
            assert result > current, f"Interwał {interval} nie zwrócił daty późniejszej"

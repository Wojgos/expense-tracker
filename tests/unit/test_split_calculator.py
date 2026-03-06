import uuid
import pytest
from decimal import Decimal
from backend.app.services.split_calculator import (
    calculate_equal_split,
    calculate_exact_split,
    calculate_percent_split,
    calculate_shares_split,
)


@pytest.fixture
def user_ids():
    return [
        uuid.UUID("00000000-0000-0000-0000-000000000001"),
        uuid.UUID("00000000-0000-0000-0000-000000000002"),
        uuid.UUID("00000000-0000-0000-0000-000000000003"),
        uuid.UUID("00000000-0000-0000-0000-000000000004"),
    ]


class TestCalculateEqualSplit:
    def test_equal_split_perfect_division(self, user_ids):
        """Test ideal division: 100.00 split equally among 4 people."""
        result = calculate_equal_split(Decimal("100.00"), user_ids[:4])
        assert result[user_ids[0]] == Decimal("25.00")
        assert result[user_ids[1]] == Decimal("25.00")
        assert result[user_ids[2]] == Decimal("25.00")
        assert result[user_ids[3]] == Decimal("25.00")
        assert sum(result.values()) == Decimal("100.00")

    def test_equal_split_with_remainder(self, user_ids):
        """Test split with remainder: 10.00 among 3 people."""
        result = calculate_equal_split(Decimal("10.00"), user_ids[:3])
        assert result[user_ids[0]] == Decimal("3.33")
        assert result[user_ids[1]] == Decimal("3.33")
        assert result[user_ids[2]] == Decimal("3.34")
        assert sum(result.values()) == Decimal("10.00")

    def test_equal_split_small_amount_two_people(self, user_ids):
        """Test split of 0.01 among 2 people."""
        result = calculate_equal_split(Decimal("0.01"), user_ids[:2])
        assert result[user_ids[0]] == Decimal("0.00")
        assert result[user_ids[1]] == Decimal("0.01")
        assert sum(result.values()) == Decimal("0.01")

    def test_equal_split_single_person(self, user_ids):
        """Test split among one person - gets the whole amount."""
        result = calculate_equal_split(Decimal("99.99"), user_ids[:1])
        assert result[user_ids[0]] == Decimal("99.99")
        assert len(result) == 1
        assert sum(result.values()) == Decimal("99.99")

    def test_equal_split_zero_amount(self, user_ids):
        """Test split of zero amount among participants."""
        result = calculate_equal_split(Decimal("0.00"), user_ids[:3])
        assert result[user_ids[0]] == Decimal("0.00")
        assert result[user_ids[1]] == Decimal("0.00")
        assert result[user_ids[2]] == Decimal("0.00")
        assert sum(result.values()) == Decimal("0.00")

    def test_equal_split_large_group(self, user_ids):
        """Test split among large group: 1.00 split among 100 people."""
        large_group = [uuid.UUID(f"00000000-0000-0000-0000-{i:012d}") for i in range(1, 101)]
        result = calculate_equal_split(Decimal("1.00"), large_group)
        assert len(result) == 100
        assert sum(result.values()) == Decimal("1.00")
        assert all(v == Decimal("0.01") for v in list(result.values()))

    def test_equal_split_large_amount_precision(self, user_ids):
        """Test precision with very large amount using Decimal."""
        large_amount = Decimal("999999.99")
        result = calculate_equal_split(large_amount, user_ids[:3])
        assert sum(result.values()) == large_amount
        assert all(v.as_tuple().exponent >= -2 for v in result.values())

    def test_equal_split_empty_list_raises_error(self):
        """Test that empty participant list raises ZeroDivisionError."""
        with pytest.raises(ZeroDivisionError):
            calculate_equal_split(Decimal("100.00"), [])


class TestCalculateExactSplit:
    def test_exact_split_correct_sum(self, user_ids):
        """Test correct sum: 50.00 = 20.00 + 30.00."""
        amounts = {
            user_ids[0]: Decimal("20.00"),
            user_ids[1]: Decimal("30.00"),
        }
        result = calculate_exact_split(Decimal("50.00"), amounts)
        assert result == amounts
        assert sum(result.values()) == Decimal("50.00")

    def test_exact_split_sum_too_small(self, user_ids):
        """Test validation error: sum is too small by one penny."""
        amounts = {
            user_ids[0]: Decimal("20.00"),
            user_ids[1]: Decimal("29.99"),
        }
        with pytest.raises(ValueError, match="sum to"):
            calculate_exact_split(Decimal("50.00"), amounts)

    def test_exact_split_sum_too_large(self, user_ids):
        """Test validation error: sum is too large by one penny."""
        amounts = {
            user_ids[0]: Decimal("20.00"),
            user_ids[1]: Decimal("30.01"),
        }
        with pytest.raises(ValueError, match="sum to"):
            calculate_exact_split(Decimal("50.00"), amounts)

    def test_exact_split_all_zeros(self, user_ids):
        """Test validation of zero sum with zero amounts."""
        amounts = {
            user_ids[0]: Decimal("0.00"),
            user_ids[1]: Decimal("0.00"),
            user_ids[2]: Decimal("0.00"),
        }
        result = calculate_exact_split(Decimal("0.00"), amounts)
        assert result == amounts

    def test_exact_split_empty_dict(self):
        """Test with empty amounts dictionary - should validate correctly for 0.00."""
        result = calculate_exact_split(Decimal("0.00"), {})
        assert result == {}

    def test_exact_split_negative_amounts(self, user_ids):
        """Test with negative amounts (refund/correction scenario)."""
        amounts = {
            user_ids[0]: Decimal("100.00"),
            user_ids[1]: Decimal("-50.00"),
        }
        result = calculate_exact_split(Decimal("50.00"), amounts)
        assert sum(result.values()) == Decimal("50.00")


class TestCalculatePercentSplit:
    def test_percent_split_standard_distribution(self, user_ids):
        """Test standard distribution: 50%, 25%, 25%."""
        percentages = {
            user_ids[0]: Decimal("50"),
            user_ids[1]: Decimal("25"),
            user_ids[2]: Decimal("25"),
        }
        result = calculate_percent_split(Decimal("100.00"), percentages)
        assert result[user_ids[0]] == Decimal("50.00")
        assert result[user_ids[1]] == Decimal("25.00")
        assert result[user_ids[2]] == Decimal("25.00")
        assert sum(result.values()) == Decimal("100.00")

    def test_percent_split_uneven_percentages(self, user_ids):
        """Test uneven split: 33.33%, 33.33%, 33.34%."""
        percentages = {
            user_ids[0]: Decimal("33.33"),
            user_ids[1]: Decimal("33.33"),
            user_ids[2]: Decimal("33.34"),
        }
        result = calculate_percent_split(Decimal("100.00"), percentages)
        assert sum(result.values()) == Decimal("100.00")
        assert result[user_ids[2]] == Decimal("33.34")

    def test_percent_split_sum_less_than_100(self, user_ids):
        """Test validation error: percentages sum to less than 100."""
        percentages = {
            user_ids[0]: Decimal("49.99"),
            user_ids[1]: Decimal("50.00"),
        }
        with pytest.raises(ValueError, match="Percentages sum"):
            calculate_percent_split(Decimal("100.00"), percentages)

    def test_percent_split_sum_greater_than_100(self, user_ids):
        """Test validation error: percentages sum to more than 100."""
        percentages = {
            user_ids[0]: Decimal("50.01"),
            user_ids[1]: Decimal("50.00"),
        }
        with pytest.raises(ValueError, match="Percentages sum"):
            calculate_percent_split(Decimal("100.00"), percentages)

    def test_percent_split_single_person_100_percent(self, user_ids):
        """Test one person getting 100%."""
        percentages = {user_ids[0]: Decimal("100")}
        result = calculate_percent_split(Decimal("250.50"), percentages)
        assert result[user_ids[0]] == Decimal("250.50")
        assert len(result) == 1

    def test_percent_split_with_zero_percentages(self, user_ids):
        """Test split with one person 100% and others 0%."""
        percentages = {
            user_ids[0]: Decimal("100"),
            user_ids[1]: Decimal("0"),
            user_ids[2]: Decimal("0"),
        }
        result = calculate_percent_split(Decimal("50.00"), percentages)
        assert result[user_ids[0]] == Decimal("50.00")
        assert result[user_ids[1]] == Decimal("0.00")
        assert result[user_ids[2]] == Decimal("0.00")

    def test_percent_split_small_amount_precision(self, user_ids):
        """Test rounding precision with small amounts and percentages."""
        percentages = {
            user_ids[0]: Decimal("33.33"),
            user_ids[1]: Decimal("33.33"),
            user_ids[2]: Decimal("33.34"),
        }
        result = calculate_percent_split(Decimal("0.99"), percentages)
        assert sum(result.values()) == Decimal("0.99")
        assert all(v.as_tuple().exponent >= -2 for v in result.values())

    def test_percent_split_key_order_last_gets_remainder(self, user_ids):
        """Test that last person always gets the remainder for rounding."""
        percentages = {
            user_ids[0]: Decimal("33.33"),
            user_ids[1]: Decimal("33.33"),
            user_ids[2]: Decimal("33.34"),
        }
        result = calculate_percent_split(Decimal("10.00"), percentages)
        last_person_share = result[user_ids[2]]
        assert last_person_share > Decimal("3.33")
        assert sum(result.values()) == Decimal("10.00")


class TestCalculateSharesSplit:
    def test_shares_split_equal_shares(self, user_ids):
        """Test simple shares: 1:1 (split equally)."""
        shares = {
            user_ids[0]: 1,
            user_ids[1]: 1,
        }
        result = calculate_shares_split(Decimal("100.00"), shares)
        assert result[user_ids[0]] == Decimal("50.00")
        assert result[user_ids[1]] == Decimal("50.00")
        assert sum(result.values()) == Decimal("100.00")

    def test_shares_split_proportional_2_1_1(self, user_ids):
        """Test proportional shares: 2:1:1 (50%, 25%, 25%)."""
        shares = {
            user_ids[0]: 2,
            user_ids[1]: 1,
            user_ids[2]: 1,
        }
        result = calculate_shares_split(Decimal("100.00"), shares)
        assert result[user_ids[0]] == Decimal("50.00")
        assert result[user_ids[1]] == Decimal("25.00")
        assert result[user_ids[2]] == Decimal("25.00")
        assert sum(result.values()) == Decimal("100.00")

    def test_shares_split_equal_with_remainder(self, user_ids):
        """Test equal shares 1:1:1 with remainder: 10.00."""
        shares = {
            user_ids[0]: 1,
            user_ids[1]: 1,
            user_ids[2]: 1,
        }
        result = calculate_shares_split(Decimal("10.00"), shares)
        assert sum(result.values()) == Decimal("10.00")
        assert result[user_ids[2]] >= Decimal("3.33")

    def test_shares_split_zero_shares_raises_error(self, user_ids):
        """Test that total shares of zero raises ValueError."""
        shares = {
            user_ids[0]: 0,
            user_ids[1]: 0,
        }
        with pytest.raises(ValueError, match="Total shares cannot be zero"):
            calculate_shares_split(Decimal("100.00"), shares)

    def test_shares_split_very_large_shares(self, user_ids):
        """Test with very large share numbers: 1,000,000:1."""
        shares = {
            user_ids[0]: 1_000_000,
            user_ids[1]: 1,
        }
        result = calculate_shares_split(Decimal("100.00"), shares)
        assert sum(result.values()) == Decimal("100.00")
        assert result[user_ids[0]] > Decimal("99.00")

    def test_shares_split_many_equal_shares(self, user_ids):
        """Test with many people each having 1 share."""
        many_people = [uuid.UUID(f"00000000-0000-0000-0000-{i:012d}") for i in range(1, 51)]
        shares = {person: 1 for person in many_people}
        result = calculate_shares_split(Decimal("100.00"), shares)
        assert len(result) == 50
        assert sum(result.values()) == Decimal("100.00")
        assert all(v >= Decimal("2") for v in result.values())

    def test_shares_split_single_person(self, user_ids):
        """Test with single person - should get full amount."""
        shares = {user_ids[0]: 5}
        result = calculate_shares_split(Decimal("75.50"), shares)
        assert result[user_ids[0]] == Decimal("75.50")
        assert len(result) == 1

    def test_shares_split_fractional_result_precision(self, user_ids):
        """Test precision when shares create fractional results."""
        shares = {
            user_ids[0]: 3,
            user_ids[1]: 2,
            user_ids[2]: 1,
        }
        result = calculate_shares_split(Decimal("7.00"), shares)
        assert sum(result.values()) == Decimal("7.00")
        assert all(v.as_tuple().exponent >= -2 for v in result.values())

import uuid
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal


def calculate_equal_split(
    total: Decimal, participant_ids: list[uuid.UUID]
) -> dict[uuid.UUID, Decimal]:
    """Split equally. Remainder (from rounding) goes to the last participant."""
    n = len(participant_ids)
    per_person = (total / n).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    remainder = total - per_person * n

    result = {uid: per_person for uid in participant_ids}
    result[participant_ids[-1]] += remainder
    return result


def calculate_exact_split(
    total: Decimal, amounts: dict[uuid.UUID, Decimal]
) -> dict[uuid.UUID, Decimal]:
    """Validate that exact amounts sum to total."""
    actual_sum = sum(amounts.values())
    if actual_sum != total:
        raise ValueError(
            f"Exact amounts sum to {actual_sum}, but total is {total}"
        )
    return amounts


def calculate_percent_split(
    total: Decimal, percentages: dict[uuid.UUID, Decimal]
) -> dict[uuid.UUID, Decimal]:
    """Calculate amounts from percentages. Must sum to 100."""
    pct_sum = sum(percentages.values())
    if pct_sum != Decimal("100"):
        raise ValueError(f"Percentages sum to {pct_sum}, expected 100")

    result = {}
    allocated = Decimal("0")
    items = list(percentages.items())

    for uid, pct in items[:-1]:
        amount = (total * pct / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        result[uid] = amount
        allocated += amount

    last_uid = items[-1][0]
    result[last_uid] = total - allocated
    return result


def calculate_shares_split(
    total: Decimal, shares: dict[uuid.UUID, int]
) -> dict[uuid.UUID, Decimal]:
    """Split proportionally by shares (e.g. 2,1,1 = 50%,25%,25%)."""
    total_shares = sum(shares.values())
    if total_shares == 0:
        raise ValueError("Total shares cannot be zero")

    result = {}
    allocated = Decimal("0")
    items = list(shares.items())

    for uid, s in items[:-1]:
        amount = (total * s / total_shares).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        result[uid] = amount
        allocated += amount

    last_uid = items[-1][0]
    result[last_uid] = total - allocated
    return result

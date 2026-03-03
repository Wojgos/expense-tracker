import uuid
from decimal import Decimal

from dataclasses import dataclass


@dataclass
class SuggestedTransfer:
    from_user: uuid.UUID
    to_user: uuid.UUID
    amount: Decimal


def compute_balances(
    expenses: list[dict],
    settlements: list[dict],
) -> dict[uuid.UUID, Decimal]:
    """
    Compute net balance for each user in a group.

    expenses: list of {"paid_by": UUID, "splits": [{"user_id": UUID, "owed_amount": Decimal}]}
    settlements: list of {"paid_by": UUID, "paid_to": UUID, "amount": Decimal}

    Returns {user_id: net_balance} where positive = others owe you, negative = you owe others.
    """
    balances: dict[uuid.UUID, Decimal] = {}

    for exp in expenses:
        payer = exp["paid_by"]
        for split in exp["splits"]:
            debtor = split["user_id"]
            owed = split["owed_amount"]
            balances[payer] = balances.get(payer, Decimal("0")) + owed
            balances[debtor] = balances.get(debtor, Decimal("0")) - owed

    for sett in settlements:
        sender = sett["paid_by"]
        receiver = sett["paid_to"]
        amount = sett["amount"]
        balances[sender] = balances.get(sender, Decimal("0")) + amount
        balances[receiver] = balances.get(receiver, Decimal("0")) - amount

    return balances


def minimize_transactions(
    balances: dict[uuid.UUID, Decimal],
) -> list[SuggestedTransfer]:
    """
    Greedy algorithm: repeatedly match the largest creditor with the largest debtor.
    Returns the minimal set of transfers to settle all debts.
    """
    creditors: list[tuple[uuid.UUID, Decimal]] = []
    debtors: list[tuple[uuid.UUID, Decimal]] = []

    for uid, balance in balances.items():
        if balance > Decimal("0.01"):
            creditors.append((uid, balance))
        elif balance < Decimal("-0.01"):
            debtors.append((uid, -balance))

    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    transfers: list[SuggestedTransfer] = []
    ci, di = 0, 0

    while ci < len(creditors) and di < len(debtors):
        creditor_id, credit = creditors[ci]
        debtor_id, debt = debtors[di]

        amount = min(credit, debt)
        amount = amount.quantize(Decimal("0.01"))

        transfers.append(
            SuggestedTransfer(from_user=debtor_id, to_user=creditor_id, amount=amount)
        )

        credit -= amount
        debt -= amount

        if credit < Decimal("0.01"):
            ci += 1
        else:
            creditors[ci] = (creditor_id, credit)

        if debt < Decimal("0.01"):
            di += 1
        else:
            debtors[di] = (debtor_id, debt)

    return transfers

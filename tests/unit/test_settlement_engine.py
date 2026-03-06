import uuid
from decimal import Decimal

import pytest

from app.services.settlement_engine import compute_balances, minimize_transactions, SuggestedTransfer   


def generatorUuid():
    return uuid.uuid4()


def test_single_expense_two_participants():
    rafal = generatorUuid()
    domino = generatorUuid()

    expenses = [
        {
            "paid_by": rafal,
            "splits": [
                {"user_id": domino, "owed_amount": Decimal("100")},
            ],
        }
    ]

    balances = compute_balances(expenses, [])
    assert balances[rafal] == Decimal("100")
    assert balances[domino] == Decimal("-100")

def test_multiple_expenses_cumulative():
    rafal = generatorUuid()
    domino = generatorUuid()
    arek = generatorUuid()

    expenses = [
        {
            "paid_by": rafal,
            "splits": [
                {"user_id": domino, "owed_amount": Decimal("50")},
                {"user_id": arek, "owed_amount": Decimal("100")},
            ],
        },
        {
            "paid_by": domino,
            "splits": [
                {"user_id": rafal, "owed_amount": Decimal("150")},
                {"user_id": arek, "owed_amount": Decimal("50")},
            ],
        },
    ]

    balances = compute_balances(expenses, [])
    assert balances[rafal] == Decimal("0")
    assert balances[domino] == Decimal("150")
    assert balances[arek] == Decimal("-150")

def test_settlement_reduces_debt():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    expenses = [
        {
            "paid_by": rafal,
            "splits": [
                {"user_id": domino, "owed_amount": Decimal("100")},
            ],
        }
    ]

    settlements = [
        {
            "paid_by": domino,
            "paid_to": rafal,
            "amount": Decimal("50"),
        }
    ]

    balances = compute_balances(expenses, settlements)
    assert balances[rafal] == Decimal("50")
    assert balances[domino] == Decimal("-50")   
        
def test_empty_data_returns_empty():
    balances = compute_balances(expenses=[], settlements=[])
    assert balances == {}

def test_payer_also_in_splits():
    rafal = generatorUuid()
    
    expenses = [
        {
            "paid_by": rafal,
            "splits": [
                {"user_id": rafal, "owed_amount": Decimal("100")},
            ],
        }
    ]
    
    balances = compute_balances(expenses, [])
    assert balances[rafal] == Decimal("0")    

def test_many_settlements_same_people():
    rafal = generatorUuid()
    domino = generatorUuid()
    arek = generatorUuid()

    expenses = [
        {
            "paid_by": rafal,
            "splits": [
                {"user_id": domino, "owed_amount": Decimal("100")},
                {"user_id": arek, "owed_amount": Decimal("100")},
            ],
        }
    ]

    settlements = [
        {
            "paid_by": domino,
            "paid_to": rafal,
            "amount": Decimal("30"),
        },
        {
            "paid_by": domino,
            "paid_to": rafal,
            "amount": Decimal("20"),
        },
        {
            "paid_by": arek,
            "paid_to": rafal,
            "amount": Decimal("100"),
        },
    ]

    balances = compute_balances(expenses, settlements)
    
    assert balances[rafal] == Decimal("50")
    assert balances[domino] == Decimal("-50")
    assert balances[arek] == Decimal("0")

def test_simple_settlement():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    balances = {rafal: Decimal("100"), domino: Decimal("-100")}
    transfers = minimize_transactions(balances)
    assert transfers == [SuggestedTransfer(from_user=domino, to_user=rafal, amount=Decimal("100"))] 

def test_three_way_settlement():
    rafal = generatorUuid()
    domino = generatorUuid()
    arek = generatorUuid()
    
    balances = {rafal: Decimal("150"), domino: Decimal("-100"), arek: Decimal("-50")}
    transfers = minimize_transactions(balances)
    assert transfers == [SuggestedTransfer(from_user=domino, to_user=rafal, amount=Decimal("100")), SuggestedTransfer(from_user=arek, to_user=rafal, amount=Decimal("50"))]

def test_participants_with_zero_balance():
    rafal = generatorUuid()
    domino = generatorUuid()
    arek = generatorUuid()
    
    balances = {rafal: Decimal("0"), domino: Decimal("0"), arek: Decimal("0")}
    transfers = minimize_transactions(balances)
    assert transfers == []

def test_balances_below_treshhold_are_ignored():
    rafal = generatorUuid()
    domino = generatorUuid()

    balances = {rafal: Decimal("0.001"), domino: Decimal("-0.005")}
    transfers = minimize_transactions(balances)
    assert transfers == []

def test_complex_settlement():
    rafal = generatorUuid()
    domino = generatorUuid()
    arek = generatorUuid()
    wojtek = generatorUuid()
    kuba = generatorUuid()
    
    expenses = [
        {
            "paid_by": rafal,
            "splits": [
                {"user_id": domino, "owed_amount": Decimal("100")},
                {"user_id": arek, "owed_amount": Decimal("100")},
                {"user_id": wojtek, "owed_amount": Decimal("100")},
                {"user_id": kuba, "owed_amount": Decimal("100")},
            ],
        },
        {
            "paid_by": domino,
            "splits": [
                {"user_id": rafal, "owed_amount": Decimal("100")},
                {"user_id": arek, "owed_amount": Decimal("100")},
                {"user_id": wojtek, "owed_amount": Decimal("100")},
                {"user_id": kuba, "owed_amount": Decimal("100")},
            ],
        },
        {
            "paid_by": arek,
            "splits": [
                {"user_id": rafal, "owed_amount": Decimal("100")},
                {"user_id": domino, "owed_amount": Decimal("100")},
                {"user_id": wojtek, "owed_amount": Decimal("100")},
                {"user_id": kuba, "owed_amount": Decimal("100")},
            ],
        },
        {
            "paid_by": wojtek,
            "splits": [
                {"user_id": rafal, "owed_amount": Decimal("100")},
                {"user_id": domino, "owed_amount": Decimal("100")},
                {"user_id": arek, "owed_amount": Decimal("100")},
                {"user_id": kuba, "owed_amount": Decimal("100")},
            ],
        },
        {
            "paid_by": kuba,
            "splits": [
                {"user_id": rafal, "owed_amount": Decimal("100")},
                {"user_id": domino, "owed_amount": Decimal("100")},
                {"user_id": arek, "owed_amount": Decimal("100")},
                {"user_id": wojtek, "owed_amount": Decimal("100")},
            ],
        },
    ]
    settlements = [
        {
            "paid_by": rafal,
            "paid_to": domino,
            "amount": Decimal("100"),
        },
        {
            "paid_by": rafal,
            "paid_to": arek,
            "amount": Decimal("100"),
        },
        {
            "paid_by": rafal,
            "paid_to": wojtek,
            "amount": Decimal("100"),
        },
        {
            "paid_by": rafal,
            "paid_to": kuba,
            "amount": Decimal("100"),
        },
        {
            "paid_by": domino,
            "paid_to": rafal,
            "amount": Decimal("100"),
        },
        {
            "paid_by": domino,
            "paid_to": arek,
            "amount": Decimal("100"),
        },
        {
            "paid_by": domino,
            "paid_to": wojtek,
            "amount": Decimal("100"),
        },
        {
            "paid_by": domino,
            "paid_to": kuba,
            "amount": Decimal("100"),
        },
        {
            "paid_by": arek,
            "paid_to": rafal,
            "amount": Decimal("100"),
        },
        {
            "paid_by": arek,
            "paid_to": domino,
            "amount": Decimal("100"),
        },
        {
            "paid_by": arek,
            "paid_to": wojtek,
            "amount": Decimal("100"),
        },
        {
            "paid_by": arek,
            "paid_to": kuba,
            "amount": Decimal("100"),
        },
        {
            "paid_by": wojtek,
            "paid_to": rafal,
            "amount": Decimal("100"),
        },
        {
            "paid_by": wojtek,
            "paid_to": domino,
            "amount": Decimal("100"),
        },
        {
            "paid_by": wojtek,
            "paid_to": arek,
            "amount": Decimal("100"),
        },
        {
            "paid_by": wojtek,
            "paid_to": kuba,
            "amount": Decimal("100"),
        },
        {
            "paid_by": kuba,
            "paid_to": rafal,
            "amount": Decimal("100"),
        },
        {
            "paid_by": kuba,
            "paid_to": domino,
            "amount": Decimal("100"),
        },
        {
            "paid_by": kuba,
            "paid_to": arek,
            "amount": Decimal("100"),
        },
        {
            "paid_by": kuba,
            "paid_to": wojtek,
            "amount": Decimal("100"),
        },
    ]
    
    balances = compute_balances(expenses, settlements)
    assert balances[rafal] == Decimal("0")
    assert balances[domino] == Decimal("0")
    assert balances[arek] == Decimal("0")
    assert balances[wojtek] == Decimal("0")
    assert balances[kuba] == Decimal("0")
    
    transfers = minimize_transactions(balances)
    assert transfers == []  

def test_decimal_transfers_are_rounded():
    rafal = generatorUuid()
    domino = generatorUuid()
    arek = generatorUuid()

    balances = {
        rafal: Decimal("33.333"),
        domino: Decimal("-16.667"),
        arek: Decimal("-16.666"),
    }

    transfers = minimize_transactions(balances)

    for t in transfers:
        assert t.amount == t.amount.quantize(Decimal("0.01"))
        assert t.amount > Decimal("0")
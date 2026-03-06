import uuid
from decimal import Decimal
from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.expense import ExpenseCreate
from app.db.models.expense import SplitType


def generatorUuid():
    return uuid.uuid4() 

def test_equal_split_valid():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    expense = ExpenseCreate(
        description="Test",
        amount=Decimal("100"),
        currency="PLN",
        expense_date=date.today(),
        split_type=SplitType.EQUAL,
        participant_ids=[rafal, domino],
    )
    assert expense.split_type == SplitType.EQUAL
    assert expense.participant_ids == [rafal, domino]
    assert expense.amount == Decimal("100")
    assert expense.currency == "PLN"
    assert expense.expense_date == date.today()
    assert expense.description == "Test"

def test_negative_amount_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    with pytest.raises(ValidationError):
        expense = ExpenseCreate(
            description="Test",
            amount=Decimal("-100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.EQUAL,
            participant_ids=[rafal, domino],
        )   

def test_zero_amount_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    with pytest.raises(ValidationError):
        expense = ExpenseCreate(
            description="Test",
            amount=Decimal("0"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.EQUAL,
            participant_ids=[rafal, domino],
        )       

def test_empty_participant_ids_raises_error():
    rafal = generatorUuid()
    
    with pytest.raises(ValidationError):
        expense = ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.EQUAL,
            participant_ids=[],
        )       

def test_exact_split_valid():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    expense = ExpenseCreate(
        description="Test",
        amount=Decimal("100"),
        currency="PLN",
        expense_date=date.today(),
        split_type=SplitType.EXACT,
        participant_ids=[rafal, domino],
        exact_amounts={
            rafal: Decimal("50"),
            domino: Decimal("50"),
        },
    )
    assert expense.split_type == SplitType.EXACT
    assert expense.participant_ids == [rafal, domino]
    assert expense.amount == Decimal("100")
    assert expense.exact_amounts == {rafal: Decimal("50"), domino: Decimal("50")}

def test_exact_split_missing_details_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    with pytest.raises(ValidationError):
        expense = ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.EXACT,
            participant_ids=[rafal, domino],
        )       

def test_exact_split_wrong_details_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    with pytest.raises(ValidationError):
        expense = ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.EXACT,
            participant_ids=[rafal, domino],
            exact_amounts={
                rafal: Decimal("50"),
            },
        )           

def test_exact_split_extra_key_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    intruder = generatorUuid()
    
    with pytest.raises(ValidationError):
        ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.EXACT,
            participant_ids=[rafal, domino],
            exact_amounts={
                rafal: Decimal("50"),
                intruder: Decimal("50"),
            },
        )

def test_percent_split_valid():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    expense = ExpenseCreate(
        description="Test",
        amount=Decimal("100"),
        currency="PLN",
        expense_date=date.today(),
        split_type=SplitType.PERCENT,
        participant_ids=[rafal, domino],
        percentages={
            rafal: Decimal("50"),
            domino: Decimal("50"),
        },
    )
    assert expense.split_type == SplitType.PERCENT
    assert expense.participant_ids == [rafal, domino]
    assert expense.amount == Decimal("100")
    assert expense.percentages == {rafal: Decimal("50"), domino: Decimal("50")}

def test_percent_split_missing_details_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    with pytest.raises(ValidationError):
        expense = ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.PERCENT,
            participant_ids=[rafal, domino],
        )           

def test_percent_split_wrong_details_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    with pytest.raises(ValidationError):
        expense = ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.PERCENT,
            participant_ids=[rafal, domino],
            percentages={
                rafal: Decimal("50"),
            },
        )           

def test_percent_split_extra_key_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    intruder = generatorUuid()
    
    with pytest.raises(ValidationError):
        ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.PERCENT,
            participant_ids=[rafal, domino],
            percentages={
                rafal: Decimal("50"),
                intruder: Decimal("50"),
            },
        )

def test_shares_split_valid():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    expense = ExpenseCreate(
        description="Test",
        amount=Decimal("100"),
        currency="PLN",
        expense_date=date.today(),
        split_type=SplitType.SHARES,
        participant_ids=[rafal, domino],
        shares={
            rafal: 1,
            domino: 1,
        },
    )
    assert expense.split_type == SplitType.SHARES
    assert expense.participant_ids == [rafal, domino]
    assert expense.amount == Decimal("100")
    assert expense.shares == {rafal: 1, domino: 1}

def test_shares_split_missing_details_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    with pytest.raises(ValidationError):
        expense = ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.SHARES,
            participant_ids=[rafal, domino],
        )           

def test_shares_split_wrong_details_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    
    with pytest.raises(ValidationError):
        expense = ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.SHARES,
            participant_ids=[rafal, domino],
            shares={
                rafal: 1,
            },
        )           

def test_shares_split_extra_key_raises_error():
    rafal = generatorUuid()
    domino = generatorUuid()
    intruder = generatorUuid()
    
    with pytest.raises(ValidationError):
        ExpenseCreate(
            description="Test",
            amount=Decimal("100"),
            currency="PLN",
            expense_date=date.today(),
            split_type=SplitType.SHARES,
            participant_ids=[rafal, domino],
            shares={
                rafal: 1,
                intruder: 2,
            },
        )
import uuid
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserLogin, Token
from app.schemas.group import GroupCreate, GroupUpdate, MemberResponse
from app.schemas.expense import ExpenseCreate
from app.schemas.settlement import SettlementCreate
from app.schemas.currency import ConvertRequest, ConvertResponse
from app.db.models.expense import SplitType
from app.db.models.group import GroupRole


def test_user_create_invalid_email_raises():
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", password="secret", display_name="X")


def test_user_create_missing_password_raises():
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.com", display_name="X")


def test_token_default_type_is_bearer():
    t = Token(access_token="abc.def.ghi")
    assert t.token_type == "bearer"


def test_user_login_invalid_email_raises():
    with pytest.raises(ValidationError):
        UserLogin(email="invalid", password="pass")


def test_group_create_missing_name_raises():
    with pytest.raises(ValidationError):
        GroupCreate()


def test_group_update_both_none_allowed():
    g = GroupUpdate()
    assert g.name is None
    assert g.description is None


def test_member_response_role_admin():
    uid = uuid.uuid4()
    m = MemberResponse(user_id=uid, display_name="Rafal", email="r@r.com", role=GroupRole.ADMIN)
    assert m.role == GroupRole.ADMIN


def test_expense_create_currency_defaults_to_pln():
    a = uuid.uuid4()
    e = ExpenseCreate(
        description="X", amount=Decimal("50"), expense_date=date.today(),
        split_type=SplitType.EQUAL, participant_ids=[a],
    )
    assert e.currency == "PLN"


def test_expense_create_currency_override():
    a = uuid.uuid4()
    e = ExpenseCreate(
        description="X", amount=Decimal("30"), currency="EUR",
        expense_date=date.today(), split_type=SplitType.EQUAL, participant_ids=[a],
    )
    assert e.currency == "EUR"


def test_expense_create_shares_unequal_values():
    a, b, c = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    e = ExpenseCreate(
        description="T", amount=Decimal("100"), expense_date=date.today(),
        split_type=SplitType.SHARES, participant_ids=[a, b, c], shares={a: 3, b: 2, c: 1},
    )
    assert e.shares[a] == 3
    assert e.shares[c] == 1


def test_settlement_create_default_currency():
    s = SettlementCreate(paid_to=uuid.uuid4(), amount=Decimal("75"))
    assert s.currency == "PLN"


def test_convert_request_defaults():
    r = ConvertRequest(amount=Decimal("100"))
    assert r.from_currency == "EUR"
    assert r.to_currency == "PLN"
    assert r.rate_date is None


def test_convert_response_fields():
    r = ConvertResponse(
        original_amount=Decimal("100"),
        from_currency="EUR",
        converted_amount=Decimal("432"),
        to_currency="PLN",
        rate=Decimal("4.32"),
        rate_date=date.today(),
    )
    assert r.rate == Decimal("4.32")
    assert r.from_currency == "EUR"




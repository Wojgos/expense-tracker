import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.group import (
    create_group,
    get_group_by_id,
    update_group,
    delete_group,
    get_user_membership,
    add_member,
    remove_member,
)
from app.crud.settlement import create_settlement, get_settlements_for_group
from app.crud.expense import create_expense, get_expense_by_id, delete_expense, _compute_splits
from app.db.models.group import Group, GroupRole, UserGroup
from app.db.models.expense import Expense, SplitType
from app.schemas.expense import ExpenseCreate


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
class TestGroupCRUD:

    async def test_create_group_creator_gets_admin_role(self, mock_db):
        creator_id = uuid.uuid4()
        await create_group(mock_db, "Test", None, creator_id)
        membership_call = mock_db.add.call_args_list[1][0][0]
        assert isinstance(membership_call, UserGroup)
        assert membership_call.role == GroupRole.ADMIN
        assert membership_call.user_id == creator_id

    async def test_create_group_no_description(self, mock_db):
        group = await create_group(mock_db, "Dom", None, uuid.uuid4())
        assert group.description is None
        assert mock_db.add.call_count == 2

    async def test_get_group_by_id_not_found(self, mock_db):
        mock_db.get.return_value = None
        assert await get_group_by_id(mock_db, uuid.uuid4()) is None

    async def test_update_group_only_name(self, mock_db):
        group = Group(name="Stara", description="Opis", created_by=uuid.uuid4())
        updated = await update_group(mock_db, group, name="Nowa", description=None)
        assert updated.name == "Nowa"
        assert updated.description == "Opis"

    async def test_update_group_both_fields(self, mock_db):
        group = Group(name="A", description="B", created_by=uuid.uuid4())
        updated = await update_group(mock_db, group, name="X", description="Y")
        assert updated.name == "X"
        assert updated.description == "Y"

    async def test_delete_group_calls_delete_and_flush(self, mock_db):
        group = Group(name="Del", created_by=uuid.uuid4())
        await delete_group(mock_db, group)
        mock_db.delete.assert_called_once_with(group)
        mock_db.flush.assert_called_once()

    async def test_get_user_membership_not_found(self, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        assert await get_user_membership(mock_db, uuid.uuid4(), uuid.uuid4()) is None

    async def test_add_member_default_role(self, mock_db):
        uid, gid = uuid.uuid4(), uuid.uuid4()
        membership = await add_member(mock_db, gid, uid)
        assert membership.role == GroupRole.MEMBER
        assert membership.user_id == uid
        assert membership.group_id == gid

    async def test_add_member_admin_role(self, mock_db):
        membership = await add_member(mock_db, uuid.uuid4(), uuid.uuid4(), role=GroupRole.ADMIN)
        assert membership.role == GroupRole.ADMIN

    async def test_remove_member_calls_delete(self, mock_db):
        membership = UserGroup(user_id=uuid.uuid4(), group_id=uuid.uuid4())
        await remove_member(mock_db, membership)
        mock_db.delete.assert_called_once_with(membership)


@pytest.mark.asyncio
class TestSettlementCRUD:

    async def test_create_settlement_fields(self, mock_db):
        gid, payer, receiver = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        s = await create_settlement(mock_db, gid, payer, receiver, Decimal("50.00"))
        assert s.group_id == gid
        assert s.paid_by == payer
        assert s.paid_to == receiver
        assert s.amount == Decimal("50.00")
        assert s.currency == "PLN"

    async def test_create_settlement_custom_currency(self, mock_db):
        s = await create_settlement(
            mock_db, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), Decimal("100.00"), currency="EUR"
        )
        assert s.currency == "EUR"

    async def test_get_settlements_empty(self, mock_db):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        assert await get_settlements_for_group(mock_db, uuid.uuid4()) == []


@pytest.mark.asyncio
class TestExpenseCRUD:

    async def test_create_expense_stores_fields(self, mock_db):
        gid, payer, a, b = uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        data = ExpenseCreate(
            description="Obiad",
            amount=Decimal("100"),
            expense_date=date.today(),
            split_type=SplitType.EQUAL,
            participant_ids=[a, b],
        )
        expense = await create_expense(mock_db, gid, payer, data)
        assert expense.group_id == gid
        assert expense.paid_by == payer
        assert expense.amount == Decimal("100")
        assert expense.description == "Obiad"

    async def test_get_expense_by_id_not_found(self, mock_db):
        mock_db.get.return_value = None
        assert await get_expense_by_id(mock_db, uuid.uuid4()) is None

    async def test_delete_expense_calls_delete(self, mock_db):
        expense = Expense(description="Del", amount=Decimal("5"))
        await delete_expense(mock_db, expense)
        mock_db.delete.assert_called_once_with(expense)
        mock_db.flush.assert_called_once()

    def test_compute_splits_shares_proportional(self):
        a, b = uuid.uuid4(), uuid.uuid4()
        data = ExpenseCreate(
            description="T", amount=Decimal("100"), expense_date=date.today(),
            split_type=SplitType.SHARES, participant_ids=[a, b], shares={a: 1, b: 3},
        )
        result = _compute_splits(data)
        assert result[a] == Decimal("25.00")
        assert result[b] == Decimal("75.00")

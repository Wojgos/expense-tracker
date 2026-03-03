import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.expense import Expense, ExpenseSplit, SplitType
from app.schemas.expense import ExpenseCreate
from app.services.split_calculator import (
    calculate_equal_split,
    calculate_exact_split,
    calculate_percent_split,
    calculate_shares_split,
)


def _compute_splits(
    data: ExpenseCreate,
) -> dict[uuid.UUID, Decimal]:
    match data.split_type:
        case SplitType.EQUAL:
            return calculate_equal_split(data.amount, data.participant_ids)
        case SplitType.EXACT:
            return calculate_exact_split(data.amount, data.exact_amounts)
        case SplitType.PERCENT:
            return calculate_percent_split(data.amount, data.percentages)
        case SplitType.SHARES:
            return calculate_shares_split(data.amount, data.shares)


async def create_expense(
    db: AsyncSession,
    group_id: uuid.UUID,
    paid_by: uuid.UUID,
    data: ExpenseCreate,
) -> Expense:
    split_map = _compute_splits(data)

    expense = Expense(
        group_id=group_id,
        paid_by=paid_by,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        split_type=data.split_type,
        expense_date=data.expense_date,
    )
    db.add(expense)
    await db.flush()

    for user_id, owed in split_map.items():
        split = ExpenseSplit(
            expense_id=expense.id, user_id=user_id, owed_amount=owed
        )
        db.add(split)

    await db.flush()
    return expense


async def get_expenses_for_group(
    db: AsyncSession, group_id: uuid.UUID
) -> list[Expense]:
    stmt = (
        select(Expense)
        .where(Expense.group_id == group_id)
        .order_by(Expense.expense_date.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_expense_by_id(
    db: AsyncSession, expense_id: uuid.UUID
) -> Expense | None:
    return await db.get(Expense, expense_id)


async def delete_expense(db: AsyncSession, expense: Expense) -> None:
    await db.delete(expense)
    await db.flush()

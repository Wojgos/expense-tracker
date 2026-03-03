import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.recurring_expense import RecurringExpense


async def create_recurring_expense(
    db: AsyncSession, group_id: uuid.UUID, created_by: uuid.UUID, **kwargs
) -> RecurringExpense:
    rec = RecurringExpense(group_id=group_id, created_by=created_by, **kwargs)
    db.add(rec)
    await db.flush()
    return rec


async def get_recurring_expenses_for_group(
    db: AsyncSession, group_id: uuid.UUID
) -> list[RecurringExpense]:
    stmt = (
        select(RecurringExpense)
        .where(RecurringExpense.group_id == group_id, RecurringExpense.is_active.is_(True))
        .order_by(RecurringExpense.next_run)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_due_recurring_expenses(
    db: AsyncSession, today: date
) -> list[RecurringExpense]:
    stmt = select(RecurringExpense).where(
        RecurringExpense.is_active.is_(True),
        RecurringExpense.next_run <= today,
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def deactivate_recurring_expense(
    db: AsyncSession, rec: RecurringExpense
) -> None:
    rec.is_active = False
    await db.flush()

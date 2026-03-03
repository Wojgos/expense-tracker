import logging
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from sqlalchemy import select

from app.crud.recurring_expense import get_due_recurring_expenses
from app.db.models.expense import Expense, ExpenseSplit, SplitType
from app.db.models.group import UserGroup
from app.db.models.recurring_expense import RecurrenceInterval
from app.db.session import async_session_factory
from app.services.notification_manager import manager
from app.services.split_calculator import calculate_equal_split

logger = logging.getLogger(__name__)


def _compute_next_run(current: date, interval: RecurrenceInterval) -> date:
    match interval:
        case RecurrenceInterval.WEEKLY:
            return current + timedelta(weeks=1)
        case RecurrenceInterval.MONTHLY:
            return current + relativedelta(months=1)
        case RecurrenceInterval.YEARLY:
            return current + relativedelta(years=1)


async def process_recurring_expenses():
    """Called daily by APScheduler. Creates expenses from recurring templates."""
    logger.info("Processing recurring expenses...")
    today = date.today()

    async with async_session_factory() as db:
        try:
            due_items = await get_due_recurring_expenses(db, today)
            logger.info("Found %d due recurring expenses", len(due_items))

            for rec in due_items:
                stmt = select(UserGroup.user_id).where(
                    UserGroup.group_id == rec.group_id
                )
                result = await db.execute(stmt)
                member_ids = [row[0] for row in result.all()]

                if not member_ids:
                    continue

                if rec.split_type == SplitType.EQUAL:
                    split_map = calculate_equal_split(rec.amount, member_ids)
                else:
                    split_map = calculate_equal_split(rec.amount, member_ids)

                expense = Expense(
                    group_id=rec.group_id,
                    paid_by=rec.created_by,
                    amount=rec.amount,
                    currency=rec.currency,
                    description=f"[Recurring] {rec.description}",
                    split_type=rec.split_type,
                    expense_date=today,
                )
                db.add(expense)
                await db.flush()

                for uid, owed in split_map.items():
                    db.add(ExpenseSplit(
                        expense_id=expense.id, user_id=uid, owed_amount=owed
                    ))

                rec.next_run = _compute_next_run(rec.next_run, rec.interval)

                await manager.broadcast_to_group(rec.group_id, {
                    "type": "recurring_expense_generated",
                    "expense_id": str(expense.id),
                    "description": expense.description,
                    "amount": str(expense.amount),
                })

            await db.commit()
            logger.info("Recurring expenses processed successfully")
        except Exception:
            await db.rollback()
            logger.exception("Failed to process recurring expenses")

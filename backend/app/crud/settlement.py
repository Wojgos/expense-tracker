import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.settlement import Settlement


async def create_settlement(
    db: AsyncSession,
    group_id: uuid.UUID,
    paid_by: uuid.UUID,
    paid_to: uuid.UUID,
    amount: Decimal,
    currency: str = "PLN",
) -> Settlement:
    settlement = Settlement(
        group_id=group_id,
        paid_by=paid_by,
        paid_to=paid_to,
        amount=amount,
        currency=currency,
    )
    db.add(settlement)
    await db.flush()
    return settlement


async def get_settlements_for_group(
    db: AsyncSession, group_id: uuid.UUID
) -> list[Settlement]:
    stmt = (
        select(Settlement)
        .where(Settlement.group_id == group_id)
        .order_by(Settlement.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

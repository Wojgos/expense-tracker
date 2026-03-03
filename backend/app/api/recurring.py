import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.group import get_group_by_id, get_user_membership
from app.crud.recurring_expense import (
    create_recurring_expense,
    deactivate_recurring_expense,
    get_recurring_expenses_for_group,
)
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.recurring_expense import RecurringExpenseCreate, RecurringExpenseResponse

router = APIRouter(
    prefix="/groups/{group_id}/recurring-expenses", tags=["recurring-expenses"]
)


@router.post("/", response_model=RecurringExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring(
    group_id: uuid.UUID,
    data: RecurringExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    membership = await get_user_membership(db, current_user.id, group_id)
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    rec = await create_recurring_expense(
        db,
        group_id=group_id,
        created_by=current_user.id,
        description=data.description,
        amount=data.amount,
        currency=data.currency,
        split_type=data.split_type,
        interval=data.interval,
        day_of_month=data.day_of_month,
        next_run=data.start_date,
    )
    return RecurringExpenseResponse(
        id=rec.id,
        group_id=rec.group_id,
        created_by=rec.created_by,
        creator_name=current_user.display_name,
        description=rec.description,
        amount=rec.amount,
        currency=rec.currency,
        split_type=rec.split_type,
        interval=rec.interval,
        day_of_month=rec.day_of_month,
        next_run=rec.next_run,
        is_active=rec.is_active,
    )


@router.get("/", response_model=list[RecurringExpenseResponse])
async def list_recurring(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership = await get_user_membership(db, current_user.id, group_id)
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    items = await get_recurring_expenses_for_group(db, group_id)
    return [
        RecurringExpenseResponse(
            id=r.id,
            group_id=r.group_id,
            created_by=r.created_by,
            creator_name=r.creator.display_name,
            description=r.description,
            amount=r.amount,
            currency=r.currency,
            split_type=r.split_type,
            interval=r.interval,
            day_of_month=r.day_of_month,
            next_run=r.next_run,
            is_active=r.is_active,
        )
        for r in items
    ]


@router.delete("/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_recurring(
    group_id: uuid.UUID,
    recurring_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership = await get_user_membership(db, current_user.id, group_id)
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    from sqlalchemy import select
    from app.db.models.recurring_expense import RecurringExpense

    stmt = select(RecurringExpense).where(
        RecurringExpense.id == recurring_id,
        RecurringExpense.group_id == group_id,
    )
    result = await db.execute(stmt)
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring expense not found")

    await deactivate_recurring_expense(db, rec)

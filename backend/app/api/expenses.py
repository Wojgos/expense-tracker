import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.expense import (
    create_expense,
    delete_expense,
    get_expense_by_id,
    get_expenses_for_group,
)
from app.crud.group import get_group_by_id, get_user_membership
from app.db.models.group import GroupRole
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.expense import ExpenseCreate, ExpenseResponse, SplitDetail
from app.services.notification_manager import manager

router = APIRouter(prefix="/groups/{group_id}/expenses", tags=["expenses"])


async def _require_membership(
    db: AsyncSession, user_id: uuid.UUID, group_id: uuid.UUID
):
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    membership = await get_user_membership(db, user_id, group_id)
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    return membership


def _build_expense_response(expense) -> ExpenseResponse:
    return ExpenseResponse(
        id=expense.id,
        group_id=expense.group_id,
        paid_by=expense.paid_by,
        payer_name=expense.payer.display_name,
        amount=expense.amount,
        currency=expense.currency,
        description=expense.description,
        split_type=expense.split_type,
        expense_date=expense.expense_date,
        created_at=expense.created_at,
        splits=[
            SplitDetail(user_id=s.user_id, owed_amount=s.owed_amount)
            for s in expense.splits
        ],
    )


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_endpoint(
    group_id: uuid.UUID,
    data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_membership(db, current_user.id, group_id)

    try:
        expense = await create_expense(db, group_id, current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    await db.refresh(expense)

    await manager.broadcast_to_group(group_id, {
        "type": "expense_created",
        "expense_id": str(expense.id),
        "description": expense.description,
        "amount": str(expense.amount),
        "payer_name": current_user.display_name,
    })

    return _build_expense_response(expense)


@router.get("/", response_model=list[ExpenseResponse])
async def list_expenses(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_membership(db, current_user.id, group_id)
    expenses = await get_expenses_for_group(db, group_id)
    return [_build_expense_response(e) for e in expenses]


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    group_id: uuid.UUID,
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_membership(db, current_user.id, group_id)

    expense = await get_expense_by_id(db, expense_id)
    if not expense or expense.group_id != group_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    return _build_expense_response(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_endpoint(
    group_id: uuid.UUID,
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership = await _require_membership(db, current_user.id, group_id)

    expense = await get_expense_by_id(db, expense_id)
    if not expense or expense.group_id != group_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    is_payer = expense.paid_by == current_user.id
    is_admin = membership.role == GroupRole.ADMIN
    if not is_payer and not is_admin:
        raise HTTPException(
            status_code=403, detail="Only the payer or a group admin can delete this expense"
        )

    await delete_expense(db, expense)

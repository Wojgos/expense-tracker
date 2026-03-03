import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.expense import get_expenses_for_group
from app.crud.group import get_group_by_id, get_user_membership
from app.crud.settlement import create_settlement, get_settlements_for_group
from app.crud.user import get_user_by_id
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.settlement import (
    BalanceItem,
    GroupSettlementSummary,
    SettlementCreate,
    SettlementResponse,
    SuggestedTransferResponse,
)
from app.services.notification_manager import manager
from app.services.settlement_engine import compute_balances, minimize_transactions

router = APIRouter(prefix="/groups/{group_id}/settlements", tags=["settlements"])


def _expense_to_dict(expense) -> dict:
    return {
        "paid_by": expense.paid_by,
        "splits": [
            {"user_id": s.user_id, "owed_amount": s.owed_amount}
            for s in expense.splits
        ],
    }


def _settlement_to_dict(settlement) -> dict:
    return {
        "paid_by": settlement.paid_by,
        "paid_to": settlement.paid_to,
        "amount": settlement.amount,
    }


async def _require_membership(
    db: AsyncSession, user_id: uuid.UUID, group_id: uuid.UUID
):
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    membership = await get_user_membership(db, user_id, group_id)
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    return group


@router.get("/", response_model=GroupSettlementSummary)
async def get_settlement_summary(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = await _require_membership(db, current_user.id, group_id)

    expenses = await get_expenses_for_group(db, group_id)
    settlements = await get_settlements_for_group(db, group_id)

    expense_dicts = [_expense_to_dict(e) for e in expenses]
    settlement_dicts = [_settlement_to_dict(s) for s in settlements]

    raw_balances = compute_balances(expense_dicts, settlement_dicts)
    suggested = minimize_transactions(raw_balances)

    user_cache: dict[uuid.UUID, User] = {}
    all_user_ids = set(raw_balances.keys())
    for uid in all_user_ids:
        user_cache[uid] = await get_user_by_id(db, uid)

    balances = [
        BalanceItem(
            user_id=uid,
            display_name=user_cache[uid].display_name if user_cache.get(uid) else "?",
            balance=bal,
        )
        for uid, bal in raw_balances.items()
    ]

    suggested_responses = [
        SuggestedTransferResponse(
            from_user=t.from_user,
            from_name=user_cache[t.from_user].display_name if user_cache.get(t.from_user) else "?",
            to_user=t.to_user,
            to_name=user_cache[t.to_user].display_name if user_cache.get(t.to_user) else "?",
            amount=t.amount,
        )
        for t in suggested
    ]

    settlement_responses = [
        SettlementResponse(
            id=s.id,
            group_id=s.group_id,
            paid_by=s.paid_by,
            payer_name=s.payer.display_name,
            paid_to=s.paid_to,
            receiver_name=s.receiver.display_name,
            amount=s.amount,
            currency=s.currency,
            created_at=s.created_at,
        )
        for s in settlements
    ]

    return GroupSettlementSummary(
        balances=balances,
        suggested_transfers=suggested_responses,
        settlements=settlement_responses,
    )


@router.post("/", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
async def settle_up(
    group_id: uuid.UUID,
    data: SettlementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_membership(db, current_user.id, group_id)

    if data.amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be positive")

    if data.paid_to == current_user.id:
        raise HTTPException(status_code=422, detail="Cannot settle with yourself")

    receiver = await get_user_by_id(db, data.paid_to)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    receiver_membership = await get_user_membership(db, data.paid_to, group_id)
    if not receiver_membership:
        raise HTTPException(status_code=422, detail="Receiver is not a member of this group")

    settlement = await create_settlement(
        db, group_id, current_user.id, data.paid_to, data.amount, data.currency
    )
    await db.refresh(settlement)

    await manager.broadcast_to_group(group_id, {
        "type": "settlement_created",
        "settlement_id": str(settlement.id),
        "payer_name": current_user.display_name,
        "receiver_name": receiver.display_name,
        "amount": str(settlement.amount),
    })

    return SettlementResponse(
        id=settlement.id,
        group_id=settlement.group_id,
        paid_by=settlement.paid_by,
        payer_name=settlement.payer.display_name,
        paid_to=settlement.paid_to,
        receiver_name=settlement.receiver.display_name,
        amount=settlement.amount,
        currency=settlement.currency,
        created_at=settlement.created_at,
    )

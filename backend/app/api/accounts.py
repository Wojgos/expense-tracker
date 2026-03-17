import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.crud_account import (
    create_account,
    create_transaction,
    delete_account,
    get_account_transactions,
    get_accounts_by_user,
)
from app.db.models.user import User
from app.schemas.account import (
    AccountCreate,
    AccountResponse,
    TransactionCreate,
    TransactionResponse,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountResponse])
async def read_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[AccountResponse]:
    """
    Retrieve accounts for the currently authenticated user.
    """
    return await get_accounts_by_user(db, user_id=current_user.id)


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_new_account(
    account_in: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountResponse:
    """
    Create a new account for the current user.
    """
    return await create_account(db, obj_in=account_in, user_id=current_user.id)


@router.get("/{account_id}/transactions", response_model=list[TransactionResponse])
async def read_account_transactions(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[TransactionResponse]:
    """
    Retrieve all transactions for a specific account.
    """
    return await get_account_transactions(db, account_id=account_id, user_id=current_user.id)


@router.post(
    "/{account_id}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_account_transaction(
    account_id: uuid.UUID,
    transaction_in: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    """
    Create a new transaction (income/expense) for a specific account.
    """
    transaction = await create_transaction(
        db, obj_in=transaction_in, account_id=account_id, user_id=current_user.id
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found or belongs to another user",
        )
    return transaction


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account_endpoint(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete an account and all its transactions.
    """
    deleted = await delete_account(db, account_id=account_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found or belongs to another user",
        )

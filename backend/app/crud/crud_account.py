import uuid
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.account import Account
from app.db.models.transaction import AccountTransaction
from app.schemas.account import AccountCreate, AccountUpdate, TransactionCreate


async def create_account(
    db: AsyncSession, *, obj_in: AccountCreate, user_id: uuid.UUID
) -> Account:
    db_obj = Account(
        user_id=user_id,
        name=obj_in.name,
        type=obj_in.type,
        currency=obj_in.currency,
        balance=obj_in.balance,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_accounts_by_user(
    db: AsyncSession, *, user_id: uuid.UUID
) -> Sequence[Account]:
    result = await db.execute(select(Account).where(Account.user_id == user_id))
    return result.scalars().all()


async def get_account(
    db: AsyncSession, *, account_id: uuid.UUID, user_id: uuid.UUID
) -> Account | None:
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_transaction(
    db: AsyncSession, *, obj_in: TransactionCreate, account_id: uuid.UUID, user_id: uuid.UUID
) -> AccountTransaction | None:
    # First verify account exists and belongs to user
    account_result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == user_id)
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        return None

    # Create transaction
    db_transaction = AccountTransaction(
        account_id=account_id,
        amount=obj_in.amount,
        currency=obj_in.currency,
        description=obj_in.description,
        transaction_date=obj_in.transaction_date,
    )
    db.add(db_transaction)

    # Update balance
    account.balance += obj_in.amount

    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction


async def get_account_transactions(
    db: AsyncSession, *, account_id: uuid.UUID, user_id: uuid.UUID
) -> Sequence[AccountTransaction]:
    # Check if account belongs to user
    account = await get_account(db, account_id=account_id, user_id=user_id)
    if not account:
        return []
    
    result = await db.execute(
        select(AccountTransaction)
        .where(AccountTransaction.account_id == account_id)
        .order_by(AccountTransaction.transaction_date.desc())
    )
    return result.scalars().all()


async def delete_account(
    db: AsyncSession, *, account_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    account = await get_account(db, account_id=account_id, user_id=user_id)
    if not account:
        return False
    await db.delete(account)
    await db.commit()
    return True

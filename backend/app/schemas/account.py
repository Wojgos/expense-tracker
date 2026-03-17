import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
    description: str = Field(max_length=300)
    transaction_date: date


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: uuid.UUID
    account_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class AccountBase(BaseModel):
    name: str = Field(max_length=100)
    type: str = Field(max_length=50) # Cash, Debit, etc.
    currency: str = Field(default="PLN", min_length=3, max_length=3)


class AccountCreate(AccountBase):
    balance: Decimal = Field(default=Decimal("0.00"))


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=50)


class AccountResponse(AccountBase):
    id: uuid.UUID
    user_id: uuid.UUID
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)


class AccountWithTransactionsResponse(AccountResponse):
    transactions: list[TransactionResponse] = []

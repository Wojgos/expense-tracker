import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SettlementCreate(BaseModel):
    paid_to: uuid.UUID
    amount: Decimal
    currency: str = "PLN"


class SettlementResponse(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    paid_by: uuid.UUID
    payer_name: str
    paid_to: uuid.UUID
    receiver_name: str
    amount: Decimal
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BalanceItem(BaseModel):
    user_id: uuid.UUID
    display_name: str
    balance: Decimal


class SuggestedTransferResponse(BaseModel):
    from_user: uuid.UUID
    from_name: str
    to_user: uuid.UUID
    to_name: str
    amount: Decimal


class GroupSettlementSummary(BaseModel):
    balances: list[BalanceItem]
    suggested_transfers: list[SuggestedTransferResponse]
    settlements: list[SettlementResponse]

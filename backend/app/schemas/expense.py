import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, model_validator

from app.db.models.expense import SplitType


class SplitDetail(BaseModel):
    user_id: uuid.UUID
    owed_amount: Decimal

    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    description: str
    amount: Decimal
    currency: str = "PLN"
    split_type: SplitType
    expense_date: date
    participant_ids: list[uuid.UUID]
    exact_amounts: dict[uuid.UUID, Decimal] | None = None
    percentages: dict[uuid.UUID, Decimal] | None = None
    shares: dict[uuid.UUID, int] | None = None
    account_id: uuid.UUID | None = None  # optional: deduct from personal account

    @model_validator(mode="after")
    def validate_split_data(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")

        if len(self.participant_ids) == 0:
            raise ValueError("At least one participant is required")

        ids = set(self.participant_ids)

        if self.split_type == SplitType.EXACT:
            if not self.exact_amounts:
                raise ValueError("exact_amounts required for exact split")
            if set(self.exact_amounts.keys()) != ids:
                raise ValueError("exact_amounts keys must match participant_ids")

        elif self.split_type == SplitType.PERCENT:
            if not self.percentages:
                raise ValueError("percentages required for percent split")
            if set(self.percentages.keys()) != ids:
                raise ValueError("percentages keys must match participant_ids")

        elif self.split_type == SplitType.SHARES:
            if not self.shares:
                raise ValueError("shares required for shares split")
            if set(self.shares.keys()) != ids:
                raise ValueError("shares keys must match participant_ids")

        return self


class ExpenseResponse(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    paid_by: uuid.UUID
    payer_name: str
    amount: Decimal
    currency: str
    description: str
    split_type: SplitType
    expense_date: date
    created_at: datetime
    splits: list[SplitDetail] = []

    model_config = {"from_attributes": True}

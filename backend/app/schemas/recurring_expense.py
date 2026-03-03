import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.db.models.expense import SplitType
from app.db.models.recurring_expense import RecurrenceInterval


class RecurringExpenseCreate(BaseModel):
    description: str
    amount: Decimal
    currency: str = "PLN"
    split_type: SplitType
    interval: RecurrenceInterval
    day_of_month: int | None = None
    start_date: date


class RecurringExpenseResponse(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    created_by: uuid.UUID
    creator_name: str
    description: str
    amount: Decimal
    currency: str
    split_type: SplitType
    interval: RecurrenceInterval
    day_of_month: int | None
    next_run: date
    is_active: bool

    model_config = {"from_attributes": True}

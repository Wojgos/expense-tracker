import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.db.models.expense import SplitType


class RecurrenceInterval(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class RecurringExpense(BaseModel):
    __tablename__ = "recurring_expenses"

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    description: Mapped[str] = mapped_column(String(300))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    split_type: Mapped[SplitType] = mapped_column(Enum(SplitType))

    interval: Mapped[RecurrenceInterval] = mapped_column(Enum(RecurrenceInterval))
    day_of_month: Mapped[int | None] = mapped_column(Integer, default=None)
    next_run: Mapped[date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    creator: Mapped["User"] = relationship(lazy="selectin")


from app.db.models.user import User  # noqa: E402

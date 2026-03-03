import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class SplitType(str, enum.Enum):
    EQUAL = "equal"
    EXACT = "exact"
    PERCENT = "percent"
    SHARES = "shares"


class Expense(BaseModel):
    __tablename__ = "expenses"

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), index=True
    )
    paid_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    description: Mapped[str] = mapped_column(String(300))
    split_type: Mapped[SplitType] = mapped_column(Enum(SplitType))
    expense_date: Mapped[date] = mapped_column(Date)

    splits: Mapped[list["ExpenseSplit"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan", lazy="selectin"
    )
    payer: Mapped["User"] = relationship(lazy="selectin")


class ExpenseSplit(BaseModel):
    __tablename__ = "expense_splits"

    expense_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    owed_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    expense: Mapped["Expense"] = relationship(back_populates="splits", viewonly=True)
    user: Mapped["User"] = relationship(lazy="selectin")


from app.db.models.user import User  # noqa: E402

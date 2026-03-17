import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class AccountTransaction(BaseModel):
    __tablename__ = "account_transactions"

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), index=True
    )
    # positive for income, negative for expense
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    description: Mapped[str] = mapped_column(String(300))
    transaction_date: Mapped[date] = mapped_column(Date)

    account: Mapped["Account"] = relationship(back_populates="transactions", viewonly=True)

from app.db.models.account import Account  # noqa: E402

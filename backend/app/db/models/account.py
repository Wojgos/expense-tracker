import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class Account(BaseModel):
    __tablename__ = "accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))  # e.g., 'Cash', 'Debit Card', 'Credit Card', 'Savings'
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0.00)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")

    user: Mapped["User"] = relationship(lazy="selectin")
    transactions: Mapped[list["AccountTransaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan", lazy="selectin"
    )

from app.db.models.user import User  # noqa: E402

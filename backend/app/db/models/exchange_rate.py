from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class ExchangeRate(BaseModel):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        UniqueConstraint("base_currency", "target_currency", "rate_date", name="uq_rate"),
    )

    base_currency: Mapped[str] = mapped_column(String(3), index=True)
    target_currency: Mapped[str] = mapped_column(String(3), index=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(14, 6))
    rate_date: Mapped[date] = mapped_column(Date)

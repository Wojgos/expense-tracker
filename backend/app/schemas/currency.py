from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ConvertRequest(BaseModel):
    amount: Decimal
    from_currency: str = "EUR"
    to_currency: str = "PLN"
    rate_date: date | None = None


class ConvertResponse(BaseModel):
    original_amount: Decimal
    from_currency: str
    converted_amount: Decimal
    to_currency: str
    rate: Decimal
    rate_date: date


class RateResponse(BaseModel):
    base: str
    target: str
    rate: Decimal
    rate_date: date

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.currency import ConvertRequest, ConvertResponse, RateResponse
from app.services.currency_service import convert_amount, get_exchange_rate

router = APIRouter(prefix="/currency", tags=["currency"])


@router.get("/rate", response_model=RateResponse)
async def get_rate(
    base: str = Query(default="EUR", max_length=3),
    target: str = Query(default="PLN", max_length=3),
    rate_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = rate_date or date.today()
    rate = await get_exchange_rate(db, base.upper(), target.upper(), today)
    if rate is None:
        raise HTTPException(
            status_code=404, detail=f"Exchange rate not found for {base}->{target}"
        )
    return RateResponse(base=base.upper(), target=target.upper(), rate=rate, rate_date=today)


@router.post("/convert", response_model=ConvertResponse)
async def convert(
    data: ConvertRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = data.rate_date or date.today()
    base = data.from_currency.upper()
    target = data.to_currency.upper()

    rate = await get_exchange_rate(db, base, target, today)
    if rate is None:
        raise HTTPException(
            status_code=404, detail=f"Exchange rate not found for {base}->{target}"
        )

    converted = (data.amount * rate).quantize(Decimal("0.01"))
    return ConvertResponse(
        original_amount=data.amount,
        from_currency=base,
        converted_amount=converted,
        to_currency=target,
        rate=rate,
        rate_date=today,
    )

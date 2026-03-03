import json
import logging
from datetime import date
from decimal import Decimal

import httpx
import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.exchange_rate import ExchangeRate

logger = logging.getLogger(__name__)

NBP_API_URL = "https://api.nbp.pl/api/exchangerates/tables/A/?format=json"

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis | None:
    global _redis
    if _redis is None:
        try:
            _redis = aioredis.from_url(
                settings.redis_url, decode_responses=True
            )
            await _redis.ping()
        except Exception:
            logger.warning("Redis unavailable, proceeding without cache")
            _redis = None
    return _redis


def _cache_key(base: str, target: str, rate_date: date) -> str:
    return f"rate:{base}:{target}:{rate_date.isoformat()}"


async def _get_from_redis(base: str, target: str, rate_date: date) -> Decimal | None:
    r = await get_redis()
    if not r:
        return None
    try:
        val = await r.get(_cache_key(base, target, rate_date))
        return Decimal(val) if val else None
    except Exception:
        return None


async def _set_in_redis(base: str, target: str, rate_date: date, rate: Decimal) -> None:
    r = await get_redis()
    if not r:
        return
    try:
        await r.set(
            _cache_key(base, target, rate_date),
            str(rate),
            ex=settings.exchange_rate_cache_ttl,
        )
    except Exception:
        pass


async def _get_from_db(
    db: AsyncSession, base: str, target: str, rate_date: date | None = None
) -> Decimal | None:
    stmt = select(ExchangeRate.rate).where(
        ExchangeRate.base_currency == base,
        ExchangeRate.target_currency == target,
    )
    if rate_date:
        stmt = stmt.where(ExchangeRate.rate_date == rate_date)
    stmt = stmt.order_by(ExchangeRate.rate_date.desc()).limit(1)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _save_to_db(
    db: AsyncSession, base: str, target: str, rate: Decimal, rate_date: date
) -> None:
    stmt = (
        pg_insert(ExchangeRate)
        .values(
            base_currency=base,
            target_currency=target,
            rate=rate,
            rate_date=rate_date,
        )
        .on_conflict_do_update(
            constraint="uq_rate",
            set_={"rate": rate},
        )
    )
    await db.execute(stmt)


async def _fetch_from_nbp() -> dict[str, Decimal] | None:
    """Fetch current exchange rates from NBP API. Returns {currency_code: rate_to_PLN}."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(NBP_API_URL)
            resp.raise_for_status()
            data = resp.json()

        rates: dict[str, Decimal] = {}
        for item in data[0]["rates"]:
            code = item["code"]
            mid = Decimal(str(item["mid"]))
            rates[code] = mid
        return rates
    except Exception:
        logger.warning("NBP API request failed", exc_info=True)
        return None


async def get_exchange_rate(
    db: AsyncSession, base: str, target: str, rate_date: date | None = None
) -> Decimal | None:
    """
    Get exchange rate with 3-tier fallback: Redis -> DB -> NBP API.
    All rates are relative to PLN (NBP convention).
    """
    if base == target:
        return Decimal("1")

    today = rate_date or date.today()

    cached = await _get_from_redis(base, target, today)
    if cached:
        return cached

    db_rate = await _get_from_db(db, base, target, today)
    if db_rate:
        await _set_in_redis(base, target, today, db_rate)
        return db_rate

    nbp_rates = await _fetch_from_nbp()
    if nbp_rates:
        rate = _derive_rate(base, target, nbp_rates)
        if rate:
            await _save_to_db(db, base, target, rate, today)
            await _set_in_redis(base, target, today, rate)
            return rate

    fallback = await _get_from_db(db, base, target)
    if fallback:
        logger.info("Using fallback rate from DB for %s->%s", base, target)
        return fallback

    return None


def _derive_rate(
    base: str, target: str, nbp_rates: dict[str, Decimal]
) -> Decimal | None:
    """
    NBP rates are X->PLN (e.g. 1 EUR = 4.32 PLN).
    To convert between non-PLN currencies, we go base->PLN->target.
    """
    if target == "PLN" and base in nbp_rates:
        return nbp_rates[base]

    if base == "PLN" and target in nbp_rates:
        return (Decimal("1") / nbp_rates[target]).quantize(Decimal("0.000001"))

    if base in nbp_rates and target in nbp_rates:
        rate = (nbp_rates[base] / nbp_rates[target]).quantize(Decimal("0.000001"))
        return rate

    return None


async def convert_amount(
    db: AsyncSession,
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    rate_date: date | None = None,
) -> Decimal | None:
    """Convert an amount from one currency to another."""
    if from_currency == to_currency:
        return amount

    rate = await get_exchange_rate(db, from_currency, to_currency, rate_date)
    if rate is None:
        return None
    return (amount * rate).quantize(Decimal("0.01"))

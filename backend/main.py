from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.currency import router as currency_router
from app.api.expenses import router as expenses_router
from app.api.groups import router as groups_router
from app.api.recurring import router as recurring_router
from app.api.settlements import router as settlements_router
from app.api.ws import router as ws_router
from app.api.accounts import router as accounts_router
from app.db.session import engine
from app.services.currency_service import get_redis
from app.services.scheduler import process_recurring_expenses

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        process_recurring_expenses, "cron", hour=0, minute=0, id="recurring_expenses"
    )
    scheduler.start()
    yield
    scheduler.shutdown()
    r = await get_redis()
    if r:
        await r.aclose()
    await engine.dispose()


app = FastAPI(
    title="Smart Expense Buddy",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(groups_router)
app.include_router(expenses_router)
app.include_router(settlements_router)
app.include_router(currency_router)
app.include_router(recurring_router)
app.include_router(ws_router)
app.include_router(accounts_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

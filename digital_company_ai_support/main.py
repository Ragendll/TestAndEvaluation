from contextlib import asynccontextmanager
from fastapi import FastAPI

from digital_company_ai_support.api.tickets_router import router as tickets_router
from digital_company_ai_support.db.database import init_db
import logging
logging.basicConfig(level=logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Ticket Router",
    lifespan=lifespan,
)

app.include_router(tickets_router)
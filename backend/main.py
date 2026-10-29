"""Точка входа FastAPI: python -m uvicorn backend.main:app --reload."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api import router
from backend.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Учет успеваемости студентов", lifespan=lifespan)
app.include_router(router)

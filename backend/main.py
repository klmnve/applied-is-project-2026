"""Точка входа FastAPI: python -m uvicorn backend.main:app --reload."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api import router
from backend.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Учет успеваемости студентов", lifespan=lifespan)
app.include_router(router)

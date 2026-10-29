"""Минимальный маршрут проверки работы сервера."""

from fastapi import APIRouter


router = APIRouter()


@router.get("/", tags=["status"])
def read_root() -> dict[str, str]:
    return {"status": "ok", "message": "Система учета успеваемости студентов работает"}

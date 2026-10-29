"""Совместимые импорты подключения из первой лабораторной работы."""

from backend.db import DATABASE_PATH, engine, get_session, init_db

create_db_and_tables = init_db

__all__ = ["DATABASE_PATH", "engine", "get_session", "init_db", "create_db_and_tables"]

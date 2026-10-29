"""Движок SQLite, контроль внешних ключей и создание таблиц."""

from collections.abc import Generator
from pathlib import Path
from sqlite3 import Connection

from sqlalchemy import Engine, event
from sqlmodel import Session, SQLModel, create_engine

# Импорт пакета регистрирует все четыре модели в SQLModel.metadata.
from backend import models


DATABASE_PATH = Path(__file__).resolve().parents[1] / "database.db"


def create_db_engine(database_path: Path = DATABASE_PATH, *, echo: bool = True) -> Engine:
    db_engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        echo=echo,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(db_engine, "connect")
    def enable_foreign_keys(connection: Connection, connection_record: object) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return db_engine


engine = create_db_engine()


def init_db(db_engine: Engine | None = None) -> None:
    """Создать отсутствующие таблицы; существующие данные не удалять."""
    SQLModel.metadata.create_all(db_engine if db_engine is not None else engine)


def get_session() -> Generator[Session, None, None]:
    """Отдельная сессия для каждого запроса FastAPI."""
    with Session(engine) as session:
        yield session

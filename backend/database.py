"""Подключение к SQLite и создание таблиц SQLModel."""

from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from backend.models import Student


DATABASE_PATH = Path(__file__).resolve().parent / "db.sqlite3"
engine = create_engine(
    f"sqlite:///{DATABASE_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    # Импорт Student выше регистрирует таблицу в метаданных SQLModel.
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Зависимость для будущих обработчиков, работающих с базой."""
    with Session(engine) as session:
        yield session

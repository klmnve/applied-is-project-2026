"""Базовая модель студента."""

from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    full_name: str = Field(index=True)
    group_name: str = Field(index=True)

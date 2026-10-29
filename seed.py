"""Создать БД и тестовые данные: python seed.py из корня проекта."""

from sqlalchemy import Engine, func
from sqlmodel import Session, SQLModel, select

from backend.db import engine, init_db
from backend.models import Grade, Student, Subject, Teacher


def _get_or_create(session: Session, model: type[SQLModel], **values):
    record = session.exec(select(model).filter_by(**values)).first()
    if record is None:
        record = model(**values)
        session.add(record)
        session.flush()
    return record


def seed_data(db_engine: Engine | None = None) -> dict[str, int]:
    """Добавить недостающие примеры одной транзакцией, без очистки БД."""
    db_engine = db_engine if db_engine is not None else engine
    init_db(db_engine)

    with Session(db_engine) as session:
        teachers = [
            _get_or_create(session, Teacher, full_name=name)
            for name in ("Айгуль Садыкова", "Марат Омаров", "Елена Иванова")
        ]
        subjects = [
            _get_or_create(session, Subject, name=name, teacher_id=teacher.id)
            for name, teacher in zip(
                ("Базы данных", "Программирование на Python", "Математика"), teachers
            )
        ]
        students = [
            _get_or_create(session, Student, full_name=name, group_name=group)
            for name, group in (
                ("Алихан Нурланов", "ИС-21"),
                ("Аружан Серикова", "ИС-21"),
                ("Данияр Ахметов", "ИС-22"),
            )
        ]
        for student_index, subject_index, value in (
            (0, 0, 90),
            (0, 1, 85),
            (1, 0, 95),
            (1, 2, 88),
            (2, 1, 78),
        ):
            _get_or_create(
                session,
                Grade,
                student_id=students[student_index].id,
                subject_id=subjects[subject_index].id,
                grade=value,
            )
        session.commit()
        return {
            model.__tablename__: session.exec(select(func.count()).select_from(model)).one()
            for model in (Teacher, Student, Subject, Grade)
        }


if __name__ == "__main__":
    counts = seed_data()
    print("База данных готова. Количество записей:")
    for table, count in counts.items():
        print(f"  {table}: {count}")

"""ORM-модели по ER-диаграмме системы учета успеваемости."""

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel


class Grade(SQLModel, table=True):
    """Оценка и связующая запись между студентом и предметом."""

    __tablename__ = "grades"
    __table_args__ = (CheckConstraint("grade BETWEEN 0 AND 100", name="ck_grade_range"),)

    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id", index=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True)
    grade: int = Field(ge=0, le=100)

    student: "Student" = Relationship(back_populates="grades")
    subject: "Subject" = Relationship(back_populates="grades")


class Teacher(SQLModel, table=True):
    __tablename__ = "teachers"

    id: int | None = Field(default=None, primary_key=True)
    full_name: str = Field(index=True)

    subjects: list["Subject"] = Relationship(back_populates="teacher")


class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: int | None = Field(default=None, primary_key=True)
    full_name: str = Field(index=True)
    group_name: str = Field(index=True)

    grades: list[Grade] = Relationship(back_populates="student")
    # Запись выполняется через Grade, поскольку у связи есть поле grade.
    subjects: list["Subject"] = Relationship(
        back_populates="students",
        link_model=Grade,
        sa_relationship_kwargs={"viewonly": True},
    )


class Subject(SQLModel, table=True):
    __tablename__ = "subjects"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    teacher_id: int = Field(foreign_key="teachers.id", index=True)

    teacher: Teacher = Relationship(back_populates="subjects")
    grades: list[Grade] = Relationship(back_populates="subject")
    students: list[Student] = Relationship(
        back_populates="subjects",
        link_model=Grade,
        sa_relationship_kwargs={"viewonly": True},
    )

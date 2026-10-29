"""Запуск: python -m unittest discover -s tests -v."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.db import create_db_engine, init_db
from backend.main import app
from backend.models import Grade, Student, Subject, Teacher
from seed import seed_data


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.engine = create_db_engine(Path(self.directory.name) / "test.db", echo=False)
        init_db(self.engine)

    def tearDown(self):
        self.engine.dispose()
        self.directory.cleanup()

    def test_schema_matches_er_diagram(self):
        schema = inspect(self.engine)
        expected = {
            "teachers": {"id", "full_name"},
            "students": {"id", "full_name", "group_name"},
            "subjects": {"id", "name", "teacher_id"},
            "grades": {"id", "student_id", "subject_id", "grade"},
        }
        self.assertEqual(set(schema.get_table_names()), set(expected))
        for table, columns in expected.items():
            self.assertEqual({column["name"] for column in schema.get_columns(table)}, columns)
            self.assertEqual(schema.get_pk_constraint(table)["constrained_columns"], ["id"])
        foreign_keys = {
            (table, tuple(key["constrained_columns"]), key["referred_table"])
            for table in expected
            for key in schema.get_foreign_keys(table)
        }
        self.assertEqual(foreign_keys, {
            ("subjects", ("teacher_id",), "teachers"),
            ("grades", ("student_id",), "students"),
            ("grades", ("subject_id",), "subjects"),
        })

    def test_seed_is_repeatable(self):
        expected = {"teachers": 3, "students": 3, "subjects": 3, "grades": 5}
        self.assertEqual(seed_data(self.engine), expected)
        self.assertEqual(seed_data(self.engine), expected)
        with self.engine.connect() as connection:
            self.assertEqual(connection.execute(text("PRAGMA foreign_key_check")).all(), [])

    def test_relationships_in_both_directions(self):
        seed_data(self.engine)
        with Session(self.engine) as session:
            student = session.exec(select(Student).order_by(Student.id)).first()
            self.assertEqual(len(student.grades), 2)
            self.assertEqual(len(student.subjects), 2)
            subject = student.grades[0].subject
            self.assertEqual(student.grades[0].student.id, student.id)
            self.assertEqual(len(subject.students), 2)
            self.assertIn(subject, subject.teacher.subjects)
            teacher = session.exec(select(Teacher).order_by(Teacher.id)).first()
            teacher.subjects.append(Subject(name="Дополнительный предмет"))
            student.grades.append(Grade(subject=subject, grade=100))
            session.commit()
            session.refresh(student)
            self.assertEqual(len(student.grades), 3)
            self.assertEqual(len(student.subjects), 2)
            self.assertEqual(len(teacher.subjects), 2)

    def test_invalid_foreign_keys_are_rejected(self):
        seed_data(self.engine)
        with self.engine.connect() as connection:
            self.assertEqual(connection.execute(text("PRAGMA foreign_keys")).scalar_one(), 1)
        for model in (
            Subject(name="Invalid", teacher_id=999999),
            Grade(student_id=999999, subject_id=1, grade=80),
            Grade(student_id=1, subject_id=999999, grade=80),
        ):
            with self.subTest(model=type(model).__name__), Session(self.engine) as session:
                session.add(model)
                with self.assertRaises(IntegrityError):
                    session.commit()

    def test_grade_range_is_enforced_in_database(self):
        seed_data(self.engine)
        for value in (-1, 101):
            with self.subTest(grade=value), Session(self.engine) as session:
                session.add(Grade(student_id=1, subject_id=1, grade=value))
                with self.assertRaises(IntegrityError):
                    session.commit()

    def test_required_fields_are_enforced_in_database(self):
        with Session(self.engine) as session:
            session.add(Student(full_name="Missing group"))
            with self.assertRaises(IntegrityError):
                session.commit()

    def test_fastapi_startup_and_root(self):
        with patch("backend.db.engine", self.engine), TestClient(app) as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "ok")
            self.assertEqual(client.get("/openapi.json").status_code, 200)


if __name__ == "__main__":
    unittest.main()

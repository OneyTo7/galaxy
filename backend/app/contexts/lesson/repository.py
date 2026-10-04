from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.lesson.models import Lesson
from app.contexts.lesson.schemas import LessonDomain


class LessonRepoProtocol:
    def list_by_course(self, course_id: int) -> list[LessonDomain]: ...
    def get(self, lesson_id: int) -> LessonDomain | None: ...
    def create(self, course_id: int, title: str, content: str, sort_order: int, assignment_id: int | None) -> LessonDomain: ...
    def update(self, lesson_id: int, data: dict) -> LessonDomain | None: ...
    def delete(self, lesson_id: int) -> bool: ...


class SQLAlchemyLessonRepo(LessonRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(l: Lesson) -> LessonDomain:
        return LessonDomain(
            l.id, l.course_id, l.title, l.sort_order,
            l.content, l.assignment_id, l.created_at,
        )

    def list_by_course(self, course_id):
        rows = (
            self._db.query(Lesson)
            .filter(Lesson.course_id == course_id)
            .order_by(Lesson.sort_order.asc(), Lesson.id.asc())
            .all()
        )
        return [self._to_domain(l) for l in rows]

    def get(self, lesson_id):
        l = self._db.get(Lesson, lesson_id)
        return self._to_domain(l) if l else None

    def create(self, course_id, title, content, sort_order, assignment_id):
        l = Lesson(
            course_id=course_id,
            title=title,
            content=content,
            sort_order=sort_order,
            assignment_id=assignment_id,
        )
        self._db.add(l)
        self._db.commit()
        self._db.refresh(l)
        return self._to_domain(l)

    def update(self, lesson_id, data):
        l = self._db.get(Lesson, lesson_id)
        if not l:
            return None
        for k, v in data.items():
            setattr(l, k, v)
        self._db.commit()
        self._db.refresh(l)
        return self._to_domain(l)

    def delete(self, lesson_id):
        l = self._db.get(Lesson, lesson_id)
        if not l:
            return False
        self._db.delete(l)
        self._db.commit()
        return True

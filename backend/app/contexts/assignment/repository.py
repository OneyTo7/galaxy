from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.assignment.models import Assignment, TestCase
from app.contexts.assignment.schemas import AssignmentDomain, TestCaseDomain


class AssignmentRepoProtocol:
    def create(self, teacher_id: int, data: dict, test_cases: list[dict]) -> AssignmentDomain: ...
    def get(self, assignment_id: int) -> AssignmentDomain | None: ...
    def list_by_teacher(self, teacher_id: int) -> list[AssignmentDomain]: ...
    def list_by_course(self, course_id: int) -> list[AssignmentDomain]: ...
    def update(self, assignment_id: int, data: dict) -> AssignmentDomain | None: ...
    def delete(self, assignment_id: int) -> bool: ...


class SQLAlchemyAssignmentRepo(AssignmentRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _tc_to_domain(tc: TestCase) -> TestCaseDomain:
        return TestCaseDomain(
            tc.id, tc.assignment_id, tc.name, tc.input, tc.expected_output,
            tc.is_hidden, tc.weight, tc.order,
        )

    def _to_domain(self, a: Assignment) -> AssignmentDomain:
        return AssignmentDomain(
            a.id, a.teacher_id, a.course_id, a.title, a.description, a.lang,
            a.scoring_rubric, a.reference_code, a.status, a.created_at,
            [self._tc_to_domain(tc) for tc in a.test_cases],
        )

    def create(self, teacher_id, data, test_cases):
        a = Assignment(teacher_id=teacher_id, **data)
        a.test_cases = [TestCase(**tc) for tc in test_cases]
        self._db.add(a)
        self._db.commit()
        self._db.refresh(a)
        return self._to_domain(a)

    def get(self, assignment_id):
        a = self._db.get(Assignment, assignment_id)
        return self._to_domain(a) if a else None

    def list_by_teacher(self, teacher_id):
        rows = (
            self._db.query(Assignment)
            .filter(Assignment.teacher_id == teacher_id)
            .order_by(Assignment.created_at.desc())
            .all()
        )
        return [self._to_domain(a) for a in rows]

    def list_by_course(self, course_id):
        rows = (
            self._db.query(Assignment)
            .filter(Assignment.course_id == course_id)
            .order_by(Assignment.created_at.desc())
            .all()
        )
        return [self._to_domain(a) for a in rows]

    def update(self, assignment_id, data):
        a = self._db.get(Assignment, assignment_id)
        if not a:
            return None
        for k, v in data.items():
            setattr(a, k, v)
        self._db.commit()
        self._db.refresh(a)
        return self._to_domain(a)

    def delete(self, assignment_id):
        a = self._db.get(Assignment, assignment_id)
        if not a:
            return False
        self._db.delete(a)
        self._db.commit()
        return True

from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.organization.models import Class, Course, Enrollment
from app.contexts.organization.schemas import (
    ClassDomain,
    CourseDomain,
    EnrollmentDomain,
)


class OrganizationRepoProtocol:
    def create_course(self, teacher_id: int, name: str, code: str) -> CourseDomain: ...
    def list_courses_by_teacher(self, teacher_id: int) -> list[CourseDomain]: ...
    def get_course(self, course_id: int) -> CourseDomain | None: ...
    def create_class(self, course_id: int, name: str) -> ClassDomain: ...
    def list_classes_by_course(self, course_id: int) -> list[ClassDomain]: ...
    def get_class(self, class_id: int) -> ClassDomain | None: ...
    def create_enrollment(self, class_id: int, student_id: int) -> EnrollmentDomain: ...
    def list_enrollments_by_class(self, class_id: int) -> list[EnrollmentDomain]: ...
    def is_enrolled(self, student_id: int, course_id: int) -> bool: ...


class SQLOrganizationRepo(OrganizationRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _course_to_domain(c: Course) -> CourseDomain:
        return CourseDomain(c.id, c.teacher_id, c.name, c.code, c.created_at)

    @staticmethod
    def _class_to_domain(cl: Class) -> ClassDomain:
        return ClassDomain(cl.id, cl.course_id, cl.name, cl.created_at)

    @staticmethod
    def _enr_to_domain(e: Enrollment) -> EnrollmentDomain:
        return EnrollmentDomain(e.id, e.class_id, e.student_id, e.created_at)

    def create_course(self, teacher_id, name, code):
        c = Course(teacher_id=teacher_id, name=name, code=code)
        self._db.add(c)
        self._db.commit()
        self._db.refresh(c)
        return self._course_to_domain(c)

    def list_courses_by_teacher(self, teacher_id):
        rows = (
            self._db.query(Course)
            .filter(Course.teacher_id == teacher_id)
            .order_by(Course.created_at.desc())
            .all()
        )
        return [self._course_to_domain(c) for c in rows]

    def get_course(self, course_id):
        c = self._db.get(Course, course_id)
        return self._course_to_domain(c) if c else None

    def create_class(self, course_id, name):
        cl = Class(course_id=course_id, name=name)
        self._db.add(cl)
        self._db.commit()
        self._db.refresh(cl)
        return self._class_to_domain(cl)

    def list_classes_by_course(self, course_id):
        rows = (
            self._db.query(Class)
            .filter(Class.course_id == course_id)
            .order_by(Class.created_at.desc())
            .all()
        )
        return [self._class_to_domain(cl) for cl in rows]

    def get_class(self, class_id):
        cl = self._db.get(Class, class_id)
        return self._class_to_domain(cl) if cl else None

    def create_enrollment(self, class_id, student_id):
        e = Enrollment(class_id=class_id, student_id=student_id)
        self._db.add(e)
        self._db.commit()
        self._db.refresh(e)
        return self._enr_to_domain(e)

    def list_enrollments_by_class(self, class_id):
        rows = (
            self._db.query(Enrollment)
            .filter(Enrollment.class_id == class_id)
            .order_by(Enrollment.created_at.desc())
            .all()
        )
        return [self._enr_to_domain(e) for e in rows]

    def is_enrolled(self, student_id, course_id):
        class_ids = [
            c[0] for c in self._db.query(Class.id).filter(Class.course_id == course_id).all()
        ]
        if not class_ids:
            return False
        enrolled = (
            self._db.query(Enrollment)
            .filter(Enrollment.class_id.in_(class_ids), Enrollment.student_id == student_id)
            .first()
        )
        return enrolled is not None

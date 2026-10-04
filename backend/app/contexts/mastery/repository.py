from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.mastery.models import (
    AssignmentKnowledgePoint,
    KnowledgePoint,
    MasteryEvent,
    StudentMastery,
)
from app.contexts.mastery.schemas import (
    AssignmentKnowledgePointDomain,
    KnowledgePointDomain,
    MasteryEventDomain,
    StudentMasteryDomain,
)


class MasteryRepoProtocol:
    def list_taxonomy(self) -> list[KnowledgePointDomain]: ...
    def get_kp(self, kp_id: int) -> KnowledgePointDomain | None: ...
    def get_by_codes(self, codes: list[str]) -> list[KnowledgePointDomain]: ...
    def list_by_ids(self, kp_ids: list[int]) -> list[KnowledgePointDomain]: ...
    def tags_for_assignments(
        self, assignment_ids: list[int]
    ) -> list[AssignmentKnowledgePointDomain]: ...
    def replace_assignment_tags(
        self, assignment_id: int, items: list[tuple[int, float]]
    ) -> None: ...
    def get_mastery(self, user_id: int, kp_id: int) -> StudentMasteryDomain | None: ...
    def create_mastery(
        self, user_id: int, kp_id: int, mastery: float, attempts: int, correct: int, status: str
    ) -> StudentMasteryDomain: ...
    def update_mastery(
        self, mastery_id: int, mastery: float, attempts: int, correct: int, status: str
    ) -> StudentMasteryDomain | None: ...
    def event_exists(self, user_id: int, kp_id: int, source: str, submission_id: int) -> bool: ...
    def insert_event(
        self,
        user_id: int,
        kp_id: int,
        submission_id: int,
        source: str,
        observed: bool,
        before: float,
        after: float,
    ) -> None: ...
    def list_mastery_by_users(
        self, user_ids: list[int], kp_ids: list[int] | None = None
    ) -> list[StudentMasteryDomain]: ...
    def list_events(
        self, user_id: int, kp_ids: list[int] | None = None
    ) -> list[MasteryEventDomain]: ...


class SQLAlchemyMasteryRepo(MasteryRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _kp_to_domain(k: KnowledgePoint) -> KnowledgePointDomain:
        return KnowledgePointDomain(
            k.id, k.code, k.name, k.category, k.sort_order,
            k.p_init, k.p_transit, k.p_slip, k.p_guess,
        )

    @staticmethod
    def _m_to_domain(m: StudentMastery) -> StudentMasteryDomain:
        return StudentMasteryDomain(
            m.id, m.user_id, m.knowledge_point_id, m.mastery,
            m.attempts, m.correct, m.status, m.first_seen_at, m.last_updated_at,
        )

    @staticmethod
    def _e_to_domain(e: MasteryEvent) -> MasteryEventDomain:
        return MasteryEventDomain(
            e.id, e.user_id, e.knowledge_point_id, e.submission_id,
            e.source, e.observed, e.mastery_before, e.mastery_after, e.created_at,
        )

    def list_taxonomy(self):
        rows = (
            self._db.query(KnowledgePoint)
            .order_by(KnowledgePoint.sort_order.asc(), KnowledgePoint.id.asc())
            .all()
        )
        return [self._kp_to_domain(k) for k in rows]

    def get_kp(self, kp_id):
        k = self._db.get(KnowledgePoint, kp_id)
        return self._kp_to_domain(k) if k else None

    def get_by_codes(self, codes):
        if not codes:
            return []
        rows = self._db.query(KnowledgePoint).filter(KnowledgePoint.code.in_(codes)).all()
        return [self._kp_to_domain(k) for k in rows]

    def list_by_ids(self, kp_ids):
        if not kp_ids:
            return []
        rows = self._db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()
        return [self._kp_to_domain(k) for k in rows]

    def tags_for_assignments(self, assignment_ids):
        if not assignment_ids:
            return []
        rows = (
            self._db.query(AssignmentKnowledgePoint)
            .filter(AssignmentKnowledgePoint.assignment_id.in_(assignment_ids))
            .all()
        )
        return [
            AssignmentKnowledgePointDomain(t.assignment_id, t.knowledge_point_id, t.weight)
            for t in rows
        ]

    def replace_assignment_tags(self, assignment_id, items):
        self._db.query(AssignmentKnowledgePoint).filter(
            AssignmentKnowledgePoint.assignment_id == assignment_id
        ).delete(synchronize_session=False)
        for kp_id, weight in items:
            self._db.add(
                AssignmentKnowledgePoint(
                    assignment_id=assignment_id,
                    knowledge_point_id=kp_id,
                    weight=weight,
                )
            )
        self._db.commit()

    def get_mastery(self, user_id, kp_id):
        m = (
            self._db.query(StudentMastery)
            .filter(
                StudentMastery.user_id == user_id,
                StudentMastery.knowledge_point_id == kp_id,
            )
            .first()
        )
        return self._m_to_domain(m) if m else None

    def create_mastery(self, user_id, kp_id, mastery, attempts, correct, status):
        m = StudentMastery(
            user_id=user_id,
            knowledge_point_id=kp_id,
            mastery=mastery,
            attempts=attempts,
            correct=correct,
            status=status,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        return self._m_to_domain(m)

    def update_mastery(self, mastery_id, mastery, attempts, correct, status):
        m = self._db.get(StudentMastery, mastery_id)
        if not m:
            return None
        m.mastery = mastery
        m.attempts = attempts
        m.correct = correct
        m.status = status
        from sqlalchemy import func as sa_func

        m.last_updated_at = sa_func.now()
        self._db.commit()
        self._db.refresh(m)
        return self._m_to_domain(m)

    def event_exists(self, user_id, kp_id, source, submission_id):
        return (
            self._db.query(MasteryEvent.id)
            .filter(
                MasteryEvent.user_id == user_id,
                MasteryEvent.knowledge_point_id == kp_id,
                MasteryEvent.source == source,
                MasteryEvent.submission_id == submission_id,
            )
            .first()
            is not None
        )

    def insert_event(self, user_id, kp_id, submission_id, source, observed, before, after):
        self._db.add(
            MasteryEvent(
                user_id=user_id,
                knowledge_point_id=kp_id,
                submission_id=submission_id,
                source=source,
                observed=observed,
                mastery_before=before,
                mastery_after=after,
            )
        )
        self._db.commit()

    def list_mastery_by_users(self, user_ids, kp_ids=None):
        if not user_ids:
            return []
        q = self._db.query(StudentMastery).filter(StudentMastery.user_id.in_(user_ids))
        if kp_ids is not None:
            if not kp_ids:
                return []
            q = q.filter(StudentMastery.knowledge_point_id.in_(kp_ids))
        rows = q.all()
        return [self._m_to_domain(m) for m in rows]

    def list_events(self, user_id, kp_ids=None):
        q = self._db.query(MasteryEvent).filter(MasteryEvent.user_id == user_id)
        if kp_ids is not None:
            if not kp_ids:
                return []
            q = q.filter(MasteryEvent.knowledge_point_id.in_(kp_ids))
        rows = q.order_by(MasteryEvent.created_at.asc(), MasteryEvent.id.asc()).all()
        return [self._e_to_domain(e) for e in rows]

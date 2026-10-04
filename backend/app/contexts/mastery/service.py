from __future__ import annotations

from app.contexts.assignment.service import AssignmentService
from app.contexts.evaluation.service import EvaluationService
from app.contexts.mastery import bkt
from app.contexts.mastery.repository import MasteryRepoProtocol
from app.contexts.mastery.schemas import (
    AssignmentKnowledgePointDomain,
    KnowledgePointDomain,
    MasteryEventDomain,
    StudentMasteryDomain,
)
from app.contexts.organization.service import OrganizationService
from app.contexts.submission.service import SubmissionService
from app.core.deps import CurrentUser
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError


class OvercomeMarkerProtocol:
    """误区克服标记器：由 diagnose 上下文提供实现（组合根接线）。"""

    def mark_overcome(self, user_id: int, knowledge_point_id: int) -> int: ...


class MasteryService:
    def __init__(
        self,
        repo: MasteryRepoProtocol,
        evaluation_svc: EvaluationService,
        submission_svc: SubmissionService,
        assignment_svc: AssignmentService,
        org_svc: OrganizationService,
        overcome_marker: OvercomeMarkerProtocol,
    ) -> None:
        self._repo = repo
        self._evaluation_svc = evaluation_svc
        self._submission_svc = submission_svc
        self._assignment_svc = assignment_svc
        self._org_svc = org_svc
        self._overcome = overcome_marker

    # ---------- 知识点体系 ----------

    def list_taxonomy(self) -> list[KnowledgePointDomain]:
        return self._repo.list_taxonomy()

    def list_codes(self) -> list[str]:
        return [k.code for k in self._repo.list_taxonomy()]

    def tag_practice(self, assignment_id: int, knowledge_point_id: int) -> None:
        """D3: 给变式练习作业打知识点标签（系统调用，无权限校验）。"""
        self._repo.replace_assignment_tags(assignment_id, [(knowledge_point_id, 1.0)])

    def tag_assignment(self, teacher_id: int, assignment_id: int, tags: list) -> None:
        assignment = self._assignment_svc.get(assignment_id)
        if assignment.teacher_id != teacher_id:
            raise ForbiddenError()
        codes = [t.code for t in tags]
        known = {k.code: k.id for k in self._repo.get_by_codes(codes)}
        unknown = [c for c in codes if c not in known]
        if unknown:
            raise ConflictError(f"未知知识点编码: {', '.join(unknown)}")
        self._repo.replace_assignment_tags(
            assignment_id, [(known[t.code], t.weight) for t in tags]
        )

    def get_tags(self, assignment_id: int) -> list[AssignmentKnowledgePointDomain]:
        self._assignment_svc.get(assignment_id)
        return self._repo.tags_for_assignments([assignment_id])

    # ---------- 记录观测（幂等） ----------

    def record_submission(self, submission_id: int) -> None:
        submission = self._submission_svc.get(submission_id)
        assignment = self._assignment_svc.get(submission.assignment_id)
        tags = self._repo.tags_for_assignments([assignment.id])
        if not tags:
            return
        results = self._evaluation_svc.list_by_submission(submission_id)
        if not results:
            return
        source = "variant" if assignment.kind == "practice" else "assignment"
        passed_by_case = {r.case_id: r.passed for r in results}
        total_w = sum(tc.weight for tc in assignment.test_cases)
        passed_w = sum(
            tc.weight for tc in assignment.test_cases if passed_by_case.get(tc.id)
        )
        observed = (passed_w / total_w if total_w > 0 else 0) >= bkt.PASS_RATIO_THRESHOLD
        for tag in tags:
            self._apply_event(
                submission.user_id, tag.knowledge_point_id, submission_id, source, observed
            )

    def record_diagnosis(
        self, submission_id: int, user_id: int, knowledge_point_id: int | None, confidence: float
    ) -> None:
        # 诊断是二手负证据：低置信诊断不记观测
        if knowledge_point_id is None or confidence < 0.5:
            return
        self._apply_event(
            user_id, knowledge_point_id, submission_id, "diagnosis", observed=False
        )

    def _apply_event(
        self,
        user_id: int,
        kp_id: int,
        submission_id: int,
        source: str,
        observed: bool,
    ) -> None:
        kp = self._repo.get_kp(kp_id)
        if not kp:
            return
        current = self._repo.get_mastery(user_id, kp_id)
        before = current.mastery if current else kp.p_init
        after = bkt.update(
            before,
            observed,
            source,
            slip=kp.p_slip,
            transit=kp.p_transit,
        )
        attempts = (current.attempts + 1) if current else 1
        correct = (current.correct + (1 if observed else 0)) if current else (1 if observed else 0)
        status = bkt.status_of(after, attempts)
        # 原子地更新掌握度 + 插入事件（单次 commit），并发下唯一约束保证幂等
        ok = self._repo.apply_event(
            user_id, kp_id, submission_id, source, observed,
            before, after, attempts, correct, status,
            existing_mastery_id=current.id if current else None,
        )
        if ok and observed:
            self._overcome.mark_overcome(user_id, kp_id)

    # ---------- 查询 ----------

    def _course_kps(self, course_id: int) -> list[KnowledgePointDomain]:
        assignments = self._assignment_svc.list_by_course(course_id)
        formal_ids = [a.id for a in assignments if a.kind == "formal"]
        tags = self._repo.tags_for_assignments(formal_ids)
        kp_ids = sorted({t.knowledge_point_id for t in tags})
        return self._repo.list_by_ids(kp_ids)

    def _check_teacher(self, course_id: int, user: CurrentUser) -> None:
        course = self._org_svc.get_course(course_id)
        if course.teacher_id != user.id:
            raise ForbiddenError()

    def matrix(self, course_id: int, user: CurrentUser) -> dict:
        self._check_teacher(course_id, user)
        kps = self._course_kps(course_id)
        students = self._org_svc.list_course_students(course_id)
        kp_by_id = {k.id: k for k in kps}
        rows = self._repo.list_mastery_by_users(
            [s[0] for s in students], kp_ids=list(kp_by_id) or None
        )
        by_key = {(r.user_id, r.knowledge_point_id): r for r in rows}
        cells = []
        for student_id, _name in students:
            for kp in kps:
                row = by_key.get((student_id, kp.id))
                cells.append(
                    {
                        "user_id": student_id,
                        "knowledge_point_id": kp.id,
                        "code": kp.code,
                        "name": kp.name,
                        "category": kp.category,
                        "mastery": row.mastery if row else None,
                        "attempts": row.attempts if row else 0,
                        "correct": row.correct if row else 0,
                        "status": row.status if row else "untracked",
                    }
                )
        return {
            "course_id": course_id,
            "students": [
                {"user_id": sid, "display_name": name} for sid, name in students
            ],
            "cells": cells,
        }

    def _student_points(self, course_id: int, student_id: int) -> list[dict]:
        kps = self._course_kps(course_id)
        rows = self._repo.list_mastery_by_users([student_id], kp_ids=[k.id for k in kps] or None)
        by_kp = {r.knowledge_point_id: r for r in rows}
        points = []
        for kp in kps:
            row = by_kp.get(kp.id)
            points.append(
                {
                    "user_id": student_id,
                    "knowledge_point_id": kp.id,
                    "code": kp.code,
                    "name": kp.name,
                    "category": kp.category,
                    "mastery": row.mastery if row else None,
                    "attempts": row.attempts if row else 0,
                    "correct": row.correct if row else 0,
                    "status": row.status if row else "untracked",
                }
            )
        return points

    def student_mastery(self, course_id: int, student_id: int, user: CurrentUser) -> dict:
        self._check_teacher(course_id, user)
        return {
            "course_id": course_id,
            "user_id": student_id,
            "points": self._student_points(course_id, student_id),
        }

    def my_mastery(self, course_id: int, user_id: int) -> dict:
        self._org_svc.get_course(course_id)
        if not self._org_svc.is_enrolled(user_id, course_id):
            raise ForbiddenError("未选该课程")
        return {
            "course_id": course_id,
            "user_id": user_id,
            "points": self._student_points(course_id, user_id),
        }

    def events(self, course_id: int, student_id: int, user: CurrentUser) -> list[MasteryEventDomain]:
        self._check_teacher(course_id, user)
        kps = self._course_kps(course_id)
        return self._repo.list_events(student_id, kp_ids=[k.id for k in kps] or None)

    def my_events(self, course_id: int, user_id: int) -> list[MasteryEventDomain]:
        self._org_svc.get_course(course_id)
        if not self._org_svc.is_enrolled(user_id, course_id):
            raise ForbiddenError("未选该课程")
        kps = self._course_kps(course_id)
        return self._repo.list_events(user_id, kp_ids=[k.id for k in kps] or None)

    def assignment_mastery_summary(self, assignment_id: int) -> list[dict]:
        """学情报告的掌握度摘要：各知识点班均掌握度 + 风险人数。"""
        tags = self._repo.tags_for_assignments([assignment_id])
        if not tags:
            return []
        submissions = self._submission_svc.list_by_assignment(assignment_id)
        student_ids = sorted({s.user_id for s in submissions})
        if not student_ids:
            return []
        kp_ids = sorted({t.knowledge_point_id for t in tags})
        kps = {k.id: k for k in self._repo.list_by_ids(kp_ids)}
        rows = self._repo.list_mastery_by_users(student_ids, kp_ids=kp_ids)
        summary = []
        for kp_id in kp_ids:
            kp_rows = [r for r in rows if r.knowledge_point_id == kp_id]
            if not kp_rows:
                avg = 0.0
                at_risk = 0
            else:
                avg = sum(r.mastery for r in kp_rows) / len(kp_rows)
                at_risk = sum(1 for r in kp_rows if r.status == "at_risk")
            kp = kps.get(kp_id)
            if not kp:
                continue
            summary.append(
                {
                    "knowledge_point_id": kp_id,
                    "code": kp.code,
                    "name": kp.name,
                    "category": kp.category,
                    "avg_mastery": round(avg, 3),
                    "student_count": len(kp_rows),
                    "at_risk_count": at_risk,
                }
            )
        return summary

    def difficulty_for(self, knowledge_point_id: int | None, user_id: int) -> str:
        if knowledge_point_id is None:
            return bkt.difficulty_for(None)
        row = self._repo.get_mastery(user_id, knowledge_point_id)
        return bkt.difficulty_for(row.mastery if row else None)

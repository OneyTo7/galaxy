from __future__ import annotations

from collections import Counter

from app.contexts.assignment.service import AssignmentService
from app.contexts.diagnose.service import DiagnoseService
from app.contexts.organization.service import OrganizationService
from app.contexts.report.schemas import (
    ClassReport,
    CourseReport,
    KnowledgeStat,
    LearningReport,
    MisconceptionStat,
    StudentStat,
)
from app.contexts.submission.service import SubmissionService
from app.core.deps import CurrentUser
from app.core.exceptions import ForbiddenError


class ReportService:
    def __init__(
        self,
        org_svc: OrganizationService,
        assignment_svc: AssignmentService,
        submission_svc: SubmissionService,
        diagnose_svc: DiagnoseService,
    ) -> None:
        self._org_svc = org_svc
        self._assignment_svc = assignment_svc
        self._submission_svc = submission_svc
        self._diagnose_svc = diagnose_svc

    def get_assignment_report(self, assignment_id: int, user: CurrentUser) -> LearningReport:
        assignment = self._assignment_svc.get(assignment_id)
        if assignment.teacher_id != user.id:
            raise ForbiddenError()
        submissions = self._submission_svc.list_by_assignment(assignment_id)
        sub_count = len(submissions)
        avg = sum(s.score for s in submissions) / sub_count if sub_count else 0.0

        misc_counter: Counter = Counter()
        know_counter: Counter = Counter()
        students: list[StudentStat] = []

        for s in submissions:
            diagnoses = self._diagnose_svc.list_by_submission(s.id)
            misc_type = ""
            for d in diagnoses:
                misc_counter[d.misconception_type] += 1
                know_counter[d.knowledge_point] += 1
                if not misc_type:
                    misc_type = d.misconception_type
            students.append(
                StudentStat(user_id=s.user_id, score=s.score, misconception_type=misc_type)
            )

        return LearningReport(
            assignment_id=assignment_id,
            submission_count=sub_count,
            avg_score=round(avg, 2),
            misconception_stats=[
                MisconceptionStat(misconception_type=t, count=c)
                for t, c in misc_counter.most_common()
            ],
            knowledge_stats=[
                KnowledgeStat(knowledge_point=p, count=c)
                for p, c in know_counter.most_common()
            ],
            students=students,
        )

    def get_course_report(self, course_id: int, user: CurrentUser) -> CourseReport:
        course = self._org_svc.get_course(course_id)
        if course.teacher_id != user.id:
            raise ForbiddenError()
        assignments = self._assignment_svc.list_by_course(course_id)
        assignment_count = len(assignments)
        sub_count = 0
        score_sum = 0
        misc_counter: Counter = Counter()
        know_counter: Counter = Counter()
        students_map: dict[int, StudentStat] = {}
        for a in assignments:
            submissions = self._submission_svc.list_by_assignment(a.id)
            for s in submissions:
                sub_count += 1
                score_sum += s.score
                diagnoses = self._diagnose_svc.list_by_submission(s.id)
                misc_type = ""
                for d in diagnoses:
                    misc_counter[d.misconception_type] += 1
                    know_counter[d.knowledge_point] += 1
                    if not misc_type:
                        misc_type = d.misconception_type
                students_map[s.user_id] = StudentStat(
                    user_id=s.user_id, score=s.score, misconception_type=misc_type
                )
        avg = score_sum / sub_count if sub_count else 0.0
        return CourseReport(
            course_id=course_id,
            assignment_count=assignment_count,
            submission_count=sub_count,
            avg_score=round(avg, 2),
            misconception_stats=[
                MisconceptionStat(misconception_type=t, count=c)
                for t, c in misc_counter.most_common()
            ],
            knowledge_stats=[
                KnowledgeStat(knowledge_point=p, count=c)
                for p, c in know_counter.most_common()
            ],
            students=list(students_map.values()),
        )

    def get_class_report(self, class_id: int, user: CurrentUser) -> ClassReport:
        # TODO: N+1 优化——每 submission 调 diagnose_svc.list_by_submission，建议批量查 misconception by assignment
        klass = self._org_svc.get_class(class_id)
        course = self._org_svc.get_course(klass.course_id)
        if course.teacher_id != user.id:
            raise ForbiddenError()
        course_id = klass.course_id
        enrollments = self._org_svc.list_enrollments(class_id)
        student_ids = {e.student_id for e in enrollments}
        assignments = self._assignment_svc.list_by_course(course_id)
        sub_count = 0
        score_sum = 0
        misc_counter: Counter = Counter()
        know_counter: Counter = Counter()
        students_map: dict[int, StudentStat] = {}
        for a in assignments:
            submissions = self._submission_svc.list_by_assignment(a.id)
            for s in submissions:
                if s.user_id not in student_ids:
                    continue
                sub_count += 1
                score_sum += s.score
                diagnoses = self._diagnose_svc.list_by_submission(s.id)
                misc_type = ""
                for d in diagnoses:
                    misc_counter[d.misconception_type] += 1
                    know_counter[d.knowledge_point] += 1
                    if not misc_type:
                        misc_type = d.misconception_type
                students_map[s.user_id] = StudentStat(
                    user_id=s.user_id, score=s.score, misconception_type=misc_type
                )
        avg = score_sum / sub_count if sub_count else 0.0
        return ClassReport(
            class_id=class_id,
            course_id=course_id,
            student_count=len(student_ids),
            submission_count=sub_count,
            avg_score=round(avg, 2),
            misconception_stats=[
                MisconceptionStat(misconception_type=t, count=c)
                for t, c in misc_counter.most_common()
            ],
            knowledge_stats=[
                KnowledgeStat(knowledge_point=p, count=c)
                for p, c in know_counter.most_common()
            ],
            students=list(students_map.values()),
        )

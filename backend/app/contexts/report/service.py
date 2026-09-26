from __future__ import annotations

from collections import Counter

from app.contexts.diagnose.service import DiagnoseService
from app.contexts.report.schemas import (
    KnowledgeStat,
    LearningReport,
    MisconceptionStat,
    StudentStat,
)
from app.contexts.submission.service import SubmissionService


class ReportService:
    def __init__(
        self,
        submission_svc: SubmissionService,
        diagnose_svc: DiagnoseService,
    ) -> None:
        self._submission_svc = submission_svc
        self._diagnose_svc = diagnose_svc

    def get_assignment_report(self, assignment_id: int) -> LearningReport:
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

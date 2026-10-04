from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.cheating.providers.moma import CheatingProvider
from app.contexts.cheating.repository import SQLAlchemyCheatingRepo
from app.contexts.cheating.service import CheatingService, SubmissionPeerRepoProtocol, _PeerSubmission
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.models import Submission
from app.contexts.submission.service import SubmissionService
from app.core.database import get_db


class SQLAlchemySubmissionPeerRepo(SubmissionPeerRepoProtocol):
    """同班同作业提交数据源：按 assignment_id 取其他学生提交。"""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_peers(self, assignment_id, exclude_user_id):
        rows = (
            self._db.query(Submission)
            .filter(
                Submission.assignment_id == assignment_id,
                Submission.user_id != exclude_user_id,
            )
            .all()
        )
        return [
            _PeerSubmission(submission_id=r.id, user_id=r.user_id, code=r.code)
            for r in rows
        ]


def get_cheating_service(
    db: Session = Depends(get_db),
    submission_svc: SubmissionService = Depends(get_submission_service),
) -> CheatingService:
    return CheatingService(
        submission_svc=submission_svc,
        cheating_repo=SQLAlchemyCheatingRepo(db),
        cheating_provider=CheatingProvider(),
        peer_repo=SQLAlchemySubmissionPeerRepo(db),
    )

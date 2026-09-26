from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Appeal(Base):
    __tablename__ = "appeals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("submissions.id", ondelete="CASCADE"), index=True
    )
    student_id: Mapped[int] = mapped_column(Integer, index=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    approved: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    review_comment: Mapped[str] = mapped_column(Text, default="")
    reviewer_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

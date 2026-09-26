from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    assignment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("assignments.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(Text)
    lang: Mapped[str] = mapped_column(String(16), default="python")
    status: Mapped[str] = mapped_column(String(16), default="pending")
    score: Mapped[int] = mapped_column(Integer, default=0)
    last_result: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

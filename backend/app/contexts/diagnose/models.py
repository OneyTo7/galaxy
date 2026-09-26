from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Misconception(Base):
    __tablename__ = "misconceptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("submissions.id", ondelete="CASCADE"), index=True
    )
    misconception_type: Mapped[str] = mapped_column(String(64))
    evidence: Mapped[str] = mapped_column(Text)
    knowledge_point: Mapped[str] = mapped_column(String(128))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

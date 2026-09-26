from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VariantExercise(Base):
    __tablename__ = "variant_exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("submissions.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    cases: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    scoring_points: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    lang: Mapped[str] = mapped_column(String(16), default="python")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

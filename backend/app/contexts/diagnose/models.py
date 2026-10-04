from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Misconception(Base):
    __tablename__ = "misconceptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("submissions.id", ondelete="CASCADE"), index=True
    )
    # 冗余属主，便于按学生聚合（克服时间线）；由入库时从 submission 带入
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=True)
    misconception_type: Mapped[str] = mapped_column(String(64))
    evidence: Mapped[str] = mapped_column(Text)
    knowledge_point: Mapped[str] = mapped_column(String(128))
    knowledge_point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_points.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_validated: Mapped[bool] = mapped_column(Boolean, default=True)
    # open → overcome：该知识点出现正确观测后由掌握度模型驱动翻转
    status: Mapped[str] = mapped_column(String(16), default="open")
    overcome_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

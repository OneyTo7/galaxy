from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(32), default="综合")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    # BKT 参数可按知识点覆盖，默认值见 bkt.py
    p_init: Mapped[float] = mapped_column(Float, default=0.30)
    p_transit: Mapped[float] = mapped_column(Float, default=0.20)
    p_slip: Mapped[float] = mapped_column(Float, default=0.10)
    p_guess: Mapped[float] = mapped_column(Float, default=0.20)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AssignmentKnowledgePoint(Base):
    __tablename__ = "assignment_knowledge_points"
    __table_args__ = (
        UniqueConstraint("assignment_id", "knowledge_point_id", name="uq_akp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assignment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("assignments.id", ondelete="CASCADE"), index=True
    )
    knowledge_point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), index=True
    )
    weight: Mapped[float] = mapped_column(Float, default=1.0)


class StudentMastery(Base):
    __tablename__ = "student_mastery"
    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_point_id", name="uq_mastery_user_kp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    knowledge_point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), index=True
    )
    mastery: Mapped[float] = mapped_column(Float, default=0.30)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="learning")
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class MasteryEvent(Base):
    __tablename__ = "mastery_events"
    __table_args__ = (
        # 幂等：同一提交对同一知识点同一来源只记一次（worker 重投/重复诊断安全）
        UniqueConstraint(
            "user_id",
            "knowledge_point_id",
            "source",
            "submission_id",
            name="uq_mastery_event_once",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    knowledge_point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), index=True
    )
    submission_id: Mapped[int] = mapped_column(Integer, index=True)
    source: Mapped[str] = mapped_column(String(16))  # assignment / diagnosis / variant
    observed: Mapped[bool] = mapped_column(Boolean)
    mastery_before: Mapped[float] = mapped_column(Float)
    mastery_after: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

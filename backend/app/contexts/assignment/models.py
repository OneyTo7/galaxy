from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    lang: Mapped[str] = mapped_column(String(16), default="python")
    scoring_rubric: Mapped[str] = mapped_column(Text, default="")
    reference_code: Mapped[str] = mapped_column(Text, default="")
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(16), default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan", order_by="TestCase.order"
    )


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assignment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("assignments.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(64), default="")
    input: Mapped[str] = mapped_column(Text, default="")
    expected_output: Mapped[str] = mapped_column(Text, default="")
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    weight: Mapped[int] = mapped_column(Integer, default=1)
    order: Mapped[int] = mapped_column(Integer, default=0)

    assignment: Mapped["Assignment"] = relationship(back_populates="test_cases")

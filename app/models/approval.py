from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.db.base import Base
import uuid


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflow_definitions.id"), nullable=False)
    requester_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, approved, rejected
    current_stage_order: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    workflow: Mapped["WorkflowDefinition"] = relationship(back_populates="requests")
    requester: Mapped["User"] = relationship(back_populates="requests")
    actions: Mapped[list["ApprovalAction"]] = relationship(back_populates="request")


class ApprovalAction(Base):
    __tablename__ = "approval_actions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(ForeignKey("approval_requests.id"), nullable=False)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    stage_order: Mapped[int] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)  # approved, rejected
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    acted_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request: Mapped["ApprovalRequest"] = relationship(back_populates="actions")
    actor: Mapped["User"] = relationship(back_populates="actions")
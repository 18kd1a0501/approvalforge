from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    stages: Mapped[list["WorkflowStage"]] = relationship(
        back_populates="workflow", order_by="WorkflowStage.order"
    )
    requests: Mapped[list["ApprovalRequest"]] = relationship(back_populates="workflow")


class WorkflowStage(Base):
    __tablename__ = "workflow_stages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflow_definitions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    approver_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    workflow: Mapped["WorkflowDefinition"] = relationship(back_populates="stages")
    approver: Mapped["User"] = relationship()
from pydantic import BaseModel
from datetime import datetime


class ApprovalRequestCreate(BaseModel):
    workflow_id: str
    title: str
    description: str | None = None


class ApprovalActionCreate(BaseModel):
    action: str  # "approved" or "rejected"
    comment: str | None = None


class ApprovalActionOut(BaseModel):
    id: str
    stage_order: int
    action: str
    comment: str | None
    actor_id: str
    acted_at: datetime

    model_config = {"from_attributes": True}


class ApprovalRequestOut(BaseModel):
    id: str
    workflow_id: str
    requester_id: str
    title: str
    description: str | None
    status: str
    current_stage_order: int
    created_at: datetime
    actions: list[ApprovalActionOut]

    model_config = {"from_attributes": True}
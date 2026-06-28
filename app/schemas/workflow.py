from pydantic import BaseModel


class WorkflowStageCreate(BaseModel):
    name: str
    order: int
    approver_id: str


class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    stages: list[WorkflowStageCreate]


class WorkflowStageOut(BaseModel):
    id: str
    name: str
    order: int
    approver_id: str

    model_config = {"from_attributes": True}


class WorkflowOut(BaseModel):
    id: str
    name: str
    description: str | None
    stages: list[WorkflowStageOut]

    model_config = {"from_attributes": True}
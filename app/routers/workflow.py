from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.user import User
from app.models.workflow import WorkflowDefinition, WorkflowStage
from app.schemas.workflow import WorkflowCreate, WorkflowOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/", response_model=WorkflowOut, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # validate all approver_ids exist
    approver_ids = {s.approver_id for s in payload.stages}
    result = await db.execute(select(User).where(User.id.in_(approver_ids)))
    found = {u.id for u in result.scalars().all()}
    missing = approver_ids - found
    if missing:
        raise HTTPException(status_code=400, detail=f"Approver IDs not found: {missing}")

    # validate no duplicate orders
    orders = [s.order for s in payload.stages]
    if len(orders) != len(set(orders)):
        raise HTTPException(status_code=400, detail="Stage orders must be unique")

    workflow = WorkflowDefinition(
        name=payload.name,
        description=payload.description,
    )
    db.add(workflow)
    await db.flush()

    for stage in payload.stages:
        db.add(WorkflowStage(
            workflow_id=workflow.id,
            name=stage.name,
            order=stage.order,
            approver_id=stage.approver_id,
        ))

    await db.flush()

    result = await db.execute(
        select(WorkflowDefinition)
        .where(WorkflowDefinition.id == workflow.id)
        .options(selectinload(WorkflowDefinition.stages))
    )
    return result.scalar_one()


@router.get("/", response_model=list[WorkflowOut])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkflowDefinition).options(selectinload(WorkflowDefinition.stages))
    )
    return result.scalars().all()


@router.get("/{workflow_id}", response_model=WorkflowOut)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkflowDefinition)
        .where(WorkflowDefinition.id == workflow_id)
        .options(selectinload(WorkflowDefinition.stages))
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
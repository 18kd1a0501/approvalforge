from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.workflow import WorkflowDefinition
from app.models.approval import ApprovalRequest, ApprovalAction
from fastapi import HTTPException


async def get_request_or_404(request_id: str, db: AsyncSession) -> ApprovalRequest:
    result = await db.execute(
        select(ApprovalRequest)
        .where(ApprovalRequest.id == request_id)
        .options(selectinload(ApprovalRequest.actions))
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


async def process_action(
    request: ApprovalRequest,
    actor_id: str,
    action: str,
    comment: str | None,
    db: AsyncSession,
) -> ApprovalRequest:
    if request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Request is already {request.status}"
        )

    # fetch workflow stages
    result = await db.execute(
        select(WorkflowDefinition)
        .where(WorkflowDefinition.id == request.workflow_id)
        .options(selectinload(WorkflowDefinition.stages))
    )
    workflow = result.scalar_one()
    stages = sorted(workflow.stages, key=lambda s: s.order)

    # find current stage
    current_stage = next(
        (s for s in stages if s.order == request.current_stage_order), None
    )
    if not current_stage:
        raise HTTPException(status_code=400, detail="Invalid stage state")

    # enforce correct approver
    if current_stage.approver_id != actor_id:
        raise HTTPException(
            status_code=403,
            detail="You are not the approver for this stage"
        )

    if action not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Action must be 'approved' or 'rejected'")

    # record the action
    db.add(ApprovalAction(
        request_id=request.id,
        actor_id=actor_id,
        stage_order=request.current_stage_order,
        action=action,
        comment=comment,
    ))

    if action == "rejected":
        request.status = "rejected"
    else:
        # find next stage
        next_stage = next(
            (s for s in stages if s.order > request.current_stage_order), None
        )
        if next_stage:
            request.current_stage_order = next_stage.order
        else:
            # no more stages — fully approved
            request.status = "approved"

    await db.flush()
    await db.refresh(request)
    return request
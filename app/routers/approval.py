from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.user import User
from app.models.approval import ApprovalRequest
from app.schemas.approval import ApprovalRequestCreate, ApprovalActionCreate, ApprovalRequestOut
from app.core.dependencies import get_current_user
from app.services.approval_engine import get_request_or_404, process_action

router = APIRouter(prefix="/requests", tags=["approval requests"])


@router.post("/", response_model=ApprovalRequestOut, status_code=status.HTTP_201_CREATED)
async def submit_request(
    payload: ApprovalRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = ApprovalRequest(
        workflow_id=payload.workflow_id,
        requester_id=current_user.id,
        title=payload.title,
        description=payload.description,
        status="pending",
        current_stage_order=1,
    )
    db.add(request)
    await db.flush()
    await db.refresh(request)

    result = await db.execute(
        select(ApprovalRequest)
        .where(ApprovalRequest.id == request.id)
        .options(selectinload(ApprovalRequest.actions))
    )
    return result.scalar_one()


@router.get("/", response_model=list[ApprovalRequestOut])
async def list_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ApprovalRequest)
        .where(ApprovalRequest.requester_id == current_user.id)
        .options(selectinload(ApprovalRequest.actions))
    )
    return result.scalars().all()


@router.get("/{request_id}", response_model=ApprovalRequestOut)
async def get_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_request_or_404(request_id, db)


@router.post("/{request_id}/action", response_model=ApprovalRequestOut)
async def take_action(
    request_id: str,
    payload: ApprovalActionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = await get_request_or_404(request_id, db)
    return await process_action(request, current_user.id, payload.action, payload.comment, db)
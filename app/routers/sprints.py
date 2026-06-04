from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.sprint import SprintCreate, SprintResponse, SprintSummaryResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.services import sprint_service

router = APIRouter(prefix="/api/sprints", tags=["sprints"])


@router.post("", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    payload: SprintCreate, session: AsyncSession = Depends(get_session)
) -> SprintResponse:
    return SprintResponse.model_validate(await sprint_service.create_sprint(session, payload))


@router.post("/{sprint_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def add_task_to_sprint(
    sprint_id: int, payload: TaskCreate, session: AsyncSession = Depends(get_session)
) -> TaskResponse:
    return TaskResponse.model_validate(
        await sprint_service.add_task_to_sprint(session, sprint_id, payload)
    )


@router.get("/{sprint_id}/summary", response_model=SprintSummaryResponse)
async def get_sprint_summary(
    sprint_id: int, session: AsyncSession = Depends(get_session)
) -> SprintSummaryResponse:
    return await sprint_service.get_sprint_summary(session, sprint_id)


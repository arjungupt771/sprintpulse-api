from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.enums import TaskPriority, TaskStatus
from app.schemas.task import TaskResponse, TaskStatusUpdate
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def send_done_notification(task_id: int) -> None:
    with open("notifications.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"Task {task_id} marked DONE\n")


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[TaskResponse]:
    tasks = await task_service.list_tasks(session, status, priority)
    return [TaskResponse.model_validate(task) for task in tasks]


@router.put("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    task = await task_service.update_task_status(session, task_id, payload.status)
    if task.status == TaskStatus.DONE:
        background_tasks.add_task(send_done_notification, task.id)
    return TaskResponse.model_validate(task)


@router.put("/{task_id}/assign/{engineer_id}", response_model=TaskResponse)
async def assign_engineer(
    task_id: int, engineer_id: int, session: AsyncSession = Depends(get_session)
) -> TaskResponse:
    return TaskResponse.model_validate(
        await task_service.assign_engineer(session, task_id, engineer_id)
    )


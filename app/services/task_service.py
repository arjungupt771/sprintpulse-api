from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleViolationError, EngineerUnavailableError, ResourceNotFoundError
from app.models import Engineer, Sprint, Task
from app.models.enums import TaskPriority, TaskStatus


STATUS_ORDER = [
    TaskStatus.TODO,
    TaskStatus.IN_PROGRESS,
    TaskStatus.REVIEW,
    TaskStatus.DONE,
]


async def get_task(session: AsyncSession, task_id: int) -> Task:
    task = await session.get(Task, task_id)
    if task is None:
        raise ResourceNotFoundError("Task not found")
    return task


async def list_tasks(
    session: AsyncSession,
    status: TaskStatus | None,
    priority: TaskPriority | None,
) -> list[Task]:
    query = select(Task)
    if status is not None:
        query = query.where(Task.status == status)
    if priority is not None:
        query = query.where(Task.priority == priority)
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_task_status(session: AsyncSession, task_id: int, new_status: TaskStatus) -> Task:
    task = await get_task(session, task_id)
    current_index = STATUS_ORDER.index(task.status)
    new_index = STATUS_ORDER.index(new_status)
    if new_index < current_index:
        raise BusinessRuleViolationError("Task status cannot move backwards")
    task.status = new_status
    await session.commit()
    await session.refresh(task)
    return task


async def assign_engineer(session: AsyncSession, task_id: int, engineer_id: int) -> Task:
    task = await get_task(session, task_id)
    engineer = await session.get(Engineer, engineer_id)
    if engineer is None:
        raise ResourceNotFoundError("Engineer not found")
    if not engineer.is_available:
        raise EngineerUnavailableError("Unavailable engineer cannot be assigned")
    task.engineer_id = engineer.id
    await session.commit()
    await session.refresh(task)
    return task


async def assert_sprint_exists(session: AsyncSession, sprint_id: int) -> None:
    if await session.get(Sprint, sprint_id) is None:
        raise ResourceNotFoundError("Sprint not found")


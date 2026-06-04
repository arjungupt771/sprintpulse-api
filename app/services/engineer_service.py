from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ResourceNotFoundError
from app.models import Engineer, Task
from app.models.enums import TaskStatus
from app.schemas.engineer import EngineerCreate, EngineerWorkloadResponse


MAX_ACTIVE_TASKS = 5


async def create_engineer(session: AsyncSession, payload: EngineerCreate) -> Engineer:
    engineer = Engineer(**payload.model_dump())
    session.add(engineer)
    await session.commit()
    await session.refresh(engineer)
    return engineer


async def get_engineer(session: AsyncSession, engineer_id: int) -> Engineer:
    result = await session.execute(
        select(Engineer).options(selectinload(Engineer.tasks)).where(Engineer.id == engineer_id)
    )
    engineer = result.scalar_one_or_none()
    if engineer is None:
        raise ResourceNotFoundError("Engineer not found")
    return engineer


async def get_available_engineers(session: AsyncSession, stack: str | None) -> list[Engineer]:
    result = await session.execute(
        select(Engineer).options(selectinload(Engineer.tasks)).where(Engineer.is_available.is_(True))
    )
    engineers = list(result.scalars().all())
    if stack is not None:
        engineers = [
            engineer
            for engineer in engineers
            if engineer.primary_stack.casefold() == stack.casefold()
        ]
    return [
        engineer
        for engineer in engineers
        if sum(1 for task in engineer.tasks if task.status != TaskStatus.DONE) < MAX_ACTIVE_TASKS
    ]


async def get_engineer_workload(session: AsyncSession, engineer_id: int) -> EngineerWorkloadResponse:
    engineer = await get_engineer(session, engineer_id)
    active_tasks = [task for task in engineer.tasks if task.status != TaskStatus.DONE]
    estimated = sum(task.estimated_hours for task in active_tasks)
    actual = sum(task.actual_hours for task in active_tasks)
    stack_utilisation = _stack_utilisation(engineer, active_tasks)
    capacity_status = "AT_CAPACITY" if len(active_tasks) >= MAX_ACTIVE_TASKS else "AVAILABLE"
    return EngineerWorkloadResponse(
        engineer_id=engineer.id,
        active_tasks=len(active_tasks),
        estimated_hours=round(estimated, 2),
        actual_hours=round(actual, 2),
        stack_utilisation=stack_utilisation,
        capacity_status=capacity_status,
    )


def _stack_utilisation(engineer: Engineer, tasks: list[Task]) -> str:
    if not tasks:
        return "0% active task load on primary stack"
    matching = sum(1 for task in tasks if engineer.primary_stack.casefold() in task.description.casefold())
    percentage = round((matching / len(tasks)) * 100)
    return f"{percentage}% active task load on primary stack"


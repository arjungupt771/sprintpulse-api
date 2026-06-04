from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ResourceNotFoundError
from app.models import Project, Sprint, Task
from app.models.enums import TaskStatus
from app.schemas.sprint import SprintCreate, SprintSummaryResponse
from app.schemas.task import TaskCreate


async def create_sprint(session: AsyncSession, payload: SprintCreate) -> Sprint:
    project = await session.get(Project, payload.project_id)
    if project is None:
        raise ResourceNotFoundError("Project not found")
    sprint = Sprint(**payload.model_dump())
    session.add(sprint)
    await session.commit()
    await session.refresh(sprint)
    return sprint


async def get_sprint(session: AsyncSession, sprint_id: int) -> Sprint:
    result = await session.execute(
        select(Sprint).options(selectinload(Sprint.tasks)).where(Sprint.id == sprint_id)
    )
    sprint = result.scalar_one_or_none()
    if sprint is None:
        raise ResourceNotFoundError("Sprint not found")
    return sprint


async def add_task_to_sprint(session: AsyncSession, sprint_id: int, payload: TaskCreate) -> Task:
    await get_sprint(session, sprint_id)
    task_data = payload.model_dump()
    task_data["sprint_id"] = sprint_id
    task = Task(**task_data)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_sprint_summary(session: AsyncSession, sprint_id: int) -> SprintSummaryResponse:
    sprint = await get_sprint(session, sprint_id)
    tasks = sprint.tasks
    total = len(tasks)
    done = sum(1 for task in tasks if task.status == TaskStatus.DONE)
    breakdown = {status: sum(1 for task in tasks if task.status == status) for status in TaskStatus}
    overdue_count = (
        sum(1 for task in tasks if task.status != TaskStatus.DONE) if sprint.end_date < date.today() else 0
    )
    velocity = sum(task.actual_hours for task in tasks if task.status == TaskStatus.DONE)
    return SprintSummaryResponse(
        sprint_id=sprint.id,
        completion_percentage=round((done / total) * 100, 2) if total else 0.0,
        task_breakdown=breakdown,
        overdue_count=overdue_count,
        velocity=round(velocity, 2),
    )


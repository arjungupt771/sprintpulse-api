import csv
from io import StringIO

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ResourceNotFoundError
from app.models import Client, Project, Sprint, Task
from app.models.enums import SprintStatus, TaskStatus
from app.schemas.project import ProjectCreate, ProjectHealthResponse


async def create_project(session: AsyncSession, payload: ProjectCreate) -> Project:
    client = await session.get(Client, payload.client_id)
    if client is None or client.deleted_at is not None:
        raise ResourceNotFoundError("Client not found")
    project = Project(**payload.model_dump())
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def get_project(session: AsyncSession, project_id: int) -> Project:
    result = await session.execute(
        select(Project)
        .options(selectinload(Project.sprints).selectinload(Sprint.tasks))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise ResourceNotFoundError("Project not found")
    return project


async def get_project_sprints(session: AsyncSession, project_id: int) -> list[Sprint]:
    project = await get_project(session, project_id)
    return project.sprints


async def get_project_health(session: AsyncSession, project_id: int) -> ProjectHealthResponse:
    project = await get_project(session, project_id)
    tasks = [task for sprint in project.sprints for task in sprint.tasks]
    total_tasks = len(tasks)
    done_tasks = sum(1 for task in tasks if task.status == TaskStatus.DONE)
    overdue_tasks = sum(1 for task in tasks if task.status != TaskStatus.DONE and sprint_overdue(task))

    completion_points = 35.0 * (done_tasks / total_tasks) if total_tasks else 0.0
    schedule_points = 25.0 * (1 - overdue_tasks / total_tasks) if total_tasks else 25.0
    estimated = sum(task.estimated_hours for task in tasks)
    if estimated <= 0:
        estimate_points = 20.0
    else:
        absolute_error = sum(
            abs(task.actual_hours - task.estimated_hours)
            for task in tasks
            )
        variance = min(absolute_error / estimated, 1.0)
        estimate_points = 20.0 * (1 - variance)

    sprint_points = (
        20.0 * sum(1 for sprint in project.sprints if sprint.status == SprintStatus.DONE) / len(project.sprints)
        if project.sprints
        else 0.0
    )
    score = round(completion_points + schedule_points + estimate_points + sprint_points, 2)
    return ProjectHealthResponse(
        project_id=project.id,
        score=score,
        formula="35% completion + 25% schedule + 20% estimate accuracy + 20% sprint completion",
        completion_points=round(completion_points, 2),
        schedule_points=round(schedule_points, 2),
        estimate_points=round(estimate_points, 2),
        sprint_points=round(sprint_points, 2),
    )


def sprint_overdue(task: Task) -> bool:
    from datetime import date

    return task.sprint.end_date < date.today()


async def export_project_tasks_csv(session: AsyncSession, project_id: int) -> str:
    project = await get_project(session, project_id)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "project",
            "sprint_number",
            "task_id",
            "title",
            "priority",
            "status",
            "estimated_hours",
            "actual_hours",
            "engineer_id",
        ]
    )
    for sprint in project.sprints:
        for task in sprint.tasks:
            writer.writerow(
                [
                    project.name,
                    sprint.sprint_number,
                    task.id,
                    task.title,
                    task.priority.value,
                    task.status.value,
                    task.estimated_hours,
                    task.actual_hours,
                    task.engineer_id or "",
                ]
            )
    return output.getvalue()


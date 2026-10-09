from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Client, Engineer, Project, Sprint, Task
from app.models.enums import ProjectStatus, SprintStatus, TaskPriority, TaskStatus


async def seed_minimal(session: AsyncSession) -> tuple[Client, Project, Sprint, Task, Engineer]:
    client = Client(
        name="Acme",
        industry="SaaS",
        contact_email="team@acme.example.com",
        country="USA",
    )
    engineer = Engineer(
        name="Ada",
        email="ada@example.com",
        primary_stack="PYTHON",
        experience_years=3,
        is_available=False,
    )
    session.add_all([client, engineer])
    await session.flush()
    project = Project(
        name="Sprint Tracker",
        description="API project",
        status=ProjectStatus.ACTIVE,
        start_date=date(2026, 6, 1),
        end_date=date(2026, 7, 1),
        client_id=client.id,
    )
    session.add(project)
    await session.flush()
    sprint = Sprint(
        sprint_number=1,
        goal="Ship API",
        status=SprintStatus.IN_PROGRESS,
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 14),
        project_id=project.id,
    )
    session.add(sprint)
    await session.flush()
    task = Task(
        title="Write tests",
        description="PYTHON integration tests",
        priority=TaskPriority.HIGH,
        status=TaskStatus.REVIEW,
        estimated_hours=5,
        actual_hours=2,
        sprint_id=sprint.id,
    )
    session.add(task)
    await session.commit()
    return client, project, sprint, task, engineer


@pytest.mark.asyncio
async def test_create_and_get_client(client: AsyncClient) -> None:
    response = await client.post(
        "/api/clients",
        json={
            "name": "Nova Retail",
            "industry": "Retail",
            "contact_email": "ops@nova.example.com",
            "country": "USA",
        },
    )
    assert response.status_code == 201
    client_id = response.json()["id"]

    detail = await client.get(f"/api/clients/{client_id}")
    assert detail.status_code == 200
    assert detail.json()["projects"] == []


@pytest.mark.asyncio
async def test_backwards_status_transition_returns_conflict(
    client: AsyncClient, session: AsyncSession
) -> None:
    _, _, _, task, _ = await seed_minimal(session)

    response = await client.put(f"/api/tasks/{task.id}/status", json={"status": "IN_PROGRESS"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Task status cannot move backwards"


@pytest.mark.asyncio
async def test_unavailable_engineer_assignment_returns_conflict(
    client: AsyncClient, session: AsyncSession
) -> None:
    _, _, _, task, engineer = await seed_minimal(session)

    response = await client.put(f"/api/tasks/{task.id}/assign/{engineer.id}")

    assert response.status_code == 409
    assert response.json()["detail"] == "Unavailable engineer cannot be assigned"


@pytest.mark.asyncio
async def test_sprint_summary_and_task_filter(client: AsyncClient, session: AsyncSession) -> None:
    _, _, sprint, _, _ = await seed_minimal(session)

    summary = await client.get(f"/api/sprints/{sprint.id}/summary")
    filtered = await client.get("/api/tasks?status=REVIEW&priority=HIGH")

    assert summary.status_code == 200
    assert summary.json()["task_breakdown"]["REVIEW"] == 1
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    [
        {"skip": -1},
        {"limit": 0},
        {"limit": 101},
    ],
)
async def test_client_pagination_rejects_invalid_values(
    client: AsyncClient,
    params: dict[str, int],
) -> None:
    response = await client.get("/api/clients", params=params)

    assert response.status_code == 422



@pytest.mark.asyncio
async def test_project_health_detects_offsetting_estimation_errors(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    _, project, sprint, _, _ = await seed_minimal(session)

    second_task = Task(
        title="Implement feature",
        description="Feature implementation",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.DONE,
        estimated_hours=5,
        actual_hours=8,
        sprint_id=sprint.id,
    )
    session.add(second_task)
    await session.commit()

    response = await client.get(f"/api/projects/{project.id}/health")

    assert response.status_code == 200
    assert response.json()["estimate_points"] == 8.0

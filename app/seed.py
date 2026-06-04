import asyncio
from datetime import date

from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.models import Client, Engineer, Project, Sprint, Task
from app.models.enums import ProjectStatus, SprintStatus, TaskPriority, TaskStatus


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        for model in (Task, Sprint, Project, Engineer, Client):
            await session.execute(delete(model))

        clients = [
            Client(name="Nova Retail", industry="Retail", contact_email="ops@novaretail.com", country="USA"),
            Client(name="MedAxis", industry="Healthcare", contact_email="it@medaxis.com", country="India"),
            Client(name="FinGrid", industry="Finance", contact_email="cto@fingrid.com", country="UK"),
        ]
        engineers = [
            Engineer(name="Asha Rao", email="asha@example.com", primary_stack="PYTHON", experience_years=3),
            Engineer(name="Maya Chen", email="maya@example.com", primary_stack="REACT", experience_years=2),
            Engineer(
                name="Omar Ali",
                email="omar@example.com",
                primary_stack="PYTHON",
                experience_years=5,
                is_available=False,
            ),
        ]
        session.add_all(clients + engineers)
        await session.flush()

        projects = [
            Project(
                name="Retail Sprint Tracker",
                description="Internal planning platform",
                status=ProjectStatus.ACTIVE,
                start_date=date(2026, 6, 1),
                end_date=date(2026, 8, 31),
                client_id=clients[0].id,
            ),
            Project(
                name="Claims Workflow",
                description="Healthcare workflow modernisation",
                status=ProjectStatus.ON_HOLD,
                start_date=date(2026, 5, 1),
                end_date=date(2026, 9, 30),
                client_id=clients[1].id,
            ),
        ]
        session.add_all(projects)
        await session.flush()

        sprints = [
            Sprint(
                sprint_number=1,
                goal="Build project and task foundations",
                status=SprintStatus.IN_PROGRESS,
                start_date=date(2026, 6, 1),
                end_date=date(2026, 6, 14),
                project_id=projects[0].id,
            ),
            Sprint(
                sprint_number=2,
                goal="Add analytics and reporting",
                status=SprintStatus.PLANNED,
                start_date=date(2026, 6, 15),
                end_date=date(2026, 6, 28),
                project_id=projects[0].id,
            ),
        ]
        session.add_all(sprints)
        await session.flush()

        session.add_all(
            [
                Task(
                    title="Design schema",
                    description="PYTHON SQLAlchemy model design",
                    priority=TaskPriority.HIGH,
                    status=TaskStatus.DONE,
                    estimated_hours=6,
                    actual_hours=5.5,
                    sprint_id=sprints[0].id,
                    engineer_id=engineers[0].id,
                ),
                Task(
                    title="Client CRUD",
                    description="PYTHON FastAPI routes",
                    priority=TaskPriority.HIGH,
                    status=TaskStatus.REVIEW,
                    estimated_hours=8,
                    actual_hours=7,
                    sprint_id=sprints[0].id,
                    engineer_id=engineers[0].id,
                ),
                Task(
                    title="Dashboard filters",
                    description="REACT task filtering UI contract",
                    priority=TaskPriority.MEDIUM,
                    status=TaskStatus.IN_PROGRESS,
                    estimated_hours=5,
                    actual_hours=2,
                    sprint_id=sprints[0].id,
                    engineer_id=engineers[1].id,
                ),
                Task(
                    title="Sprint summary",
                    description="PYTHON analytics endpoint",
                    priority=TaskPriority.CRITICAL,
                    status=TaskStatus.TODO,
                    estimated_hours=10,
                    actual_hours=0,
                    sprint_id=sprints[1].id,
                ),
                Task(
                    title="CSV export",
                    description="PYTHON reporting export",
                    priority=TaskPriority.LOW,
                    status=TaskStatus.TODO,
                    estimated_hours=3,
                    actual_hours=0,
                    sprint_id=sprints[1].id,
                ),
            ]
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())


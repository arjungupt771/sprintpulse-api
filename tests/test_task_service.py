from types import SimpleNamespace

import pytest

from app.core.exceptions import BusinessRuleViolationError, EngineerUnavailableError
from app.models import Engineer, Task
from app.models.enums import TaskPriority, TaskStatus
from app.services import task_service


class FakeSession:
    def __init__(self, engineer: Engineer | None = None) -> None:
        self.engineer = engineer
        self.committed = False

    async def get(self, model: type[Engineer], entity_id: int) -> Engineer | None:
        if model is Engineer and self.engineer is not None and self.engineer.id == entity_id:
            return self.engineer
        return None

    async def commit(self) -> None:
        self.committed = True

    async def refresh(self, _: object) -> None:
        return None


@pytest.mark.asyncio
async def test_task_status_cannot_move_backwards(monkeypatch: pytest.MonkeyPatch) -> None:
    task = Task(
        id=1,
        title="Review API",
        description="PYTHON review",
        priority=TaskPriority.HIGH,
        status=TaskStatus.REVIEW,
        estimated_hours=4,
        actual_hours=2,
        sprint_id=1,
    )

    async def fake_get_task(_: object, __: int) -> Task:
        return task

    monkeypatch.setattr(task_service, "get_task", fake_get_task)

    with pytest.raises(BusinessRuleViolationError):
        await task_service.update_task_status(SimpleNamespace(), 1, TaskStatus.IN_PROGRESS)


@pytest.mark.asyncio
async def test_assign_engineer_rejects_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    task = Task(
        id=1,
        title="Build API",
        description="PYTHON endpoint",
        priority=TaskPriority.HIGH,
        status=TaskStatus.TODO,
        estimated_hours=4,
        actual_hours=0,
        sprint_id=1,
    )
    engineer = Engineer(
        id=7,
        name="Unavailable Dev",
        email="unavailable@example.com",
        primary_stack="PYTHON",
        experience_years=4,
        is_available=False,
    )

    async def fake_get_task(_: object, __: int) -> Task:
        return task

    monkeypatch.setattr(task_service, "get_task", fake_get_task)

    with pytest.raises(EngineerUnavailableError):
        await task_service.assign_engineer(FakeSession(engineer), 1, 7)


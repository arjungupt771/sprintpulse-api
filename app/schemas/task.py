from pydantic import Field

from app.models.enums import TaskPriority, TaskStatus
from app.schemas.common import ApiModel, NonEmptyStringMixin


class TaskBase(NonEmptyStringMixin, ApiModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    estimated_hours: float = Field(gt=0)
    actual_hours: float = Field(default=0, ge=0)
    sprint_id: int
    engineer_id: int | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(ApiModel):
    title: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    estimated_hours: float | None = Field(default=None, gt=0)
    actual_hours: float | None = Field(default=None, ge=0)
    engineer_id: int | None = None


class TaskStatusUpdate(ApiModel):
    status: TaskStatus


class TaskResponse(TaskBase):
    id: int


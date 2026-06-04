from datetime import date

from app.models.enums import SprintStatus, TaskStatus
from app.schemas.common import ApiModel, DateRangeModel, NonEmptyStringMixin


class SprintBase(NonEmptyStringMixin, DateRangeModel):
    sprint_number: int
    goal: str
    status: SprintStatus = SprintStatus.PLANNED
    start_date: date
    end_date: date
    project_id: int


class SprintCreate(SprintBase):
    pass


class SprintResponse(SprintBase):
    id: int


class SprintSummaryResponse(ApiModel):
    sprint_id: int
    completion_percentage: float
    task_breakdown: dict[TaskStatus, int]
    overdue_count: int
    velocity: float


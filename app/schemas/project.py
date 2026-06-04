from datetime import date

from app.models.enums import ProjectStatus
from app.schemas.common import ApiModel, DateRangeModel, NonEmptyStringMixin


class ProjectBase(NonEmptyStringMixin, DateRangeModel):
    name: str
    description: str
    status: ProjectStatus = ProjectStatus.ACTIVE
    start_date: date
    end_date: date
    client_id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ApiModel):
    name: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectResponse(ProjectBase):
    id: int


class ProjectHealthResponse(ApiModel):
    project_id: int
    score: float
    formula: str
    completion_points: float
    schedule_points: float
    estimate_points: float
    sprint_points: float


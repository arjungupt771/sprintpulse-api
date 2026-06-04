from pydantic import EmailStr, Field

from app.schemas.common import ApiModel, NonEmptyStringMixin


class EngineerBase(NonEmptyStringMixin, ApiModel):
    name: str
    email: EmailStr
    primary_stack: str
    experience_years: int = Field(ge=0)
    is_available: bool = True


class EngineerCreate(EngineerBase):
    pass


class EngineerUpdate(ApiModel):
    name: str | None = None
    email: EmailStr | None = None
    primary_stack: str | None = None
    experience_years: int | None = Field(default=None, ge=0)
    is_available: bool | None = None


class EngineerResponse(EngineerBase):
    id: int


class EngineerWorkloadResponse(ApiModel):
    engineer_id: int
    active_tasks: int
    estimated_hours: float
    actual_hours: float
    stack_utilisation: str
    capacity_status: str


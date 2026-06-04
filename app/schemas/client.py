from datetime import datetime

from pydantic import EmailStr

from app.schemas.common import ApiModel, NonEmptyStringMixin


class ClientBase(NonEmptyStringMixin, ApiModel):
    name: str
    industry: str
    contact_email: EmailStr
    country: str


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ApiModel):
    name: str | None = None
    industry: str | None = None
    contact_email: EmailStr | None = None
    country: str | None = None


class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    deleted_at: datetime | None = None


class ClientWithProjects(ClientResponse):
    projects: list["ProjectResponse"] = []


from app.schemas.project import ProjectResponse  # noqa: E402

ClientWithProjects.model_rebuild()


from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.project import ProjectCreate, ProjectHealthResponse, ProjectResponse
from app.schemas.sprint import SprintResponse
from app.services import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate, session: AsyncSession = Depends(get_session)
) -> ProjectResponse:
    return ProjectResponse.model_validate(await project_service.create_project(session, payload))


@router.get("/{project_id}/sprints", response_model=list[SprintResponse])
async def get_project_sprints(
    project_id: int, session: AsyncSession = Depends(get_session)
) -> list[SprintResponse]:
    sprints = await project_service.get_project_sprints(session, project_id)
    return [SprintResponse.model_validate(sprint) for sprint in sprints]


@router.get("/{project_id}/health", response_model=ProjectHealthResponse)
async def get_project_health(
    project_id: int, session: AsyncSession = Depends(get_session)
) -> ProjectHealthResponse:
    return await project_service.get_project_health(session, project_id)


@router.get("/{project_id}/export", response_class=Response)
async def export_project_tasks(
    project_id: int, session: AsyncSession = Depends(get_session)
) -> Response:
    csv_body = await project_service.export_project_tasks_csv(session, project_id)
    return Response(
        content=csv_body,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="project-{project_id}-tasks.csv"'},
    )


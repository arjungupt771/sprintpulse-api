from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.engineer import EngineerCreate, EngineerResponse, EngineerWorkloadResponse
from app.services import engineer_service

router = APIRouter(prefix="/api/engineers", tags=["engineers"])


@router.post("", response_model=EngineerResponse, status_code=status.HTTP_201_CREATED)
async def create_engineer(
    payload: EngineerCreate, session: AsyncSession = Depends(get_session)
) -> EngineerResponse:
    return EngineerResponse.model_validate(
        await engineer_service.create_engineer(session, payload)
    )


@router.get("/available", response_model=list[EngineerResponse])
async def available_engineers(
    stack: str | None = None, session: AsyncSession = Depends(get_session)
) -> list[EngineerResponse]:
    engineers = await engineer_service.get_available_engineers(session, stack)
    return [EngineerResponse.model_validate(engineer) for engineer in engineers]


@router.get("/{engineer_id}/workload", response_model=EngineerWorkloadResponse)
async def engineer_workload(
    engineer_id: int, session: AsyncSession = Depends(get_session)
) -> EngineerWorkloadResponse:
    return await engineer_service.get_engineer_workload(session, engineer_id)


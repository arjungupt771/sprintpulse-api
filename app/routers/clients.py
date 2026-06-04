from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate, ClientWithProjects
from app.services import client_service

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate, session: AsyncSession = Depends(get_session)
) -> ClientResponse:
    return ClientResponse.model_validate(await client_service.create_client(session, payload))


@router.get("", response_model=list[ClientResponse])
async def list_clients(
    skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)
) -> list[ClientResponse]:
    clients = await client_service.list_clients(session, skip, limit)
    return [ClientResponse.model_validate(client) for client in clients]


@router.get("/{client_id}", response_model=ClientWithProjects)
async def get_client(
    client_id: int, session: AsyncSession = Depends(get_session)
) -> ClientWithProjects:
    return ClientWithProjects.model_validate(await client_service.get_client(session, client_id))


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int, payload: ClientUpdate, session: AsyncSession = Depends(get_session)
) -> ClientResponse:
    return ClientResponse.model_validate(
        await client_service.update_client(session, client_id, payload)
    )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int, session: AsyncSession = Depends(get_session)) -> None:
    await client_service.soft_delete_client(session, client_id)


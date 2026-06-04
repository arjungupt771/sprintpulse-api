from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ResourceNotFoundError
from app.models import Client
from app.schemas.client import ClientCreate, ClientUpdate


async def create_client(session: AsyncSession, payload: ClientCreate) -> Client:
    client = Client(**payload.model_dump())
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client


async def list_clients(session: AsyncSession, skip: int, limit: int) -> list[Client]:
    result = await session.execute(
        select(Client).where(Client.deleted_at.is_(None)).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_client(session: AsyncSession, client_id: int) -> Client:
    result = await session.execute(
        select(Client)
        .options(selectinload(Client.projects))
        .where(Client.id == client_id, Client.deleted_at.is_(None))
    )
    client = result.scalar_one_or_none()
    if client is None:
        raise ResourceNotFoundError("Client not found")
    return client


async def update_client(session: AsyncSession, client_id: int, payload: ClientUpdate) -> Client:
    client = await get_client(session, client_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    await session.commit()
    await session.refresh(client)
    return client


async def soft_delete_client(session: AsyncSession, client_id: int) -> None:
    client = await get_client(session, client_id)
    client.deleted_at = datetime.now(timezone.utc)
    await session.commit()


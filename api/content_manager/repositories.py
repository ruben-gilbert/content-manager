from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, List, Protocol, Type, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_manager.entities import ContentEntity, E
from content_manager.utils import get_derived_type


class Repository(Protocol[E]):
    async def add(self, entity: E) -> None:
        ...

    async def get(self) -> List[E]:
        ...

    async def get_by_id(self, id: int) -> E | None:
        ...

    async def update(self, entity: E) -> E:
        ...

    async def remove(self, id: int) -> None:
        ...


class BaseRepository(ABC, Generic[E]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._entity_type = None

    @property
    def entity_type(self) -> Type[E]:
        if not self._entity_type:
            self._entity_type = get_derived_type(self)
        return self._entity_type

    async def add(self, entity: E) -> E:
        async with self.session.begin():
            self.session.add(entity)
        return entity

    async def get(self) -> List[E]:
        async with self.session.begin():
            result = await self.session.execute(select(self.entity_type))
            return [r[0] for r in result]

    async def get_by_id(self, id: int) -> E | None:
        async with self.session.begin():
            return await self.session.get(self.entity_type, id)

    @abstractmethod
    async def update(self, entity: E) -> E:
        ...

    @abstractmethod
    async def remove(self, id: int) -> None:
        ...


R = TypeVar("R", bound=BaseRepository)


class ContentRepository(BaseRepository[ContentEntity]):
    async def add(self, entity: ContentEntity) -> ContentEntity:
        entity.last_renewed = datetime.now()
        return await super().add(entity)

    async def update(self, entity: ContentEntity) -> ContentEntity:
        async with self.session.begin():
            existing = await self.session.get(self.entity_type, entity.id)
            if not existing:
                raise ValueError(f"Content with ID {entity.id} does not exist to be updated.")
            return await self.session.merge(entity)

    async def remove(self, id: int) -> None:
        async with self.session.begin():
            await self.session.execute(delete(self.entity_type).where(self.entity_type.id == id))

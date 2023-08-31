from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, List, Protocol, Tuple, Type, TypeVar

from sqlalchemy import Select, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_manager.entities import ContentEntity, E
from content_manager.enums import ContentType
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
            q = select(self.entity_type)
            return await self.query(q)

    async def get_by_id(self, id: int) -> E | None:
        async with self.session.begin():
            return await self.session.get(self.entity_type, id)

    @abstractmethod
    async def update(self, entity: E) -> E:
        ...

    @abstractmethod
    async def remove(self, id: int) -> None:
        ...

    async def query(self, query: Select[Tuple[E]]) -> List[E]:
        async with self.session.begin():
            result = await self.session.execute(query)
            return [r[0] for r in result]


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

    async def get_by_source(self, src_name: str, src_id: int) -> ContentEntity | None:
        async with self.session.begin():
            q = (
                select(self.entity_type)
                .where(self.entity_type.source_name == src_name)
                .where(self.entity_type.source_id == src_id)
            )
            result = await self.query(q)
            return result[0] if result else None

    async def get_by_type(self, type: ContentType) -> List[ContentEntity]:
        async with self.session.begin():
            q = select(self.entity_type).where(self.entity_type.type == type)
            return await self.query(q)

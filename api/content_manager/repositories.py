from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, List, Protocol, Tuple, Type, TypeVar

from sqlalchemy import Select, and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_manager.entities import (
    ContentEntity,
    E,
    SourceContentEntity,
    SourceContentInfo,
)
from content_manager.enums import ContentType
from content_manager.utils import get_derived_type


class Repository(Protocol[E]):
    def entity_type(self) -> Type[E]:
        ...

    async def add(self, entity: E) -> E:
        ...

    async def get(self, key: Any) -> E | None:
        ...

    async def get_all(self) -> List[E]:
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

    async def get_all(self) -> List[E]:
        q = select(self.entity_type)
        return await self.query(q)

    @abstractmethod
    async def get(self, key: Any) -> E | None:
        ...

    @abstractmethod
    async def update(self, entity: E) -> E:
        ...

    @abstractmethod
    async def remove(self, key: Any) -> None:
        ...

    # TODO: Use .all()?
    async def query(self, query: Select[Tuple[E]]) -> List[E]:
        async with self.session.begin():
            result = await self.session.execute(query)
            return [r[0] for r in result]


R = TypeVar("R", bound=BaseRepository)


class ContentRepository(BaseRepository[ContentEntity]):
    async def update(self, entity: ContentEntity) -> ContentEntity:
        async with self.session.begin():
            existing = await self.session.get(self.entity_type, entity.id)
            if not existing:
                raise ValueError(f"Content with ID {entity.id} does not exist to be updated.")
            return await self.session.merge(entity)

    async def remove(self, id: int) -> None:
        async with self.session.begin():
            await self.session.execute(delete(self.entity_type).where(self.entity_type.id == id))

    async def get(self, key: int) -> ContentEntity | None:
        async with self.session.begin():
            return await self.session.get(self.entity_type, key)

    # TODO: Fix this...
    async def get_by_source(self, src: SourceContentInfo) -> ContentEntity | None:
        q = select(self.entity_type).where(
            and_(
                self.entity_type.sources.has(SourceContentEntity.name == src.name).all_(),
                self.entity_type.sources.has(SourceContentEntity.id == src.id),
            )
        )
        result = await self.query(q)
        return result[0] if result else None

    async def get_by_type(self, type: ContentType) -> List[ContentEntity]:
        q = select(self.entity_type).where(self.entity_type.type == type)
        return await self.query(q)


class SourceRepository(BaseRepository[SourceContentEntity]):
    async def add(self, entity: SourceContentEntity) -> SourceContentEntity:
        entity.last_renewed = datetime.now()
        return await super().add(entity)

    async def get(self, key: SourceContentInfo) -> SourceContentEntity | None:
        async with self.session.begin():
            return await self.session.get(self.entity_type, (key.name, key.id))

    async def update(self, entity: SourceContentEntity) -> SourceContentEntity:
        async with self.session.begin():
            existing = await self.session.get(self.entity_type, (entity.name, entity.id))
            if not existing:
                raise ValueError(
                    f"Source '{entity.name}' does not have a content item with ID {entity.id} to be updated."
                )
            return await self.session.merge(entity)

    async def remove(self, key: SourceContentInfo) -> None:
        async with self.session.begin():
            await self.session.execute(
                delete(self.entity_type)
                .where(self.entity_type.name == key.name)
                .where(self.entity_type.id == key.id)
            )

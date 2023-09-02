from datetime import datetime
from typing import Any, List, Protocol, Sequence, Tuple, Type, TypeVar

from sqlalchemy import Row, Select, and_, delete, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_manager.entities import (
    ContentEntity,
    Entity,
    SourceContentEntity,
    SourceContentInfo,
)
from content_manager.enums import ContentType

EntityType = TypeVar("EntityType", bound=Entity)


def get_entity_primary_key(entity_type: Type[EntityType]) -> str | Tuple[str]:
    pk_val = inspect(entity_type).primary_key
    if len(pk_val) == 1:
        return pk_val[0].name
    else:
        return tuple([pk.name for pk in pk_val])


class Repository(Protocol[EntityType]):
    entity_type: Type[EntityType]
    entity_pk: str | Tuple[str]
    session: AsyncSession

    async def add(self, entity: EntityType) -> EntityType:
        ...

    async def get(self, key: Any) -> EntityType | None:
        ...

    async def get_all(self) -> List[EntityType]:
        ...

    async def update(self, entity: EntityType) -> EntityType:
        ...

    async def remove(self, key: Any) -> None:
        ...


class BaseRepository(Repository[EntityType]):
    def __init__(self, entity_type: Type[EntityType], session: AsyncSession) -> None:
        self.entity_type = entity_type
        self.session = session
        self._entity_pk = None

    @property
    def entity_pk(self) -> str | Tuple[str]:
        if not self._entity_pk:
            self._entity_pk = get_entity_primary_key(self.entity_type)
        return self._entity_pk

    async def add(self, entity: EntityType) -> EntityType:
        async with self.session.begin():
            self.session.add(entity)
            return entity

    async def get_all(self) -> Sequence[Row[Tuple[EntityType]]]:
        q = select(self.entity_type)
        return await self.query(q)

    async def get(self, key: Any) -> EntityType | None:
        async with self.session.begin():
            return await self.session.get(self.entity_type, key)

    async def update(self, entity: EntityType) -> EntityType:
        async with self.session.begin():
            existing = await self.session.get(self.entity_type, self.entity_pk)
            if not existing:
                raise ValueError(f"Item does not exist to be updated.")
            return await self.session.merge(entity)

    async def remove(self, key: Any) -> None:
        async with self.session.begin():
            entity = self.session.get(self.entity_type, key)
            await self.session.delete(entity)

    async def query(self, query: Select[Tuple[EntityType]]) -> Sequence[Row[Tuple[EntityType]]]:
        async with self.session.begin():
            result = await self.session.execute(query)
            return result.all()


class ContentRepository(BaseRepository[ContentEntity]):
    # TODO: Fix this...
    async def get_by_source(self, src: SourceContentInfo) -> ContentEntity | None:
        q = select(self.entity_type).where(
            and_(
                self.entity_type.sources.has(SourceContentEntity.name == src.name).all_(),
                self.entity_type.sources.has(SourceContentEntity.id == src.id),
            )
        )
        result = await self.query(q)
        return result[0][0] if result else None

    async def get_by_type(self, t: ContentType) -> Sequence[Row[Tuple[ContentEntity]]]:
        q = select(self.entity_type).where(self.entity_type.type == t)
        return await self.query(q)


class SourceRepository(BaseRepository[SourceContentEntity]):
    async def add(self, entity: SourceContentEntity) -> SourceContentEntity:
        entity.last_renewed = datetime.now()
        return await super().add(entity)

    # TODO: Test this to see if the base implementation of update/remove works properly based on finding PKs
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

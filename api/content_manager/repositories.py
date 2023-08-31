from datetime import datetime
from typing import Generic, List, Protocol, Type, TypeVar

from sqlalchemy import select
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


# TODO: Finish making this class compatible with Repository Protocol (missing methods)
class BaseRepository(Generic[E]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._entity_type = None

    @property
    def entity_type(self) -> Type[E]:
        """
        The derived entity type of this repository.
        """
        if not self._entity_type:
            self._entity_type = get_derived_type(self)
        return self._entity_type

    async def add(self, entity: E) -> E:
        """
        TODO
        """
        async with self.session.begin():
            self.session.add(entity)
        return entity

    async def get(self) -> List[E]:
        """
        TODO
        """
        async with self.session.begin():
            result = await self.session.execute(select(self.entity_type))
            return [r[0] for r in result]

    async def get_by_id(self, id: int) -> E | None:
        """
        TODO
        """
        async with self.session.begin():
            return await self.session.get(self.entity_type, id)


R = TypeVar("R", bound=BaseRepository)


class ContentRepository(BaseRepository[ContentEntity]):
    async def add(self, entity: ContentEntity) -> ContentEntity:
        entity.last_renewed = datetime.now()
        return await super().add(entity)

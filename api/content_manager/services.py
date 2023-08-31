from typing import Generic, List, Protocol, Type

from content_manager.enums import ContentType
from content_manager.models import Content, M
from content_manager.repositories import ContentRepository, R
from content_manager.utils import get_derived_type


class Service(Protocol[R]):
    repository: R


class BaseService(Generic[M, R]):
    def __init__(self, repository: R) -> None:
        self.repository = repository
        self._model_type = None

    @property
    def model_type(self) -> Type[M]:
        if not self._model_type:
            self._model_type = get_derived_type(self)
        return self._model_type

    async def add(self, model: M) -> M:
        entity = await self.repository.add(
            self.repository.entity_type(**model.model_dump(exclude_none=True))
        )
        return self.model_type.model_validate(entity)

    async def get_all(self) -> List[M]:
        entities = await self.repository.get()
        return [self.model_type.model_validate(e) for e in entities]

    async def get_by_id(self, id: int) -> M | None:
        e = await self.repository.get_by_id(id)
        if not e:
            return None
        return self.model_type.model_validate(e)


class ContentService(BaseService[Content, ContentRepository]):
    async def get_all_by_content_type(self, content_type: ContentType) -> List[Content]:
        # TODO: complete this + repository code
        return []

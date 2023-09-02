from typing import List, Protocol, Type, TypeVar

from pydantic import BaseModel

from content_manager.enums import ContentType
from content_manager.models import Content
from content_manager.repositories import BaseRepository, ContentRepository

ModelType = TypeVar("ModelType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class Service(Protocol[ModelType, RepositoryType]):
    model_type: Type[ModelType]
    repository: RepositoryType


class BaseService(Service[ModelType, RepositoryType]):
    def __init__(self, model_type: Type[ModelType], repository: RepositoryType) -> None:
        self.model_type = model_type
        self.repository = repository

    async def add(self, model: ModelType) -> ModelType:
        entity = await self.repository.add(
            self.repository.entity_type(**model.model_dump(exclude_none=True))
        )
        return self.model_type.model_validate(entity)

    async def get_all(self) -> List[ModelType]:
        entities = await self.repository.get_all()
        return [self.model_type.model_validate(e[0]) for e in entities]

    async def get_by_id(self, id: int) -> ModelType | None:
        e = await self.repository.get(id)
        if not e:
            return None
        return self.model_type.model_validate(e)


class ContentService(BaseService[Content, ContentRepository]):
    async def get_all_by_content_type(self, content_type: ContentType) -> List[Content]:
        entities = await self.repository.get_by_type(content_type)
        return [self.model_type.model_validate(e[0]) for e in entities]

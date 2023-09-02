from typing import List

from fastapi import APIRouter, Response, status

from content_manager.db import DbSession
from content_manager.entities import ContentEntity
from content_manager.enums import ContentType
from content_manager.exceptions import NotFoundException
from content_manager.models import Content, Error
from content_manager.repositories import ContentRepository
from content_manager.services import ContentService

router = APIRouter(prefix="/content", tags=["Content"])
# TODO: Get DI working + classes rather than global variables...
repo = ContentRepository(ContentEntity, DbSession())
service = ContentService(Content, repo)


# TODO: This might end up being a common util?  How to share it?
def _get_route_name(fn, **params):
    return f"{router.url_path_for(fn.__name__, **params)}"


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_content() -> List[Content]:
    return await service.get_all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_content(content: Content, response: Response) -> Content:
    # TODO: Reject duplicate creation (here or in Service?)
    model = await service.add(content)
    response.headers["Location"] = _get_route_name(get_content_by_id, id=model.id)
    return model


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": Error, "description": "The Content was not found"}},
)
async def get_content_by_id(id: int) -> Content:
    model = await service.get_by_id(id)
    if not model:
        raise NotFoundException(detail=f"Content with ID {id} does not exist")
    return model


@router.get("/movies", status_code=status.HTTP_200_OK)
async def get_all_movies() -> List[Content]:
    return await service.get_all_by_content_type(ContentType.movie)

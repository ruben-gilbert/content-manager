from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel

from content_manager.enums import ContentType

M = TypeVar("M", bound=BaseModel)


class Error(BaseModel):
    message: str
    status_code: int


class ContentBase(BaseModel):
    source_name: str
    source_id: int
    source_type: ContentType


# TODO: Can this just be deleted?
class ContentIn(ContentBase):
    pass


class Content(ContentBase):
    id: int | None = None
    last_renewed: datetime | None = None

    class Config:
        from_attributes = True

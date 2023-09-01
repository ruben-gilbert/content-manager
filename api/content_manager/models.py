from __future__ import annotations

from datetime import datetime
from typing import List, TypeVar

from pydantic import BaseModel

from content_manager.enums import ContentType

M = TypeVar("M", bound=BaseModel)


class Error(BaseModel):
    message: str
    status_code: int


class Source(BaseModel):
    name: str
    id: str
    last_renewed: datetime
    content_id: int
    content: Content


class Content(BaseModel):
    id: int | None = None
    name: str
    type: ContentType
    sources: List[Source] = []

    class Config:
        from_attributes = True

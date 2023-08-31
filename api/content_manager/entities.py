from datetime import datetime
from typing import TypeVar

from sqlalchemy import DateTime, Enum, Identity, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from content_manager.enums import ContentType


class Entity(AsyncAttrs, DeclarativeBase):
    pass


E = TypeVar("E", bound=Entity)


class ContentEntity(Entity):
    __tablename__ = "content"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    source_name: Mapped[str] = mapped_column(String(50))
    source_id: Mapped[int] = mapped_column(Integer)
    source_type: Mapped[ContentType] = mapped_column(Enum(ContentType))
    last_renewed: Mapped[datetime] = mapped_column(DateTime)

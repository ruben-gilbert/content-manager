from __future__ import annotations

from datetime import datetime
from typing import List, TypeVar

from pydantic.dataclasses import dataclass
from sqlalchemy import DateTime, Enum, ForeignKey, Identity, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from content_manager.enums import ContentType


class Entity(AsyncAttrs, DeclarativeBase):
    pass


E = TypeVar("E", bound=Entity)


@dataclass
class SourceContentInfo:
    name: str
    id: int


class SourceContentEntity(Entity):
    __tablename__ = "source_content"

    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    last_renewed: Mapped[datetime] = mapped_column(DateTime)

    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
    content: Mapped[ContentEntity] = relationship(back_populates="sources")


class ContentEntity(Entity):
    __tablename__ = "content"

    # TODO: Maybe include a column for a list of aliases for the name?
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    type: Mapped[ContentType] = mapped_column(Enum(ContentType))

    sources: Mapped[List[SourceContentEntity]] = relationship(
        back_populates="content", lazy="selectin"
    )

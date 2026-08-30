from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.application.dtos import PostDTO
from backend.domain.entities import PostStatus


class PostCreateRequest(BaseModel):
    author_id: uuid.UUID
    title: str
    content: str = ""


class PostUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None


class PostResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    content: str
    status: PostStatus
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None

    @classmethod
    def from_dto(cls, dto: PostDTO) -> PostResponse:
        return cls(
            id=dto.id,
            author_id=dto.author_id,
            title=dto.title,
            content=dto.content,
            status=dto.status,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            published_at=dto.published_at,
        )


class PostsPageResponse(BaseModel):
    items: list[PostResponse]
    limit: int
    offset: int

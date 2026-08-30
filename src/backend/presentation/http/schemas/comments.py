from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.application.dtos import CommentDTO


class CommentCreateRequest(BaseModel):
    author_id: uuid.UUID
    content: str


class CommentResponse(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: CommentDTO) -> CommentResponse:
        return cls(
            id=dto.id,
            post_id=dto.post_id,
            author_id=dto.author_id,
            content=dto.content,
            created_at=dto.created_at,
        )


class CommentsPageResponse(BaseModel):
    items: list[CommentResponse]
    limit: int
    offset: int

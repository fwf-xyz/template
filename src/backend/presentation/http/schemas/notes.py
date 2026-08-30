from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.application.dtos import NoteDTO


class NoteCreateRequest(BaseModel):
    title: str
    content: str = ""


class NoteUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None


class NoteResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: NoteDTO) -> NoteResponse:
        return cls(
            id=dto.id,
            title=dto.title,
            content=dto.content,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class NotesPageResponse(BaseModel):
    items: list[NoteResponse]
    limit: int
    offset: int

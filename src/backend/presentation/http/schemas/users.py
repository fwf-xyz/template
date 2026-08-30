from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.application.dtos import UserDTO


class UserCreateRequest(BaseModel):
    email: str
    username: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: UserDTO) -> UserResponse:
        return cls(
            id=dto.id,
            email=dto.email,
            username=dto.username,
            created_at=dto.created_at,
        )

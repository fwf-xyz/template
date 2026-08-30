import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PostStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass(kw_only=True)
class User:
    id: uuid.UUID
    email: str
    username: str
    created_at: datetime


@dataclass(kw_only=True)
class Post:
    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    content: str
    status: PostStatus
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None


@dataclass(kw_only=True)
class Comment:
    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime

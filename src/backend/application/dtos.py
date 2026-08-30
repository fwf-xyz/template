import uuid
from dataclasses import dataclass
from datetime import datetime

from backend.domain.entities import PostStatus

# --- users ---


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserCommand:
    email: str
    username: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteUserCommand:
    user_id: uuid.UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class GetUserQuery:
    user_id: uuid.UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDTO:
    id: uuid.UUID
    email: str
    username: str
    created_at: datetime


# --- posts ---


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePostCommand:
    author_id: uuid.UUID
    title: str
    content: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdatePostCommand:
    post_id: uuid.UUID
    title: str | None = None
    content: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishPostCommand:
    post_id: uuid.UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ArchivePostCommand:
    post_id: uuid.UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class DeletePostCommand:
    post_id: uuid.UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class GetPostQuery:
    post_id: uuid.UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ListPostsQuery:
    limit: int
    offset: int
    author_id: uuid.UUID | None = None
    status: PostStatus | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PostDTO:
    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    content: str
    status: PostStatus
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None


# --- comments ---


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateCommentCommand:
    post_id: uuid.UUID
    author_id: uuid.UUID
    content: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteCommentCommand:
    comment_id: uuid.UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ListCommentsQuery:
    post_id: uuid.UUID
    limit: int
    offset: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CommentDTO:
    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime

import uuid
from contextlib import AbstractAsyncContextManager
from typing import Protocol

from backend.domain.entities import Comment, Post, PostStatus, User


class TransactionManager(Protocol):
    def transaction(self) -> AbstractAsyncContextManager[None]: ...


class UsersPort(Protocol):
    async def get_by_id(self, user_id: uuid.UUID) -> User: ...

    async def add(self, user: User) -> User: ...

    async def delete(self, user_id: uuid.UUID) -> bool: ...


class PostsPort(Protocol):
    async def get_by_id(self, post_id: uuid.UUID) -> Post: ...

    async def get_many(
        self,
        *,
        limit: int,
        offset: int,
        author_id: uuid.UUID | None = None,
        status: PostStatus | None = None,
    ) -> list[Post]: ...

    async def add(self, post: Post) -> Post: ...

    async def update(self, post: Post) -> Post: ...

    async def delete(self, post_id: uuid.UUID) -> bool: ...


class CommentsPort(Protocol):
    async def get_many(self, *, post_id: uuid.UUID, limit: int, offset: int) -> list[Comment]: ...

    async def add(self, comment: Comment) -> Comment: ...

    async def delete(self, comment_id: uuid.UUID) -> bool: ...


class PersistenceGateway(Protocol):
    manager: TransactionManager
    users: UsersPort
    posts: PostsPort
    comments: CommentsPort

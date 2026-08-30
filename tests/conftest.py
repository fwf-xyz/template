import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest

from backend.application.exceptions import ConflictError, NotFoundError
from backend.domain.entities import Comment, Post, PostStatus, User


class FakeTransactionManager:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        try:
            yield
        except BaseException:
            self.rollbacks += 1
            raise
        self.commits += 1


class FakeUsersAdapter:
    def __init__(self) -> None:
        self.storage: dict[uuid.UUID, User] = {}

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        try:
            return self.storage[user_id]
        except KeyError:
            raise NotFoundError("User not found") from None

    async def add(self, user: User) -> User:
        if any(
            u.email == user.email or u.username == user.username
            for u in self.storage.values()
        ):
            raise ConflictError("User with this email or username already exists")
        self.storage[user.id] = user
        return user

    async def delete(self, user_id: uuid.UUID) -> bool:
        return self.storage.pop(user_id, None) is not None


class FakePostsAdapter:
    def __init__(self) -> None:
        self.storage: dict[uuid.UUID, Post] = {}

    async def get_by_id(self, post_id: uuid.UUID) -> Post:
        try:
            return self.storage[post_id]
        except KeyError:
            raise NotFoundError("Post not found") from None

    async def get_many(
        self,
        *,
        limit: int,
        offset: int,
        author_id: uuid.UUID | None = None,
        status: PostStatus | None = None,
    ) -> list[Post]:
        posts = sorted(self.storage.values(), key=lambda p: p.created_at, reverse=True)
        if author_id is not None:
            posts = [p for p in posts if p.author_id == author_id]
        if status is not None:
            posts = [p for p in posts if p.status is status]
        return posts[offset : offset + limit]

    async def add(self, post: Post) -> Post:
        self.storage[post.id] = post
        return post

    async def update(self, post: Post) -> Post:
        if post.id not in self.storage:
            raise NotFoundError("Post not found")
        self.storage[post.id] = post
        return post

    async def delete(self, post_id: uuid.UUID) -> bool:
        return self.storage.pop(post_id, None) is not None


class FakeCommentsAdapter:
    def __init__(self) -> None:
        self.storage: dict[uuid.UUID, Comment] = {}

    async def get_many(
        self, *, post_id: uuid.UUID, limit: int, offset: int
    ) -> list[Comment]:
        comments = sorted(
            (c for c in self.storage.values() if c.post_id == post_id),
            key=lambda c: c.created_at,
        )
        return comments[offset : offset + limit]

    async def add(self, comment: Comment) -> Comment:
        self.storage[comment.id] = comment
        return comment

    async def delete(self, comment_id: uuid.UUID) -> bool:
        return self.storage.pop(comment_id, None) is not None


class FakeGateway:
    def __init__(self) -> None:
        self.manager = FakeTransactionManager()
        self.users = FakeUsersAdapter()
        self.posts = FakePostsAdapter()
        self.comments = FakeCommentsAdapter()


@pytest.fixture
def gateway() -> FakeGateway:
    return FakeGateway()

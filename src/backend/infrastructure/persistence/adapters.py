import uuid
from collections.abc import Mapping
from typing import Any

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.exceptions import ConflictError, NotFoundError
from backend.domain.entities import Comment, Post, PostStatus, User
from backend.infrastructure.persistence.tables import comments_table, posts_table, users_table


class SqlUsersAdapter:
    """UsersPort implementation: SQL, row-to-entity mapping, and translation
    of SQLAlchemy errors into application errors. Does not manage transactions.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        stmt = sa.select(users_table).where(users_table.c.id == user_id)
        row = (await self._session.execute(stmt)).mappings().first()
        if row is None:
            raise NotFoundError("User not found")
        return self._to_entity(row)

    async def add(self, user: User) -> User:
        stmt = sa.insert(users_table).values(**self._to_row(user)).returning(*users_table.c)
        try:
            row = (await self._session.execute(stmt)).mappings().one()
        except IntegrityError as exc:
            raise ConflictError("User with this email or username already exists") from exc
        return self._to_entity(row)

    async def delete(self, user_id: uuid.UUID) -> bool:
        stmt = (
            sa.delete(users_table)
            .where(users_table.c.id == user_id)
            .returning(users_table.c.id)
        )
        deleted_id = (await self._session.execute(stmt)).scalar_one_or_none()
        return deleted_id is not None

    @staticmethod
    def _to_entity(row: Mapping[str, Any]) -> User:
        return User(
            id=row["id"],
            email=row["email"],
            username=row["username"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _to_row(user: User) -> dict[str, Any]:
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at,
        }


class SqlPostsAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, post_id: uuid.UUID) -> Post:
        stmt = sa.select(posts_table).where(posts_table.c.id == post_id)
        row = (await self._session.execute(stmt)).mappings().first()
        if row is None:
            raise NotFoundError("Post not found")
        return self._to_entity(row)

    async def get_many(
        self,
        *,
        limit: int,
        offset: int,
        author_id: uuid.UUID | None = None,
        status: PostStatus | None = None,
    ) -> list[Post]:
        stmt = (
            sa.select(posts_table)
            .order_by(posts_table.c.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if author_id is not None:
            stmt = stmt.where(posts_table.c.author_id == author_id)
        if status is not None:
            stmt = stmt.where(posts_table.c.status == status.value)
        rows = (await self._session.execute(stmt)).mappings().all()
        return [self._to_entity(row) for row in rows]

    async def add(self, post: Post) -> Post:
        stmt = sa.insert(posts_table).values(**self._to_row(post)).returning(*posts_table.c)
        try:
            row = (await self._session.execute(stmt)).mappings().one()
        except IntegrityError as exc:
            raise ConflictError("Post author does not exist") from exc
        return self._to_entity(row)

    async def update(self, post: Post) -> Post:
        values = self._to_row(post)
        values.pop("id")
        stmt = (
            sa.update(posts_table)
            .where(posts_table.c.id == post.id)
            .values(**values)
            .returning(*posts_table.c)
        )
        row = (await self._session.execute(stmt)).mappings().first()
        if row is None:
            raise NotFoundError("Post not found")
        return self._to_entity(row)

    async def delete(self, post_id: uuid.UUID) -> bool:
        stmt = (
            sa.delete(posts_table)
            .where(posts_table.c.id == post_id)
            .returning(posts_table.c.id)
        )
        deleted_id = (await self._session.execute(stmt)).scalar_one_or_none()
        return deleted_id is not None

    @staticmethod
    def _to_entity(row: Mapping[str, Any]) -> Post:
        return Post(
            id=row["id"],
            author_id=row["author_id"],
            title=row["title"],
            content=row["content"],
            status=PostStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            published_at=row["published_at"],
        )

    @staticmethod
    def _to_row(post: Post) -> dict[str, Any]:
        return {
            "id": post.id,
            "author_id": post.author_id,
            "title": post.title,
            "content": post.content,
            "status": post.status.value,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "published_at": post.published_at,
        }


class SqlCommentsAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_many(self, *, post_id: uuid.UUID, limit: int, offset: int) -> list[Comment]:
        stmt = (
            sa.select(comments_table)
            .where(comments_table.c.post_id == post_id)
            .order_by(comments_table.c.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.execute(stmt)).mappings().all()
        return [self._to_entity(row) for row in rows]

    async def add(self, comment: Comment) -> Comment:
        stmt = (
            sa.insert(comments_table)
            .values(**self._to_row(comment))
            .returning(*comments_table.c)
        )
        try:
            row = (await self._session.execute(stmt)).mappings().one()
        except IntegrityError as exc:
            raise ConflictError("Comment references a missing post or author") from exc
        return self._to_entity(row)

    async def delete(self, comment_id: uuid.UUID) -> bool:
        stmt = (
            sa.delete(comments_table)
            .where(comments_table.c.id == comment_id)
            .returning(comments_table.c.id)
        )
        deleted_id = (await self._session.execute(stmt)).scalar_one_or_none()
        return deleted_id is not None

    @staticmethod
    def _to_entity(row: Mapping[str, Any]) -> Comment:
        return Comment(
            id=row["id"],
            post_id=row["post_id"],
            author_id=row["author_id"],
            content=row["content"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _to_row(comment: Comment) -> dict[str, Any]:
        return {
            "id": comment.id,
            "post_id": comment.post_id,
            "author_id": comment.author_id,
            "content": comment.content,
            "created_at": comment.created_at,
        }

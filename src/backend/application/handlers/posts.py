import uuid
from dataclasses import dataclass

from backend.application.dtos import (
    ArchivePostCommand,
    CreatePostCommand,
    DeletePostCommand,
    GetPostQuery,
    ListPostsQuery,
    PostDTO,
    PublishPostCommand,
    UpdatePostCommand,
)
from backend.application.exceptions import NotFoundError
from backend.application.ports import PersistenceGateway
from backend.application.presenters import present_post
from backend.domain.services import apply_post_patch, archive_post, build_post, publish_post


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePostHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: CreatePostCommand, /) -> PostDTO:
        post = build_post(
            id=uuid.uuid4(), author_id=cmd.author_id, title=cmd.title, content=cmd.content
        )
        async with self.gateway.manager.transaction():
            # Автор проверяется в той же транзакции, что и вставка поста.
            await self.gateway.users.get_by_id(cmd.author_id)
            saved = await self.gateway.posts.add(post)
        return present_post(saved)


@dataclass(frozen=True, slots=True, kw_only=True)
class GetPostHandler:
    gateway: PersistenceGateway

    async def __call__(self, query: GetPostQuery, /) -> PostDTO:
        post = await self.gateway.posts.get_by_id(query.post_id)
        return present_post(post)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListPostsHandler:
    gateway: PersistenceGateway

    async def __call__(self, query: ListPostsQuery, /) -> list[PostDTO]:
        posts = await self.gateway.posts.get_many(
            limit=query.limit,
            offset=query.offset,
            author_id=query.author_id,
            status=query.status,
        )
        return [present_post(post) for post in posts]


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdatePostHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: UpdatePostCommand, /) -> PostDTO:
        async with self.gateway.manager.transaction():
            post = await self.gateway.posts.get_by_id(cmd.post_id)
            apply_post_patch(post, title=cmd.title, content=cmd.content)
            saved = await self.gateway.posts.update(post)
        return present_post(saved)


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishPostHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: PublishPostCommand, /) -> PostDTO:
        async with self.gateway.manager.transaction():
            post = await self.gateway.posts.get_by_id(cmd.post_id)
            publish_post(post)
            saved = await self.gateway.posts.update(post)
        return present_post(saved)


@dataclass(frozen=True, slots=True, kw_only=True)
class ArchivePostHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: ArchivePostCommand, /) -> PostDTO:
        async with self.gateway.manager.transaction():
            post = await self.gateway.posts.get_by_id(cmd.post_id)
            archive_post(post)
            saved = await self.gateway.posts.update(post)
        return present_post(saved)


@dataclass(frozen=True, slots=True, kw_only=True)
class DeletePostHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: DeletePostCommand, /) -> None:
        async with self.gateway.manager.transaction():
            deleted = await self.gateway.posts.delete(cmd.post_id)
            if not deleted:
                raise NotFoundError("Post not found")

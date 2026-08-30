import uuid
from dataclasses import dataclass

from backend.application.dtos import (
    CommentDTO,
    CreateCommentCommand,
    DeleteCommentCommand,
    ListCommentsQuery,
)
from backend.application.exceptions import NotFoundError
from backend.application.ports import PersistenceGateway
from backend.application.presenters import present_comment
from backend.domain.services import build_comment


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateCommentHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: CreateCommentCommand, /) -> CommentDTO:
        # The post status is checked in the same transaction as the comment insert:
        # the post cannot get archived between the check and the write.
        async with self.gateway.manager.transaction():
            post = await self.gateway.posts.get_by_id(cmd.post_id)
            await self.gateway.users.get_by_id(cmd.author_id)
            comment = build_comment(
                id=uuid.uuid4(), post=post, author_id=cmd.author_id, content=cmd.content
            )
            saved = await self.gateway.comments.add(comment)
        return present_comment(saved)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListCommentsHandler:
    gateway: PersistenceGateway

    async def __call__(self, query: ListCommentsQuery, /) -> list[CommentDTO]:
        await self.gateway.posts.get_by_id(query.post_id)
        comments = await self.gateway.comments.get_many(
            post_id=query.post_id, limit=query.limit, offset=query.offset
        )
        return [present_comment(comment) for comment in comments]


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteCommentHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: DeleteCommentCommand, /) -> None:
        async with self.gateway.manager.transaction():
            deleted = await self.gateway.comments.delete(cmd.comment_id)
            if not deleted:
                raise NotFoundError("Comment not found")

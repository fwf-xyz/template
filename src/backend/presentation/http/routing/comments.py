import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, status

from backend.application.dtos import (
    CreateCommentCommand,
    DeleteCommentCommand,
    ListCommentsQuery,
)
from backend.application.handlers.comments import (
    CreateCommentHandler,
    DeleteCommentHandler,
    ListCommentsHandler,
)
from backend.application.ports import PersistenceGateway
from backend.presentation.http.schemas.comments import (
    CommentCreateRequest,
    CommentResponse,
    CommentsPageResponse,
)

router = APIRouter(tags=["comments"], route_class=DishkaRoute)


@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: uuid.UUID,
    payload: CommentCreateRequest,
    gateway: FromDishka[PersistenceGateway],
) -> CommentResponse:
    handler = CreateCommentHandler(gateway=gateway)
    dto = await handler(
        CreateCommentCommand(
            post_id=post_id, author_id=payload.author_id, content=payload.content
        )
    )
    return CommentResponse.from_dto(dto)


@router.get("/posts/{post_id}/comments")
async def list_comments(
    post_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> CommentsPageResponse:
    handler = ListCommentsHandler(gateway=gateway)
    dtos = await handler(ListCommentsQuery(post_id=post_id, limit=limit, offset=offset))
    return CommentsPageResponse(
        items=[CommentResponse.from_dto(dto) for dto in dtos],
        limit=limit,
        offset=offset,
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
) -> None:
    handler = DeleteCommentHandler(gateway=gateway)
    await handler(DeleteCommentCommand(comment_id=comment_id))

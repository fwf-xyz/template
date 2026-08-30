import uuid
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, status

from backend.application.dtos import (
    ArchivePostCommand,
    CreatePostCommand,
    DeletePostCommand,
    GetPostQuery,
    ListPostsQuery,
    PublishPostCommand,
    UpdatePostCommand,
)
from backend.application.handlers.posts import (
    ArchivePostHandler,
    CreatePostHandler,
    DeletePostHandler,
    GetPostHandler,
    ListPostsHandler,
    PublishPostHandler,
    UpdatePostHandler,
)
from backend.application.ports import PersistenceGateway
from backend.domain.entities import PostStatus
from backend.presentation.http.schemas.posts import (
    PostCreateRequest,
    PostResponse,
    PostsPageResponse,
    PostUpdateRequest,
)

router = APIRouter(prefix="/posts", tags=["posts"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreateRequest,
    gateway: FromDishka[PersistenceGateway],
) -> PostResponse:
    handler = CreatePostHandler(gateway=gateway)
    dto = await handler(
        CreatePostCommand(
            author_id=payload.author_id, title=payload.title, content=payload.content
        )
    )
    return PostResponse.from_dto(dto)


@router.get("/{post_id}")
async def get_post(
    post_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
) -> PostResponse:
    handler = GetPostHandler(gateway=gateway)
    dto = await handler(GetPostQuery(post_id=post_id))
    return PostResponse.from_dto(dto)


@router.get("")
async def list_posts(
    gateway: FromDishka[PersistenceGateway],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    author_id: uuid.UUID | None = None,
    status_filter: Annotated[PostStatus | None, Query(alias="status")] = None,
) -> PostsPageResponse:
    handler = ListPostsHandler(gateway=gateway)
    dtos = await handler(
        ListPostsQuery(limit=limit, offset=offset, author_id=author_id, status=status_filter)
    )
    return PostsPageResponse(
        items=[PostResponse.from_dto(dto) for dto in dtos],
        limit=limit,
        offset=offset,
    )


@router.patch("/{post_id}")
async def update_post(
    post_id: uuid.UUID,
    payload: PostUpdateRequest,
    gateway: FromDishka[PersistenceGateway],
) -> PostResponse:
    handler = UpdatePostHandler(gateway=gateway)
    dto = await handler(
        UpdatePostCommand(post_id=post_id, title=payload.title, content=payload.content)
    )
    return PostResponse.from_dto(dto)


@router.post("/{post_id}/publish")
async def publish_post(
    post_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
) -> PostResponse:
    handler = PublishPostHandler(gateway=gateway)
    dto = await handler(PublishPostCommand(post_id=post_id))
    return PostResponse.from_dto(dto)


@router.post("/{post_id}/archive")
async def archive_post(
    post_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
) -> PostResponse:
    handler = ArchivePostHandler(gateway=gateway)
    dto = await handler(ArchivePostCommand(post_id=post_id))
    return PostResponse.from_dto(dto)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
) -> None:
    handler = DeletePostHandler(gateway=gateway)
    await handler(DeletePostCommand(post_id=post_id))

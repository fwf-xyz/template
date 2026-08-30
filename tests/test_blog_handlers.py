import uuid

import pytest

from backend.application.dtos import (
    ArchivePostCommand,
    CreateCommentCommand,
    CreatePostCommand,
    CreateUserCommand,
    DeletePostCommand,
    ListPostsQuery,
    PublishPostCommand,
    UpdatePostCommand,
)
from backend.application.exceptions import ConflictError, NotFoundError
from backend.application.handlers.comments import CreateCommentHandler
from backend.application.handlers.posts import (
    ArchivePostHandler,
    CreatePostHandler,
    DeletePostHandler,
    ListPostsHandler,
    PublishPostHandler,
    UpdatePostHandler,
)
from backend.application.handlers.users import CreateUserHandler
from backend.domain.entities import PostStatus
from backend.domain.exceptions import InvalidUserError, PostStatusError

from .conftest import FakeGateway


async def _make_user(gateway: FakeGateway, email: str = "a@example.com", name: str = "author"):
    return await CreateUserHandler(gateway=gateway)(
        CreateUserCommand(email=email, username=name)
    )


async def _make_post(gateway: FakeGateway, author_id: uuid.UUID, title: str = "Post"):
    return await CreatePostHandler(gateway=gateway)(
        CreatePostCommand(author_id=author_id, title=title, content="text")
    )


# --- users ---


async def test_create_user_normalizes_email_and_commits(gateway: FakeGateway) -> None:
    dto = await _make_user(gateway, email="  A@Example.COM ")

    assert dto.email == "a@example.com"
    assert gateway.manager.commits == 1


async def test_create_user_with_invalid_email_fails_before_transaction(
    gateway: FakeGateway,
) -> None:
    with pytest.raises(InvalidUserError):
        await _make_user(gateway, email="not-an-email")

    assert not gateway.users.storage
    assert gateway.manager.commits == 0


async def test_duplicate_user_conflicts_and_rolls_back(gateway: FakeGateway) -> None:
    await _make_user(gateway)

    with pytest.raises(ConflictError):
        await _make_user(gateway)

    assert gateway.manager.rollbacks == 1


# --- posts ---


async def test_create_post_for_missing_author_raises_not_found(gateway: FakeGateway) -> None:
    with pytest.raises(NotFoundError):
        await _make_post(gateway, author_id=uuid.uuid4())

    assert not gateway.posts.storage
    assert gateway.manager.rollbacks == 1


async def test_new_post_is_draft(gateway: FakeGateway) -> None:
    user = await _make_user(gateway)

    post = await _make_post(gateway, author_id=user.id)

    assert post.status is PostStatus.DRAFT
    assert post.published_at is None


async def test_publish_draft_sets_status_and_timestamp(gateway: FakeGateway) -> None:
    user = await _make_user(gateway)
    post = await _make_post(gateway, author_id=user.id)

    published = await PublishPostHandler(gateway=gateway)(PublishPostCommand(post_id=post.id))

    assert published.status is PostStatus.PUBLISHED
    assert published.published_at is not None


async def test_publish_twice_is_rejected(gateway: FakeGateway) -> None:
    user = await _make_user(gateway)
    post = await _make_post(gateway, author_id=user.id)
    await PublishPostHandler(gateway=gateway)(PublishPostCommand(post_id=post.id))

    with pytest.raises(PostStatusError):
        await PublishPostHandler(gateway=gateway)(PublishPostCommand(post_id=post.id))


async def test_archived_post_is_read_only(gateway: FakeGateway) -> None:
    user = await _make_user(gateway)
    post = await _make_post(gateway, author_id=user.id)
    await ArchivePostHandler(gateway=gateway)(ArchivePostCommand(post_id=post.id))

    with pytest.raises(PostStatusError):
        await UpdatePostHandler(gateway=gateway)(
            UpdatePostCommand(post_id=post.id, title="new title")
        )


async def test_update_post_changes_fields(gateway: FakeGateway) -> None:
    user = await _make_user(gateway)
    post = await _make_post(gateway, author_id=user.id)

    updated = await UpdatePostHandler(gateway=gateway)(
        UpdatePostCommand(post_id=post.id, title="  Renamed  ")
    )

    assert updated.title == "Renamed"
    assert updated.content == "text"


async def test_delete_missing_post_raises_not_found(gateway: FakeGateway) -> None:
    with pytest.raises(NotFoundError):
        await DeletePostHandler(gateway=gateway)(DeletePostCommand(post_id=uuid.uuid4()))


async def test_list_posts_filters_by_status(gateway: FakeGateway) -> None:
    user = await _make_user(gateway)
    draft = await _make_post(gateway, author_id=user.id, title="Draft")
    published = await _make_post(gateway, author_id=user.id, title="Published")
    await PublishPostHandler(gateway=gateway)(PublishPostCommand(post_id=published.id))

    result = await ListPostsHandler(gateway=gateway)(
        ListPostsQuery(limit=10, offset=0, status=PostStatus.PUBLISHED)
    )

    assert [p.id for p in result] == [published.id]
    assert draft.id not in [p.id for p in result]


# --- comments ---


async def test_comment_on_draft_is_rejected(gateway: FakeGateway) -> None:
    user = await _make_user(gateway)
    post = await _make_post(gateway, author_id=user.id)

    with pytest.raises(PostStatusError):
        await CreateCommentHandler(gateway=gateway)(
            CreateCommentCommand(post_id=post.id, author_id=user.id, content="hi")
        )

    assert not gateway.comments.storage
    assert gateway.manager.rollbacks == 1


async def test_comment_on_published_post_is_created(gateway: FakeGateway) -> None:
    author = await _make_user(gateway)
    reader = await _make_user(gateway, email="r@example.com", name="reader")
    post = await _make_post(gateway, author_id=author.id)
    await PublishPostHandler(gateway=gateway)(PublishPostCommand(post_id=post.id))

    comment = await CreateCommentHandler(gateway=gateway)(
        CreateCommentCommand(post_id=post.id, author_id=reader.id, content="  nice post  ")
    )

    assert comment.content == "nice post"
    assert comment.post_id == post.id
    assert comment.id in gateway.comments.storage

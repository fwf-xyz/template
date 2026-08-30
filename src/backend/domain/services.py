import uuid
from datetime import UTC, datetime

from backend.domain.constants import (
    MAX_COMMENT_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_POST_CONTENT_LENGTH,
    MAX_TITLE_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_USERNAME_LENGTH,
)
from backend.domain.entities import Comment, Post, PostStatus, User
from backend.domain.exceptions import (
    InvalidCommentError,
    InvalidPostError,
    InvalidUserError,
    PostStatusError,
)


def build_user(*, id: uuid.UUID, email: str, username: str) -> User:
    return User(
        id=id,
        email=normalize_email(email),
        username=_validated_username(username),
        created_at=_now(),
    )


def build_post(*, id: uuid.UUID, author_id: uuid.UUID, title: str, content: str) -> Post:
    now = _now()
    return Post(
        id=id,
        author_id=author_id,
        title=_validated_title(title),
        content=_validated_post_content(content),
        status=PostStatus.DRAFT,
        created_at=now,
        updated_at=now,
        published_at=None,
    )


def apply_post_patch(post: Post, *, title: str | None = None, content: str | None = None) -> None:
    if post.status is PostStatus.ARCHIVED:
        raise PostStatusError("Archived post is read-only")
    if title is None and content is None:
        raise InvalidPostError("Nothing to update")
    if title is not None:
        post.title = _validated_title(title)
    if content is not None:
        post.content = _validated_post_content(content)
    post.updated_at = _now()


def publish_post(post: Post) -> None:
    if post.status is not PostStatus.DRAFT:
        raise PostStatusError(f"Only a draft can be published, post is {post.status}")
    now = _now()
    post.status = PostStatus.PUBLISHED
    post.published_at = now
    post.updated_at = now


def archive_post(post: Post) -> None:
    if post.status is PostStatus.ARCHIVED:
        raise PostStatusError("Post is already archived")
    post.status = PostStatus.ARCHIVED
    post.updated_at = _now()


def build_comment(*, id: uuid.UUID, post: Post, author_id: uuid.UUID, content: str) -> Comment:
    ensure_commentable(post)
    return Comment(
        id=id,
        post_id=post.id,
        author_id=author_id,
        content=_validated_comment_content(content),
        created_at=_now(),
    )


def ensure_commentable(post: Post) -> None:
    if post.status is not PostStatus.PUBLISHED:
        raise PostStatusError("Comments are allowed only on published posts")


def normalize_email(email: str) -> str:
    email = email.strip().lower()
    if len(email) > MAX_EMAIL_LENGTH:
        raise InvalidUserError(f"Email must be at most {MAX_EMAIL_LENGTH} characters")
    local, sep, domain = email.partition("@")
    if not sep or not local or "." not in domain or domain.startswith("."):
        raise InvalidUserError("Invalid email address")
    return email


def _validated_username(username: str) -> str:
    username = username.strip()
    if len(username) < MIN_USERNAME_LENGTH:
        raise InvalidUserError(f"Username must be at least {MIN_USERNAME_LENGTH} characters")
    if len(username) > MAX_USERNAME_LENGTH:
        raise InvalidUserError(f"Username must be at most {MAX_USERNAME_LENGTH} characters")
    return username


def _validated_title(title: str) -> str:
    title = title.strip()
    if not title:
        raise InvalidPostError("Title must not be empty")
    if len(title) > MAX_TITLE_LENGTH:
        raise InvalidPostError(f"Title must be at most {MAX_TITLE_LENGTH} characters")
    return title


def _validated_post_content(content: str) -> str:
    if len(content) > MAX_POST_CONTENT_LENGTH:
        raise InvalidPostError(
            f"Content must be at most {MAX_POST_CONTENT_LENGTH} characters"
        )
    return content


def _validated_comment_content(content: str) -> str:
    content = content.strip()
    if not content:
        raise InvalidCommentError("Comment must not be empty")
    if len(content) > MAX_COMMENT_LENGTH:
        raise InvalidCommentError(f"Comment must be at most {MAX_COMMENT_LENGTH} characters")
    return content


def _now() -> datetime:
    return datetime.now(tz=UTC)

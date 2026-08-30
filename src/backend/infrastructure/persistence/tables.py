import sqlalchemy as sa

from backend.domain.constants import MAX_EMAIL_LENGTH, MAX_TITLE_LENGTH, MAX_USERNAME_LENGTH

metadata = sa.MetaData()

users_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("email", sa.String(MAX_EMAIL_LENGTH), nullable=False, unique=True),
    sa.Column("username", sa.String(MAX_USERNAME_LENGTH), nullable=False, unique=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

posts_table = sa.Table(
    "posts",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "author_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    sa.Column("title", sa.String(MAX_TITLE_LENGTH), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("status", sa.String(20), nullable=False, index=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
)

comments_table = sa.Table(
    "comments",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "post_id",
        sa.Uuid(),
        sa.ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    sa.Column(
        "author_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

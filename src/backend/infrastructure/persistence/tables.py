import sqlalchemy as sa

from backend.domain.constants import MAX_TITLE_LENGTH

metadata = sa.MetaData()

notes_table = sa.Table(
    "notes",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("title", sa.String(MAX_TITLE_LENGTH), nullable=False, unique=True),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

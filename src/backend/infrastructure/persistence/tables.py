import sqlalchemy as sa

metadata = sa.MetaData()

notes_table = sa.Table(
    "notes",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("title", sa.String(200), nullable=False, unique=True),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

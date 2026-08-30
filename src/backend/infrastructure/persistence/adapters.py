import uuid
from collections.abc import Mapping
from typing import Any

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.exceptions import ConflictError, NotFoundError
from backend.domain.entities import Note
from backend.infrastructure.persistence.tables import notes_table


class SqlNotesAdapter:
    """Реализация NotesPort: SQL, маппинг строк в доменную сущность
    и перевод ошибок SQLAlchemy в ошибки приложения. Транзакциями не управляет.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, note_id: uuid.UUID) -> Note:
        stmt = sa.select(notes_table).where(notes_table.c.id == note_id)
        row = (await self._session.execute(stmt)).mappings().first()
        if row is None:
            raise NotFoundError("Note not found")
        return _row_to_note(row)

    async def get_many(self, *, limit: int, offset: int) -> list[Note]:
        stmt = (
            sa.select(notes_table)
            .order_by(notes_table.c.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.execute(stmt)).mappings().all()
        return [_row_to_note(row) for row in rows]

    async def add(self, note: Note) -> Note:
        stmt = sa.insert(notes_table).values(**_note_to_row(note)).returning(*notes_table.c)
        try:
            row = (await self._session.execute(stmt)).mappings().one()
        except IntegrityError as exc:
            raise ConflictError("Note with this title already exists") from exc
        return _row_to_note(row)

    async def update(self, note: Note) -> Note:
        values = _note_to_row(note)
        values.pop("id")
        stmt = (
            sa.update(notes_table)
            .where(notes_table.c.id == note.id)
            .values(**values)
            .returning(*notes_table.c)
        )
        try:
            row = (await self._session.execute(stmt)).mappings().first()
        except IntegrityError as exc:
            raise ConflictError("Note with this title already exists") from exc
        if row is None:
            raise NotFoundError("Note not found")
        return _row_to_note(row)

    async def delete(self, note_id: uuid.UUID) -> bool:
        stmt = (
            sa.delete(notes_table)
            .where(notes_table.c.id == note_id)
            .returning(notes_table.c.id)
        )
        deleted_id = (await self._session.execute(stmt)).scalar_one_or_none()
        return deleted_id is not None


def _row_to_note(row: Mapping[str, Any]) -> Note:
    return Note(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _note_to_row(note: Note) -> dict[str, Any]:
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }

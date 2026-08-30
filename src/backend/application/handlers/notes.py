import uuid
from dataclasses import dataclass

from backend.application.dtos import (
    CreateNoteCommand,
    DeleteNoteCommand,
    GetNoteQuery,
    ListNotesQuery,
    NoteDTO,
    UpdateNoteCommand,
)
from backend.application.exceptions import NotFoundError
from backend.application.ports import PersistenceGateway
from backend.application.presenters import present_note
from backend.domain.services import apply_note_patch, build_note


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateNoteHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: CreateNoteCommand, /) -> NoteDTO:
        note = build_note(id=uuid.uuid4(), title=cmd.title, content=cmd.content)
        async with self.gateway.manager.transaction():
            saved = await self.gateway.notes.add(note)
        return present_note(saved)


@dataclass(frozen=True, slots=True, kw_only=True)
class GetNoteHandler:
    gateway: PersistenceGateway

    async def __call__(self, query: GetNoteQuery, /) -> NoteDTO:
        note = await self.gateway.notes.get_by_id(query.note_id)
        return present_note(note)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListNotesHandler:
    gateway: PersistenceGateway

    async def __call__(self, query: ListNotesQuery, /) -> list[NoteDTO]:
        notes = await self.gateway.notes.get_many(limit=query.limit, offset=query.offset)
        return [present_note(note) for note in notes]


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateNoteHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: UpdateNoteCommand, /) -> NoteDTO:
        # Чтение и запись — в одной транзакции: между ними патч не потеряет инварианты.
        async with self.gateway.manager.transaction():
            note = await self.gateway.notes.get_by_id(cmd.note_id)
            apply_note_patch(note, title=cmd.title, content=cmd.content)
            saved = await self.gateway.notes.update(note)
        return present_note(saved)


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteNoteHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: DeleteNoteCommand, /) -> None:
        async with self.gateway.manager.transaction():
            deleted = await self.gateway.notes.delete(cmd.note_id)
            if not deleted:
                raise NotFoundError("Note not found")

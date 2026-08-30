import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateNoteCommand:
    title: str
    content: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateNoteCommand:
    note_id: uuid.UUID
    title: str | None = None
    content: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteNoteCommand:
    note_id: uuid.UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class GetNoteQuery:
    note_id: uuid.UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ListNotesQuery:
    limit: int
    offset: int


@dataclass(frozen=True, slots=True, kw_only=True)
class NoteDTO:
    id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

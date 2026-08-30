from backend.application.dtos import NoteDTO
from backend.domain.entities import Note


def present_note(note: Note) -> NoteDTO:
    return NoteDTO(
        id=note.id,
        title=note.title,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )

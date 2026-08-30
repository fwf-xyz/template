import uuid
from datetime import UTC, datetime

from backend.domain.entities import Note
from backend.domain.exceptions import InvalidNoteError

MAX_TITLE_LENGTH = 200
MAX_CONTENT_LENGTH = 10_000


def build_note(*, id: uuid.UUID, title: str, content: str) -> Note:
    now = datetime.now(tz=UTC)
    return Note(
        id=id,
        title=_validated_title(title),
        content=_validated_content(content),
        created_at=now,
        updated_at=now,
    )


def apply_note_patch(note: Note, *, title: str | None = None, content: str | None = None) -> None:
    if title is None and content is None:
        raise InvalidNoteError("Nothing to update")
    if title is not None:
        note.title = _validated_title(title)
    if content is not None:
        note.content = _validated_content(content)
    note.updated_at = datetime.now(tz=UTC)


def _validated_title(title: str) -> str:
    title = title.strip()
    if not title:
        raise InvalidNoteError("Title must not be empty")
    if len(title) > MAX_TITLE_LENGTH:
        raise InvalidNoteError(f"Title must be at most {MAX_TITLE_LENGTH} characters")
    return title


def _validated_content(content: str) -> str:
    if len(content) > MAX_CONTENT_LENGTH:
        raise InvalidNoteError(f"Content must be at most {MAX_CONTENT_LENGTH} characters")
    return content

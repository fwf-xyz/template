import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest

from backend.application.dtos import (
    CreateNoteCommand,
    DeleteNoteCommand,
    GetNoteQuery,
    ListNotesQuery,
    UpdateNoteCommand,
)
from backend.application.exceptions import ConflictError, NotFoundError
from backend.application.handlers.notes import (
    CreateNoteHandler,
    DeleteNoteHandler,
    GetNoteHandler,
    ListNotesHandler,
    UpdateNoteHandler,
)
from backend.domain.entities import Note
from backend.domain.exceptions import InvalidNoteError


class FakeTransactionManager:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        try:
            yield
        except BaseException:
            self.rollbacks += 1
            raise
        self.commits += 1


class FakeNotesAdapter:
    def __init__(self) -> None:
        self.storage: dict[uuid.UUID, Note] = {}

    async def get_by_id(self, note_id: uuid.UUID) -> Note:
        try:
            return self.storage[note_id]
        except KeyError:
            raise NotFoundError("Note not found") from None

    async def get_many(self, *, limit: int, offset: int) -> list[Note]:
        notes = sorted(self.storage.values(), key=lambda n: n.created_at, reverse=True)
        return notes[offset : offset + limit]

    async def add(self, note: Note) -> Note:
        if any(existing.title == note.title for existing in self.storage.values()):
            raise ConflictError("Note with this title already exists")
        self.storage[note.id] = note
        return note

    async def update(self, note: Note) -> Note:
        if note.id not in self.storage:
            raise NotFoundError("Note not found")
        self.storage[note.id] = note
        return note

    async def delete(self, note_id: uuid.UUID) -> bool:
        return self.storage.pop(note_id, None) is not None


class FakeGateway:
    def __init__(self) -> None:
        self.manager = FakeTransactionManager()
        self.notes = FakeNotesAdapter()


@pytest.fixture
def gateway() -> FakeGateway:
    return FakeGateway()


async def test_create_note_persists_and_commits(gateway: FakeGateway) -> None:
    handler = CreateNoteHandler(gateway=gateway)

    dto = await handler(CreateNoteCommand(title="  first  ", content="hello"))

    assert dto.title == "first"  # домен нормализует title
    assert dto.id in gateway.notes.storage
    assert gateway.manager.commits == 1


async def test_create_note_with_empty_title_rejected_before_transaction(
    gateway: FakeGateway,
) -> None:
    handler = CreateNoteHandler(gateway=gateway)

    with pytest.raises(InvalidNoteError):
        await handler(CreateNoteCommand(title="   ", content=""))

    assert not gateway.notes.storage
    assert gateway.manager.commits == 0
    assert gateway.manager.rollbacks == 0


async def test_create_duplicate_title_conflicts_and_rolls_back(gateway: FakeGateway) -> None:
    handler = CreateNoteHandler(gateway=gateway)
    await handler(CreateNoteCommand(title="same", content=""))

    with pytest.raises(ConflictError):
        await handler(CreateNoteCommand(title="same", content="other"))

    assert gateway.manager.rollbacks == 1


async def test_get_missing_note_raises_not_found(gateway: FakeGateway) -> None:
    handler = GetNoteHandler(gateway=gateway)

    with pytest.raises(NotFoundError):
        await handler(GetNoteQuery(note_id=uuid.uuid4()))


async def test_update_note_changes_fields_in_one_transaction(gateway: FakeGateway) -> None:
    created = await CreateNoteHandler(gateway=gateway)(
        CreateNoteCommand(title="old", content="old content")
    )

    dto = await UpdateNoteHandler(gateway=gateway)(
        UpdateNoteCommand(note_id=created.id, title="new")
    )

    assert dto.title == "new"
    assert dto.content == "old content"
    assert dto.updated_at >= created.updated_at
    assert gateway.manager.commits == 2


async def test_update_with_empty_patch_rejected(gateway: FakeGateway) -> None:
    created = await CreateNoteHandler(gateway=gateway)(CreateNoteCommand(title="a", content=""))

    with pytest.raises(InvalidNoteError):
        await UpdateNoteHandler(gateway=gateway)(UpdateNoteCommand(note_id=created.id))

    assert gateway.manager.rollbacks == 1


async def test_delete_note_removes_it(gateway: FakeGateway) -> None:
    created = await CreateNoteHandler(gateway=gateway)(CreateNoteCommand(title="a", content=""))

    await DeleteNoteHandler(gateway=gateway)(DeleteNoteCommand(note_id=created.id))

    assert not gateway.notes.storage


async def test_delete_missing_note_raises_not_found(gateway: FakeGateway) -> None:
    with pytest.raises(NotFoundError):
        await DeleteNoteHandler(gateway=gateway)(DeleteNoteCommand(note_id=uuid.uuid4()))


async def test_list_notes_paginates(gateway: FakeGateway) -> None:
    create = CreateNoteHandler(gateway=gateway)
    for i in range(5):
        await create(CreateNoteCommand(title=f"note-{i}", content=""))

    page = await ListNotesHandler(gateway=gateway)(ListNotesQuery(limit=2, offset=1))

    assert len(page) == 2

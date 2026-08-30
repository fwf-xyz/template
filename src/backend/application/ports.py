import uuid
from contextlib import AbstractAsyncContextManager
from typing import Protocol

from backend.domain.entities import Note


class TransactionManager(Protocol):
    def transaction(self) -> AbstractAsyncContextManager[None]:
        """Граница атомарной операции: commit при выходе, rollback при исключении."""
        ...


class NotesPort(Protocol):
    async def get_by_id(self, note_id: uuid.UUID) -> Note: ...

    async def get_many(self, *, limit: int, offset: int) -> list[Note]: ...

    async def add(self, note: Note) -> Note: ...

    async def update(self, note: Note) -> Note: ...

    async def delete(self, note_id: uuid.UUID) -> bool: ...


class PersistenceGateway(Protocol):
    """Всё, что application-слой знает о хранилище. Реализация живёт в infrastructure."""

    manager: TransactionManager
    notes: NotesPort

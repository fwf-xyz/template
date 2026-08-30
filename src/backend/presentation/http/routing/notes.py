import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, status

from backend.application.dtos import (
    CreateNoteCommand,
    DeleteNoteCommand,
    GetNoteQuery,
    ListNotesQuery,
    UpdateNoteCommand,
)
from backend.application.handlers.notes import (
    CreateNoteHandler,
    DeleteNoteHandler,
    GetNoteHandler,
    ListNotesHandler,
    UpdateNoteHandler,
)
from backend.application.ports import PersistenceGateway
from backend.presentation.http.schemas.notes import (
    NoteCreateRequest,
    NoteResponse,
    NotesPageResponse,
    NoteUpdateRequest,
)

router = APIRouter(prefix="/notes", tags=["notes"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreateRequest,
    gateway: FromDishka[PersistenceGateway],
) -> NoteResponse:
    handler = CreateNoteHandler(gateway=gateway)
    dto = await handler(CreateNoteCommand(title=payload.title, content=payload.content))
    return NoteResponse.from_dto(dto)


@router.get("/{note_id}")
async def get_note(
    note_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
) -> NoteResponse:
    handler = GetNoteHandler(gateway=gateway)
    dto = await handler(GetNoteQuery(note_id=note_id))
    return NoteResponse.from_dto(dto)


@router.get("")
async def list_notes(
    gateway: FromDishka[PersistenceGateway],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> NotesPageResponse:
    handler = ListNotesHandler(gateway=gateway)
    dtos = await handler(ListNotesQuery(limit=limit, offset=offset))
    return NotesPageResponse(
        items=[NoteResponse.from_dto(dto) for dto in dtos],
        limit=limit,
        offset=offset,
    )


@router.patch("/{note_id}")
async def update_note(
    note_id: uuid.UUID,
    payload: NoteUpdateRequest,
    gateway: FromDishka[PersistenceGateway],
) -> NoteResponse:
    handler = UpdateNoteHandler(gateway=gateway)
    dto = await handler(
        UpdateNoteCommand(note_id=note_id, title=payload.title, content=payload.content)
    )
    return NoteResponse.from_dto(dto)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
) -> None:
    handler = DeleteNoteHandler(gateway=gateway)
    await handler(DeleteNoteCommand(note_id=note_id))

import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from backend.application.dtos import CreateUserCommand, DeleteUserCommand, GetUserQuery
from backend.application.handlers.users import (
    CreateUserHandler,
    DeleteUserHandler,
    GetUserHandler,
)
from backend.application.ports import PersistenceGateway
from backend.presentation.http.schemas.users import UserCreateRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    gateway: FromDishka[PersistenceGateway],
) -> UserResponse:
    handler = CreateUserHandler(gateway=gateway)
    dto = await handler(CreateUserCommand(email=payload.email, username=payload.username))
    return UserResponse.from_dto(dto)


@router.get("/{user_id}")
async def get_user(
    user_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
) -> UserResponse:
    handler = GetUserHandler(gateway=gateway)
    dto = await handler(GetUserQuery(user_id=user_id))
    return UserResponse.from_dto(dto)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    gateway: FromDishka[PersistenceGateway],
) -> None:
    handler = DeleteUserHandler(gateway=gateway)
    await handler(DeleteUserCommand(user_id=user_id))

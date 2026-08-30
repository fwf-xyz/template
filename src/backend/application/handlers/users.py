import uuid
from dataclasses import dataclass

from backend.application.dtos import (
    CreateUserCommand,
    DeleteUserCommand,
    GetUserQuery,
    UserDTO,
)
from backend.application.exceptions import NotFoundError
from backend.application.ports import PersistenceGateway
from backend.application.presenters import present_user
from backend.domain.services import build_user


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: CreateUserCommand, /) -> UserDTO:
        user = build_user(id=uuid.uuid4(), email=cmd.email, username=cmd.username)
        async with self.gateway.manager.transaction():
            saved = await self.gateway.users.add(user)
        return present_user(saved)


@dataclass(frozen=True, slots=True, kw_only=True)
class GetUserHandler:
    gateway: PersistenceGateway

    async def __call__(self, query: GetUserQuery, /) -> UserDTO:
        user = await self.gateway.users.get_by_id(query.user_id)
        return present_user(user)


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteUserHandler:
    gateway: PersistenceGateway

    async def __call__(self, cmd: DeleteUserCommand, /) -> None:
        async with self.gateway.manager.transaction():
            deleted = await self.gateway.users.delete(cmd.user_id)
            if not deleted:
                raise NotFoundError("User not found")

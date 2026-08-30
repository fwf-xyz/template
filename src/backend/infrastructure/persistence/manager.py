from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


class TransactionManagerImpl:
    """Transaction boundaries on top of a single request-scoped session.

    The session lives for the whole HTTP request (provided by DI), while a
    transaction exists only inside `transaction()`. A nested call does not open
    a second transaction — it joins the already open one, and only the outermost
    boundary commits or rolls back.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._depth = 0

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        if self._depth > 0:
            self._depth += 1
            try:
                yield
            finally:
                self._depth -= 1
            return

        self._depth = 1
        try:
            if not self._session.in_transaction():
                await self._session.begin()
            try:
                yield
            except BaseException:
                await self._session.rollback()
                raise
            await self._session.commit()
        finally:
            self._depth = 0

from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.persistence.adapters import (
    SqlCommentsAdapter,
    SqlPostsAdapter,
    SqlUsersAdapter,
)
from backend.infrastructure.persistence.manager import TransactionManagerImpl


class PersistenceGatewayImpl:
    """Single access point to storage: the transaction manager plus adapters,
    all on top of the same request-scoped session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.manager = TransactionManagerImpl(session)
        self.users = SqlUsersAdapter(session)
        self.posts = SqlPostsAdapter(session)
        self.comments = SqlCommentsAdapter(session)

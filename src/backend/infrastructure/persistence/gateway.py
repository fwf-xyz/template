from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.persistence.adapters import SqlNotesAdapter
from backend.infrastructure.persistence.manager import TransactionManagerImpl


class PersistenceGatewayImpl:
    """Единая точка доступа к хранилищу: менеджер транзакций + адаптеры,
    все поверх одной и той же request-scoped сессии.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.manager = TransactionManagerImpl(session)
        self.notes = SqlNotesAdapter(session)

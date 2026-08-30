from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from backend.application.ports import PersistenceGateway
from backend.infrastructure.persistence.gateway import PersistenceGatewayImpl
from backend.infrastructure.persistence.session import create_engine, create_session_factory
from backend.presentation.settings import Settings


class AppProvider(Provider):
    """Scope.APP — на всё время жизни процесса: пул соединений и фабрика сессий."""

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    @provide(scope=Scope.APP)
    async def engine(self) -> AsyncIterator[AsyncEngine]:
        engine = create_engine(
            self._settings.database_url,
            echo=self._settings.db_echo,
            pool_size=self._settings.db_pool_size,
            max_overflow=self._settings.db_max_overflow,
        )
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(engine)


class RequestProvider(Provider):
    """Scope.REQUEST — на один HTTP-запрос: одна сессия и гейтвей поверх неё."""

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def gateway(self, session: AsyncSession) -> PersistenceGateway:
        return PersistenceGatewayImpl(session)

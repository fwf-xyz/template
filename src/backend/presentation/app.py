from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from backend.presentation.di.container import build_container
from backend.presentation.http.errors import setup_exception_handlers
from backend.presentation.http.routing.router import api_router
from backend.presentation.settings import Settings


def create_app() -> FastAPI:
    settings = Settings()
    container = build_container(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await container.close()

    app = FastAPI(title="Blog API", lifespan=lifespan)
    setup_dishka(container, app)
    setup_exception_handlers(app)
    app.include_router(api_router)
    return app

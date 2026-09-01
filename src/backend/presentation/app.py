from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.application.exceptions import AppError
from backend.domain.exceptions import DomainError, PostStatusError
from backend.presentation.di.container import build_container
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
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(DomainError, _domain_error_handler)
    app.add_exception_handler(PostStatusError, _post_status_error_handler)
    app.include_router(api_router)
    return app


def _app_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AppError):
        raise exc
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": str(exc)},
    )


def _domain_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, DomainError):
        raise exc
    return JSONResponse(
        status_code=400,
        content={"code": "domain.invalid", "message": str(exc)},
    )


def _post_status_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, PostStatusError):
        raise exc
    return JSONResponse(
        status_code=409,
        content={"code": "post.status_conflict", "message": str(exc)},
    )

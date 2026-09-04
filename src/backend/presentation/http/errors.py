from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.application.exceptions import AppError
from backend.domain.exceptions import DomainError, PostStatusError

_DOMAIN_ERROR_STATUS: dict[type[DomainError], tuple[int, str]] = {
    PostStatusError: (409, "post.status_conflict"),
    DomainError: (400, "domain.invalid"),
}


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _handle_app_error)
    app.add_exception_handler(DomainError, _handle_domain_error)


def _handle_app_error(_request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AppError):
        raise exc
    return _error_response(exc.status_code, exc.code, str(exc))


def _handle_domain_error(_request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, DomainError):
        raise exc
    for cls in type(exc).__mro__:
        if cls in _DOMAIN_ERROR_STATUS:
            status_code, code = _DOMAIN_ERROR_STATUS[cls]
            return _error_response(status_code, code, str(exc))
    raise exc


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message})

from typing import ClassVar


class AppError(Exception):
    """Base application error: caught at the HTTP edge and turned into a JSON response."""

    status_code: ClassVar[int] = 400
    code: ClassVar[str] = "app.error"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"

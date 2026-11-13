"""Application errors and response handlers."""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Base application error."""

    error_type = "internal_error"
    default_message = "Internal server error"
    status_code = 500

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class UnauthorizedError(ApiError):
    """Missing or invalid API key."""

    error_type = "unauthorized"
    default_message = "Invalid or missing API key"
    status_code = 401


class NotFoundError(ApiError):
    """Requested resource does not exist."""

    error_type = "not_found"
    default_message = "Resource not found"
    status_code = 404


class ForbiddenError(ApiError):
    """Operation is forbidden for the current user."""

    error_type = "forbidden"
    default_message = "Access denied"
    status_code = 403


class ConflictError(ApiError):
    """Operation conflicts with the current state."""

    error_type = "conflict"
    default_message = "Operation conflicts with current state"
    status_code = 409


def error_response(
    status_code: int,
    error_type: str,
    message: str,
) -> JSONResponse:
    """Build an error response in the project format."""
    return JSONResponse(
        status_code=status_code,
        content={
            "result": False,
            "error_type": error_type,
            "error_message": message,
        },
    )


async def api_error_handler(
    _: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle expected application errors."""
    assert isinstance(exc, ApiError)
    return error_response(
        exc.status_code,
        exc.error_type,
        exc.message,
    )


async def validation_error_handler(
    _: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle invalid request bodies and parameters."""
    assert isinstance(exc, RequestValidationError)
    messages = [
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    ]
    return error_response(
        422,
        "validation_error",
        "; ".join(messages),
    )


async def http_error_handler(
    _: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle HTTP errors, including unknown routes."""
    assert isinstance(exc, StarletteHTTPException)
    return error_response(
        exc.status_code,
        "http_error",
        str(exc.detail),
    )


async def unexpected_error_handler(
    _: Request,
    exc: Exception,
) -> JSONResponse:
    """Log unexpected errors without exposing internals."""
    logger.exception("Unhandled application error")
    return error_response(
        500,
        "internal_error",
        "Internal server error",
    )

"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import UnauthorizedError
from app.models import User

api_key_header = APIKeyHeader(name="api-key", auto_error=False)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    api_key: Annotated[str | None, Depends(api_key_header)],
) -> User:
    """Resolve the current user by the `api-key` header."""
    if not api_key:
        raise UnauthorizedError()

    user = db.scalar(
        select(User).where(User.api_key == api_key)
    )

    if user is None:
        raise UnauthorizedError()

    return user
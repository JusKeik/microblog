"""Demo data used for local development and demonstration."""

from sqlalchemy import select

from app.database import SessionLocal
from app.models import User


def seed_demo_data() -> None:
    """Create demo users if the database is empty."""
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)):
            return

        db.add_all(
            [
                User(name="Alice", api_key="test-key-alice"),
                User(name="Bob", api_key="test-key-bob"),
                User(name="Carol", api_key="test-key-carol"),
            ]
        )
        db.commit()
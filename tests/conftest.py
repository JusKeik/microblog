from collections.abc import Generator
from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.database import get_db
from app.main import app
from app.models import Base, User

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Provide an isolated database session for each test."""
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        users = [
            User(name="Alice", api_key="alice-key"),
            User(name="Bob", api_key="bob-key"),
            User(name="Carol", api_key="carol-key"),
        ]
        session.add_all(users)
        session.commit()

        yield session

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session, tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client using the test database."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db

    @asynccontextmanager
    async def test_lifespan(_):
        yield

    monkeypatch.setattr(app.router, "lifespan_context", test_lifespan)
    monkeypatch.setattr(get_settings(), "media_directory", str(tmp_path / "media"))
    for route in app.routes:
        if getattr(route, "name", None) == "media":
            (tmp_path / "media").mkdir(exist_ok=True)
            monkeypatch.setattr(route.app, "directory", str(tmp_path / "media"))
            monkeypatch.setattr(route.app, "all_directories", [str(tmp_path / "media")])
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

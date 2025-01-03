import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """Create a test instance of the FastAPI application."""
    return app


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def test_db(test_db_engine: Any) -> Generator[Session, None, None]:
    """Create a test database session."""
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    db = session_local()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for making HTTP requests."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

"""Main FastAPI application module."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from database import create_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from health.routes import router as health_router
from jira.routes import router as jira_router
from logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager.

    This runs on startup and shutdown of the application.

    Args:
        app: The FastAPI application instance

    Yields:
        None
    """
    logger.info("Application starting up")
    logger.info("API docs available at: /api/docs")
    create_tables()  # Create database tables on startup
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Jira Agent API",
    description="API for interacting with Jira using an AI agent",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(health_router)
app.include_router(jira_router)

# Log registered routes
for route in app.routes:
    logger.info(f"Registered route: {route.path} [{','.join(route.methods)}]")

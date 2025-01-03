from config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logger import logger
from routes import health, jira, test

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jira.router)
app.include_router(test.router)
app.include_router(health.router)


@app.on_event("startup")
async def startup_event() -> None:
    """Log when the application starts"""
    logger.info("Application starting up")
    logger.info(f"API docs available at: {settings.API_V1_STR}/docs")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Log when the application shuts down"""
    logger.info("Application shutting down")

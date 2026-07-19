"""
Guardian Council AI - FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.utils.exceptions import GuardianCouncilError
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Agentic AI Emergency Decision Support System powered by "
        "LangGraph multi-agent orchestration and Retrieval-Augmented Generation."
    ),
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(GuardianCouncilError)
async def guardian_council_exception_handler(
    request: Request,
    exc: GuardianCouncilError,
) -> JSONResponse:
    """Return a consistent JSON error payload for known application errors."""
    logger.error("GuardianCouncilError on %s: %s", request.url.path, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all handler so unexpected errors never leak stack traces."""
    logger.exception("Unhandled exception on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred.",
        },
    )
@app.on_event("startup")
async def on_startup():
    logger.info(
        "Starting %s in '%s' environment",
        settings.APP_NAME,
        settings.APP_ENV,
    )


# Routers
from app.routes import agents, chat, documents, health, ingest, report

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(agents.router)
app.include_router(documents.router)
app.include_router(report.router)


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict:
    """Basic root endpoint confirming the API is reachable."""
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "environment": settings.APP_ENV,
    }
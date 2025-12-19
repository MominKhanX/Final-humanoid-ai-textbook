"""
FastAPI Application Entry Point for RAG Chatbot Backend
Intelligent Q&A System for NeuroBot Physical AI & Humanoid Robotics Textbook
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from src.config import settings
from src.database import db, qdrant
from src.api import chat, health
from src.middleware.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("[INFO] Starting RAG Chatbot Backend...")

    # Connect to databases
    await db.connect()
    await qdrant.connect()
    await qdrant.create_collection_if_not_exists()

    # Run database migrations
    await run_migrations()

    print("[OK] All services connected and ready")

    yield

    # Shutdown
    print("[INFO] Shutting down...")
    await db.disconnect()
    print("[OK] Shutdown complete")


app = FastAPI(
    title="NeuroBot RAG Chatbot API",
    description="Intelligent Q&A system using Retrieval-Augmented Generation for Physical AI & Humanoid Robotics textbook",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware - Allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully"""
    print(f"[ERROR] Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": time.time(),
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation error",
            "message": str(exc),
            "timestamp": time.time(),
        },
    )


# Include Routers
app.include_router(health.router, tags=["health"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])


async def run_migrations():
    """Run database migrations"""
    try:
        # Read and execute migration SQL
        with open("src/database/migrations/001_initial_schema.sql", "r") as f:
            migration_sql = f.read()

        await db.execute(migration_sql)
        print("[OK] Database migrations applied")
    except Exception as e:
        print(f"[ERROR] Migration error: {e}")
        # Don't fail startup if migrations already applied
        pass


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NeuroBot RAG Chatbot API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )

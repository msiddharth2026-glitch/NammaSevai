import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import engine, Base
from .routers import schemes, assistant, admin, voice, feedback
from .seeds.seed_data import seed_database
from .middleware.security import (
    SecurityHeadersMiddleware,
    RateLimitingMiddleware,
    RequestSizeLimitMiddleware
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nammasevai.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Security audit check
    settings.check_production_security()
    
    # Startup: ensure tables exist, run migrations, and seed default schemes
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    try:
        from .database_migration import run_database_migrations
        run_database_migrations()
    except Exception as e:
        logger.error(f"Error during schema migration: {e}")
    logger.info("Running database seed check...")
    try:
        seed_database()
    except Exception as e:
        logger.error(f"Error during startup database seed: {e}")
    yield
    # Shutdown
    logger.info("Shutting down NammaSevai AI backend...")

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "NammaSevai AI is a voice-first government welfare scheme discovery assistant "
        "for Indian citizens, especially Tamil Nadu residents. "
        "Allows citizens to describe personal situations in Tamil, Tanglish or English "
        "and discover matching schemes using structured eligibility conditions."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security and Hardening Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RequestSizeLimitMiddleware, 
    max_body_bytes=settings.MAX_REQUEST_BODY_BYTES
)
app.add_middleware(
    RateLimitingMiddleware,
    requests_per_minute=settings.RATE_LIMIT_GENERAL_PER_MINUTE,
    match_requests_per_minute=settings.RATE_LIMIT_MATCH_PER_MINUTE,
    admin_requests_per_minute=settings.RATE_LIMIT_ADMIN_PER_MINUTE
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Error Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred. Please try again."
        }
    )

# Include API Routers
app.include_router(schemes.router)
app.include_router(assistant.router)
app.include_router(admin.router)
app.include_router(voice.router)
app.include_router(feedback.router)

# Health check
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected",
        "dialect": engine.dialect.name
    }

# Mount static folders if present in the workspace
workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_path = os.path.join(workspace_dir, "static")
assets_path = os.path.join(workspace_dir, "assets")
index_html_path = os.path.join(workspace_dir, "index.html")

if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    icon_path = os.path.join(assets_path, "bharatsevai_minimal.svg")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(assets_path, "nammasevai_minimal.svg")
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/svg+xml")
    return Response(status_code=204)

@app.get("/manifest.json", include_in_schema=False)
def manifest():
    manifest_path = os.path.join(workspace_dir, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/manifest+json")
    return Response(status_code=404)

@app.get("/", include_in_schema=False)
def serve_frontend_index():
    if os.path.exists(index_html_path):
        return FileResponse(index_html_path)
    return {"message": "BharatSevai AI Backend is running. Frontend index.html not found at workspace root."}

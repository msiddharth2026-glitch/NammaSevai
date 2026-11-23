from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .database import engine, Base
from .routers import schemes, assistant

# Create database tables if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NammaSevai AI API",
    description="Voice-First Welfare Scheme Discovery Engine for Citizens of Tamil Nadu",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(schemes.router)
app.include_router(assistant.router)

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "service": "NammaSevai AI FastAPI Backend",
        "db": "Connected",
        "ready": True
    }

"""
ApplyIQ FastAPI Microservice
Handles AI/ML operations: resume parsing, embeddings, re-ranking,
cover letter generation, email classification, and skill gap analysis.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

from routers import recommend, profile, embeddings, cover_letter, email_classifier, skill_gap, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize connections on startup."""
    print("🚀 ApplyIQ API starting up...")
    yield
    print("🛑 ApplyIQ API shutting down...")

app = FastAPI(
    title="ApplyIQ AI Microservice",
    description="AI/ML backend for job recommendation, resume parsing, and auto-apply",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Next.js web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000"),
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Internal API key auth
FASTAPI_SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY", "")

async def verify_internal_key(x_api_key: str = Header(None)):
    if FASTAPI_SECRET_KEY and x_api_key != FASTAPI_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")
    return x_api_key

# Register routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(embeddings.router, prefix="/embeddings", tags=["embeddings"])
app.include_router(recommend.router, prefix="/recommend", tags=["recommend"])
app.include_router(cover_letter.router, prefix="/cover-letter", tags=["cover-letter"])
app.include_router(email_classifier.router, prefix="/email", tags=["email"])
app.include_router(skill_gap.router, prefix="/skill-gap", tags=["skill-gap"])

@app.get("/")
async def root():
    return {"status": "ok", "service": "ApplyIQ AI Microservice", "version": "1.0.0"}

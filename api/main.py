import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from api.routers import upload, chat

load_dotenv()

# ─────────────────────────────────────────
# Logging setup
# ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("api")


# ─────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown"""
    logger.info("🚀 Video Editing Agent API starting...")
    logger.info(f"CLOUDINARY_CLOUD_NAME set: {'✅' if os.getenv('CLOUDINARY_CLOUD_NAME') else '❌'}")
    logger.info(f"CLOUDINARY_API_KEY set: {'✅' if os.getenv('CLOUDINARY_API_KEY') else '❌'}")
    logger.info(f"CLOUDINARY_API_SECRET set: {'✅' if os.getenv('CLOUDINARY_API_SECRET') else '❌'}")
    logger.info(f"OPENAI_API_KEY set: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    yield
    logger.info("👋 Video Editing Agent API shutting down...")


# ─────────────────────────────────────────
# App
# ─────────────────────────────────────────
app = FastAPI(
    title="Video Editing Agent API",
    description="AI-powered video editing agent that processes natural language editing requests",
    version="1.0.0",
    lifespan=lifespan
)


# ─────────────────────────────────────────
# CORS
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production → restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# Global error handler
# ─────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# ─────────────────────────────────────────
# Routers
# ─────────────────────────────────────────
app.include_router(upload.router)
app.include_router(chat.router)


# ─────────────────────────────────────────
# Health check
# ─────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "cloudinary": "set" if os.getenv("CLOUDINARY_CLOUD_NAME") else "missing",
        "openai_key": "set" if os.getenv("OPENAI_API_KEY") else "missing",
    }


# ─────────────────────────────────────────
# Run
# ─────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
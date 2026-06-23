from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .database import init_db
from .routers import auth, games, scores

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Snake Arena API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(scores.router, prefix="/api")
app.include_router(games.router, prefix="/api")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Check candidates in order: exact file, pre-rendered route index, SPA fallback
    for candidate in (
        FRONTEND_DIR / full_path,
        FRONTEND_DIR / full_path / "index.html",
        FRONTEND_DIR / "index.html",
    ):
        if candidate.is_file():
            return FileResponse(candidate)
    return JSONResponse({"detail": "Not found"}, status_code=404)

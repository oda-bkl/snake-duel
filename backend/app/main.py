from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, games, scores

app = FastAPI(title="Snake Arena API", version="1.0.0")

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

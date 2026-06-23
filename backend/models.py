from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class GameMode(str, Enum):
    walls = "walls"
    wrap = "wrap"


class User(BaseModel):
    id: str
    username: str


class AuthSession(BaseModel):
    user: User
    token: str


class Point(BaseModel):
    x: int
    y: int


class ScoreEntry(BaseModel):
    id: str
    userId: str
    username: str
    mode: GameMode
    score: int
    createdAt: int  # Unix ms


class ActiveGame(BaseModel):
    id: str
    userId: str
    username: str
    mode: GameMode
    score: int
    snake: list[Point]
    food: Point
    gridSize: int
    alive: bool
    updatedAt: int  # Unix ms


# ── Request bodies ────────────────────────────────────────────────────────────


class SignupRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class SubmitScoreRequest(BaseModel):
    mode: GameMode
    score: int


class UpsertGameRequest(BaseModel):
    id: str | None = None
    userId: str
    mode: GameMode
    score: int
    snake: list[Point]
    food: Point
    gridSize: int
    alive: bool

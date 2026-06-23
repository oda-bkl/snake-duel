from enum import Enum

from pydantic import BaseModel, Field


class GameMode(str, Enum):
    walls = "walls"
    wrap = "wrap"


class Point(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class User(BaseModel):
    id: str
    username: str


class AuthSession(BaseModel):
    user: User
    token: str


class ScoreEntry(BaseModel):
    id: str
    userId: str
    username: str
    mode: GameMode
    score: int = Field(ge=0)
    createdAt: int  # Unix ms


class ActiveGame(BaseModel):
    id: str
    userId: str
    username: str
    mode: GameMode
    score: int = Field(ge=0)
    snake: list[Point]
    food: Point
    gridSize: int = Field(ge=1)
    alive: bool
    updatedAt: int  # Unix ms


# ---- Request bodies ----


class SignupRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginRequest(BaseModel):
    username: str
    password: str


class ScoreSubmitRequest(BaseModel):
    mode: GameMode
    score: int = Field(ge=0)


class UpsertGameRequest(BaseModel):
    id: str
    userId: str
    mode: GameMode
    score: int = Field(ge=0)
    snake: list[Point]
    food: Point
    gridSize: int = Field(ge=1)
    alive: bool

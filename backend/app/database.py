"""SQLAlchemy engine, session, and ORM table definitions."""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import Boolean, Column, Integer, String, Text, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./snake_arena.db")

_is_sqlite = DATABASE_URL.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}
_engine_kwargs: dict = {"connect_args": _connect_args}

if DATABASE_URL == "sqlite:///:memory:":
    from sqlalchemy.pool import StaticPool
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)


class TokenRow(Base):
    __tablename__ = "tokens"

    token = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)


class ScoreRow(Base):
    __tablename__ = "scores"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(Integer, nullable=False)


class GameRow(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    snake = Column(Text, nullable=False)   # JSON array of {x, y}
    food = Column(Text, nullable=False)    # JSON {x, y}
    grid_size = Column(Integer, nullable=False)
    alive = Column(Boolean, nullable=False)
    updated_at = Column(Integer, nullable=False)


def init_db() -> None:
    Base.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

"""Store: persistent data via SQLAlchemy + in-memory SSE pub/sub."""

import asyncio
import json
import secrets
from dataclasses import dataclass

from sqlalchemy import func

from .database import (
    GameRow,
    ScoreRow,
    TokenRow,
    UserRow,
    get_session,
)
from .models import ActiveGame, GameMode, Point, ScoreEntry, User


@dataclass
class UserRecord:
    id: str
    username: str
    password_hash: str

    def to_user(self) -> User:
        return User(id=self.id, username=self.username)


def _row_to_user(row: UserRow) -> UserRecord:
    return UserRecord(id=row.id, username=row.username, password_hash=row.password_hash)


def _row_to_score(row: ScoreRow) -> ScoreEntry:
    return ScoreEntry(
        id=row.id,
        userId=row.user_id,
        username=row.username,
        mode=GameMode(row.mode),
        score=row.score,
        createdAt=row.created_at,
    )


def _row_to_game(row: GameRow) -> ActiveGame:
    return ActiveGame(
        id=row.id,
        userId=row.user_id,
        username=row.username,
        mode=GameMode(row.mode),
        score=row.score,
        snake=[Point(**p) for p in json.loads(row.snake)],
        food=Point(**json.loads(row.food)),
        gridSize=row.grid_size,
        alive=row.alive,
        updatedAt=row.updated_at,
    )


def _game_to_row(game: ActiveGame) -> GameRow:
    return GameRow(
        id=game.id,
        user_id=game.userId,
        username=game.username,
        mode=game.mode.value,
        score=game.score,
        snake=json.dumps([p.model_dump() for p in game.snake]),
        food=json.dumps(game.food.model_dump()),
        grid_size=game.gridSize,
        alive=game.alive,
        updated_at=game.updatedAt,
    )


class Store:
    def __init__(self) -> None:
        self._global_subs: list[asyncio.Queue] = []
        self._game_subs: dict[str, list[asyncio.Queue]] = {}

    # ---- Users ----

    def add_user(self, record: UserRecord) -> None:
        with get_session() as session:
            session.merge(UserRow(
                id=record.id,
                username=record.username,
                password_hash=record.password_hash,
            ))

    def get_user_by_username(self, username: str) -> UserRecord | None:
        with get_session() as session:
            row = session.query(UserRow).filter(
                func.lower(UserRow.username) == username.lower()
            ).first()
            return _row_to_user(row) if row else None

    def get_user_by_id(self, user_id: str) -> UserRecord | None:
        with get_session() as session:
            row = session.get(UserRow, user_id)
            return _row_to_user(row) if row else None

    def username_taken(self, username: str) -> bool:
        with get_session() as session:
            return session.query(UserRow).filter(
                func.lower(UserRow.username) == username.lower()
            ).count() > 0

    # ---- Tokens ----

    def create_token(self, user_id: str) -> str:
        token = "t_" + secrets.token_urlsafe(24)
        with get_session() as session:
            session.add(TokenRow(token=token, user_id=user_id))
        return token

    def get_user_by_token(self, token: str) -> UserRecord | None:
        with get_session() as session:
            row = session.get(TokenRow, token)
            if row is None:
                return None
            user_row = session.get(UserRow, row.user_id)
            return _row_to_user(user_row) if user_row else None

    def invalidate_token(self, token: str) -> None:
        with get_session() as session:
            row = session.get(TokenRow, token)
            if row:
                session.delete(row)

    # ---- Scores ----

    def add_score(self, entry: ScoreEntry) -> None:
        with get_session() as session:
            session.merge(ScoreRow(
                id=entry.id,
                user_id=entry.userId,
                username=entry.username,
                mode=entry.mode.value,
                score=entry.score,
                created_at=entry.createdAt,
            ))

    def get_leaderboard(self, mode: GameMode, limit: int) -> list[ScoreEntry]:
        with get_session() as session:
            rows = (
                session.query(ScoreRow)
                .filter(ScoreRow.mode == mode.value)
                .order_by(ScoreRow.score.desc())
                .limit(limit)
                .all()
            )
            return [_row_to_score(row) for row in rows]

    # ---- Games ----

    def upsert_game(self, game: ActiveGame) -> ActiveGame:
        with get_session() as session:
            session.merge(_game_to_row(game))
        self._notify_global()
        self._notify_game(game.id, game)
        return game

    def _seed_game(self, game: ActiveGame) -> None:
        """Insert a game without triggering SSE notifications."""
        with get_session() as session:
            session.merge(_game_to_row(game))

    def get_game(self, game_id: str) -> ActiveGame | None:
        with get_session() as session:
            row = session.get(GameRow, game_id)
            return _row_to_game(row) if row else None

    def list_active_games(self) -> list[ActiveGame]:
        with get_session() as session:
            rows = session.query(GameRow).order_by(GameRow.updated_at.desc()).all()
            return [_row_to_game(row) for row in rows]

    def delete_game(self, game_id: str) -> None:
        with get_session() as session:
            row = session.get(GameRow, game_id)
            if row:
                session.delete(row)
        self._notify_global()
        self._notify_game(game_id, None)

    # ---- SSE pub/sub ----

    def subscribe_global(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._global_subs.append(q)
        return q

    def unsubscribe_global(self, q: asyncio.Queue) -> None:
        try:
            self._global_subs.remove(q)
        except ValueError:
            pass

    def subscribe_game(self, game_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._game_subs.setdefault(game_id, []).append(q)
        return q

    def unsubscribe_game(self, game_id: str, q: asyncio.Queue) -> None:
        subs = self._game_subs.get(game_id, [])
        try:
            subs.remove(q)
        except ValueError:
            pass
        if not subs:
            self._game_subs.pop(game_id, None)

    def _notify_global(self) -> None:
        games = self.list_active_games()
        for q in list(self._global_subs):
            q.put_nowait(games)

    def _notify_game(self, game_id: str, game: ActiveGame | None) -> None:
        for q in list(self._game_subs.get(game_id, [])):
            q.put_nowait(game)


store = Store()

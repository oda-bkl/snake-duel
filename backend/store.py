from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

import bcrypt

from models import ActiveGame, GameMode, Point, ScoreEntry, User


def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _check_pw(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


@dataclass
class _UserRecord:
    user: User
    hashed_password: str


@dataclass
class Store:
    _users: dict[str, _UserRecord] = field(default_factory=dict)  # id -> record
    _usernames: dict[str, str] = field(default_factory=dict)  # username -> id
    _tokens: dict[str, str] = field(default_factory=dict)  # token -> user_id
    _scores: list[ScoreEntry] = field(default_factory=list)
    _games: dict[str, ActiveGame] = field(default_factory=dict)  # id -> game

    # ── Users ─────────────────────────────────────────────────────────────────

    def create_user(self, username: str, password: str) -> tuple[User, str]:
        if username in self._usernames:
            raise ValueError("username taken")
        uid = secrets.token_hex(8)
        user = User(id=uid, username=username)
        self._users[uid] = _UserRecord(user=user, hashed_password=_hash_pw(password))
        self._usernames[username] = uid
        token = self._issue_token(uid)
        return user, token

    def authenticate(self, username: str, password: str) -> tuple[User, str] | None:
        uid = self._usernames.get(username)
        if uid is None:
            return None
        record = self._users[uid]
        if not _check_pw(password, record.hashed_password):
            return None
        token = self._issue_token(uid)
        return record.user, token

    def revoke_token(self, token: str) -> None:
        self._tokens.pop(token, None)

    def user_for_token(self, token: str) -> User | None:
        uid = self._tokens.get(token)
        if uid is None:
            return None
        return self._users[uid].user

    def _issue_token(self, uid: str) -> str:
        token = secrets.token_urlsafe(32)
        self._tokens[token] = uid
        return token

    # ── Scores ────────────────────────────────────────────────────────────────

    def add_score(self, user: User, mode: GameMode, score: int) -> ScoreEntry:
        entry = ScoreEntry(
            id=secrets.token_hex(8),
            userId=user.id,
            username=user.username,
            mode=mode,
            score=score,
            createdAt=_now_ms(),
        )
        self._scores.append(entry)
        return entry

    def leaderboard(self, mode: GameMode, limit: int) -> list[ScoreEntry]:
        filtered = [s for s in self._scores if s.mode == mode]
        return sorted(filtered, key=lambda s: s.score, reverse=True)[:limit]

    # ── Active games ──────────────────────────────────────────────────────────

    def upsert_game(self, user: User, req_id: str | None, data: dict) -> ActiveGame:
        gid = req_id or secrets.token_hex(8)
        game = ActiveGame(
            id=gid,
            userId=user.id,
            username=user.username,
            updatedAt=_now_ms(),
            **data,
        )
        self._games[gid] = game
        return game

    def list_games(self) -> list[ActiveGame]:
        return list(self._games.values())

    def get_game(self, gid: str) -> ActiveGame | None:
        return self._games.get(gid)

    def end_game(self, gid: str) -> bool:
        if gid not in self._games:
            return False
        del self._games[gid]
        return True


# ── Module-level singleton ────────────────────────────────────────────────────

store = Store()


def reset_store() -> None:
    """Replace the singleton with a fresh seeded store. Used in tests."""
    global store
    store = Store()
    _seed(store)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _seed(s: Store) -> None:
    alice, _ = s.create_user("alice", "password123")
    bob, _ = s.create_user("bob", "letmein")
    charlie, _ = s.create_user("charlie", "secret")

    s.add_score(alice, GameMode.walls, 320)
    s.add_score(alice, GameMode.walls, 180)
    s.add_score(bob, GameMode.walls, 450)
    s.add_score(bob, GameMode.wrap, 210)
    s.add_score(charlie, GameMode.wrap, 390)
    s.add_score(charlie, GameMode.walls, 120)

    s.upsert_game(
        alice,
        None,
        dict(
            mode=GameMode.walls,
            score=60,
            snake=[Point(x=5, y=5), Point(x=4, y=5)],
            food=Point(x=8, y=3),
            gridSize=20,
            alive=True,
        ),
    )
    s.upsert_game(
        bob,
        None,
        dict(
            mode=GameMode.wrap,
            score=30,
            snake=[Point(x=10, y=10)],
            food=Point(x=2, y=15),
            gridSize=20,
            alive=True,
        ),
    )


_seed(store)

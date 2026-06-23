"""In-memory store with pub/sub for SSE."""

import asyncio
import secrets
import time
from dataclasses import dataclass, field

from .models import ActiveGame, GameMode, Point, ScoreEntry, User


@dataclass
class UserRecord:
    id: str
    username: str
    password_hash: str

    def to_user(self) -> User:
        return User(id=self.id, username=self.username)


class Store:
    def __init__(self) -> None:
        self.users: dict[str, UserRecord] = {}       # id -> record
        self._by_username: dict[str, str] = {}       # username -> id
        self.tokens: dict[str, str] = {}             # token -> user_id
        self.scores: dict[str, ScoreEntry] = {}      # id -> entry
        self.games: dict[str, ActiveGame] = {}       # id -> game

        # SSE subscribers
        self._global_subs: list[asyncio.Queue] = []
        self._game_subs: dict[str, list[asyncio.Queue]] = {}

    # ---- Users ----

    def add_user(self, record: UserRecord) -> None:
        self.users[record.id] = record
        self._by_username[record.username.lower()] = record.id

    def get_user_by_username(self, username: str) -> UserRecord | None:
        uid = self._by_username.get(username.lower())
        return self.users.get(uid) if uid else None

    def get_user_by_id(self, user_id: str) -> UserRecord | None:
        return self.users.get(user_id)

    def username_taken(self, username: str) -> bool:
        return username.lower() in self._by_username

    # ---- Tokens ----

    def create_token(self, user_id: str) -> str:
        token = "t_" + secrets.token_urlsafe(24)
        self.tokens[token] = user_id
        return token

    def get_user_by_token(self, token: str) -> UserRecord | None:
        uid = self.tokens.get(token)
        return self.users.get(uid) if uid else None

    def invalidate_token(self, token: str) -> None:
        self.tokens.pop(token, None)

    # ---- Scores ----

    def add_score(self, entry: ScoreEntry) -> None:
        self.scores[entry.id] = entry

    def get_leaderboard(self, mode: GameMode, limit: int) -> list[ScoreEntry]:
        entries = [s for s in self.scores.values() if s.mode == mode]
        entries.sort(key=lambda s: s.score, reverse=True)
        return entries[:limit]

    # ---- Games ----

    def upsert_game(self, game: ActiveGame) -> ActiveGame:
        self.games[game.id] = game
        self._notify_global()
        self._notify_game(game.id, game)
        return game

    def get_game(self, game_id: str) -> ActiveGame | None:
        return self.games.get(game_id)

    def list_active_games(self) -> list[ActiveGame]:
        games = list(self.games.values())
        games.sort(key=lambda g: g.updatedAt, reverse=True)
        return games

    def delete_game(self, game_id: str) -> None:
        self.games.pop(game_id, None)
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


# ---------------------------------------------------------------------------
# Singleton + seed data
# ---------------------------------------------------------------------------

store = Store()


def _now_ms() -> int:
    return int(time.time() * 1000)


def _seed(s: Store) -> None:
    from .security import hash_password

    seed_users = [
        ("u_alice01", "alice", "password123"),
        ("u_bob002",  "bob",   "letmein"),
        ("u_charlie3","charlie","snake4life"),
    ]
    for uid, uname, pw in seed_users:
        s.add_user(UserRecord(id=uid, username=uname, password_hash=hash_password(pw)))

    base = _now_ms() - 3_600_000  # 1 hour ago
    seed_scores = [
        ScoreEntry(id="s_a001", userId="u_alice01", username="alice",   mode=GameMode.walls, score=42, createdAt=base),
        ScoreEntry(id="s_a002", userId="u_alice01", username="alice",   mode=GameMode.wrap,  score=31, createdAt=base + 600_000),
        ScoreEntry(id="s_b001", userId="u_bob002",  username="bob",     mode=GameMode.walls, score=58, createdAt=base + 120_000),
        ScoreEntry(id="s_b002", userId="u_bob002",  username="bob",     mode=GameMode.wrap,  score=19, createdAt=base + 900_000),
        ScoreEntry(id="s_c001", userId="u_charlie3",username="charlie", mode=GameMode.walls, score=77, createdAt=base + 300_000),
        ScoreEntry(id="s_c002", userId="u_charlie3",username="charlie", mode=GameMode.wrap,  score=45, createdAt=base + 1_200_000),
    ]
    for entry in seed_scores:
        s.add_score(entry)

    now = _now_ms()
    seed_games = [
        ActiveGame(
            id="g_live1", userId="u_bob002", username="bob", mode=GameMode.walls,
            score=17,
            snake=[Point(x=5, y=5), Point(x=4, y=5), Point(x=3, y=5)],
            food=Point(x=8, y=3),
            gridSize=20, alive=True, updatedAt=now - 2_000,
        ),
        ActiveGame(
            id="g_live2", userId="u_charlie3", username="charlie", mode=GameMode.wrap,
            score=9,
            snake=[Point(x=10, y=10), Point(x=10, y=11)],
            food=Point(x=15, y=7),
            gridSize=20, alive=True, updatedAt=now - 5_000,
        ),
    ]
    for game in seed_games:
        s.games[game.id] = game  # bypass pub/sub during seed


_seed(store)

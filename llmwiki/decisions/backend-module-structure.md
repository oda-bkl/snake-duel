---
type: decision
title: Backend module structure
description: FastAPI app split into models, store, auth, and per-resource routers; store is a module-level singleton replaced by reset_store() in tests.
tags: [backend, fastapi, architecture, testing]
related_files: [backend/main.py, backend/models.py, backend/store.py, backend/auth.py, backend/routers/auth_router.py, backend/routers/scores_router.py, backend/routers/games_router.py]
timestamp: 2026-06-23
---

## Layout

```
backend/
├── main.py          # FastAPI app, CORS middleware, router registration
├── models.py        # Pydantic models (GameMode, User, AuthSession, ScoreEntry, ActiveGame) + request bodies
├── store.py         # In-memory Store dataclass + module-level singleton `store`
├── auth.py          # get_current_user / get_optional_user FastAPI dependencies
└── routers/
    ├── auth_router.py    # /api/auth/*
    ├── scores_router.py  # /api/scores/*
    └── games_router.py   # /api/games/*
```

## Singleton pattern

`store.py` exposes a module-level `store = Store()` that all routers import as `import store as st` and access via `st.store`. This indirection allows `reset_store()` to swap the singleton in tests:

```python
def reset_store() -> None:
    global store
    store = Store()
    _seed(store)
```

Tests use `autouse=True` on a `fresh_store` fixture so every test starts from a clean seeded state.

## Auth dependency pattern

`auth.py` provides two FastAPI dependencies:
- `get_current_user` — raises HTTP 401 if no valid bearer token
- `get_optional_user` — returns `User | None`, used for `GET /auth/session`

Both depend on FastAPI's `HTTPBearer(auto_error=False)` so unauthenticated requests return `None` credentials rather than an automatic 401 (allowing optional-auth routes to work).

## Routing prefix

All routers are mounted with `prefix="/api"` in `main.py`, matching the frontend's `httpClient.ts` which sends requests to `/api/*`.

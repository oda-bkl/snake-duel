---
type: api
title: Snake Duel REST API
description: Full contract for the FastAPI backend. Canonical source is openapi.yaml at the repo root.
tags: [backend, api, rest, openapi, auth, scores, games]
related_files: [openapi.yaml, backend/routers/auth_router.py, backend/routers/scores_router.py, backend/routers/games_router.py]
timestamp: 2026-06-23
---

Canonical spec: `openapi.yaml` at repo root (OpenAPI 3.1).

All paths are prefixed `/api`. Auth uses `Authorization: Bearer <token>`.

## Auth endpoints (no auth required unless noted)

| Method | Path | Auth | Body / Params | Returns |
|---|---|---|---|---|
| POST | `/api/auth/signup` | — | `{username, password}` | `AuthSession` |
| POST | `/api/auth/login` | — | `{username, password}` | `AuthSession` |
| POST | `/api/auth/logout` | Bearer | — | 204 |
| GET | `/api/auth/session` | — | — | `AuthSession \| null` |

`GET /auth/session` echoes the token from the request header back in the response body. This is how the frontend restores session on page load.

## Scores

| Method | Path | Auth | Body / Params | Returns |
|---|---|---|---|---|
| POST | `/api/scores` | Bearer | `{mode, score}` | `ScoreEntry` |
| GET | `/api/scores/leaderboard` | — | `?mode=walls\|wrap&limit=10` | `ScoreEntry[]` sorted desc |

## Active games

| Method | Path | Auth | Body / Params | Returns |
|---|---|---|---|---|
| GET | `/api/games/active` | — | — | `ActiveGame[]` |
| POST | `/api/games/active` | Bearer | `UpsertGameRequest` | `ActiveGame` |
| GET | `/api/games/active/{id}` | — | — | `ActiveGame \| null` |
| POST | `/api/games/active/{id}/end` | Bearer | — | 204 |

`POST /api/games/active` is an upsert: omit `id` to create, include it to update. Server sets `username` from the auth token and `updatedAt` from server time. The frontend polls `/api/games/active/{id}` every 2 s for spectating (see [decisions/subscribe-pattern.md](../decisions/subscribe-pattern.md)).

## Key types

```
AuthSession  { user: User, token: string }
User         { id: string, username: string }
ScoreEntry   { id, userId, username, mode, score, createdAt: ms }
ActiveGame   { id, userId, username, mode, score, snake: Point[], food: Point, gridSize, alive, updatedAt: ms }
GameMode     "walls" | "wrap"
```

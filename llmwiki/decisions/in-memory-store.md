---
type: decision
title: In-memory store (no database yet)
description: All data lives in a Store dataclass in process memory. Seeded with fake users, scores, and active games on startup. Swapped out for a fresh copy in tests via reset_store().
tags: [backend, store, in-memory, seed-data, testing]
related_files: [backend/store.py]
timestamp: 2026-06-23
---

## Structure

`Store` is a plain dataclass with five dicts/lists:

| Field | Type | Key |
|---|---|---|
| `_users` | `dict[str, _UserRecord]` | user id |
| `_usernames` | `dict[str, str]` | username → user id |
| `_tokens` | `dict[str, str]` | token → user id |
| `_scores` | `list[ScoreEntry]` | — |
| `_games` | `dict[str, ActiveGame]` | game id |

## Auth

Passwords hashed with `bcrypt` directly (not via passlib — see [gotchas/passlib-bcrypt-compat.md](../gotchas/passlib-bcrypt-compat.md)).

Tokens are `secrets.token_urlsafe(32)` values stored in `_tokens`. Multiple tokens per user are allowed (each login issues a new one). Logout revokes the specific token from the Authorization header.

`GET /auth/session` echoes the token back from the request so the frontend can restore session on page load. See [integrations/auth-token-flow.md](../integrations/auth-token-flow.md).

## Seed data

Three users (alice/password123, bob/letmein, charlie/secret), six scores across both modes, two active games. Seed runs at module import and again on `reset_store()`.

## Migration path

When a real database is added, replace `Store` methods with DB queries. The router layer and Pydantic models stay unchanged. The `reset_store()` pattern becomes `reset_db()` or a pytest fixture with transaction rollback.

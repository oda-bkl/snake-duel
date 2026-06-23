---
type: decision
title: Server owns game IDs; id is optional in upsertActiveGame
description: upsertActiveGame accepts optional id. First call omits id; server generates and returns it. Subsequent calls pass the stored id for updates.
tags: [api, active-games, ids]
related_files: [frontend/src/services/api.ts, frontend/src/services/mockApi.ts, frontend/src/routes/play.tsx]
timestamp: 2026-06-23
---

`ApiService.upsertActiveGame` signature:
```ts
upsertActiveGame(game: Omit<ActiveGame, "id" | "username" | "updatedAt"> & { id?: string }): Promise<ActiveGame>
```

In `play.tsx`:
- `gameIdRef` starts as `null`.
- First `upsertActiveGame` call passes `id: undefined`; the returned `ActiveGame.id` is stored in `gameIdRef.current`.
- Subsequent calls pass the stored id.
- `reset()` sets `gameIdRef.current = null` so a new game gets a fresh server-assigned id.
- `endActiveGame` checks `if (gameIdRef.current)` before calling.

`mockApi` generates a random id (`uid("g")`) when no id is provided, preserving backward compatibility.

The original code generated the id client-side with `Math.random()`, which would conflict with server-assigned ids.

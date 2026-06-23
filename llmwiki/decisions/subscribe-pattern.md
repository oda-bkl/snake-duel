---
type: decision
title: Callback-based subscribe* methods; polling in realApi, SSE/WS future
description: subscribeActiveGame and subscribeActiveGames use a (data) => void callback and return an unsubscribe function. Real backend uses 2s polling; SSE/WS is the intended upgrade.
tags: [api, real-time, polling, sse, websocket]
related_files: [frontend/src/services/api.ts, frontend/src/services/realApi.ts, frontend/src/routes/watch.tsx, frontend/src/routes/watch.$id.tsx]
timestamp: 2026-06-23
---

The `ApiService` interface uses a callback pattern for real-time game state:
```ts
subscribeActiveGame(id: string, cb: (game: ActiveGame | null) => void): () => void;
subscribeActiveGames(cb: (games: ActiveGame[]) => void): () => void;
```
Return value is an unsubscribe function. Callers use `useEffect(() => getApi().subscribeActiveGames(setGames), [])`.

**mockApi**: in-memory `Map` + `Set` of subscribers; synchronous notification on every upsert/end.

**realApi**: polling loop every `POLL_MS = 2000` ms using `getActiveGame` / `listActiveGames`. Loop breaks when game is not alive. Unsubscribe sets `cancelled = true`.

**OpenAPI note**: these methods have no REST mapping. The OpenAPI spec covers HTTP endpoints only. Real-time is a separate protocol concern (SSE on `/api/games/active/stream` or WebSocket).

**Upgrade path**: replace the `while (!cancelled)` polling loop in `realApi` with an EventSource or WebSocket without changing any consumer code.

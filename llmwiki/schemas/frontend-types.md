---
type: schema
title: Core TypeScript types — User, AuthSession, ScoreEntry, ActiveGame
description: All shared data types live in frontend/src/services/types.ts. These are the source of truth for the OpenAPI schema.
tags: [types, schema, openapi]
related_files: [frontend/src/services/types.ts]
timestamp: 2026-06-23
---

```ts
type GameMode = "walls" | "wrap";

interface User { id: string; username: string; }

interface AuthSession { user: User; token: string; }

interface ScoreEntry {
  id: string; userId: string; username: string;
  mode: GameMode; score: number; createdAt: number;  // epoch ms
}

interface ActiveGame {
  id: string; userId: string; username: string;
  mode: GameMode; score: number;
  snake: Array<{ x: number; y: number }>;
  food: { x: number; y: number };
  gridSize: number; alive: boolean; updatedAt: number;  // epoch ms
}
```

**Known mismatch**: `createdAt` and `updatedAt` are `number` (epoch ms) in the frontend. REST backends typically return ISO 8601 strings. A conversion layer will be needed in `realApi` or the types should be widened.

`ActiveGame.snake` is the full snake body array sent on every tick (110 ms). This is acceptable for mock but will be expensive over HTTP — consider sending snake length + head position only, or switching to WebSocket.

# Frontend Issues

## Bug fixes

### 1. Logout lands on `/auth` instead of `/`
`AppHeader.tsx:27` calls `router.navigate({ to: "/auth" })` instead of `"/"`. One-line fix.
- fix this

### 2. Light theme missing
`styles.css` `:root` block contains dark values (dark background, dark card). The `.dark` block is a slightly different dark theme. No light theme is defined at all, and there is no toggle button.
- add a light theme, add a toggle to the ui to switch

### 3. Watch games broken cross-client
`subscribeActiveGames` and `subscribeActiveGame` are in-memory only (`mockApi.ts:62-74`). Opening a second tab or refreshing shows no games. Real-time watching across clients needs WebSocket or SSE.
- leave it as is for now

---

## Security

### 4. Auth token is never used after login
`AuthContext.tsx` extracts `session.user` but discards `session.token`. When a real backend exists, every protected request needs `Authorization: Bearer <token>`. There is no mechanism to carry the token forward.
- fix it

### 5. No error handling on logout
`AppHeader.tsx:24-29`: the async logout has no try/catch. A failure leaves the user stuck as logged-in with no feedback.
- fix it
---

## Backend readiness (OpenAPI prep)

### 6. No HTTP client abstraction
No fetch wrapper, no base URL config. A real `ApiService` implementation needs a shared `apiFetch()` function that injects auth headers and normalizes errors (401, 422, 5xx).
- fix it

### 7. `subscribe*` methods cannot map to OpenAPI/HTTP
`subscribeActiveGame` and `subscribeActiveGames` use a callback pattern. REST cannot model this. The OpenAPI spec describes endpoints; the real-time layer (SSE or WebSocket) needs a separate protocol doc. The `ApiService` interface design is good for hiding this from consumers.
- fix it

### 8. `createdAt` is `number` (epoch ms), but backends return ISO strings
`types.ts:18`. The real implementation will need a conversion layer, or the type needs to be widened to `number | string`.
- ignore for now

### 9. Game IDs are client-generated
`play.tsx:25` creates `g_${Math.random()...}`. With a real backend, the server should own ID generation. This affects how `upsertActiveGame` is designed (create vs. update semantics).
- fix it

### 10. No API base URL env variable
The URL needs to come from `VITE_API_URL` (or similar) rather than being hardcoded per implementation.
- fix it

### 11. `upsertActiveGame` sends full game state on every tick
Every 110 ms, the full snake array is sent to the API (`play.tsx:67-80`). Fine for mock/localStorage but impractical for HTTP. Need to rethink for the real backend (WebSocket push, or separate heartbeat vs. state endpoints).
- ignore for now

---

## Code quality

### 12. Suppressed lint warning hides a stale-closure bug
`play.tsx:93`: `// eslint-disable-line react-hooks/exhaustive-deps` suppresses a missing-dep warning on the "handle death" effect. `user` and `running` are used inside but excluded from deps — score could be submitted with a stale `user` value.
- fix

### 13. Pointless `useMemo`
`play.tsx:95`: `const high = useMemo(() => state.score, [state.score])` just aliases `state.score`. Should be removed.
- fix

### 14. No error state in Leaderboard
`leaderboard.tsx:37`: if the API call rejects, `rows` stays `null` and the UI shows "Loading…" forever. Needs an error branch.
- fix
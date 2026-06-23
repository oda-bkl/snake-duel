---
type: decision
title: ApiService interface with mock and real implementations
description: The frontend defines a single ApiService interface; mockApi satisfies it via localStorage, realApi satisfies it via HTTP. setApi() swaps the implementation.
tags: [api, architecture, mock, testing]
related_files: [frontend/src/services/api.ts, frontend/src/services/mockApi.ts, frontend/src/services/realApi.ts]
timestamp: 2026-06-23
---

`src/services/api.ts` exports `ApiService` (interface), `getApi()`, `setApi()`, `getAuthToken()`, `setAuthToken()`.

- Default implementation: `mockApi` (localStorage + in-memory pub/sub).
- Real implementation: `realApi` (HTTP via `apiFetch`, polling for subscribe*).
- Swap at runtime: call `setApi(realApi)` at app startup to enable the real backend.

`setApi` is the only place to swap; all consumers call `getApi()` so they are unaware of the transport.

Token lifecycle is managed by `AuthContext` (calls `setAuthToken` on login/signup/logout/session restore) and consumed by `apiFetch` via `getAuthToken`.

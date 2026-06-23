---
type: integration
title: Auth token flow from login to HTTP requests
description: AuthContext calls setAuthToken on every auth state change; apiFetch reads it via getAuthToken to inject Authorization headers.
tags: [auth, token, http, context]
related_files: [frontend/src/contexts/AuthContext.tsx, frontend/src/services/api.ts, frontend/src/services/httpClient.ts]
timestamp: 2026-06-23
---

Token is a module-level variable in `api.ts`:
```ts
let _token: string | null = null;
export function getAuthToken() { return _token; }
export function setAuthToken(token: string | null) { _token = token; }
```

`AuthContext` manages lifecycle:
- On mount: `currentSession()` → `setAuthToken(s?.token ?? null)`
- On login/signup: `setAuthToken(s.token)`
- On logout: `setAuthToken(null)`

`apiFetch` (`httpClient.ts`) injects the token:
```ts
const token = getAuthToken();
headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) }
```

**Limitation**: token is in-memory only and lost on page refresh. The mock persists the full session (including token) in `localStorage` via `SESSION_KEY`, so `currentSession()` restores it. The real backend's `currentSession` endpoint must also return the token (or use HTTP-only cookies, in which case the `Authorization` header approach is replaced by `credentials: 'include'`).
